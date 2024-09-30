import codecs
import json
import os
import threading
import time
from typing import Callable

import chardet
from pynput import keyboard

from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.config import conf
from sakura.factory.PlayerFactory import get_player
from sakura.interface.Player import Player
from sakura.registrar.listener_registers import listener_registers

paused = True


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


def play_song(notes, player: Player, key_mapping, playing_name: Callable[[], str],
              is_paused: Callable[[], bool] = lambda: False):
    prev_note_time = notes[0]['time']
    current_playing_name = playing_name()
    # 等待第一个音符按下的时间
    for note in notes:
        if current_playing_name != playing_name():
            return
        key = note['key']
        current_time = note['time']
        wait_time = current_time - prev_note_time
        if wait_time > 0:
            for item in listener_registers:
                item.listener(current_time, prev_note_time, wait_time, notes[-1]['time'], key)
        time.sleep(wait_time / 1000)
        while is_paused():
            time.sleep(1)
        threading.Thread(target=player.press, args=(key_mapping[key], conf,)).start()
        prev_note_time = note['time']


def listener(key):
    global paused
    if key == keyboard.Key.f4:
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
    keyboard.Listener(on_press=listener).start()
    play_song(song_notes, p, km,lambda: file_name, lambda: paused)
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
