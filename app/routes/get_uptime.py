from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.logic.arm_store import get_server_uptime
from app.logic.cosmos_store import find_user_server_by_google_nameidentifier
from app.logic.utils import not_none, authenticate

get_uptime_bp = Blueprint("get_uptime_bp", __name__)


@get_uptime_bp.route('/get-uptime')
@cross_origin(supports_credentials=True)
def deploy_dedicated():
    success, google_name_identifier, principal = authenticate(request)
    if not success:
        return jsonify({}), 401

    servername = not_none(request.args.get("servername"))
    from_date = not_none(request.args.get("from"))
    to_date = not_none(request.args.get("to"))

    try:
        datetime.strptime(from_date, '%Y-%M-%d')
        datetime.strptime(to_date, '%Y-%M-%d')
    except:
        return jsonify({}), 400

    server = find_user_server_by_google_nameidentifier(google_name_identifier, servername)

    data_points = get_server_uptime(server["capp_name"], from_date, to_date)

    return jsonify(data_points), 200
