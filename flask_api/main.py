import logging
from datetime import datetime, timezone

import flask
from flask import request

from api.data.entity import Data, Localization
from api.db.clickhouse import Clickhouse

FORMAT = '%(asctime)-15s %(level)-10s %(message)s'
logging.basicConfig(format=FORMAT)

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.logger = logging.getLogger('real_data_api')
clickhouse_client = Clickhouse()


@app.route('/get_device_ids', methods=['GET'])
def get_device_ids():
    try:
        device_ids_list = clickhouse_client.get_device_ids()
    except BaseException as be:
        return f'API exception: {be}', 500

    return str(device_ids_list)


@app.route('/get_localization', methods=['GET'])
def get_localization():
    device_id = request.args.get('device_id', 'any')
    localization = clickhouse_client.get_localization(device_id)
    return str(localization.to_json())


@app.route('/location', methods=['GET'])
def location():
    latitude = float(request.args.get('latitude', "0.0"))
    longitude = float(request.args.get('longitude', "0.0"))
    altitude = float(request.args.get('altitude', "0.0"))
    device_id = request.args.get('device_id', "any")
    data = Data(
        device_id=device_id,
        altitude=altitude,
        localization=Localization(
            lat=latitude, lon=longitude, timestamp=datetime.now(tz=timezone.utc)
        )
    )
    clickhouse_client.send_localization(data.device_id, data.localization)
    return str(data.localization)


app.run(host='0.0.0.0')
