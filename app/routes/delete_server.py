import os
import base64
from flask import Blueprint, request, jsonify, json, current_app
from flask_cors import cross_origin

from app.logic.arm_store import delete_user_server
from app.logic.cosmos_store import find_user_server_by_google_nameidentifier
from app.logic.utils import parse_principal_name_identifier

delete_server_bp = Blueprint("delete_dedicated_bp", __name__)


@delete_server_bp.route('/delete-dedicated')
@cross_origin(supports_credentials=True)
def delete_dedicated():
    # Authentication
    current_app.logger.info(f"x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)
    current_app.logger.info(f"google nameidentifier: {google_name_identifier}")

    # Retrieve user_server
    servername = request.args.get("servername")
    user_server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    # Delete
    delete_user_server(user_server)

    return jsonify({}), 200
