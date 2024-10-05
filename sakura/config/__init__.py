import os

import yaml

from .Config import Config


def _load_yaml_config():
    with open(os.path.join(os.getcwd(), 'config.yaml'), 'r', encoding='UTF-8') as f:
        return yaml.safe_load(f)


def save_conf(c: Config):
    with open(os.path.join(os.getcwd(), 'config.yaml'), 'w', encoding='UTF-8') as f:
        yaml.dump(c.model_dump(), f)


def load_conf() -> Config:
    data = _load_yaml_config()
    return Config(**data)


conf = load_conf()
