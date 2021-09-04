import logging
from datetime import datetime, timezone

import flask
from flask import request, json

from api.data.entity import Data, Localization
from api.db.clickhouse import Clickhouse
from api.data.utils import Default
from flask_restx import Api, Resource, fields

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, force=True)
app = flask.Flask(__name__)
app.config["DEBUG"] = True
api = Api(app, version='1.0', title='Real Data API', description='API for the Real Data project')
clickhouse_client = Clickhouse()

localization_fields = api.model('Localization', {
    "lat": fields.Float,
    "lon": fields.Float,
    "timestampStr": fields.String
})


@api.route('/get_localizations', endpoint='get_localizations')
@api.doc(params={'device_id': 'ID of the device'})
class Localizations(Resource):
    @api.response(200, 'Success', [localization_fields])
    def get(self):
        device_id = request.args.get('device_id', None)

        if not device_id:
            return f'get request is missing parameter "device_id"'

        timestamp_from = request.args.get('from', None)
        timestamp_to = request.args.get('to', None)

        if timestamp_from:
            try:
                datetime.strptime(timestamp_from, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return f'parameter "from" should have format "2019-01-15 00:00:00"'

        if timestamp_to:
            try:
                datetime.strptime(timestamp_to, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return f'parameter "to" should have format "2019-01-15 00:00:00"'

        try:
            localizations = clickhouse_client.get_localizations(device_id, timestamp_from, timestamp_to)
        except BaseException as be:
            return f'API exception: {be}', 500

        return str([
            localization.to_json() for localization in localizations
        ])


@api.route('/get_devices_timestamps', endpoint='get_devices_timestamps')
class DevicesTimestamps(Resource):
    def get(self):
        try:
            device_id_to_timestamp = clickhouse_client.get_device_id_to_timestamp()
        except BaseException as be:
            return f'API exception: {be}', 500

        return str({
            device_id: timestamp.strftime(Default.DATETIME_FORMAT)
            for device_id, timestamp in device_id_to_timestamp.items()
        })


@api.route('/get_localization', endpoint='get_localization')
class Localization(Resource):
    def get(self):
        device_id = request.args.get('device_id', 'any')
        localization = clickhouse_client.get_localization(device_id)
        return str(localization.to_json())


@api.route('/location', endpoint='location')
class Location(Resource):
    def get(self):
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


app.run(host='0.0.0.0', port=5050)
