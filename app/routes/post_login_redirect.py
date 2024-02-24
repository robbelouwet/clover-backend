import os
import flask
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app.logic.cosmos_store import find_first_user_server

redirect_frontend_bp = Blueprint("redirect_frontend", __name__)


@redirect_frontend_bp.route('/post-login-redirect')
@cross_origin(supports_credentials=True)
def redirect():
    return flask.redirect(os.environ.get("FRONTEND_HOST"))
