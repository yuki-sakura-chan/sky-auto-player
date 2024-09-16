import os

from sakura.interface.Player import Player

adb_path = ''


# 模拟点击屏幕的方法
def click(x, y):
    os.system(f'{adb_path} shell input tap {x} {y}')


class AndroidPlayer(Player):
    key_mapping = {
        "C": {"x": 700, "y": 225}, "D": {"x": 955, "y": 235}, "E": {"x": 1200, "y": 245}, "F": {"x": 1445, "y": 255},
        "G": {"x": 1700, "y": 265},
        "A": {"x": 700, "y": 430}, "B": {"x": 950, "y": 440}, "C1": {"x": 1200, "y": 450}, "D1": {"x": 1445, "y": 460},
        "E1": {"x": 1700, "y": 470},
        "F1": {"x": 700, "y": 710}, "G1": {"x": 950, "y": 720}, "A1": {"x": 1200, "y": 730},
        "B1": {"x": 1445, "y": 740},
        "C2": {"x": 1700, "y": 750}
    }

    def press(self, key, conf):
        click(self.key_mapping[key]["x"], self.key_mapping[key]["y"])

    def __init__(self, conf):
        global adb_path
        adb_path = conf.adb['path']
        # 判断是否是绝对路径
        if not os.path.isabs(adb_path):
            adb_path = os.path.join(os.getcwd(), adb_path)
