from flask import json

from main import api
from main import app

app.config["SERVER_NAME"] = "datareal.pl"
app.app_context().__enter__()

with open('doc.json', 'w') as doc_file:
    doc_file.write(json.dumps(api.__schema__))
