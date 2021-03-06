import os
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple

from clickhouse_driver import Client

from api.data.entity import Localization, DeviceTimestampsRange
from api.db.interface import DBAdapter
from api.utils import logger
from api.data.utils import Default


class Const:
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Clickhouse(DBAdapter):
    def __init__(self):
        self._host = os.getenv('CH_CLIENT_HOST')
        self._db_name = os.getenv('CH_DB')
        self.client = Client(self._host, database=self._db_name)

    def send_localization(self, device_id: str, localization: Localization):
        self.client.execute(f"INSERT INTO {self._db_name}.localization (*) values "
                            f"('{device_id}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', "
                            f"{localization.lon}, {localization.lat})")

    def get_localization(self, device_id: str) -> Localization:
        sql_cmd = \
            f"SELECT timestamp, lon, lat FROM {self._db_name}.localization " + \
            f"WHERE id = '{device_id}' order by timestamp desc limit 1"
        logger.info(f'SQL CMD: {sql_cmd}')
        localization_list = self.client.execute(sql_cmd)  # The method returns List of Tuples

        if len(localization_list) == 0:
            return Localization()

        localization = Localization(
            timestamp_str=localization_list[0][0].strftime(Default.DATETIME_FORMAT),
            lon=localization_list[0][1],
            lat=localization_list[0][2]
        )
        return localization

    def get_device_ids(self) -> List[str]:
        sql_cmd = f"SELECT DISTINCT id from {self._db_name}.localization  order by timestamp desc limit 10"
        # The method returns List of Tuples
        device_ids_list = self.client.execute(sql_cmd)
        logger.info(f'SQL CMD: {sql_cmd}')
        return [device_id_tuple[0] for device_id_tuple in device_ids_list]

    def get_device_timestamps_range(self, id_starts_with: Optional[str] = None,
                                   limit: int = 10) -> Set[DeviceTimestampsRange]:
        sql_cmd = f"select id, min(timestamp), max(timestamp) from {self._db_name}.localization"
        device_timestamps_range = set()

        if id_starts_with:
            sql_cmd = sql_cmd + f" where startsWith(id, '{id_starts_with}')"

        sql_cmd = sql_cmd + f" group by id limit {limit}"
        logger.info(f'SQL CMD: {sql_cmd}')
        devices_timestamps_list = self.client.execute(sql_cmd)
        # The method returns List of Tuples
        for device_timestamp_tuple in devices_timestamps_list:
            device_timestamps_range.add(
                DeviceTimestampsRange(
                    device_id=device_timestamp_tuple[0],
                    timestamp_from=device_timestamp_tuple[1].strftime(Default.DATETIME_FORMAT),
                    timestamp_to=device_timestamp_tuple[2].strftime(Default.DATETIME_FORMAT)
                )
            )

        return device_timestamps_range

    def get_localizations(self, device_id: str, timestamp_from: Optional[datetime],
                          timestamp_to: Optional[datetime]) -> List[Localization]:
        sql_cmd = f"select id, lat, lon, timestamp from {self._db_name}.localization " \
                  f"where id = '{device_id}' "

        if timestamp_from:
            sql_cmd = sql_cmd + f" and timestamp > toDateTime('{timestamp_from.strftime(Const.DATE_TIME_FORMAT)}')"

        if timestamp_to:
            sql_cmd = sql_cmd + f" and timestamp < toDateTime('{timestamp_to.strftime(Const.DATE_TIME_FORMAT)}')"

        sql_cmd = sql_cmd + " order by timestamp"
        logger.info(f'SQL CMD: {sql_cmd}')
        localizations_list = self.client.execute(sql_cmd)
        return [
            Localization(
                lat=localization_tuple[1],
                lon=localization_tuple[2],
                timestamp_str=localization_tuple[3].strftime(Default.DATETIME_FORMAT)
            ) for localization_tuple in localizations_list
        ]
