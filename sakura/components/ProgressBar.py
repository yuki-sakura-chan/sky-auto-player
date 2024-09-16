import sys

from sakura.interface.PressListener import PressListener


class ProgressBar(PressListener):
    current_second: int = 0

    def listener(self, current_time, prev_time, wait_time, last_time, key):
        print('\r', end='')
        # 获取时间百分比
        print(f'弹奏进度{int(current_time / last_time * 100)}%：'
              f'{'▋' * int(current_time / last_time * 50)}'
              f'{' ' * (50 - int(current_time / last_time * 50))}'
              f'共{int(last_time) / 1000}s', end='')
        sys.stdout.flush()


