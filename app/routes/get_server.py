import os
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app.logic.cosmos_store import find_first_user_server

get_server = Blueprint("get_server_bp", __name__)


@get_server.route('/get-server')
@cross_origin(supports_credentials=True)
def get_default_server():
    return jsonify(find_first_user_server()), 200
