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
from sakura.registrar.listener_registers import listener_registers

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
def load_json(file_path: str) -> dict or None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read(1024))['encoding']
    try:
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode JSON file {file_path} using detected encoding {encoding}: {e}")


class PlayCallback:
    is_termination = Callable[[], bool]
    is_paused = Callable[[], bool]
    cb = Callable[[], None]
    termination_cb = Callable[[], None]

    def __init__(self, is_termination: Callable[[], bool] = False, is_paused: Callable[[], bool] = False,
                 cb: Callable[[], None] = None, termination_cb: Callable[[], None] = None):
        self.is_termination = is_termination
        self.is_paused = is_paused
        self.cb = cb
        self.termination_cb = termination_cb


def play_song(notes: list[dict], player: Player, key_mapping: dict, play_cb: PlayCallback, prev_note_time: int = None):
    try:
        grouped_notes = [
            (t, [note['key'] for note in group])
            for t, group in groupby(notes, key=lambda x: x['time'])
        ]
    except (IndexError, KeyError, TypeError) as e:
        raise ValueError(f"Invalid notes data: missing required key {e}")
    # 等待第一个音符按下的时间
    if prev_note_time is None:
        prev_note_time = grouped_notes[0][0]
    
    for i, (current_time, note_group) in enumerate(grouped_notes):
        wait_time = (current_time - prev_note_time) / 1000
        if wait_time < 0:
            continue
        
        time.sleep(wait_time)
        while play_cb.is_paused():
            time.sleep(0.1)
        
        # 检查是否终止播放（放在这里是为了让音符播放的时间更准确）
        if play_cb.is_termination():
            play_cb.termination_cb()
            return
        for key in note_group:
            mapped_key = key_mapping.get(key)
            if mapped_key:
                executor.submit(player.press, mapped_key, conf)
                for item in listener_registers:
                    item.listener(lambda: current_time, lambda: prev_note_time, lambda: wait_time,
                        lambda: notes[-1]['time'], mapped_key, play_cb.is_paused,)
        prev_note_time = current_time
    # 播放完毕后的回调
    play_cb.cb()


def listener():
    global paused
    paused = not paused


def main():
    file_path = conf.file_path
    file_list = get_file_list(file_path)
    for index, file in enumerate(file_list):
        print(index + 1, file)
    select_index = input('输入数字选择歌曲：')
    select_index_int = int(select_index)
    if select_index_int > len(file_list):
        print("输入有误，程序结束")
        return
    file_name = file_list[select_index_int - 1]
    json_list = load_json(f'{file_path}/{file_name}')
    song_notes = json_list[0]['songNotes']
    register_listener(keyboard.Key.f4, listener, '暂停/继续')
    play_song(song_notes, p, km, PlayCallback(lambda: False, lambda: paused, lambda: None, lambda: None))
    time.sleep(2)


if __name__ == '__main__':
    mapping_dict = {
        "json": JsonMapper()
    }
    mapping_type = conf.mapping.type
    km = mapping_dict[mapping_type].get_key_mapping()
    player_type = conf.player.type
    p = get_player(player_type, conf)
    main()
