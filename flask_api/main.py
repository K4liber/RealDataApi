import logging
from datetime import datetime, timezone

import flask
from flask import request
from flask_restx import Api, Resource

from api import SECRET_KEY
from api.data.entity import Data, Localization, DeviceTimestamp
from api.data.functions import get_timestamps_range
from api.db.clickhouse import Clickhouse
from api.data.utils import Default
from api.model import localization_fields, device_to_timestamp_fields

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, force=True)
app = flask.Flask(__name__)
app.config["DEBUG"] = True
api = Api(app, version='1.0', title="UCantHide API", description='API for the UCantHide project')
clickhouse_client = Clickhouse()

localization_model = api.model('Localization', localization_fields)
device_to_timestamp_model = api.model('DeviceToTimestamp', device_to_timestamp_fields)


@api.route('/get_localizations', endpoint='get_localizations')
@api.doc(params={
    'device_id': 'ID of the device',
    'from': f'Starting timestamp for localizations of the device. '
            f'Format={datetime.now().strftime(Default.DATETIME_ARG_FORMAT)}',
    'to': f'Ending timestamp for localizations of the device. '
            f'Format={datetime.now().strftime(Default.DATETIME_ARG_FORMAT)}'
})
class Localizations(Resource):
    @api.response(200, 'Success', [localization_model])
    def get(self):
        try:
            device_id = request.args.get('device_id', None)

            if not device_id:
                return f'get request is missing parameter "device_id"'

            arg_from_str = request.args.get('from', None)
            arg_to_str = request.args.get('to', None)
            arg_from = None
            arg_to = None

            if arg_from_str:
                try:
                    arg_from = datetime.strptime(arg_from_str, Default.DATETIME_ARG_FORMAT)
                except ValueError:
                    return f'parameter "from" should have format {Default.DATETIME_ARG_FORMAT}'

            if arg_to_str:
                try:
                    arg_to = datetime.strptime(arg_to_str, Default.DATETIME_ARG_FORMAT)
                except ValueError:
                    return f'parameter "to" should have format {Default.DATETIME_ARG_FORMAT}'

            timestamp_from, timestamp_to = get_timestamps_range(arg_from, arg_to)
            localizations = clickhouse_client.get_localizations(
                device_id, timestamp_from, timestamp_to)
        except BaseException as be:
            return f'API exception: {be}', 500

        return str([
            localization.to_json() for localization in localizations
        ])


@api.route('/get_devices_timestamps', endpoint='get_devices_timestamps')
@api.doc(params={'id_starts_with': 'Start of the device`s ID (optional)'})
class DevicesTimestamps(Resource):
    @api.response(200, 'Success', [device_to_timestamp_model], mimetype='application/json')
    def get(self):
        try:
            device_id_to_timestamp = clickhouse_client.get_device_id_to_timestamp(
                request.args.get('id_starts_with', None)
            )
        except BaseException as be:
            return f'API exception: {be}', 500

        sorted_values = {k: v for k, v in sorted(device_id_to_timestamp.items(), key=lambda item: item[1])}
        return str(
            [
                DeviceTimestamp(
                    device_id=device_id,
                    timestamp_str=timestamp.strftime(Default.DATETIME_FORMAT)
                ).to_json() for device_id, timestamp in sorted_values.items()
            ]
        )


@api.route('/get_localization', endpoint='get_localization')
@api.doc(params={'device_id': 'ID of the device'})
class GetLocalization(Resource):
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def get(self):
        device_id = request.args.get('device_id', None)

        if not device_id:
            return f'get request is missing parameter "device_id"'

        localization = clickhouse_client.get_localization(device_id)
        return str(localization.to_json())


upload_parser = api.parser()
upload_parser.add_argument('latitude', type=float, location='form', required=True)
upload_parser.add_argument('longitude', type=float, location='form', required=True)
upload_parser.add_argument('altitude', type=float, location='form', required=True)
upload_parser.add_argument('device_id', type=str, location='form', required=True)
upload_parser.add_argument('secret_key', type=str, location='form', required=True)


@api.route('/location', endpoint='location')
class Location(Resource):
    @api.doc(description="Save location data to the database.")
    @api.expect(upload_parser)
    @api.response(500, 'Invalid values')
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def post(self):
        args = upload_parser.parse_args()

        if not SECRET_KEY or SECRET_KEY != args['secret_key']:
            return f'Wrong secret key = "{args["secret_key"]}"', 401

        data = Data(
            device_id=args['device_id'],
            altitude=float(args['altitude']),
            localization=Localization(
                lat=float(args['latitude']),
                lon=float(args['longitude']),
                timestamp_str=datetime.now(tz=timezone.utc).strftime(Default.DATETIME_FORMAT)
            )
        )
        clickhouse_client.send_localization(data.device_id, data.localization)
        return str(data.localization.to_json()), 200


app.run(host='0.0.0.0', port=5000)
