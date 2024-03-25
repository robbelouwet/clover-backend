import os
import flask
from flask import Blueprint
from flask_cors import cross_origin

redirect_frontend_bp = Blueprint("redirect_frontend", __name__)


@redirect_frontend_bp.route('/post-login-redirect')
@cross_origin(supports_credentials=True)
def redirect():
    return flask.redirect("https://" + os.environ.get("DNS_ZONE"))
