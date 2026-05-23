from typing import List

from pydantic import BaseModel

from sakura.db.model.SongModel import SongModel


class PageData(BaseModel):
    size: int = 15
    data: List[SongModel] = []
    total: int = 0

    def get_page_number(self) -> int:
        return (self.total + self.size - 1) // self.size
