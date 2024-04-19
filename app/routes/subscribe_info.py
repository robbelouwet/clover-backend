import hashlib
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app.logic.cosmos_store import upsert_email
from app.logic.utils import not_none

subscribe_info_bp = Blueprint("subscribe_info_bp", __name__)


@subscribe_info_bp.route('/subscribe-info')
@cross_origin(supports_credentials=True)
def get_user_server():
    # Querystring param
    email = not_none(request.args.get("email"))

    # Generate idempotent record ID
    m = hashlib.sha256()
    m.update(bytes(email, 'utf-8'))

    upsert_email({
        "id": m.hexdigest(),
        "email": email
    })

    return jsonify({}), 200