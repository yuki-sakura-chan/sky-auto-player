from abc import ABC, abstractmethod


class Player(ABC):
    @abstractmethod
    def press(self, key: str, conf):
        pass
