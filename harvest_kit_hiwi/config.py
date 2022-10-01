import os
import pathlib
import yaml
import time
from typing import List

from decouple import config

PATH = pathlib.Path(__file__).parent.absolute()
CONFIG_PATH = os.path.join(PATH, 'config.yml')
CONFIG_PATH = config('HARVEST_HIWI_CONFIG', default=CONFIG_PATH)


def load_config(path=CONFIG_PATH):
    with open(path, mode='r') as file:
        return yaml.safe_load(file)


class Singleton(type):
    """
    This is metaclass definition, which implements the singleton pattern. The objective is that whatever
    class uses this as a metaclass does not work like a traditional class anymore, where upon calling the
    constructor a NEW instance is returned. This class overwrites the constructor behavior to return the
    same instance upon calling the constructor.
    This makes sure that always just a single instance exists in the runtime!

    **USAGE**

    To implement a class as a singleton it simply has to use this class as the metaclass.

    .. code-block:: python
        class MySingleton(metaclass=Singleton):
            def __init__(self):
                # The constructor still works the same, after all it needs to be called ONCE to create the
                # the first and only instance.
                pass
        # All of those actually return the same instance!
        a = MySingleton()
        b = MySingleton()
        c = MySingleton()
        print(a is b) # true

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    """
    This is a singleton class, which implements the access to the config file.
    """

    def __init__(self):
        self.id = hash(time.time)
        self.path = CONFIG_PATH

        # -- LOAD THE DATA FROM FILE
        self.data = load_config(self.path)

    def load(self, path: str) -> None:
        """
        This function loads a custom config file at the absolute string `path`

        :returns: None
        """
        self.path = path
        self.data = load_config(path)

    # == IMPLEMENTING DICT FUNCTIONALITY ==

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        # For list or tuple, a whole sub-dict structure of keys is checked
        if isinstance(item, list) or isinstance(item, tuple):
            current_data = self.data
            for element in item:
                if not isinstance(element, dict) or element not in current_data.keys():
                    return False
                else:
                    current_data = current_data[element]

            return True

        # For everything else, mainly string, the normal dict check is performed.
        return item in self.data.keys()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    # == WRAPPER METHODS ==

    def is_harvest_configured(self) -> bool:
        return (
            self.get_harvest_token() is not None
            and self.get_harvest_id() is not None
        )

    # -- trivial config values --

    # ~ harvest

    def get_harvest_url(self) -> str:
        return self.data['harvest']['api_url']

    def get_harvest_id(self) -> str:
        return self.data['harvest']['account_id']

    def get_harvest_token(self) -> str:
        return self.data['harvest']['account_token']

    def get_harvest_project_id(self) -> str:
        return self.data['harvest']['project_id']

    # ~ function

    def do_merge_daily(self) -> bool:
        return bool(self.data['function']['merge_daily'])

    def do_monthly_leave(self) -> bool:
        return bool(self.data['function']['monthly_leave'])

    def do_clip_hours(self) -> bool:
        return bool(self.data['function']['clip_overtime'])

    # ~ personal

    def get_name(self) -> str:
        return self.data['personal']['name']

    def get_institute(self) -> str:
        return self.data['personal']['institute']

    def get_personnel_number(self) -> str:
        return self.data['personal']['personnel_number']

    def get_hourly_rate(self) -> str:
        return self.data['personal']['hourly_rate']

    def get_working_hours(self) -> str:
        return self.data['personal']['working_hours']

    def get_monthly_leave(self) -> str:
        return self.data['personal']['monthly_leave']


CONFIG = Config()
