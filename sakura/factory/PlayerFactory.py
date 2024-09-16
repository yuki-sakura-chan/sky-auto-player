import importlib
from sakura.factory import player_mapper


def get_player(player_type: str, conf: any):
    player = player_mapper.get(player_type)
    if player:
        module = importlib.import_module(player['module'])
        class_ = getattr(module, player['class'])
        return class_(conf)
    else:
        raise ValueError(f"Player type {player_type} not found")
