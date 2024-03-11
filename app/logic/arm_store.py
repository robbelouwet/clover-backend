import os
import random
import time

from flask import current_app

from app.logic.cosmos_store import delete_server_entity
from app.logic.utils import az_cli, not_none


def delete_user_server(user_server):
    rg = os.environ.get("RG")

    # Delete the container app
    command1 = f'containerapp delete -g {rg} -n {user_server["capp_name"]} --yes'
    current_app.logger.info(f"executing: {command1}")
    az_cli(command1)

    # Delete the container app env storage definition
    command3 = f'containerapp env storage remove ' + \
               f'--name {user_server["capp_env_name"]} ' + \
               f'--resource-group {rg} ' + \
               f'--storage-name {user_server["st_def_name"]} ' + \
               f'--yes'
    current_app.logger.info(f"executing: {command3}")
    az_cli(command3)

    # Delete the file share
    command2 = f'storage share delete ' + \
               f'--account-name {user_server["st_acc_name"]} ' + \
               f'--name {user_server["share"]} ' + \
               f'--fail-not-exist'
    current_app.logger.info(f"executing: {command2}")
    az_cli(command2)

    # Delete the server entity in the DB
    delete_server_entity(user_server["id"])


def deploy_user_server(servername, dry_run, memory, vcpu):
    rg = not_none(os.environ.get("RG"))
    capp_env = not_none(os.environ.get("CAPP_ENVIRONMENT_NAME"))
    st_acc_name = not_none(os.environ.get("ST_ACC_NAME"))
    port = random.randint(49152, 65535)  # a random unreserved port
    deployment_name = f'{servername}-paper-dedicated-deployment'

    try:
        return az_cli(f'deployment group {"what-if" if dry_run is not None else "create"} ' +
                      f'-n {deployment_name} ' +
                      f'--resource-group {rg} ' +
                      f'--template-file dedicated-server.json ' +
                      f'--parameters appName=paper ' +
                      f'storageName={st_acc_name} servername={servername} cappEnvName={capp_env} exposedServerPort={port} ' +
                      f'memoryMB={memory * 1024} vcpu={vcpu}'), port, deployment_name
    except Exception as e:
        raise e
        # TODO: find out resource names without arm template in order to ensure deletion


def get_replica_count(capp_name: str):
    rg = not_none(os.environ.get("RG"))

    response = az_cli(f'containerapp revision list '
                      f'--name {capp_name} '
                      f'--resource-group {rg} '
                      f'--all')

    if len(response) != 1:
        raise ValueError(f"Container app has more than 1 replica: {response}")

    return int(response[0]["properties"]["replicas"])
