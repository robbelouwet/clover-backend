import io
import os
from flask import Blueprint, request, jsonify, Response
from flask_cors import cross_origin
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient

fs_relay = Blueprint("list_dir_bp", __name__)


@fs_relay.route('/list-dir')
@cross_origin(supports_credentials=True)
def list_dir():
    conn_string = os.environ.get("ST_ACC_CONN_STRING")

    path = request.args.get('path')
    if path is None:
        path = ""
    elif len(path) >= 1 and path[0] == '/':
        path = path[1:]

    share = request.args.get('share')

    print(f"path: {path}, share: {share}")

    parent_dir = ShareDirectoryClient.from_connection_string(
        conn_str=conn_string,
        share_name=share,
        directory_path=path)

    contents = []
    for item in parent_dir.list_directories_and_files():
        contents.append({'name': item.name, 'is_directory': item.is_directory})

    return jsonify(contents), 200


@fs_relay.route('/get-file')
@cross_origin(supports_credentials=True)
def get_file():
    conn_string = os.environ.get("ST_ACC_CONN_STRING")
    print(f"conn_string: {conn_string}")

    file_path = request.args.get('filepath')
    share = request.args.get('share')

    if len(file_path) >= 1 and file_path[0] == '/':
        file_path = file_path[1:]

    print(f"path: {file_path}, share: {share}")

    file_client = ShareFileClient.from_connection_string(
        conn_str=conn_string, share_name=share, file_path=file_path)

    stream = io.BytesIO()
    file_client.download_file().readinto(stream)

    return Response(stream.getvalue(), headers={
        'Content-Type': 'application/octet-stream',
    }), 200


@fs_relay.route('/upsert-file', methods=['POST'])
@cross_origin(supports_credentials=True)
def upsert_file():
    conn_string = os.environ.get("ST_ACC_CONN_STRING")

    file_path = request.args.get('filepath')
    share = request.args.get('share')

    print(f"path: {file_path}, share: {share}")

    if len(file_path) >= 1 and file_path[0] == '/':
        file_path = file_path[1:]

    file_client = ShareFileClient.from_connection_string(conn_str=conn_string,
                                                         share_name=share,
                                                         file_path=file_path)

    content = request.get_data(as_text=False)

    content_length = request.content_length
    if content_length is not None and content_length > 2048 * 2048:  # 1 MiB
        return jsonify({"error": "Request payload is too large"}), 413  # 413: Payload Too Large

    file_client.upload_file(data=content)

    return jsonify({}), 200

# if __name__ == "__main__":
#     asyncio.run(upsert_file())