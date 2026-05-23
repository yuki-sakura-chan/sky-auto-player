import json
import sqlite3

from sakura.config import conf, app_data
from sakura.db.model.SongModel import SongModel


class SongClient:
    __DB_PATH__: str

    def __init__(self):
        db_dir = app_data / 'db'
        if not db_dir.exists():
            db_dir.mkdir()
        self.__DB_PATH__ = db_dir / conf.db.name
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

    def delete_by_id(self, song_id: int) -> bool:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                        DELETE FROM SONGS WHERE ID = ?
            ''', (song_id,))
            conn.commit()
            return cursor.rowcount > 0

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

    def select_count(self, keyword: str = '') -> int:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                        SELECT COUNT(*)
                        FROM SONGS
                        WHERE NAME LIKE ?
            ''', (f'%{keyword}%',))
            return cursor.fetchone()[0]

    def page(self, current: int, keyword: str = '', size: int = 15) -> list[SongModel]:
        with sqlite3.connect(self.__DB_PATH__) as conn:
            off: int = (current - 1) * size
            cursor = conn.cursor()
            cursor.execute('''
                        SELECT ID, NAME, AUTHOR, BPM
                        FROM SONGS
                        WHERE NAME LIKE ?
                        LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', size, off,))
            return [SongModel(id=row[0], name=row[1], author=row[2], bpm=row[3]) for row in
                    cursor.fetchall()]

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
                           LIMIT 1
                           ''')
            return cursor.fetchone()[0] == 0
