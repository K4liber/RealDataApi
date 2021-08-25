import os
from datetime import datetime, timezone

import flask
from flask import request, render_template

from api.data.entity import Data, Localization
from api.db.clickhouse import Clickhouse

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = flask.Flask(__name__, template_folder=ASSETS_DIR, static_folder=ASSETS_DIR)
app.config["DEBUG"] = True
clickhouse_client = Clickhouse()
data = Data(Localization(0.0, 0.0), None, None)


@app.route("/")
def mapview():
    return render_template('map.html', data=data)


@app.route('/location', methods=['GET'])
def location():
    latitude = float(request.args.get('latitude', "0.0"))
    longitude = float(request.args.get('longitude', "0.0"))
    data.localization.lon = longitude
    data.localization.lat = latitude
    data.timestamp = datetime.now(tz=timezone.utc)
    clickhouse_client.send_location('any', data.localization)
    return str(data.localization)


app.run(host='0.0.0.0')
