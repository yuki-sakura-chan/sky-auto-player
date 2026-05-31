import importlib

from sakura.config import Config
from sakura.factory import player_mapper, key_mapper
from sakura.interface.Mapper import Mapper


def get_player(player_type: str, conf: Config):
    player = player_mapper.get(player_type)
    if player:
        module = importlib.import_module(player['module'])
        class_ = getattr(module, player['class'])
        return class_(conf)
    else:
        raise ValueError(f"Player type {player_type} not found")

def get_mapper(mapping_type: str) -> Mapper:
    mapper = key_mapper.get(mapping_type)
    if mapper:
        module = importlib.import_module(mapper['module'])
        class_ = getattr(module, mapper['class'])
        return class_()
    else:
        raise ValueError(f"Mapping type {mapping_type} not found")