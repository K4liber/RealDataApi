from datetime import datetime

from flask_restx import fields

from api.data.utils import Default

localization_fields = {
    "lat": fields.Float(example=52.01),
    "lon": fields.Float(example=26.19),
    "timestamp_str": fields.String(example=datetime.now().strftime(Default.DATETIME_FORMAT))
}

device_to_timestamp_fields = {
    "device_id": fields.String(example="85471171"),
    "timestamp_str": fields.String(example=datetime.now().strftime(Default.DATETIME_FORMAT))
}
