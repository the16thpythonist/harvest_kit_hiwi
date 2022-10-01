import datetime
import unittest
import os
import json

from harvest_kit_hiwi.processing import TimeSpan

from .util import ASSETS_PATH
from .util import LOGGER


class TestTimeSpan(unittest.TestCase):

    time_entries_path = os.path.join(ASSETS_PATH, 'time_entries.json')
    time_entries = None

    @classmethod
    def setUpClass(cls) -> None:
        with open(cls.time_entries_path) as file:
            cls.time_entries = json.load(file)

    def test_loading_time_entries_works(self):
        self.assertTrue(os.path.exists(self.time_entries_path))
        self.assertIsInstance(self.time_entries, list)
        self.assertNotEqual(0, len(self.time_entries))

    def test_construction_basically_works(self):
        ts_1 = TimeSpan(
            start=datetime.datetime.now(),
            end=datetime.datetime.now(),
            description_set=set()
        )
        self.assertIsInstance(ts_1, TimeSpan)

    def test_constructing_from_time_entry_works(self):
        for te in self.time_entries:
            ts = TimeSpan.from_time_entry(te)
            self.assertIsInstance(ts, TimeSpan)

    def test_collision_detection_works(self):
        td_1 = datetime.timedelta(hours=1)
        td_2 = datetime.timedelta(hours=2)

        # These two should not collide since they are only one hour long and two hours apart
        ts_1 = TimeSpan(datetime.datetime.now(), datetime.datetime.now() + td_1)
        ts_2 = TimeSpan(datetime.datetime.now() + td_2, datetime.datetime.now() + td_2 + td_1)
        LOGGER.info(ts_1)
        LOGGER.info(ts_2)
        self.assertFalse(ts_1.collides_with(ts_2))

        # The bitwise AND operator can be used to perform a collision check
        self.assertFalse(ts_1 & ts_2)

        # These two should collide since they are two hours long but only one hour apart
        ts_1 = TimeSpan(datetime.datetime.now(), datetime.datetime.now() + td_2)
        ts_2 = TimeSpan(datetime.datetime.now() + td_1, datetime.datetime.now() + td_2 + td_1)
        self.assertTrue(ts_1.collides_with(ts_2))

    def test_merge_works(self):
        td_1 = datetime.timedelta(hours=1)
        td_2 = datetime.timedelta(hours=2)

        # Merging these two should create a single time span which is 3 hours long and whose start time
        # is determined by whichever element is the "front" of the merge operation
        ts_1 = TimeSpan(datetime.datetime.now(), datetime.datetime.now() + td_1, {'hello'})
        ts_2 = TimeSpan(datetime.datetime.now() + td_1, datetime.datetime.now() + td_1 + td_2, {'world'})
        ts_3 = ts_1.merge(ts_2)
        self.assertEqual(3, ts_3.duration)
        self.assertEqual(ts_1.start_datetime, ts_3.start_datetime)
        self.assertSetEqual({'hello', 'world'}, ts_3.description_set)

        # The ADD operator can be used to performs a merge
        ts_3 = ts_1 + ts_2
        self.assertEqual(3, ts_3.duration)
        self.assertEqual(ts_1.start_datetime, ts_3.start_datetime)

    def test_sum_works(self):
        td_1 = datetime.timedelta(hours=1)

        # Does the "sum" operation work with merging?
        ts_1 = TimeSpan(datetime.datetime.now(), datetime.datetime.now() + td_1)
        ts_2 = TimeSpan(datetime.datetime.now() + td_1 * 1, datetime.datetime.now() + td_1 * 2)
        ts_3 = TimeSpan(datetime.datetime.now() + td_1 * 2, datetime.datetime.now() + td_1 * 3)

        td_sum = sum([ts_2, ts_3], start=ts_1)
        self.assertIsInstance(td_sum, TimeSpan)
        self.assertEqual(3, td_sum.duration)



