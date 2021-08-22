import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import flask
from flask import request, render_template


ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = flask.Flask(__name__, template_folder=ASSETS_DIR, static_folder=ASSETS_DIR)
app.config["DEBUG"] = True


@dataclass
class Location:
    lat: float
    lon: float


@dataclass
class Data:
    location: Location
    timestamp: Optional[datetime]
    altitude: Optional[float]


data = Data(Location(0.0, 0.0), None, None)


@app.route("/")
def mapview():
    return render_template('map.html', data=data)


@app.route('/location', methods=['GET'])
def location():
    latitude = float(request.args.get('latitude', "0.0"))
    longitude = float(request.args.get('longitude', "0.0"))
    data.location.lon = longitude
    data.location.lat = latitude
    data.timestamp = datetime.now(tz=timezone.utc)
    return str(data.location)


app.run(host='0.0.0.0', port=80)
