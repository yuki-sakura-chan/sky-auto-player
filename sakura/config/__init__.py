import os

import yaml

from .Config import Config


def _load_yaml_config():
    with open(os.path.join(os.getcwd(), 'config.yaml'), 'r', encoding='UTF-8') as f:
        return yaml.safe_load(f)


def dict_to_object(cls, data: dict):
    if isinstance(data, dict):
        # 检查类的 __init__ 方法参数
        init_args = cls.__init__.__annotations__
        # 构建类的参数
        kwargs = {}
        for key, value in data.items():
            if key in init_args:
                arg_type = init_args[key]
                # 如果参数是类，递归调用 dict_to_object
                if isinstance(value, dict):
                    kwargs[key] = dict_to_object(arg_type, value)
                else:
                    kwargs[key] = value
        # 返回类的实例
        return cls(**kwargs)
    return data


def _load_conf() -> Config:
    data = _load_yaml_config()
    return dict_to_object(Config, data)


conf = _load_conf()
