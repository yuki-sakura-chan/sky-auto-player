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

    def listener(self, current_time: Callable[[], int], prev_time: Callable[[], int], 
             wait_time: Callable[[], int], last_time: Callable[[], int], 
             key, is_paused: Callable[[], bool]):
        if not self.thread_is_running:
            t = threading.Thread(
                target=manage_progress_thread,
                args=(current_time, last_time, is_paused, 
                      self.progress_slider, self.current_time_label,
                      self.remain_time_label, self.stop),
                daemon=True
            )
            t.start()
            self.thread_is_running = True

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
    try:
        current_second = int(current_time() / 1000)
        last_second = int(last_time() / 1000)
        
        while current_second <= last_second:
            if is_paused():
                stop()
                return
                
            current_second = int(current_time() / 1000)
            
            minutes = current_second // 60
            seconds = current_second % 60
            current_time_label.setText(f'{minutes}:{seconds:02d}')
            
            remain_seconds = last_second - current_second
            remain_minutes = remain_seconds // 60
            remain_seconds = remain_seconds % 60
            remain_time_label.setText(f'{remain_minutes}:{remain_seconds:02d}')
            
            progress_slider.setValue(current_second)
            
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in progress thread: {e}")
    finally:
        stop()
