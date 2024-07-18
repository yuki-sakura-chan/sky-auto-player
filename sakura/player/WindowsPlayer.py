# -*- coding: utf-8 -*-
import time

from sakura.player.Player import Player
import pydirectinput


class WindowsPlayer(Player):
    key_mapping = {
        "C": "y", "D": "u", "E": "i", "F": "o", "G": "p",
        "A": "h", "B": "j", "C1": "k", "D1": "l", "E1": ";",
        "F1": "n", "G1": "m", "A1": ",", "B1": ".", "C2": "/"
    }

    def press(self, key, time_interval):
        note = self.key_mapping[key]
        pydirectinput.keyUp(note)
        time.sleep(time_interval)
        pydirectinput.keyDown(note)
