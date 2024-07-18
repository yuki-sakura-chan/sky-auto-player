# -*- coding: utf-8 -*-
import os
from sakura.config.Config import conf

import pygame

from sakura.player.Player import Player


class Demo(Player):
    key_mapping = {
        "C": "0", "D": "1", "E": "2", "F": "3", "G": "4",
        "A": "5", "B": "6", "C1": "7", "D1": "8", "E1": "9",
        "F1": "10", "G1": "11", "A1": "12", "B1": "13", "C2": "14"
    }
    audio = []
    channels = []
    num_channels = 0

    def press(self, key, time_interval):
        note = self.key_mapping[key]
        self.channels[int(note) % len(self.channels)].play(self.audio[int(note)])

    def __init__(self):
        cwd = os.getcwd()
        pygame.init()
        pygame.mixer.init()
        self.num_channels = pygame.mixer.get_num_channels()
        self.channels = [pygame.mixer.Channel(i) for i in range(self.num_channels)]
        for i in range(15):
            self.audio.append(
                pygame.mixer.Sound(os.path.join(cwd, f'resources/Instruments/{conf.player['instruments']}/{i}.wav')))
