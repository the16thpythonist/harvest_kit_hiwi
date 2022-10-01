import os
import sys
import pathlib
import logging

from decouple import AutoConfig

from harvest_kit_hiwi.config import CONFIG

PATH = pathlib.Path(__file__).parent.absolute()
ASSETS_PATH = os.path.join(PATH, 'assets')

LOGGER = logging.getLogger('Testing')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
# LOGGER.addHandler(logging.NullHandler())

config = AutoConfig(PATH)
config_path = config('HARVEST_HIWI_CONFIG')
CONFIG.load(config_path)
