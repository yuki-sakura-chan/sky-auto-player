import threading
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby
from typing import Callable

from sakura.components.TimeManager import TimeManager
from sakura.config import conf
from sakura.config.sakura_logging import logger
from sakura.factory.PlayerFactory import get_player
from sakura.interface.Player import Player


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


class SakuraPlayer:
    def __init__(self, song_notes: list, time_manager: TimeManager, cb: Callable[[], None] = lambda: None):
        self.song_notes = song_notes
        self.time_manager = time_manager
        self.is_playing = False
        self.is_finished = False
        self.cb = cb
        self.last_time = 0
        self.current_executor = None
        self.current_thread = None
        self.key_mapping = None
        self.player = None
        
    def play(self, player: Player, key_mapping: dict, start_time: int = None):
        self.player = player
        self.key_mapping = key_mapping
        self.stop()
        time.sleep(0.1)
        
        self.is_finished = False
        self.is_playing = True
        
        if start_time is not None:
            self.time_manager.set_current_time(start_time * 1000)
        else:
            self.time_manager.set_current_time(0)
            
        self.time_manager.set_duration(self.last_time)
        self.time_manager.set_playing(True)
        
        filtered_notes = [
            note for note in self.song_notes 
            if note['time'] >= self.time_manager.get_current_time()
        ]
        
        self._start_playback(filtered_notes, start_time)

    def pause(self):
        self.is_playing = False
        self.time_manager.set_playing(False)

    def stop(self):
        self.is_finished = True
        self.is_playing = False
        if self.current_executor:
            self.current_executor.shutdown(wait=False)
            self.current_executor = None
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=0.1)
        self.current_thread = None

    def continue_play(self):
        if not self.player or not self.key_mapping:
            logger.error("Player or key mapping not initialized")
            return
            
        self.stop()
        time.sleep(0.1)
            
        self.is_playing = True
        self.is_finished = False
        
        current_time = self.time_manager.get_current_time()
        filtered_notes = [
            note for note in self.song_notes 
            if note['time'] >= current_time
        ]
        
        self._start_playback(filtered_notes)

    def _start_playback(self, filtered_notes: list, start_time: int = None):
        if start_time is not None:
            self.time_manager.set_current_time(start_time * 1000)
        
        self.time_manager.set_duration(self.last_time)
        self.time_manager.set_playing(True)
        
        play_cb = PlayCallback(
            lambda: self.is_finished,
            lambda: not self.is_playing,
            self.callback,
            self.termination_cb
        )
        
        self.current_executor = ThreadPoolExecutor(max_workers=4)
        self.current_thread = threading.Thread(
            target=play_song,
            args=(filtered_notes, self.player, self.key_mapping, 
                  play_cb, self.time_manager, self.current_executor)
        )
        self.current_thread.daemon = True
        self.current_thread.start()

    def callback(self):
        self.is_playing = False
        self.cb()

    def termination_cb(self):
        pass
