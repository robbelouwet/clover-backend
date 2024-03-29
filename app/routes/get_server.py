import base64
import os
from flask import Blueprint, request, jsonify, current_app, json
from flask_cors import cross_origin

from app.logic.arm_store import show_dedicated_user_server, start_dedicated_user_server, stop_dedicated_user_server
from app.logic.bedrock_ping import ping_unconnected_bedrock
from app.logic.cosmos_store import find_user_server_by_google_nameidentifier, \
    find_all_user_servers_by_google_nameidentifier
from app.logic.java_ping import ping_java
from app.logic.utils import parse_principal_name_identifier, not_none, authenticate

get_user_server_bp = Blueprint("get_user_server_bp", __name__)
get_all_user_servers_bp = Blueprint("get_all_user_servers_bp", __name__)
ping_server_bp = Blueprint("ping_server_bp", __name__)
poll_bedrock_server_bp = Blueprint("poll_bedrock_server_bp", __name__)
start_dedicated_server_bp = Blueprint("start_dedicated_server_bp", __name__)
stop_dedicated_server_bp = Blueprint("stop_dedicated_server_bp", __name__)
get_server_state_bp = Blueprint("get_server_state_bp", __name__)


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

    current_app.logger.debug(f"Pinging {server['server_host']}:25565")

    try:
        resp = ping_java(server["server_host"], 25565)
    except:
        return jsonify({"error": "Timeout"}), 500

    return jsonify(resp), 200


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
    try:
        result = ping_unconnected_bedrock(server["server_host"], 19132 )
    except:
        return jsonify({"error": "Timeout"}), 500

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


@start_dedicated_server_bp.route('/start-dedicated')
@cross_origin(supports_credentials=True)
def start_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))

    # Get the server
    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    start_dedicated_user_server(server)


@stop_dedicated_server_bp.route('/stop-dedicated')
@cross_origin(supports_credentials=True)
def stop_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))

    # Get the server
    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    stop_dedicated_user_server(server)


@get_server_state_bp.route('/get-state-dedicated')
@cross_origin(supports_credentials=True)
def stop_server():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Querystring param
    servername = not_none(request.args.get("servername"))

    # Get the server
    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    result = show_dedicated_user_server(server)

    return jsonify({
        'state': result["containers"][0]["instanceView"]["currentState"]["state"]
    }), 200
