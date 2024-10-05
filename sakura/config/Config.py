from pydantic import BaseModel


class Player(BaseModel):
    instruments: str
    type: str
    volume: float


class Mapping(BaseModel):
    type: str


class ADB(BaseModel):
    path: str


class Config(BaseModel):
    file_path: str
    adb: ADB
    player: Player
    mapping: Mapping
