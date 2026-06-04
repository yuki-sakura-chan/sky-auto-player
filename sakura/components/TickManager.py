import time

from PySide6.QtCore import QObject, Signal

# Ticks Per Quarter note
TPQ = 480


class TickManager(QObject):
    tick_changed = Signal(int)
    bpm_changed = Signal()

    def __init__(self, bpm=60):
        super().__init__()
        self._pause_total = 0
        self._pause_start = 0
        self._bpm = bpm
        self._start_time = 0
        self._start_tick = 0

    def set_bpm(self, bpm):
        self._bpm = bpm
        self.bpm_changed.emit()

    def update_bpm(self, bpm):
        if self._bpm + bpm <= 0:
            return
        self._bpm += bpm
        self.bpm_changed.emit()

    def set_start_tick(self, tick):
        self._start_tick = tick

    def reset_pause(self):
        self._pause_start = 0
        self._pause_total = 0

    def pause(self):
        self._pause_start = time.perf_counter()

    def tick_continue(self):
        if self._pause_start > 0:
            self._pause_total += time.perf_counter() - self._pause_start

    def start(self):
        self._start_time = time.perf_counter()

    def current_tick(self):
        now = time.perf_counter()
        elapsed = (
                now
                - self._start_time
                - self._pause_total
        )
        tick = int(elapsed * self.tick_per_second() + self._start_tick)
        self.tick_changed.emit(tick)
        return tick

    def tick_conver(self, time_ms: int) -> int:
        return int(time_ms / 1000 * (self._bpm * TPQ / 60))

    def time_conver(self, tick: int) -> int:
        return int((tick * 60) / (self._bpm * TPQ)) * 1000

    def tick_per_second(self) -> float:
        return (self._bpm * TPQ) / 60
