import os
from datetime import datetime

from clickhouse_driver import Client

from api.data.entity import Localization
from api.db.interface import DBAdapter


class Clickhouse(DBAdapter):
    def __init__(self):
        self._user = os.getenv('CH_USER')
        self._password = os.getenv('CH_PASSWORD')
        self.client = Client(
            'localhost', user=self._user, password=self._password, port=9000, database='real_data_prod')

    def send_location(self, device_id: str, localization: Localization):
        self.client.execute(f"INSERT INTO real_data_prod.localization (*) values "
                            f"({device_id}, '{datetime.now().strftime('YYYY-MM-DD hh:mm:ss')}', "
                            f"{localization.lon}, {localization.lat})")
