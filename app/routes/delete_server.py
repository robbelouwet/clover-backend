import base64
from flask import Blueprint, request, jsonify, json, current_app
from flask_cors import cross_origin

from app.logic.arm_store import delete_user_server
from app.logic.cosmos_store import find_user_server_by_google_nameidentifier
from app.logic.utils import parse_principal_name_identifier, authenticate

delete_server_bp = Blueprint("delete_dedicated_bp", __name__)


@delete_server_bp.route('/delete-paper-dedicated')
@cross_origin(supports_credentials=True)
def delete_dedicated():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Retrieve user_server
    servername = request.args.get("servername")
    user_server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    # Delete
    delete_user_server(user_server)

    return jsonify({}), 200
