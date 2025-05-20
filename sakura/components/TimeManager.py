import threading
import time

from PySide6.QtCore import QObject, Signal


class TimeManager(QObject):
    timeChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self._current_time = 0
        self._total_duration = 0
        self._update_interval = 10
        self._is_playing = False
        self._force_update = False
        self._update_thread = None
        self._stop_thread = False
        self._thread_lock = threading.Lock()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        with self._thread_lock:
            self._stop_thread = True
            self._is_playing = False
        if self._update_thread:
            self._update_thread.join(timeout=0.2)
            self._update_thread = None

    def _update_time(self):
        last_update = time.time() * 1000
        while not self._stop_thread:
            current = time.time() * 1000
            with self._thread_lock:
                if self._is_playing:
                    elapsed = current - last_update
                    self.set_current_time(min(
                        self._current_time + int(elapsed),
                        self._total_duration
                    ))
            last_update = current
            time.sleep(self._update_interval / 1000)

    def set_update_interval(self, interval_ms: int):
        self._update_interval = max(10, interval_ms)
        
    def set_current_time(self, time_ms: int):
        if not self._force_update and self._current_time != time_ms:
            self._current_time = time_ms
            self.timeChanged.emit(time_ms)
            
    def force_set_time(self, time_ms: int):
        self._force_update = True
        self._current_time = time_ms
        self.timeChanged.emit(time_ms)
        self._force_update = False
        
    def set_duration(self, duration_ms: int):
        self._total_duration = duration_ms
        
    def get_current_time(self) -> int:
        return self._current_time
        
    def get_duration(self) -> int:
        return self._total_duration
        
    def set_playing(self, is_playing: bool):
        self._is_playing = is_playing
        if is_playing and not self._update_thread:
            self._stop_thread = False
            self._update_thread = threading.Thread(target=self._update_time, daemon=True)
            self._update_thread.start()
        elif not is_playing:
            self.cleanup()
        
    def is_playing(self) -> bool:
        return self._is_playing
