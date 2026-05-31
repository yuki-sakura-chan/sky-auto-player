from pydantic import BaseModel


class Note(BaseModel):
    tick: int
    key: str
