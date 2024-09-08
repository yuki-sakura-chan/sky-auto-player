import importlib
from sakura.config.PlayerMapperConfig import player_mapper


def get_player(player_type):
    player = player_mapper.get(player_type)
    if player:
        module = importlib.import_module(player['module'])
        class_ = getattr(module, player['class'])
        return class_()
    else:
        raise ValueError(f"Player type {player_type} not found")
