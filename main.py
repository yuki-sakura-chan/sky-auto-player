import time

from pynput import keyboard

from sakura.components.TimeManager import TimeManager
from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.components.player.SakuraPlayer import SakuraPlayer
from sakura.config import conf
from sakura.db.JsonPick import load_json, get_file_list
from sakura.factory.PlayerFactory import get_player
from sakura.listener import register_listener

paused = True

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
    
    player = SakuraPlayer(song_notes, time_manager)
    player.play(p, km)
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
