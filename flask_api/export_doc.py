from flask import json

from main import api
from main import app

app.config["SERVER_NAME"] = "ucanthide.eu"
app.app_context().__enter__()

with open('api_swagger.json', 'w') as doc_file:
    doc_file.write(json.dumps(api.__schema__))
