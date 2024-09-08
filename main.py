# -*- coding: utf-8 -*-
import codecs
import json
import os
import sys
import threading
import time

import chardet

from pynput import keyboard
from sakura.config.Config import Config, conf
from sakura.mapper.JsonMapper import JsonMapper
from sakura.factory.PlayerFactory import get_player
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


def play_song(notes):
    prev_note_time = notes[0]['time']
    # 等待第一个音符按下的时间
    for note in notes:
        key = note['key']
        wait_time = note['time'] - prev_note_time
        time.sleep(wait_time / 1000)
        while paused:
            time.sleep(1)
        threading.Thread(target=player.press, args=(key_mapping[key],)).start()
        prev_note_time = note['time']


# 获取最后一个音符，并且获取时长
def get_last_note_time(song_notes) -> int:
    last_note = song_notes[-1]
    return int(last_note['time'] / 1000)


# 显示进度条
def show_progress_bar(current_time, total_time):
    print('\r', end='')
    # 获取时间百分比
    print(f'时间进度{int(current_time / total_time * 100)}%：'
          f'{'▋' * int(current_time / total_time * 50)}'
          f'{' ' * (50 - int(current_time / total_time * 50))}'
          f'{current_time}s/{total_time}s', end='')
    while paused:
        time.sleep(1)
    current_time += 1
    sys.stdout.flush()
    time.sleep(1)
    if current_time <= total_time:
        show_progress_bar(current_time, total_time)


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
    json_list = load_json(f'{file_path}/{file_list[select_index_int - 1]}')
    song_notes = json_list[0]['songNotes']
    keyboard.Listener(on_press=listener).start()
    thread = threading.Thread(target=show_progress_bar, args=(0, get_last_note_time(song_notes),))
    # 设置为守护线程
    thread.daemon = True
    thread.start()
    play_song(song_notes)
    thread.join()
    # 等待播放完全结束
    time.sleep(2)


if __name__ == '__main__':
    Config.load_yaml_config()
    mapping_dict = {
        "json": JsonMapper()
    }
    mapping_type = conf.mapping['type']
    key_mapping = mapping_dict[mapping_type].get_key_mapping()
    player_type = conf.player['type']
    player = get_player(player_type)
    main()
