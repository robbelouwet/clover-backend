from azure.cli.core import get_default_cli
import os

from app.logic.cosmos_store import get_cosmos_client


def find_user_server(user_id: str, server_name: str) -> dict:
    client = get_cosmos_client()

    q = f'SELECT * FROM c WHERE c.user_name = "{user_id}" AND c.server_name = "{server_name}"'

    database_id = os.environ.get("COSMOS_DB_NAME")
    container_id = os.environ.get("COSMOS_SERVERS_CONTAINER_NAME")

    result_set = client.QueryItems("dbs/" + database_id + "/colls/" + container_id, q,
                                   {'enableCrossPartitionQuery': True})

    results = [doc for doc in result_set]
    if len(results) == 0:
        return None
    elif len(results) > 1:
        raise ValueError("Cosmos query returned multiple hits!")
    return results[0]


def parse_principal_name_identifier(client_principal) -> str:
    for claim in client_principal["claims"]:
        if "nameidentifier" in claim["type"]:
            return True, claim["val"]
    return False, None


def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True