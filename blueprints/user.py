from flask import Blueprint, jsonify, request
import constants
import datastore as ds

bp = Blueprint('user', __name__, url_prefix='/users')


@bp.route('', methods=['GET'])
def users_get():
    if request.method == 'GET':
        return jsonify(ds.get_all(constants.user, request.host_url))
