import logging
from datetime import datetime, timezone

import flask
from flask import request
from flask_restx import Api, Resource

from api.data.entity import Data, Localization
from api.db.clickhouse import Clickhouse
from api.data.utils import Default
from api.model import localization_fields, device_to_timestamp_fields, location_fields

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, force=True)
app = flask.Flask(__name__)
app.config["DEBUG"] = True
api = Api(app, version='1.0', title="UCantHide API", description='API for the UCantHide project')
clickhouse_client = Clickhouse()

localization_model = api.model('Localization', localization_fields)
device_to_timestamp_model = api.model('DeviceToTimestamp', device_to_timestamp_fields)
location_model = api.model('Location', location_fields)


@api.route('/get_localizations', endpoint='get_localizations')
@api.doc(params={'device_id': 'ID of the device'})
class Localizations(Resource):
    @api.response(200, 'Success', [localization_model])
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
@api.doc(params={'id_starts_with': 'Start of the device`s ID (optional)'})
class DevicesTimestamps(Resource):
    @api.response(200, 'Success', device_to_timestamp_model, mimetype='application/json')
    def get(self):
        try:
            device_id_to_timestamp = clickhouse_client.get_device_id_to_timestamp(
                request.args.get('id_starts_with', None)
            )
        except BaseException as be:
            return f'API exception: {be}', 500

        return str({
            device_id: timestamp.strftime(Default.DATETIME_FORMAT)
            for device_id, timestamp in device_id_to_timestamp.items()
        })


@api.route('/get_localization', endpoint='get_localization')
@api.doc(params={'device_id': 'ID of the device'})
class Localization(Resource):
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def get(self):
        device_id = request.args.get('device_id', None)

        if not device_id:
            return f'get request is missing parameter "device_id"'

        localization = clickhouse_client.get_localization(device_id)
        return str(localization.to_json())


@api.route('/location', endpoint='location')
@api.doc(params={
    'latitude': 'Latitude of the device',
    'longitude': 'Longitude of the device',
    'altitude': 'Altitude of the device',
    'device_id': 'ID of the device'
})
class Location(Resource):
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def get(self):
        arg_names = {'latitude', 'longitude', 'altitude', 'device_id'}
        arg_name_to_values = dict()

        for arg_name in arg_names:
            arg_name_to_values[arg_name] = request.args.get('latitude', None)

        required_arg_names = {'latitude', 'longitude', 'altitude', 'device_id'}

        for required_arg_name in required_arg_names:
            if not arg_name_to_values[required_arg_name]:
                return f'get request is missing parameter "{required_arg_name}"', 500

        data = Data(
            device_id=arg_name_to_values['device_id'],
            altitude=float(arg_name_to_values['altitude']),
            localization=Localization(
                lat=float(arg_name_to_values['latitude']),
                lon=float(arg_name_to_values['longitude']),
                timestamp_str=datetime.now(tz=timezone.utc).strftime(Default.DATETIME_FORMAT)
            )
        )
        clickhouse_client.send_localization(data.device_id, data.localization)
        return str(data.localization.to_json())

    @api.doc(description="Save location data to the database.")
    @api.expect(location_model)
    @api.response(500, 'Invalid values')
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def post(self):
        return str({})


app.run(host='0.0.0.0', port=5050)
