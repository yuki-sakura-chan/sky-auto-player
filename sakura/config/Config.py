import os

import yaml


def load_yaml_config():
    with open(os.path.join(os.getcwd(), 'config.yaml'), 'r', encoding='UTF-8') as f:
        return yaml.safe_load(f)


class Config:
    __config: any

    def __init__(self):
        self.__config = load_yaml_config()

    def get(self, keys):
        keys_list = keys.split('.')
        value = self.__config
        for key in keys_list:
            value = value.get(key)
            if value is None:
                return None
        return value


conf = Config()
