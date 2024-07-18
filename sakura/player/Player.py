# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Player(ABC):
    @abstractmethod
    def press(self, key, time_interval):
        pass
