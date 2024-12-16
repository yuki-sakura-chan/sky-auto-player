from pydantic import BaseModel


class Player(BaseModel):
    source: str
    instruments: str
    type: str
    volume: float


class Mapping(BaseModel):
    type: str


class ADB(BaseModel):
    path: str


class Control(BaseModel):
    speed: str

class Config(BaseModel):
    file_path: str
    adb: ADB
    player: Player
    mapping: Mapping
    control: Control
