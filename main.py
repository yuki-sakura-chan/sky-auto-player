import codecs
import json
import os
import time
from itertools import groupby
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import chardet
from pynput import keyboard

from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.config import conf
from sakura.factory.PlayerFactory import get_player
from sakura.interface.Player import Player
from sakura.listener import register_listener
from sakura.config.sakura_logging import logger
from sakura.registrar.listener_registers import listener_registers
from sakura.components.TimeManager import TimeManager

paused = True

# 创建一个线程池，可以设置 max_workers 来控制最大并发线程数
executor = ThreadPoolExecutor(max_workers=15)


# 获取指定目录下的文件列表
def get_file_list(file_path: str = 'resources') -> list[str]:
    if not os.path.isdir(file_path):
        raise ValueError(f"Directory does not exist: {file_path}")
    allowed_extensions = ['.json', '.txt', '.skysheet']
    return [
        file
        for root, dirs, files in os.walk(file_path)
        for file in files
        if os.path.splitext(file)[1].lower() in allowed_extensions
    ]


# 加载json文件
def load_json(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            encoding = chardet.detect(f.read(1024))['encoding']
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode JSON file {file_path} using detected encoding {encoding}: {e}")


class PlayCallback:
    def __init__(self, is_termination: Callable[[], bool] = lambda: False, 
                 is_paused: Callable[[], bool] = lambda: False,
                 cb: Callable[[], None] = None, 
                 termination_cb: Callable[[], None] = None):
        self.is_termination = is_termination
        self.is_paused = is_paused
        self.cb = cb
        self.termination_cb = termination_cb


def play_song(notes: list[dict], player: Player, key_mapping: dict, 
              play_cb: PlayCallback, time_manager: TimeManager, executor: ThreadPoolExecutor):
    try:
        grouped_notes = [
            (t, [note['key'] for note in group])
            for t, group in groupby(notes, key=lambda x: x['time'])
        ]
        
        current_time = time_manager.get_current_time()
        
        for note_time, note_group in grouped_notes:
            if play_cb.is_termination():
                return
                
            if note_time < current_time:
                continue
                
            wait_time = (note_time - current_time) / 1000
            time.sleep(wait_time)
            
            while play_cb.is_paused():
                if play_cb.is_termination():
                    return
                time.sleep(0.1)
                
            current_time = note_time
            time_manager.set_current_time(current_time)
            
            for key in note_group:
                if mapped_key := key_mapping.get(key):
                    try:
                        executor.submit(player.press, mapped_key, conf)
                    except RuntimeError:
                        return
                        
        if play_cb.cb:
            play_cb.cb()
    except Exception as e:
        logger.error(f"Error in play_song: {e}")


def listener() -> None:
    global paused
    paused = not paused


def main() -> None:
    file_path = conf.file_path
    file_list = get_file_list(file_path)
    for index, file in enumerate(file_list, 1):
        print(f"{index}. {file}")
    try:
        select_index = int(input('Enter the number to select a song: '))
        if not 1 <= select_index <= len(file_list):
            raise ValueError("Invalid input")
    except ValueError:
        print("Invalid input. Program terminated.")
        return
    
    file_name = file_list[select_index - 1]
    json_list = load_json(f'{file_path}/{file_name}')
    song_notes = json_list[0]['songNotes']
    register_listener(keyboard.Key.f4, listener, 'Pause/Resume')
    play_song(song_notes, p, km, PlayCallback(lambda: False, lambda: paused, lambda: None, lambda: None), time_manager, executor)
    time.sleep(2)


if __name__ == '__main__':
    try:
        mapping_dict = {
            "json": JsonMapper()
        }
        mapping_type = conf.mapping.type
        km = mapping_dict[mapping_type].get_key_mapping()
        player_type = conf.player.type
        p = get_player(player_type, conf)
        time_manager = TimeManager()
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
