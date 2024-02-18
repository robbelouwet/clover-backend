import base64
import logging
import os
import uuid

from flask import Blueprint, request, jsonify, make_response, json
from flask_cors import cross_origin
import random
from azure.cli.core import get_default_cli

from app.routes.common import get_cosmos_client, parse_principal_name_identifier

deploy_server = Blueprint("deploy_dedicated_bp", __name__)

# Allowed values according to Azure Container Apps consumption profiles
allowed_values = [[0.5, 1], [1, 2], [1.5, 3], [2, 4]]


@deploy_server.route('/deploy-dedicated')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    logging.info(f"x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    # Validate google service principal authentication
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)

    logging.info(f"google_nameidentifier: {google_name_identifier}")
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
    print(f"cwd: {os.getcwd()}")
    port = random.randint(49152, 65535)  # a random unreserved port
    deployment_name = f'{servername}-paper-dedicated-deployment'
    response = az_cli(f'deployment group {"what-if" if dry_run is not None else "create"} ' +
                      f'-n {deployment_name} ' +
                      f'--resource-group {rg} ' +
                      f'--template-file dedicated-server.json ' +
                      f'--parameters appName=paper ' +
                      f'storageName={st_acc_name} servername={servername} cappEnvName={capp_env} exposedServerPort={port} ' +
                      f'memoryMB={memory * 1024} vcpu={vcpu}')

    print(f"response: {response}")

    if dry_run is not None:
        return make_response({}, 200) if response else make_response({}, 500)

    # Upload server data to cosmos
    create_server_entity(
        server_host=response["properties"]["outputs"]["host"]["value"],
        google_name_identifier="robbelouwet",  # google_name_identifier,
        server_port=port,
        share=response["properties"]["outputs"]["shareName"]["value"]
    )

    # Return response
    return jsonify({
        'deployment_name': deployment_name,
        'server': response["properties"]["outputs"]["host"]["value"]
    }), 200


def create_server_entity(server_host, server_port, google_name_identifier, share):
    client = get_cosmos_client()
    container = client \
        .get_database_client(os.environ.get("COSMOS_DB_NAME")) \
        .get_container_client(os.environ.get("COSMOS_CONTAINER_NAME"))

    container.upsert_item({
        "id": str(uuid.uuid4()),
        "serverHost": server_host,
        "port": server_port,
        "google_name_identifier": google_name_identifier,
        "share": share
    })

def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True
