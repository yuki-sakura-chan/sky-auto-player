# -*- coding: utf-8 -*-
import os

import yaml


class Config:
    file_path = ''
    mapping = {}
    player = {}

    @staticmethod
    def load_yaml_config():
        with open(os.path.join(os.getcwd(), 'config.yaml'), 'r', encoding='UTF-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            conf.file_path = config['file_path']
            conf.mapping = config['mapping']
            conf.player = config['player']


conf = Config()
