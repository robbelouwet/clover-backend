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


def create_server_entity(doc):
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
