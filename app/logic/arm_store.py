import os
import random
import time

from flask import current_app

from app.logic.cosmos_store import delete_server_entity
from app.logic.utils import az_cli, not_none


def delete_dedicated_user_server(user_server):
    rg = os.environ.get("RG")
    record_name = user_server["server_host"].split(".")[0]
    record_zone = '.'.join(user_server["server_host"].split('.')[1:])

    # Delete the container instance
    command1 = (f'resource delete '
                f'-g {rg} '
                f'--ids {user_server["aci_id"]}')
    current_app.logger.info(f"executing: {command1}")
    az_cli(command1)

    # Delete the file share
    command2 = (f'resource delete '
                f'-g {rg} '
                f'--ids {user_server["file_share_id"]}')
    current_app.logger.info(f"executing: {command2}")
    az_cli(command2)

    # Delete the DNS cname record
    command3 = (f'resource delete '
                f'-g {rg} '
                f'--ids {user_server["dns_record_id"]}')
    current_app.logger.info(f"executing: {command3}")
    az_cli(command3)

    # Delete the server entity in the DB
    delete_server_entity(user_server["id"])


def stop_dedicated_user_server(user_server):
    rg = os.environ.get("RG")

    # Stop the container instance
    command1 = f'container stop -g {rg} -n {user_server["aci_id"].split("/")[-1:][0]}'
    current_app.logger.info(f"executing: {command1}")
    az_cli(command1)


def start_dedicated_user_server(user_server):
    rg = os.environ.get("RG")

    # Stop the container instance
    command1 = f'container start -g {rg} -n {user_server["aci_id"].split("/")[-1:][0]}'
    current_app.logger.info(f"executing: {command1}")
    az_cli(command1)


def show_dedicated_user_server(user_server):
    rg = os.environ.get("RG")

    # Stop the container instance
    command1 = f'container show -g {rg} -n {user_server["aci_id"].split("/")[-1:][0]}'
    current_app.logger.info(f"executing: {command1}")
    return az_cli(command1)


def deploy_user_server(servername, kind, dry_run, memory, vcpu):
    rg = not_none(os.environ.get("RG"))
    dns_zone = not_none(os.environ.get("DNS_ZONE"))
    capp_env = not_none(os.environ.get("CAPP_ENVIRONMENT_NAME"))
    st_acc_name = not_none(os.environ.get("ST_ACC_NAME"))
    port = random.randint(49152, 65535)  # a random unreserved port
    deployment_name = f'{servername}-{kind}-dedicated-deployment'

    velocity_secret = not_none(os.environ.get("VELOCITY_SECRET"))

    try:
        # if kind == "bedrock":
        command = f'deployment group {"what-if" if dry_run is not None else "create"} ' + \
                  f'-n {deployment_name} ' + \
                  f'--resource-group {rg} ' + \
                  f'--template-file dedicated-server.json ' + \
                  f'--parameters appName={kind} storageName={st_acc_name} servername={servername} ' + \
                  f'dnsZone={dns_zone} memoryMB={memory} vcpu={vcpu}'
        current_app.logger.info(f"Deploying: {command}")
        return az_cli(command), port, deployment_name
    # else:
    #     command = f'deployment group {"what-if" if dry_run is not None else "create"} ' + \
    #               f'-n {deployment_name} ' + \
    #               f'--resource-group {rg} ' + \
    #               f'--template-file paper-dedicated.json ' + \
    #               f'--parameters appName=paper ' + \
    #               f'storageName={st_acc_name} servername={servername} cappEnvName={capp_env} ' \
    #               f'exposedServerPort={port} memoryMB={memory * 1024} vcpu={vcpu} dnsZone={dns_zone} ' \
    #               f'velocitySecret={velocity_secret}'
    #     current_app.logger.info(f"Deploying: {command}")
    #     return az_cli(command), port, deployment_name

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


def get_server_uptime(capp_name: str, date_from: str, date_to: str):
    rg = not_none(os.environ.get("RG"))

    return az_cli(f'az monitor metrics list '
                  f'--resource {capp_name} '
                  f'--resource-group {rg} '
                  f'--resource-type /Microsoft.App/containerApps '
                  f'--aggregation average '
                  f'--metric "Replicas" '
                  f'--interval "PT1H" '
                  f'--start-time {date_from} '
                  f'--end-time {date_to}')
