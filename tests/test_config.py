import unittest
import os

from harvest_kit_hiwi.config import load_config
from harvest_kit_hiwi.config import Config
from harvest_kit_hiwi.config import CONFIG

from .util import ASSETS_PATH
from .util import LOGGER


class TestConfig(unittest.TestCase):

    config_path = os.path.join(ASSETS_PATH, 'sample.config.yml')

    def test_loading_yml_file_works(self):
        self.assertTrue(os.path.exists(self.config_path))
        data = load_config(self.config_path)
        self.assertIsInstance(data, dict)
        self.assertIn('harvest', data)

    def test_config_path(self):
        LOGGER.info(f'config: {CONFIG.path}')
        self.assertTrue(True)

    def test_config_singleton(self):
        config = Config()
        self.assertIsInstance(config, Config)

        # This will test if it is indeed the same config instance
        config_alt = Config()
        self.assertEqual(config.id, config_alt.id)
        self.assertEqual(config, config_alt)

    def test_some_getters_of_config(self):
        config = Config()

        value = config.get_harvest_id()
        self.assertIsInstance(value, str)
        self.assertNotEqual(0, len(value))

        value = config.get_harvest_url()
        self.assertIsInstance(value, str)
        self.assertNotEqual(0, len(value))

        value = config.is_harvest_configured()
        self.assertTrue(value)
