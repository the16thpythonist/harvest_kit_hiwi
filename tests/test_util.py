import unittest
import os

from decouple import config

from harvest_kit_hiwi.util import VERSION_PATH
from harvest_kit_hiwi.util import get_version

from .util import LOGGER


class TestUtilFunctions(unittest.TestCase):

    def test_version_file_exists(self):
        self.assertTrue(os.path.exists(VERSION_PATH))

    def test_get_version(self):
        version = get_version()
        self.assertIsInstance(version, str)
        self.assertNotEqual(0, len(version))
