import time

from PySide6.QtCore import QObject, Signal

# Ticks Per Quarter note
TPQ = 480


class TickManager(QObject):
    tick_changed = Signal(int)

    def __init__(self, bpm=60):
        super().__init__()
        self.pause_total = 0
        self.pause_start = 0
        self.bpm = bpm
        self.start_time = 0
        self.start_tick = 0

    def set_bpm(self, bpm):
        self.bpm = bpm

    def set_start_tick(self, tick):
        self.start_tick = tick

    def reset_pause(self):
        self.pause_start = 0
        self.pause_total = 0

    def pause(self):
        self.pause_start = time.perf_counter()

    def tick_continue(self):
        if self.pause_start > 0:
            self.pause_total += time.perf_counter() - self.pause_start

    def start(self):
        self.start_time = time.perf_counter()

    def current_tick(self):
        now = time.perf_counter()
        elapsed = (
                now
                - self.start_time
                - self.pause_total
        )
        tick = int(elapsed * self.tick_per_second() + self.start_tick)
        self.tick_changed.emit(tick)
        return tick

    def tick_conver(self, time_ms: int) -> int:
        return int(time_ms / 1000 * (self.bpm * TPQ / 60))

    def time_conver(self, tick: int) -> int:
        return int((tick * 60) / (self.bpm * TPQ)) * 1000

    def tick_per_second(self) -> float:
        return (self.bpm * TPQ) / 60
