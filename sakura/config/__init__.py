import os
from pathlib import Path

import yaml

from .Config import Config

app_data = Path(os.getenv('LOCALAPPDATA')) / 'sky-auto-player'
if not app_data.exists():
    app_data.mkdir()
__config_path__ = app_data / 'config.yaml'


def _config_exist() -> bool:
    return __config_path__.exists()


def _create_config() -> Config:
    c = Config()
    __config_path__.write_text('', encoding='utf-8')
    save_conf(c)
    return c


def _load_yaml_config():
    try:
        with open(__config_path__, 'r', encoding='UTF-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


def save_conf(c: Config):
    try:
        with open(__config_path__, 'w', encoding='UTF-8') as f:
            yaml.dump(c.model_dump(), f)
    except Exception as e:
        raise IOError(f"Failed to save configuration: {e}")


def load_conf() -> Config:
    try:
        # 配置文件不存在就创建一个新的配置文件
        if not _config_exist():
            return _create_config()
        data = _load_yaml_config()
        return Config(**data)
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")


conf = load_conf()
