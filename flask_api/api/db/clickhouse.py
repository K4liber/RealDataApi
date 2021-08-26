import os
from datetime import datetime

from clickhouse_driver import Client

from api.data.entity import Localization
from api.db.interface import DBAdapter
from api.utils import logger


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
        localization_list = self.client.execute(sql_cmd)
        # The method returns List of Tuples
        localization = Localization(
            timestamp=localization_list[0][0],
            lon=localization_list[0][1],
            lat=localization_list[0][2]
        )
        return localization
