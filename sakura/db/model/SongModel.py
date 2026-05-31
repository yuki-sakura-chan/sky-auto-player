from typing import Any

from pydantic import BaseModel

from sakura.db.model.Note import Note


class SongModel(BaseModel):
    id: int = None
    name: str = ''
    author: str = ''
    bpm: int = 60
    pitchLevel: int = 1
    songNotes: list[Note] = []
    detail: str = ''
    # 外部数据id
    sid: int = None
