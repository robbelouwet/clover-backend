import base64
import os

import flask
from azure.cli.core import get_default_cli
from flask import current_app, json

from app.logic.cosmos_store import get_cosmos_client

# Allowed values according to Azure Container Apps consumption profiles
allowed_values = [["0.5", "1"], ["1", "2"], ["1.5", "3"], ["2", "4"]]
dedicated_kinds = ["bedrock", "paper"]
consumption_kinds = ["paper"]


def parse_principal_name_identifier(client_principal) -> str:
    for claim in client_principal["claims"]:
        if "nameidentifier" in claim["typ"]:  # This isn't a typo
            return claim["val"]
    return None


def az_cli(args_str) -> dict:
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error


def authenticate(r: flask.Request) -> (bool, str, dict):
    #return True, "117339767971594071042", {}

    header = r.headers.get('x-ms-client-principal')
    if header is None:
        return False, None, None

    current_app.logger.info(f"x-ms-client-principal: {header}")
    client_principal = json.loads(base64.b64decode(header))
    google_name_identifier = parse_principal_name_identifier(client_principal)
    current_app.logger.info(f"google nameidentifier: {google_name_identifier}")

    return True, google_name_identifier, client_principal


def not_none(val) -> any:
    if val is None:
        raise ValueError("Value is None!")
    return val
