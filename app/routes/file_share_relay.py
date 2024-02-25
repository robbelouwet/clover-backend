import base64
import io
import os
from flask import Blueprint, request, jsonify, Response, current_app, json
from flask_cors import cross_origin
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient

from app.logic.cosmos_store import find_user_server_by_google_nameidentifier
from app.logic.utils import parse_principal_name_identifier

fs_relay_bp = Blueprint("fs_relay_bp", __name__)


@fs_relay_bp.route('/list-dir')
@cross_origin(supports_credentials=True)
def list_dir():
    # Authentication
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)

    servername = request.args.get('servername')
    path = request.args.get('path')

    if path is None:
        path = ""
    elif len(path) >= 1 and path[0] == '/':
        path = path[1:]

    # Get the file share
    user_server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)
    share = user_server["share"]

    current_app.logger.info(f"path: {path}, share: {share}")

    conn_string = os.environ.get("ST_ACC_CONN_STRING")
    parent_dir = ShareDirectoryClient.from_connection_string(
        conn_str=conn_string,
        share_name=share,
        directory_path=path)

    contents = []
    for item in parent_dir.list_directories_and_files():
        contents.append({'name': item.name, 'is_directory': item.is_directory})

    return jsonify(contents), 200


@fs_relay_bp.route('/get-file')
@cross_origin(supports_credentials=True)
def get_file():
    # Authentication
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)

    servername = request.args.get('servername')
    file_path = request.args.get('filepath')

    # Get the file share
    user_server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)
    share = user_server["share"]

    if len(file_path) >= 1 and file_path[0] == '/':
        file_path = file_path[1:]

    conn_string = os.environ.get("ST_ACC_CONN_STRING")
    file_client = ShareFileClient.from_connection_string(
        conn_str=conn_string, share_name=share, file_path=file_path)

    stream = io.BytesIO()
    file_client.download_file().readinto(stream)

    return Response(stream.getvalue(), headers={
        'Content-Type': 'application/octet-stream',
    }), 200


@fs_relay_bp.route('/upsert-file', methods=['POST'])
@cross_origin(supports_credentials=True)
def upsert_file():
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    # Validate google service principal authentication
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)

    file_path = request.args.get('filepath')
    servername = request.args.get('servername')

    # Get the file share
    user_server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)
    share = user_server["share"]

    current_app.logger.info(f"path: {file_path}, share: {share}")

    if len(file_path) >= 1 and file_path[0] == '/':
        file_path = file_path[1:]

    conn_string = os.environ.get("ST_ACC_CONN_STRING")
    file_client = ShareFileClient.from_connection_string(conn_str=conn_string,
                                                         share_name=share,
                                                         file_path=file_path)

    content = request.get_data(as_text=False)

    content_length = request.content_length
    if content_length is not None and content_length > 2048:  # 2 KiB
        return jsonify({"error": "Request payload is too large"}), 413  # 413: Payload Too Large

    file_client.upload_file(data=content)

    return jsonify({}), 200
