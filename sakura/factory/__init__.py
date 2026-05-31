# Description: This file contains the mapping of player type to player class.
player_mapper = {
    "win": {
        "class": "WindowsPlayer",
        "module": "sakura.components.player.WindowsPlayer"
    },
    "android": {
        "class": "AndroidPlayer",
        "module": "sakura.components.player.AndroidPlayer"
    },
    "demo": {
        "class": "DemoPlayer",
        "module": "sakura.components.player.DemoPlayer"
    }
}

key_mapper = {
    "json": {
        "class": "JsonMapper",
        "module": "sakura.components.mapper.JsonMapper"
    }
}