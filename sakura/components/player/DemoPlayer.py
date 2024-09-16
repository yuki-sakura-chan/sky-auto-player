import os

import pygame

from sakura.interface.Player import Player


class DemoPlayer(Player):
    key_mapping = {
        "C": "0", "D": "1", "E": "2", "F": "3", "G": "4",
        "A": "5", "B": "6", "C1": "7", "D1": "8", "E1": "9",
        "F1": "10", "G1": "11", "A1": "12", "B1": "13", "C2": "14"
    }
    audio = []
    channels = []
    num_channels = 0
    press_num = 0

    def press(self, key, conf):
        self.press_num += 1
        note = self.key_mapping[key]
        channel = self.channels[self.press_num % self.num_channels]
        channel.set_volume(conf.get('player.volume'))
        channel.play(self.audio[int(note)])

    def __init__(self, conf):
        cwd = os.getcwd()
        pygame.init()
        pygame.mixer.init()
        self.num_channels = pygame.mixer.get_num_channels()
        self.channels = [pygame.mixer.Channel(i) for i in range(self.num_channels)]
        for i in range(15):
            self.audio.append(
                pygame.mixer.Sound(os.path.join(cwd, f'resources/Instruments/{conf.get('player.instruments')}/{i}.wav')))

    def __del__(self):
        pygame.quit()
        pygame.mixer.quit()
        print("\nDemo player is destroyed.")
