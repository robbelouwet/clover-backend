import os
import uuid
import base64
from flask import Blueprint, request, jsonify, json
from flask_cors import cross_origin
from app.logic.arm_store import deploy_user_server
from app.logic.cosmos_store import upsert_server_entity, find_user_server_by_google_nameidentifier
from app.logic.utils import allowed_values, parse_principal_name_identifier, not_none, authenticate, kinds
from flask import current_app

deploy_server_bp = Blueprint("deploy_dedicated_bp", __name__)


@deploy_server_bp.route('/deploy-dedicated')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    # Authentication
    success, google_name_identifier, principal = authenticate(request)
    if not success: return jsonify({}), 401

    # Arguments
    memory = not_none(int(request.args.get("memory")))
    vcpu = not_none(int(request.args.get("cpu")))
    kind = request.args.get("kind", "java")
    servername = not_none(not_none(request.args.get("servername")))
    dry_run = request.args.get("dry-run", default=None)

    # Ensure correct value for kind
    if kind not in kinds:
        return jsonify({"error": f"Kind {kind} not allowed! Allowed values: {json.dumps(kinds)}."}), 400

    # Ensure that the combination [nameidentifier, servername] doesn't already exist
    existing = find_user_server_by_google_nameidentifier(google_name_identifier, servername)
    if existing is not None: return jsonify(
        {"error": "User already has a server with this name!"}), 400  # Upload server data to cosmos

    # Upsert ahead of deployment to avoid re-deploying the same server before the deployment succeeds
    current_app.logger.info(f"Upserting ahead of deployment...")
    user_server_id = str(uuid.uuid4())
    user_server = {
        "id": user_server_id,
        "server_name": servername,
        "kind": kind,
        "provisioned": False,
        "primary_oauth_account": {
            "provider": "google",
            "id": google_name_identifier,
            "google": principal
        },
        "oauth_accounts": []
    }
    upsert_server_entity(user_server)

    # Perform deployment
    current_app.logger.info(f"Deploying resources")
    response, port, deployment_name = deploy_user_server(servername, kind, dry_run, memory, vcpu)
    current_app.logger.info(f"response: {response}")

    if dry_run is not None: return jsonify({}), 200 if response else jsonify({}), 500

    # Upsert with deployment-relevant information
    user_server.update({
        "provisioned": True,
        "server_host": response["properties"]["outputs"]["host"]["value"],
        "kind": kind,

        "aci_id": response["properties"]["outputs"]["aciId"]["value"],
        "file_share_id": response["properties"]["outputs"]["fileShareId"]["value"],
        "dns_record_id": response["properties"]["outputs"]["dnsRecordId"]["value"],
    })

    current_app.logger.debug(f"Upserting updated entry: {user_server}")
    upsert_server_entity(user_server)

    # Return response
    return jsonify({
        'id': user_server_id,
        'deployment_name': deployment_name,
        'server': response["properties"]["outputs"]["host"]["value"]
    }), 200
