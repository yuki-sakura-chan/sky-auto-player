import codecs
import json
import os

import chardet

from sakura.config.sakura_logging import logger
from sakura.db.DBManager import song_client
from sakura.db.model.SongModel import SongModel


# 获取指定目录下的文件列表
def get_file_list(file_path: str = 'resources') -> list[str]:
    if not os.path.isdir(file_path):
        raise ValueError(f"Directory does not exist: {file_path}")
    allowed_extensions = ['.json', '.txt', '.skysheet']
    return [
        file
        for root, dirs, files in os.walk(file_path)
        for file in files
        if os.path.splitext(file)[1].lower() in allowed_extensions
    ]


def load_json(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            encoding = chardet.detect(f.read(1024))['encoding']
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode JSON file {file_path} using detected encoding {encoding}: {e}")


def load_locale_data(file_path: str, file_list: list[str]) -> None:
    for file in file_list:
        data = load_json(f'{file_path}/{file}')[0]
        model: SongModel = SongModel(**data)
        song_client.insert(model)
        logger.info('成功将%s插入到数据库中', model.name)
