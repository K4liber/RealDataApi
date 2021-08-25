import os
from datetime import datetime
from unittest import TestCase
from clickhouse_driver import Client


class TestClickhouse(TestCase):
    def setUp(self) -> None:
        self.client = Client(
            'localhost', user='default', password='Lolp2222', port=9000, database='real_data_prod')

    def test_tables(self):
        tables = self.client.execute('SHOW TABLES')
        self.assertEqual(tables, [('localization',)])

    def test_insert(self):
        self.client.execute(f"INSERT INTO real_data_prod.localization (*) values "
                            f"('imei', '{datetime.now().strftime('YYYY-MM-DD hh:mm:ss')}', 0.1, 0.1)")

    def test_any(self):
        import subprocess
        output = subprocess.check_output("ip route show | awk '/default/ {print $3}'", shell=True, encoding='UTF-8')
        print(output)