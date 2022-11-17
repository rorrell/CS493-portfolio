from flask import Blueprint, jsonify, request
import constants
import datastore as ds
import auth
from utils import generalUtils, fishUtils

bp = Blueprint('fish', __name__, url_prefix='/fish')


@bp.route('', methods=['POST', 'GET'])
def fish_post_get():
    if request.method == 'POST':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        err = fishUtils.required_attributes_error(content)
        if err is not None:
            return err, 400

        if ds.name_exists(constants.fish, content['name']):
            return {
                'Error': 'Fish already exists with the name: ' +
                         content['name'] + '.'
            }, 403

        fish = generalUtils.get_json_from_content(content)
        fish['ownerId'] = owner

        fish = ds.post(constants.fish, fish, request.host_url)

        return jsonify(ds.add_attributes_to_fish(fish, request.host_url)), 201
    elif request.method == 'GET':
        owner = auth.get_id_from_jwt(request)

        args = request.args
        cursor = args.get('cursor')
        if cursor is not None:
            cursor = cursor.encode()
        fish, next_cursor = ds.get_all_fish_with_aquariums(
            owner, request.host_url, cursor)
        count_fish = len(ds.get_by_owner(constants.fish, owner,
                                         request.host_url))

        obj = {
            'fish': fish,
            'totalItems': count_fish
        }
        if next_cursor is not None:
            obj['next'] = request.base_url + '?cursor' + next_cursor.decode()

        return jsonify(obj), 200


@bp.route('/<id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def fish_get_put_patch_delete(id):
    if request.method == 'GET':
        owner = auth.get_id_from_jwt(request)

        fish = ds.get_fish_with_aquarium(int(id), request.host_url)

        err = fishUtils.not_found_error(fish)
        if err is not None:
            return err, 404

        if fish['owner']['id'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        return jsonify(fish)
    elif request.method == 'PATCH':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        fish = ds.get_by_id(constants.fish, int(id), request.host_url)

        if fish is None:
            return fishUtils.not_found_error(fish), 404

        if fish['ownerId'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        if 'name' in content and ds.name_exists(
                constants.fish, content['name'],
                expect_one=fish['name'] == content['name']):
            return {
                'Error': 'Fish already exists with the name: ' + content['name'] + '.'
            }, 403

        fish = ds.patch(constants.fish, int(id),
                       generalUtils.get_json_from_content(content),
                       request.host_url)

        return jsonify(ds.add_attributes_to_fish(fish, request.host_url))
    elif request.method == 'PUT':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        err = fishUtils.required_attributes_error(content)
        if err is not None:
            return err, 400

        fish = ds.get_by_id(constants.fish, int(id), request.host_url)

        if fish is None:
            return fishUtils.not_found_error(fish), 404

        if fish['ownerId'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        if 'name' in content and ds.name_exists(
                constants.fish, content['name'],
                expect_one=fish['name'] == content['name']):
            return {
                'Error': 'Fish already exists with the name: ' + content['name'] + '.'
            }, 403

        fish = ds.patch(constants.fish, int(id),
                        generalUtils.get_json_from_content(content),
                        request.host_url)

        return jsonify(ds.add_attributes_to_fish(fish, request.host_url))
    elif request.method == 'DELETE':
        owner = auth.get_id_from_jwt(request)

        status = ds.delete_if_owned(constants.fish, int(id), owner)

        response = ''
        if status == 401:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, status)
        elif status == 404:
            response = {
                'Error': 'No fish with this fish_id exists.'
            }

        return response, status
