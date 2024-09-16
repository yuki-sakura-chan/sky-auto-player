from abc import ABC, abstractmethod

class PressListener(ABC):

    @abstractmethod
    def listener(self, current_time, prev_time, wait_time, last_time, key):
        pass
