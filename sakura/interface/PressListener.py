from abc import ABC, abstractmethod
from typing import Callable


class PressListener(ABC):

    @abstractmethod
    def listener(self, current_time, prev_time, wait_time, last_time, key, is_paused: Callable[[], bool]):
        pass
