import threading
import time
from typing import Callable

from qfluentwidgets import Slider, CaptionLabel

from sakura.config.sakura_logging import logger
from sakura.interface.PressListener import PressListener


class SakuraPlayBaseBar(PressListener):
    progress_slider: Slider
    current_time_label: CaptionLabel
    remain_time_label: CaptionLabel

    def __init__(self, progress_slider: Slider, current_time_label: CaptionLabel, remain_time_label: CaptionLabel):
        self.progress_slider = progress_slider
        self.current_time_label = current_time_label
        self.remain_time_label = remain_time_label

    def listener(self, current_time, prev_time, wait_time, last_time, key, is_paused: Callable[[], bool]):
        pass


class SakuraProgressBar(SakuraPlayBaseBar):
    thread_is_running = False

    def listener(self, current_time: Callable[[], int], prev_time: Callable[[], int], wait_time: Callable[[], int], last_time: Callable[[], int], key, is_paused: Callable[[], bool]):
        if not self.thread_is_running:
            t = threading.Thread(target=manage_progress_thread, args=(
                current_time, last_time, is_paused, self.progress_slider, self.current_time_label,
                self.remain_time_label, self.stop,))
            t.daemon = True
            t.start()
            self.thread_is_running = True

    def stop(self):
        self.thread_is_running = False


def manage_progress_thread(current_time, last_time, is_paused: Callable[[], bool], progress_slider: Slider,
                           current_time_label: CaptionLabel, remain_time_label: CaptionLabel, stop: Callable[[], None]):
    # 计算当前秒
    current_second = int(current_time() / 1000)
    # 计算当前秒数的余数
    remain_second = current_time() % 1000
    time.sleep(remain_second / 1000)
    # 计算剩余秒数
    last_second = int(last_time() / 1000)
    while current_second <= last_second:
        if is_paused():
            stop()
            return
        current_second = int(current_time() / 1000)
        last_second = int(last_time() / 1000)
        # 更新进度条
        progress_slider.setValue(int(current_second / last_second * 100))
        # 更新当前时间
        current_time_label.setText(f'{current_second // 60}:{current_second % 60:02d}')
        # 更新剩余时间
        logger.info("current_second: %s, last_second: %s", current_second, last_second)
        remain_time_label.setText(
            f'{(last_second - current_second) // 60}:{(last_second - current_second) % 60:02d}')
        time.sleep(0.5)
    remain_time_label.setText('0:00')
    progress_slider.setValue(100)
    stop()
