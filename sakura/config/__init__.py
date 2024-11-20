import os

import yaml

from .Config import Config


def _load_yaml_config():
    try:
        with open(os.path.join(os.getcwd(), 'config.yaml'), 'r', encoding='UTF-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


def save_conf(c: Config):
    try:
        with open(os.path.join(os.getcwd(), 'config.yaml'), 'w', encoding='UTF-8') as f:
            yaml.dump(c.model_dump(), f)
    except Exception as e:
        raise IOError(f"Failed to save configuration: {e}")


def load_conf() -> Config:
    try:
        data = _load_yaml_config()
        return Config(**data)
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")

conf = load_conf()
