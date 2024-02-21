import os
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app.logic.cosmos_store import delete_server_entity, find_user_server
from app.logic.utils import az_cli

delete_server = Blueprint("delete_dedicated_bp", __name__)


@delete_server.route('/delete-dedicated')
@cross_origin(supports_credentials=True)
def delete_dedicated():
    # print(f"x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    # # Validate google service principal authentication
    # client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    # google_name_identifier = parse_principal_name_identifier(client_principal)
    #
    # print(f"google_nameidentifier: {google_name_identifier}")
    # # if not google_name_identifier: return jsonify({}), 401

    # user = find_by_google_name_identifier(google_name_identifier)
    servername = request.args.get("servername")
    user_server = find_user_server("robbelouwet", servername)
    rg = os.environ.get("ST_ACC_RG")

    # Delete the container
    command1 = f'containerapp delete -g {rg} -n {user_server["capp_name"]} --yes'
    print(f"executing: {command1}")
    az_cli(command1)

    # Delete the file share
    command2 = f'storage share delete ' + \
               f'--account-name {user_server["st_acc_name"]} ' + \
               f'--name {user_server["share"]} ' + \
               f'--fail-not-exist'
    print(f"executing: {command2}")
    az_cli(command2)

    # Delete the container app env storage definition
    command3 = f'containerapp env storage remove ' + \
               f'--name {user_server["capp_env_name"]} ' + \
               f'--resource-group {rg} ' + \
               f'--storage-name {user_server["st_def_name"]} ' + \
               f'--yes'
    print(f"executing: {command3}")
    az_cli(command3)

    delete_server_entity(user_server["id"])

    return jsonify({}), 200
