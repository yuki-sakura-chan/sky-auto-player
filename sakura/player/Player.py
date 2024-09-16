from abc import ABC, abstractmethod


class Player(ABC):
    conf: any

    @abstractmethod
    def press(self, key: str, conf):
        pass

    @abstractmethod
    def __init__(self, conf: any):
        self.conf = conf
        pass
