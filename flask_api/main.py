import logging
from datetime import datetime, timezone

import flask
from flask import request

from api.data.entity import Data, Localization
from api.db.clickhouse import Clickhouse
from api.data.utils import Default


FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, force=True)
app = flask.Flask(__name__)
app.config["DEBUG"] = True
clickhouse_client = Clickhouse()


@app.route('/get_devices_timestamps', methods=['GET'])
def get_devices_timestamps():
    try:
        device_id_to_timestamp = clickhouse_client.get_device_id_to_timestamp()
    except BaseException as be:
        return f'API exception: {be}', 500

    return str({
        device_id: timestamp.strftime(Default.DATETIME_FORMAT)
        for device_id, timestamp in device_id_to_timestamp.items()
    })


# TODO rm it - deprecated
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
            lat=latitude, lon=longitude, timestamp_str=datetime.now(tz=timezone.utc).strftime(Default.DATETIME_FORMAT)
        )
    )
    clickhouse_client.send_localization(data.device_id, data.localization)
    return str(data.localization)


app.run(host='0.0.0.0')
