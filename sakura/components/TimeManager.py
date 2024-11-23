from typing import Callable
from PySide6.QtCore import QObject, Signal

class TimeManager(QObject):
    timeChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self._current_time = 0
        self._total_duration = 0
        self._is_playing = False
        self._force_update = False
        
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
        
    def is_playing(self) -> bool:
        return self._is_playing