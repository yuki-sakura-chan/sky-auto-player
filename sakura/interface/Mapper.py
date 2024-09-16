from abc import ABC, abstractmethod


class Mapper(ABC):

    @abstractmethod
    def get_key_mapping(self):
        pass
