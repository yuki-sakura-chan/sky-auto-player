# 一个按键只负责一个功能，新注册的按键会覆盖旧的按键
from typing import Callable, Any

from pynput import keyboard

from sakura.config.sakura_logging import logger


class ListenerDetail:
    describe: str
    func: Callable

    def __init__(self, func: Callable, describe: str = ''):
        self.describe = describe
        self.func = func


listener_dict: dict[Any, ListenerDetail] = {}


def listener(key):
    logger.debug(f'按键 {key} 被按下')
    if key in listener_dict:
        listener_dict[key].func()


# 开始监听
keyboard.Listener(on_press=listener).start()


# 注册监听
def register_listener(key, func: Callable, describe: str = ''):
    listener_dict[key] = ListenerDetail(func, describe)
