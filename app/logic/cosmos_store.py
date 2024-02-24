from azure.cosmos.cosmos_client import CosmosClient
import os


def get_cosmos_client() -> CosmosClient:
    # cs = os.environ.get("CLIENT_SECRET")
    url = os.environ.get('COSMOS_ENDPOINT')

    # # Can we auth through AD MID?
    # if cs is not None and len(cs) > 0:
    #     tenant_id = os.environ.get('TENANT_ID')
    #     client_id = os.environ.get('CLIENT_ID')
    #
    #     # Using ClientSecretCredential
    #     aad_credentials = ClientSecretCredential(
    #         tenant_id=tenant_id,
    #         client_id=client_id,
    #         client_secret=cs)
    #
    #     return CosmosClient()

    # else:
    key = os.environ.get('COSMOS_KEY')
    return CosmosClient(url, {'masterKey': key})


def upsert_server_entity(doc):
    client = get_cosmos_client()

    database_id = os.environ.get("COSMOS_DB_NAME")
    container_id = os.environ.get("COSMOS_SERVERS_CONTAINER_NAME")

    client.UpsertItem("dbs/" + database_id + "/colls/" + container_id, doc)


def delete_server_entity(id: str):
    client = get_cosmos_client()

    database_id = os.environ.get("COSMOS_DB_NAME")
    container_id = os.environ.get("COSMOS_SERVERS_CONTAINER_NAME")

    client.DeleteItem("dbs/" + database_id + "/colls/" + container_id + "/docs/" + id,
                      {'partitionKey': id})


def find_user_server_by_google_nameidentifier(nameidentifier: str, server_name: str):
    client = get_cosmos_client()

    q = (f'SELECT * FROM c WHERE c.primary_oauth_account.id = "{nameidentifier}" ' +
         f'AND c.server_name = "{server_name}"')

    database_id = os.environ.get("COSMOS_DB_NAME")
    container_id = os.environ.get("COSMOS_SERVERS_CONTAINER_NAME")

    result_set = client.QueryItems("dbs/" + database_id + "/colls/" + container_id, q,
                                   {'enableCrossPartitionQuery': True})

    results = [doc for doc in result_set]
    if len(results) == 0: return None
    elif len(results) > 1: raise ValueError("Cosmos query returned multiple hits!")
    return results[0]


def find_first_user_server() -> dict:
    client = get_cosmos_client()

    q = f'SELECT TOP 1 * FROM c'

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
