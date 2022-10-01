import os
import json
import unittest
from pprint import pprint

import requests
from dateutil import parser

from harvest_kit_hiwi.config import CONFIG
from harvest_kit_hiwi.harvest import HarvestApi

from .util import LOGGER
from .util import ASSETS_PATH


HEADERS = {
    'Authorization': f'Bearer {CONFIG.get_harvest_token()}',
    'Harvest-Account-Id': f'{CONFIG.get_harvest_id()}',
    'User-Agent': 'Kit Hiwi'
}


@unittest.skipIf(not CONFIG.is_harvest_configured(), 'No harvest account provided for testing')
class TestHarvest(unittest.TestCase):

    time_entries_url = CONFIG.get_harvest_url() + 'time_entries'
    projects_url = CONFIG.get_harvest_url() + 'projects'

    datetime_format = ''

    session = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.session = requests.session()
        cls.session.headers.update(HEADERS)

    def test_retrieve_project_information(self):
        """
        We need to know the project_id of the project which is used for the Hiwi time tracking...
        """
        response = self.session.get(self.projects_url)
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertNotEqual(0, len(data))

    def test_retrieve_raw_data(self):
        self.assertTrue(True)

        params = {
            'project_id': '34329740'
        }

        response = self.session.get(self.time_entries_url, params=params)
        LOGGER.info(f'response status code: {response.status_code}')
        LOGGER.info(f'response payload length: {len(response.content)}')
        self.assertEqual(200, response.status_code)

        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertNotEqual(0, len(data))

        time_entries = data['time_entries']
        for te in time_entries:
            started_time = te['created_at']
            started_time = parser.parse(started_time)
            hours = te['hours']
            LOGGER.info(f'{started_time} --- {hours}')


@unittest.skipIf(not CONFIG.is_harvest_configured(), 'No harvest account provided for testing')
class TestHarvestApi(unittest.TestCase):

    time_entries_path = os.path.join(ASSETS_PATH, 'time_entries.json')

    def test_construction_basically_works(self):
        api = HarvestApi(
            url=CONFIG.get_harvest_url(),
            account_id=CONFIG.get_harvest_id(),
            account_token=CONFIG.get_harvest_token()
        )
        self.assertIsInstance(api, HarvestApi)

    def test_get_projects(self):
        api = HarvestApi(
            url=CONFIG.get_harvest_url(),
            account_id=CONFIG.get_harvest_id(),
            account_token=CONFIG.get_harvest_token()
        )
        projects = api.get_projects()
        self.assertIsInstance(projects, list)
        self.assertNotEqual(0, len(projects))

    def test_get_time_entries(self):
        api = HarvestApi(
            url=CONFIG.get_harvest_url(),
            account_id=CONFIG.get_harvest_id(),
            account_token=CONFIG.get_harvest_token()
        )
        time_entries = api.get_time_entries(project_id=CONFIG.get_harvest_project_id())
        self.assertIsInstance(time_entries, list)
        self.assertNotEqual(0, len(time_entries))
        for te in time_entries:
            self.assertIsInstance(te, dict)

        with open(self.time_entries_path, mode='w') as file:
            json.dump(time_entries, file)
