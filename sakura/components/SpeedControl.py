import time
from typing import Callable

from sakura.interface.PressListener import PressListener


class SpeedControl(PressListener):

    get_sleep_time: Callable[[], float] = lambda : 0

    def __init__(self, get_sleep_time: Callable[[], float]):
        self.get_sleep_time = get_sleep_time


    def listener(self, current_time: Callable[[], int], prev_time: Callable[[], int], wait_time: Callable[[], int], last_time: Callable[[], int], key, is_paused: Callable[[], bool]):
        time.sleep(self.get_sleep_time())
