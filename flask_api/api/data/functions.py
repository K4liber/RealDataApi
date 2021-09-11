from datetime import datetime, timedelta
from typing import Tuple, Optional

from api.data.utils import Default


def get_timestamps_range(timestamp_from: Optional[datetime], timestamp_to: Optional[datetime],
                         max_range: int = Default.TIMESTAMPS_RANGE_IN_DAYS) -> Tuple[datetime, datetime]:
    """

    :param timestamp_from:
    :param timestamp_to:
    :param max_range: Max range of the timestamps in days.
    :return:
    """
    max_timedelta = timedelta(days=max_range)

    if timestamp_from is None and timestamp_to is None:
        return datetime.now() - max_timedelta, datetime.now()

    if timestamp_to is None:
        timestamp_to = datetime.now()

    if timestamp_from is None:
        timestamp_from = timestamp_to - max_timedelta

    if timestamp_from >= timestamp_to:
        raise ValueError(f'timestamps_from ({timestamp_from.strftime(Default.DATETIME_FORMAT)} '
                         f'>= timestamp_to ({timestamp_to.strftime(Default.DATETIME_FORMAT)})')

    timestamps_range = timestamp_to - timestamp_from

    if timestamps_range > max_timedelta:
        timestamp_from = timestamp_to - max_timedelta

    return timestamp_from, timestamp_to
