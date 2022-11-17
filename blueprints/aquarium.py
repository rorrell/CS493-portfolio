from flask import Blueprint, jsonify, request, g
import constants
import datastore as ds
import auth
from utils import generalUtils, aquariumUtils

bp = Blueprint('aquarium', __name__, url_prefix='/aquariums')


@bp.route('', methods=['POST', 'GET'])
def aquariums_post_get():
    if request.method == 'POST':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        err = aquariumUtils.required_attributes_error(content)
        if err is not None:
            return err, 400

        if ds.name_exists(constants.aquarium, content['name']):
            return {
                'Error': 'Aquarium already exists with the name: ' +
                         content['name'] + '.'
            }, 403

        aquarium = generalUtils.get_json_from_content(content)
        aquarium['ownerId'] = owner

        aquarium = ds.post(constants.aquarium, aquarium, request.host_url)

        return jsonify(ds.add_attributes_to_aquarium(aquarium,
                                                     request.host_url)), 201
    elif request.method == 'GET':
        owner = auth.get_id_from_jwt(request)

        args = request.args
        cursor = args.get('cursor')
        if cursor is not None:
            cursor = cursor.encode()
        aquariums, next_cursor = ds.get_all_aquariums_with_fish(
            owner, request.host_url, cursor)
        count_aquariums = len(ds.get_by_owner(constants.aquarium, owner,
                                             request.host_url))

        obj = {
            'aquariums': aquariums,
            'totalItems': count_aquariums
        }
        if next_cursor is not None:
            obj['next'] = request.base_url + '?cursor=' + next_cursor.decode()

        return jsonify(obj), 200


@bp.route('/<id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def aquarium_get_put_patch_delete(id):
    if request.method == 'GET':
        owner = auth.get_id_from_jwt(request)

        aquarium = ds.get_aquarium_with_fish(int(id), request.host_url)

        err = aquariumUtils.not_found_error(aquarium)
        if err is not None:
            return err, 404

        if aquarium['owner']['id'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        return jsonify(aquarium)
    elif request.method == 'PATCH':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        aquarium = ds.get_by_id(constants.aquarium, int(id),
                                request.host_url)

        if aquarium is None:
            return aquariumUtils.not_found_error(aquarium), 404

        if aquarium['ownerId'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        if 'name' in content and ds.name_exists(
                constants.aquarium,
                content['name'],
                expect_one=aquarium['name'] == content['name']):
            return {
                'Error': 'Aquarium already exists with the name: ' + content['name'] + '.'
            }, 403

        aquarium = ds.patch(constants.aquarium, int(id),
                            generalUtils.get_json_from_content(content),
                            request.host_url)

        return jsonify(ds.add_attributes_to_aquarium(
            aquarium, request.host_url))
    elif request.method == 'PUT':
        err = generalUtils.validate_content_type(request)
        if err is not None:
            return err, 406

        owner = auth.get_id_from_jwt(request)

        content = request.get_json()

        err = aquariumUtils.required_attributes_error(content)
        if err is not None:
            return err, 400

        aquarium = ds.get_by_id(constants.aquarium, int(id),
                                request.host_url)

        if aquarium is None:
            return aquariumUtils.not_found_error(aquarium), 404

        if aquarium['ownerId'] != owner:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, 401)

        if 'name' in content and ds.name_exists(
                constants.aquarium,
                content['name'],
                expect_one=aquarium['name'] == content['name']):
            return {
                'Error': 'Aquarium already exists with the name: ' + content['name'] + '.'
            }, 403

        aquarium = ds.patch(constants.aquarium, int(id),
                            generalUtils.get_json_from_content(content),
                            request.host_url)

        return jsonify(ds.add_attributes_to_aquarium(
            aquarium, request.host_url))
    elif request.method == 'DELETE':
        owner = auth.get_id_from_jwt(request)

        status = ds.delete_aquarium_and_remove_fish_if_owned(int(id), owner)

        response = ''
        if status == 401:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, status)
        elif status == 404:
            response = {
                'Error': 'No aquarium with this aquarium_id exists.'
            }

        return response, status


@bp.route('/<id>/fish/<fish_id>', methods=['PUT', 'DELETE'])
def aquarium_fish_put_delete(id, fish_id):
    if request.method == 'PUT':
        owner = auth.get_id_from_jwt(request)

        status = ds.put_fish_in_aquarium(owner, int(fish_id), int(id),
                                         request.host_url)

        response = ''
        if status == 401:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, status)
        elif status == 403:
            response = {
                'Error': 'The fish is already in another aquarium.'
            }
        elif status == 404:
            response = {
                'Error': 'The specified aquarium and/or fish does not exist.'
            }

        return response, status
    elif request.method == 'DELETE':
        owner = auth.get_id_from_jwt(request)

        status = ds.delete_fish_from_aquarium(owner, int(fish_id), int(id),
                                              request.host_url)

        response = ''
        if status == 401:
            raise auth.AuthError({
                'Error': 'You do not have access to this resource.'
            }, status)
        elif status == 403:
            response = {
                'Error': 'The fish is already in another aquarium.'
            }
        elif status == 404:
            response = {
                'Error': 'The specified aquarium and/or fish does not exist.'
            }

        return response, status

