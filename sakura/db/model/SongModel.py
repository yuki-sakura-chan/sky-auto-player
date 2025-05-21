from typing import Any

from pydantic import BaseModel


class SongModel(BaseModel):
    id: int = None
    name: str = ''
    author: str = ''
    bpm: int = 300
    pitchLevel: int = 1
    songNotes: list[dict[str, Any]] = []
    detail: str = ''
    # 外部数据id
    sid: int = None
