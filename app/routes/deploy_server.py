import os
from flask import Blueprint, request, jsonify, make_response
from flask_cors import cross_origin
import random
from azure.cli.core import get_default_cli
import secrets
from json import loads

deploy_server = Blueprint("deploy_dedicated_bp", __name__)

# Allowed values according to Azure Container Apps consumption profiles
allowed_values = [[0.5, 1], [1, 2], [1.5, 3], [2, 4]]


@deploy_server.route('/deploy-dedicated')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    memory = int(request.args.get("memory"))
    vcpu = int(request.args.get("cpu"))
    servername = request.args.get("servername")
    dry_run = request.args.get("dry-run", default="false")

    if [vcpu, memory] not in allowed_values:
        return jsonify({"error": f"The specified combination of resources is not allowed, "
                                 f"allowed values of [cpu, memory] are: {allowed_values}"}), 400

    rg = os.environ.get("ST_ACC_RG")
    capp_env = os.environ.get("CAPP_ENVIRONMENT_NAME")
    st_acc_name = os.environ.get("ST_ACC_NAME")

    # secret_password = request.args.get('secret')
    #
    # if secret_password != 'appel':
    #     return 401

    print(f"cwd: {os.getcwd()}")
    port = random.randint(49152, 65535)  # a random unreserved port
    # servername = secrets.token_hex(4)
    deployment_name = f'{servername}-paper-dedicated-deployment'
    response = az_cli(f'deployment group {"what-if" if dry_run.lower() == "true" else "create"} ' +
                      f'-n {deployment_name} ' +
                      f'--resource-group {rg} ' +
                      f'--template-file dedicated-server.json ' +
                      f'--parameters appName=paper ' +
                      f'storageName={st_acc_name} servername={servername} cappEnvName={capp_env} exposedServerPort={port} ' +
                      f'memoryMB={memory*1024} vcpu={vcpu}')

    print(f"response: {response}")

    if dry_run:
        return make_response({}, 200) if response else make_response({}, 500)

    return jsonify({
        'deployment_name': deployment_name,
        'server': response["properties"]["outputs"]["host"]["value"]
    }), 200


def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True
