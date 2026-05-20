
from pydantic import BaseModel


class Player(BaseModel):
    instruments: str = 'Piano'
    type: str = 'demo'
    volume: float = 0.5


class Mapping(BaseModel):
    type: str = 'json'


class ADB(BaseModel):
    path: str = ''


class Control(BaseModel):
    speed: str = '0.01'

class DB(BaseModel):
    name: str = 'sap.db'

class Config(BaseModel):
    file_path: str = 'resources/music/studio/txt'
    region: str = 'zh-CN'
    adb: ADB = ADB()
    player: Player = Player()
    mapping: Mapping = Mapping()
    control: Control = Control()
    db: DB = DB()
