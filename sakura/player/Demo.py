# -*- coding: utf-8 -*-
from sakura.player.Player import Player


class Demo(Player):

    key_mapping = {}

    def press(self, key):
        print(f"Demo: {key} pressed")

