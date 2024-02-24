import os
import uuid
import base64
from flask import Blueprint, request, jsonify, json
from flask_cors import cross_origin
from app.logic.arm_store import deploy_user_server
from app.logic.cosmos_store import upsert_server_entity
from app.logic.utils import allowed_values, parse_principal_name_identifier, not_none
from flask import current_app

from app.routes.get_server import get_user_server

deploy_server_bp = Blueprint("deploy_dedicated_bp", __name__)


@deploy_server_bp.route('/deploy-dedicated')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    # Authentication
    current_app.logger.info(f"print: x-ms-client-principal: {request.headers.get('x-ms-client-principal')}")
    client_principal = json.loads(base64.b64decode(request.headers.get('x-ms-client-principal')))
    google_name_identifier = parse_principal_name_identifier(client_principal)
    current_app.logger.info(f"google nameidentifier: {google_name_identifier}")

    # Parse & set up deployment params
    memory = int(request.args.get("memory"))
    vcpu = int(request.args.get("cpu"))
    servername = not_none(request.args.get("servername"))
    dry_run = request.args.get("dry-run", default=None)

    # Ensure that foreign key [nameidentifier, servername] doesn't already exist
    existing = get_user_server(google_name_identifier, servername)
    if existing is not None: return jsonify(
        {"error": "User already has a server with this name!"}), 400  # Upload server data to cosmos

    # Ensure valid memory & vcpu specification
    if [vcpu, memory] not in allowed_values:
        return jsonify({"error": f"The specified combination of resources is not allowed, "
                                 f"allowed values of [cpu, memory] are: {allowed_values}"}), 400

    # Upsert ahead of deployment to avoid re-deploying the same server before the deployment succeeds
    user_server_id = str(uuid.uuid4())
    user_server = {
        "id": user_server_id,
        "server_name": servername,
        "provisioned": False,
        "primary_oauth_account": {
            "provider": "google",
            "id": google_name_identifier,
            "google": client_principal
        },
        "oauth_accounts": []
    }
    upsert_server_entity(user_server)

    # Perform deployment
    capp_env = not_none(os.environ.get("CAPP_ENVIRONMENT_NAME"))
    response, port, deployment_name = deploy_user_server(servername, dry_run, memory, vcpu)
    current_app.logger.info(f"response: {response}")

    if dry_run is not None: return jsonify({}), 200 if response else jsonify({}), 500

    # Upsert with deployment-relevant information
    user_server = user_server.update({
        "provisioned": True,
        "server_host": response["properties"]["outputs"]["host"]["value"].split(':')[0],
        "server_port": port,
        "st_acc_name": response["properties"]["outputs"]["stAccName"]["value"],
        "share": response["properties"]["outputs"]["shareName"]["value"],
        "capp_env_name": capp_env,
        "capp_name": response["properties"]["outputs"]["cappName"]["value"],
        "st_def_name": response["properties"]["outputs"]["stDefName"]["value"]
    })
    upsert_server_entity(user_server)

    # Return response
    return jsonify({
        'id': user_server_id,
        'deployment_name': deployment_name,
        'server': response["properties"]["outputs"]["host"]["value"]
    }), 200
