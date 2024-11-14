import codecs
import json
import os
import time
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
executor = ThreadPoolExecutor(max_workers=10)


# 获取指定目录下的文件列表
def get_file_list(file_path='resources') -> list:
    file_list = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            file_list.append(file)
    return file_list


# 加载json文件
def load_json(file_path) -> dict or None:
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']

    try:
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"读取JSON文件出错: {e}")
        return None


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


def play_song(notes, player: Player, key_mapping, play_cb: PlayCallback):
    prev_note_time = notes[0]['time']
    # 等待第一个音符按下的时间
    for note in notes:
        key = note['key']
        current_time = note['time']
        wait_time = current_time - prev_note_time
        time.sleep(wait_time / 1000)
        while play_cb.is_paused():
            time.sleep(1)
        # 检查是否终止播放（放在这里是为了让音符播放的时间更准确）
        if play_cb.is_termination():
            play_cb.termination_cb()
            return
        executor.submit(player.press, key_mapping[key], conf)
        if wait_time > 0:
            for item in listener_registers:
                item.listener(lambda: current_time,lambda: prev_note_time,lambda: wait_time,lambda: notes[-1]['time'], key, play_cb.is_paused)
        prev_note_time = note['time']
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
