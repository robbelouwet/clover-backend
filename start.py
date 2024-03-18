from flask import Flask

from app.routes.delete_server import delete_server_bp
from app.routes.deploy_server import deploy_server_bp
from app.routes.file_share_relay import fs_relay_bp
from app.routes.get_server import get_user_server_bp, get_all_user_servers_bp, ping_server_bp
from app.routes.get_uptime import get_uptime_bp
from app.routes.post_login_redirect import redirect_frontend_bp
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('.dev.env'))

app = Flask(__name__)

CORS(app, support_credentials=True)

app.register_blueprint(deploy_server_bp)
app.register_blueprint(delete_server_bp)
app.register_blueprint(get_uptime_bp)
app.register_blueprint(fs_relay_bp)
app.register_blueprint(get_user_server_bp)
app.register_blueprint(get_all_user_servers_bp)
app.register_blueprint(redirect_frontend_bp)
app.register_blueprint(ping_server_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
