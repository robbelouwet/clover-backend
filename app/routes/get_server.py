import base64
import os
from flask import Blueprint, request, jsonify, current_app, json
from flask_cors import cross_origin

from app.logic.cosmos_store import find_user_server_by_google_nameidentifier, \
    find_all_user_servers_by_google_nameidentifier
from app.logic.utils import parse_principal_name_identifier, not_none

# get_server_bp = Blueprint("get_server_bp", __name__)
get_user_server_bp = Blueprint("get_user_server_bp", __name__)
get_all_user_servers_bp = Blueprint("get_all_user_servers_bp", __name__)


@get_user_server_bp.route('/get-user-server')
@cross_origin(supports_credentials=True)
def get_user_server():
    # Authentication
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)
    current_app.logger.info(f"google nameidentifier: {google_name_identifier}")

    # Querystring param
    servername = not_none(request.args.get("servername"))

    return jsonify(find_user_server_by_google_nameidentifier(google_name_identifier, servername)), 200


@get_all_user_servers_bp.route('/get-all-user-servers')
@cross_origin(supports_credentials=True)
def get_user_server():
    # Authentication
    # current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    # client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = "117339767971594071042"  # parse_principal_name_identifier(client_principal)
    current_app.logger.info(f"google nameidentifier: {google_name_identifier}")

    return jsonify(find_all_user_servers_by_google_nameidentifier(google_name_identifier)), 200
