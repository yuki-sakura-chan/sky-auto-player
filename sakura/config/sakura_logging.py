import logging
from datetime import datetime
from pathlib import Path

from sakura.config import app_data


class LoggerFactory:
    _inited = False

    @classmethod
    def init(cls, app_data: Path):

        if cls._inited:
            return

        log_dir = app_data / 'logs'

        if not log_dir.exists():
            log_dir.mkdir(parents=True)

        log_file = log_dir / datetime.now().strftime(
            'sap_%Y-%m-%d.log'
        )

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        root = logging.getLogger()

        root.setLevel(logging.INFO)

        # 文件输出
        file_handler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding='utf-8'
        )

        file_handler.setFormatter(formatter)

        root.addHandler(file_handler)

        # 控制台输出
        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        root.addHandler(console_handler)

        cls._inited = True

    @staticmethod
    def get_logger(obj):

        # obj 原名 object
        if isinstance(obj, str):
            return logging.getLogger(obj)

        return logging.getLogger(
            obj.__class__.__name__
        )


LoggerFactory.init(app_data)
