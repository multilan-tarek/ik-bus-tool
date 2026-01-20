import json
import os.path
from json import JSONDecodeError

CONFIG_FILE_PATH = ".config"


class Config:
    def __init__(self):
        if not os.path.exists(CONFIG_FILE_PATH):
            self.write_config()
            return

        self.load_config()

    def load_config(self):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config_data = config_file.read()

        try:
            config_data = json.loads(config_data)
        except JSONDecodeError:
            self.reset_config()
            return

        for key, val in config_data.items():
            setattr(self, key, val)

    def reset_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            os.remove(CONFIG_FILE_PATH)

        self.write_config()

    def write_config(self):
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(self.__dict__))

    def __getattr__(self, name):
        return None