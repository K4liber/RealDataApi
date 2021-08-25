import os
from datetime import datetime

from clickhouse_driver import Client

from api.data.entity import Localization
from api.db.interface import DBAdapter


class Clickhouse(DBAdapter):
    def __init__(self):
        self._host = os.getenv('CH_CLIENT_HOST')
        self._db_name = os.getenv('CH_DB')
        self.client = Client(self._host, database=self._db_name)

    def send_location(self, device_id: str, localization: Localization):
        self.client.execute(f"INSERT INTO {self._db_name}.localization (*) values "
                            f"('{device_id}', '{datetime.now().strftime('YYYY-MM-DD hh:mm:ss')}', "
                            f"{localization.lon}, {localization.lat})")
