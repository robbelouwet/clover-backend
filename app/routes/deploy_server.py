import logging
import os
import uuid
import base64
from flask import Blueprint, request, jsonify, make_response, json
from flask_cors import cross_origin
import random
from app.logic.cosmos_store import create_server_entity
from app.logic.utils import allowed_values, az_cli, parse_principal_name_identifier
from flask import current_app

deploy_server = Blueprint("deploy_dedicated_bp", __name__)


@deploy_server.route('/deploy-dedicated')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    logging.info(f"logger: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    # Validate google service principal authentication
    # client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = "robbelouwet"  # parse_principal_name_identifier(client_principal)

    current_app.logger.info(f"google_nameidentifier: {google_name_identifier}")
    # if not google_name_identifier: return jsonify({}), 401

    # Parse & set up deployment params
    memory = int(request.args.get("memory"))
    vcpu = int(request.args.get("cpu"))
    servername = request.args.get("servername")
    dry_run = request.args.get("dry-run", default=None)

    if [vcpu, memory] not in allowed_values:
        return jsonify({"error": f"The specified combination of resources is not allowed, "
                                 f"allowed values of [cpu, memory] are: {allowed_values}"}), 400

    # Perform deployment
    rg = os.environ.get("ST_ACC_RG")
    capp_env = os.environ.get("CAPP_ENVIRONMENT_NAME")
    st_acc_name = os.environ.get("ST_ACC_NAME")
    # current_app.logger.info(f"cwd: {os.getcwd()}")
    port = random.randint(49152, 65535)  # a random unreserved port
    deployment_name = f'{servername}-paper-dedicated-deployment'
    response = az_cli(f'deployment group {"what-if" if dry_run is not None else "create"} ' +
                      f'-n {deployment_name} ' +
                      f'--resource-group {rg} ' +
                      f'--template-file dedicated-server.json ' +
                      f'--parameters appName=paper ' +
                      f'storageName={st_acc_name} servername={servername} cappEnvName={capp_env} exposedServerPort={port} ' +
                      f'memoryMB={memory * 1024} vcpu={vcpu}')

    current_app.logger.info(f"response: {response}")

    if dry_run is not None:
        return make_response({}, 200) if response else make_response({}, 500)

    # Upload server data to cosmos
    user_id = str(uuid.uuid4())
    create_server_entity({
        "id": user_id,
        "server_name": servername,
        "user_name": "robbelouwet",  # google_name_identifier
        "server_host": response["properties"]["outputs"]["host"]["value"].split(':')[0],
        "server_port": port,
        "st_acc_name": response["properties"]["outputs"]["stAccName"]["value"],
        "share": response["properties"]["outputs"]["shareName"]["value"],
        "capp_env_name": capp_env,
        "capp_name": response["properties"]["outputs"]["cappName"]["value"],
        "st_def_name": response["properties"]["outputs"]["stDefName"]["value"]
    })

    # Return response
    return jsonify({
        'id': user_id,
        'deployment_name': deployment_name,
        'server': response["properties"]["outputs"]["host"]["value"]
    }), 200
