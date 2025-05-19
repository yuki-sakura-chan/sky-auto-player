import json
import os

from sakura.config import conf


class Locale:
    __messages__: dict[str, str]

    def messages(self, title: str) -> str:
        return self.__messages__[title]


def load_locale_messages(name: str) -> Locale:
    try:
        with open(os.path.join(os.getcwd(), f'resources/locales/{conf.region}/{name}.json'), 'r', encoding='UTF-8') as f:
            locale = Locale()
            locale.__messages__ = json.load(f)
            return locale
    except FileNotFoundError:
        raise FileNotFoundError(f"json file not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing json file: {e}")
