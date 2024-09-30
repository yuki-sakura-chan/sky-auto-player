class Player:
    instruments: str
    type: str
    volume: float

    def __init__(self, instruments: str, type: str, volume: float):
        self.instruments = instruments
        self.type = type
        self.volume = volume


class Mapping:
    type: str

    def __init__(self, type: str):
        self.type = type


class ADB:
    path: str

    def __init__(self, path: str):
        self.path = path


class Config:
    file_path: str
    adb: ADB
    player: Player
    mapping: Mapping

    def __init__(self, file_path: str, adb: ADB, player: Player, mapping: Mapping):
        self.file_path = file_path
        self.adb = adb
        self.player = player
        self.mapping = mapping

