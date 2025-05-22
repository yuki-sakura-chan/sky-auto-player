import json
import sqlite3

from sakura.config import conf
from sakura.db.model.SongModel import SongModel


class SongClient:
    __DB_PATH__: str

    def __init__(self):
        self.__DB_PATH__ = conf.db.path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.__DB_PATH__) as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS SONGS
                         (
                             ID          INTEGER PRIMARY KEY AUTOINCREMENT,
                             NAME        TEXT,
                             AUTHOR      TEXT,
                             BPM         INTEGER,
                             PITCH_LEVEL INTEGER,
                             SONG_NOTES  TEXT,
                             DETAIL      TEXT
                         )
                         ''')

    def insert(self, model: SongModel) -> int:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO SONGS (NAME, AUTHOR, BPM,
                                              PITCH_LEVEL,
                                              SONG_NOTES, DETAIL)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''',
                           (model.name, model.author, model.bpm,
                            model.pitchLevel, json.dumps(model.songNotes), model.detail))
            conn.commit()
            return cursor.lastrowid

    def select_by_name(self, name: str) -> list[SongModel]:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT ID, NAME
                           FROM SONGS
                           WHERE NAME like '%' || ? || '%'
                           ''', (name,))
            return [SongModel(id=row[0], name=row[1]) for row in cursor.fetchall()]

    def select_all(self) -> list[SongModel]:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT ID, NAME
                           FROM SONGS
                           ''')
            return [SongModel(id=row[0], name=row[1]) for row in cursor.fetchall()]

    def select_by_id(self, song_id: int) -> SongModel:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT NAME, SONG_NOTES, ID
                           FROM SONGS
                           WHERE ID = ?
                           ''', (song_id,))
            v = cursor.fetchone()
            return SongModel(name=v[0], songNotes=json.loads(v[1]), id=v[2])

    def db_is_null(self) -> bool:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT COUNT(*)
                           FROM SONGS
                           ''')
            return cursor.fetchone()[0] == 0
