import os

import dotenv
from flask import Flask

from app.routes.delete_server import delete_server
from app.routes.deploy_server import deploy_server
from app.routes.file_share_relay import fs_relay
from app.routes.get_server import get_server
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('.dev.env'))

app = Flask(__name__)

CORS(app, support_credentials=True)

app.register_blueprint(deploy_server)
app.register_blueprint(delete_server)
app.register_blueprint(fs_relay)
app.register_blueprint(get_server)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
