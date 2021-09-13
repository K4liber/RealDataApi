import logging
import os
from datetime import datetime, timezone

import flask
from flask import request, flash
from flask_restx import Api, Resource
from werkzeug.datastructures import FileStorage

from api import Config
from api.data.entity import Data, Localization, DeviceTimestamp
from api.data.functions import get_timestamps_range
from api.db.clickhouse import Clickhouse
from api.data.utils import Default
from api.model import localization_fields, device_to_timestamp_fields
from api.utils import Folder

STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, force=True)
app = flask.Flask(__name__, static_url_path='', static_folder=f'{STATIC_FOLDER}/')
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = STATIC_FOLDER
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
                return 'get request is missing parameter "device_id"'

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
    @api.response(400, 'Missing "device_id" parameter')
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def get(self):
        device_id = request.args.get('device_id', None)

        if not device_id:
            return 'get request is missing parameter "device_id"', 400

        localization = clickhouse_client.get_localization(device_id)
        return str(localization.to_json())


location_parser = api.parser()
location_parser.add_argument('latitude', type=float, location='form', required=True)
location_parser.add_argument('longitude', type=float, location='form', required=True)
location_parser.add_argument('altitude', type=float, location='form', required=True)
location_parser.add_argument('device_id', type=str, location='form', required=True)
location_parser.add_argument('secret_key', type=str, location='form', required=True)


@api.route('/location', endpoint='location')
class Location(Resource):
    @api.doc(description="Save location data to the database.")
    @api.expect(location_parser)
    @api.response(401, 'Wrong secret key')
    @api.response(200, 'Success', localization_model, mimetype='application/json')
    def post(self):
        args = location_parser.parse_args()

        if not Config.secret_key or Config.secret_key != args['secret_key']:
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


view_post_parser = api.parser()
view_post_parser.add_argument('device_id', type=str, location='form', required=True)
view_post_parser.add_argument('secret_key', type=str, location='form', required=True)
view_post_parser.add_argument('file', type=FileStorage, location='files', required=True)

view_get_parser = api.parser()
view_get_parser.add_argument('device_id', type=str, help='ID of the device', required=True)
view_get_parser.add_argument(
    'timestamp', type=str, help=f'Get the view took just before the timestamp. '
                                f'Format={datetime.now().strftime(Default.DATETIME_ARG_FORMAT)}')


@api.route('/view', endpoint='view')
class View(Resource):
    @api.doc(description="Save image to the database.")
    @api.expect(view_post_parser)
    @api.response(400, 'Invalid values')
    @api.response(200, 'Success', mimetype='application/json')
    def post(self):
        args = view_post_parser.parse_args()

        if not Config.secret_key or Config.secret_key != args['secret_key']:
            return f'Wrong secret key = "{args["secret_key"]}"', 401

        device_id = args['device_id']

        if not device_id:
            return 'POST request is missing parameter "device_id"', 400

        if 'file' not in request.files:
            flash('No file part')
            return 'No "file" part', 400

        file = request.files['file']

        if file.filename == '':
            flash('Empty filename')
            return 'Empty filename', 400

        try:
            if file:
                device_view_folder = os.path.join(app.config['UPLOAD_FOLDER'], Folder.VIEW, device_id)

                if not os.path.isdir(device_view_folder):
                    os.mkdir(device_view_folder)

                filename = os.path.join(
                    device_view_folder, f"{datetime.now().strftime(Default.DATETIME_ARG_FORMAT)}.jpeg")
                file.save(filename)
        except BaseException as be:
            return f'API exception: {be}', 500

        return 'Successful update', 200

    @api.doc(description='Return the most current view of the device')
    @api.expect(view_get_parser)
    @api.response(400, 'Invalid values')
    @api.response(200, 'Success', mimetype='image/jpeg')
    @api.produces(["image/jpeg"])
    def get(self):
        device_id = request.args.get('device_id', None)
        timestamp = request.args.get('timestamp', datetime.now().strftime(Default.DATETIME_ARG_FORMAT))

        try:
            datetime.strptime(timestamp, Default.DATETIME_ARG_FORMAT)
        except ValueError:
            return f'parameter "timestamp" show have following format: {Default.DATETIME_ARG_FORMAT}', 400

        if not device_id:
            return 'Get request is missing parameter "device_id"', 400

        device_view_path_str = str(os.path.join(app.config['UPLOAD_FOLDER'], Folder.VIEW, device_id))

        if not os.path.isdir(device_view_path_str):
            return f'There is not any view for the device {device_id} yet.', 400

        sorted_views = sorted(os.listdir(device_view_path_str), reverse=True)

        for index, filename in enumerate(sorted_views):
            if timestamp > filename:
                return app.send_static_file(os.path.join(Folder.VIEW, device_id, filename))

        return f'There is not any view for the timestamp {timestamp}.', 400


app.run(host='0.0.0.0', port=Config.port)
