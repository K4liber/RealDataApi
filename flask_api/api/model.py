from datetime import datetime

from flask_restx import fields

from api.data.utils import Default

localization_fields = {
    "lat": fields.Float,
    "lon": fields.Float,
    "timestampStr": fields.String
}

device_to_timestamp_fields = {
    "device_id": fields.String(
        description="Timestamp string",
        example=datetime.now().strftime(Default.DATETIME_FORMAT)
    )
}

location_fields = {
    'latitude': fields.Float(required=True, description="Latitude of the device.", example=15.21),
    'longitude': fields.Float(required=True, description="Longitude of the device.", example=20.72),
    'altitude': fields.Float(required=True, description="Altitude of the device.", example=301.01),
    'device_id': fields.String(required=True, description="ID of the device.", example="83456118321")
}
