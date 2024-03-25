import base64
import os
from flask import Blueprint, request, jsonify, current_app, json
from flask_cors import cross_origin

from app.logic.arm_store import show_bedrock_user_server
from app.logic.bedrock_ping import ping_unconnected_bedrock
from app.logic.cosmos_store import find_user_server_by_google_nameidentifier, \
    find_all_user_servers_by_google_nameidentifier
from app.logic.java_ping import ping
from app.logic.utils import parse_principal_name_identifier, not_none, authenticate

get_user_server_bp = Blueprint("get_user_server_bp", __name__)
get_all_user_servers_bp = Blueprint("get_all_user_servers_bp", __name__)
ping_server_bp = Blueprint("ping_server_bp", __name__)
poll_bedrock_server_bp = Blueprint("poll_bedrock_server_bp", __name__)


@get_user_server_bp.route('/get-user-server')
@cross_origin(supports_credentials=True)
def get_user_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))

    return jsonify(find_user_server_by_google_nameidentifier(google_name_identifier, servername)), 200


@get_all_user_servers_bp.route('/get-all-user-servers')
@cross_origin(supports_credentials=True)
def get_all_user_servers():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    return jsonify(find_all_user_servers_by_google_nameidentifier(google_name_identifier)), 200


# @get_server_state_bp.route('/get-server-state')
# @cross_origin(supports_credentials=True)
# def get_server_state():
#     # Authentication
#     current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
#     client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
#     google_name_identifier = parse_principal_name_identifier(client_principal)
#     current_app.logger.info(f"google nameidentifier: {google_name_identifier}")
#
#     # Querystring param
#     servername = not_none(request.args.get("servername"))
#
#     # Get the server
#     server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)
#
#     count = get_replica_count(server["capp_name"])
#
#     return jsonify({
#         "running": True if count != 0 else False
#     }), 200


@ping_server_bp.route('/ping-java-server')
@cross_origin(supports_credentials=True)
def ping_java_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))
    # return_if_idle = request.args.get("return-if-idle")

    # Get the server
    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    current_app.logger.info(f"server: {server}")

    # # Return HTTP 204 No Content if the server replica is scaled to 0, aka the server is idle
    # if return_if_idle is not None and bool(return_if_idle):
    #     count = get_replica_count(server["capp_name"])
    #     if count == 0:
    #         return jsonify({}), 204

    current_app.logger.debug(f"Pinging {server['server_host']}:25565")
    return jsonify(ping(server["server_host"])), 200


@poll_bedrock_server_bp.route('/ping-bedrock-server')
@cross_origin(supports_credentials=True)
def poll_bedrock_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))

    # Get the server
    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    current_app.logger.info(f"Pinging bedrock server: {server}")

    # Ping the bedrock server
    result = ping_unconnected_bedrock(server["server_host"], 25565)

    # layout in same structure as a java ping for front-end
    return jsonify({
        'description': {
            "text": result['description']
        },
        'version': {
            "name": "Bedrock " + result['gameVersion']
        },
        'players': {
            'online': result['currentPlayers'],
            'max': result['maxPlayers']
        }
    }), 200
