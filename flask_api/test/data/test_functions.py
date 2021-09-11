from datetime import datetime
from unittest import TestCase

from api.data.functions import get_timestamps_range
from api.data.utils import Default


class TestGetTimestampsRange(TestCase):
    def test_none_timestamps(self):
        timestamp_from, timestamp_to = get_timestamps_range(None, None)
        self.assertEqual(timestamp_to.day - datetime.now().day, 0)
        self.assertEqual((datetime.now() - timestamp_from).days, Default.TIMESTAMPS_RANGE_IN_DAYS)
