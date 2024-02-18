import logging

from azure.cosmos import CosmosClient, exceptions
from azure.identity import ClientSecretCredential, DefaultAzureCredential
import os


def find_by_google_name_identifier(id: str) -> dict:
    client = get_cosmos_client()
    container = client \
        .get_database_client(os.environ.get("COSMOS_DB_NAME")) \
        .get_container_client(os.environ.get("COSMOS_CONTAINER_NAME"))

    q = f'SELECT * FROM c WHERE c.google_name_identifier = @param_google_name_identifier'

    logging.info("query", q)

    result_set = container.query_items(
        q,
        parameters=[dict(name='@param_google_name_identifier', value=id)],
        enable_cross_partition_query=True
    )

    results = [doc for doc in result_set]
    if len(results) == 0: return None
    elif len(results) > 1: raise exceptions.CosmosResourceExistsError(message="Multiple hits found!")
    return results[0]


def parse_principal_name_identifier(client_principal) -> str:
    for claim in client_principal["claims"]:
        if "nameidentifier" in claim["type"]:
            return True, claim["val"]
    return False, None


def get_cosmos_client():
    cs = os.environ.get("CLIENT_SECRET")
    url = os.environ.get('COSMOS_ENDPOINT')

    # Can we auth through AD?
    if cs is not None and len(cs) > 0:
        tenant_id = os.environ.get('TENANT_ID')
        client_id = os.environ.get('CLIENT_ID')

        # Using ClientSecretCredential
        aad_credentials = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=cs)

        return CosmosClient(url, aad_credentials)

    # Looks for COSMOS_ENDPOINT and COSMOS_KEy to construct connection string
    else:
        key = os.environ.get('COSMOS_KEY')
        return CosmosClient(url, credential=key)
