from abc import ABC, abstractmethod

from sakura.config import Config


class Player(ABC):
    conf: any

    @abstractmethod
    def press(self, key: str, conf: Config):
        pass

    @abstractmethod
    def __init__(self, conf: Config):
        self.conf = conf
        pass
