import configparser
from typing import Dict


class Config:
    config = {}

    @staticmethod
    def get_config() -> Dict:
        if len(Config.config.keys()) == 0:
            Config.config = Config()
        return Config.config

    def __init__(self):
        self.__read_config()

    def __read_config(self):
        path = "configuration.cfg"

        import os.path

        if not os.path.isfile(path):
            path = "../" + path
            if not os.path.isfile(path):
                path = "../" + path
        config = configparser.ConfigParser()
        config.read(path)
        self.config = dict(config.items("DEFAULT"))
        print("Config has", len(self.config), "keys")

    def __getitem__(self, key):
        return self.config[key.lower()]

    def keys(self):
        return self.config.keys()
