import pydirectinput

from sakura.interface.Player import Player


class WindowsPlayer(Player):
    key_mapping = {
        "C4": "y", "D4": "u", "E4": "i", "F4": "o", "G4": "p",
        "A4": "h", "B4": "j", "C5": "k", "D5": "l", "E5": ";",
        "F5": "n", "G5": "m", "A5": ",", "B5": ".", "C6": "/"
    }

    def __init__(self, conf: any):
        pass

    def press(self, key, conf):
        note = self.key_mapping[key]
        pydirectinput.press(note)

    def cleanup(self):
        pass
