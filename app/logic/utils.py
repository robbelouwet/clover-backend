import os

from azure.cli.core import get_default_cli

from app.logic.cosmos_store import get_cosmos_client

# Allowed values according to Azure Container Apps consumption profiles
allowed_values = [[0.5, 1], [1, 2], [1.5, 3], [2, 4]]


def parse_principal_name_identifier(client_principal) -> str:
    for claim in client_principal["claims"]:
        if "nameidentifier" in claim["typ"]:  # This isn't a typo
            return claim["val"]
    return None


def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True


def not_none(val) -> any:
    if val is None:
        raise ValueError("Value is None!")
    return val
