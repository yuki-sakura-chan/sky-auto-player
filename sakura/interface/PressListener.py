from abc import ABC, abstractmethod
from typing import Callable


class PressListener(ABC):

    @abstractmethod
    def listener(self, current_time: Callable[[], int], prev_time: Callable[[], int], wait_time: Callable[[], int],
                 last_time: Callable[[], int], key, is_paused: Callable[[], bool]):
        pass
