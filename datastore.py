from google.cloud import datastore
import constants

client = datastore.Client()


def add_attributes(obj, kind, base_url):
    if obj is not None:
        if obj.key.id is not None:
            obj['id'] = obj.key.id
            obj['self'] = base_url + kind.lower() + '/' + str(obj.key.id)
        else:
            obj['id'] = obj.key.name
    return obj


def get_by_id(kind, _id, base_url):
    key = client.key(kind, _id)
    obj = client.get(key)
    return add_attributes(obj, kind, base_url)


def get_all(kind, base_url):
    query = client.query(kind=kind)
    results = list(query.fetch())
    return [add_attributes(obj, kind, base_url) for obj in results]


def get_page(query, limit, cursor=None):
    query_iter = query.fetch(start_cursor=cursor, limit=limit)
    page = next(query_iter.pages)
    next_cursor = query_iter.next_page_token

    return list(page), next_cursor


def get_all_paged(kind, limit, base_url, cursor=None):
    query = client.query(kind=kind)
    objects, next_cursor = get_page(query, limit, cursor)

    return [add_attributes(obj, kind, base_url) for obj in objects], next_cursor


def post(kind, _json, base_url):
    with client.transaction():
        incomplete_key = client.key(kind)
        obj = datastore.Entity(key=incomplete_key)
        obj.update(_json)
        client.put(obj)
    return add_attributes(obj, kind, base_url)


def patch(kind, _id, _json, base_url):
    with client.transaction():
        key = client.key(kind, _id)
        obj = client.get(key)
        if obj is None:
            return
        for key in _json:
            obj[key] = _json[key]
    client.put(obj)
    return add_attributes(obj, kind, base_url)


def delete(kind, _id):
    with client.transaction():
        key = client.key(kind, _id)
        obj = client.get(key)
        if obj is None:
            return False
        client.delete(key)
        return True


def name_exists(kind, name: str, expect_one=False):
    query = client.query(kind=kind)
    query.add_filter('name', '=', name)
    results = list(query.fetch())
    if expect_one:
        return len(results) > 1
    return len(results) > 0


def get_by_owner(kind, owner, base_url):
    query = client.query(kind=kind)
    query.add_filter('ownerId', '=', owner)
    results = list(query.fetch())
    return [add_attributes(obj, kind, base_url) for obj in results]


def get_fish_by_aquarium(aquarium_id, base_url):
    query = client.query(kind=constants.fish)
    query.add_filter('aquariumId', '=', aquarium_id)
    results = list(query.fetch())
    return [add_attributes(obj, constants.fish, base_url) for obj in results]


def add_attributes_to_aquarium(aquarium, base_url):
    aquarium['owner'] = get_by_id(constants.user, aquarium['ownerId'],
                                  base_url)
    del aquarium['ownerId']
    fish = get_fish_by_aquarium(aquarium.key.id, base_url)
    for f in fish:
        del f['gender']
        del f['color']
        del f['aquariumId']
        del f['ownerId']
    aquarium['fish'] = fish
    return aquarium


def get_aquarium_with_fish(aquarium_id, base_url):
    with client.transaction():
        aquarium = get_by_id(constants.aquarium, aquarium_id, base_url)
        if aquarium is None:
            return aquarium

        return add_attributes_to_aquarium(aquarium, base_url)


def get_all_aquariums_with_fish(owner_id, base_url, cursor=None):
    with client.transaction():
        query = client.query(kind=constants.aquarium)
        query.add_filter('ownerId', '=', owner_id)
        aquariums, next_cursor = get_page(query, 5, cursor)
        return [add_attributes_to_aquarium(
            add_attributes(aquarium, constants.aquarium, base_url), base_url)
                   for aquarium in aquariums], next_cursor


def add_attributes_to_fish(fish, base_url):
    fish['owner'] = get_by_id(constants.user, fish['ownerId'], base_url)
    del fish['ownerId']

    if 'aquariumId' in fish:
        aquarium = get_by_id(constants.aquarium, fish['aquariumId'], base_url)
        del aquarium['waterType']
        del aquarium['size']
        del aquarium['material']
        del aquarium['ownerId']
        fish['aquarium'] = aquarium
        del fish['aquariumId']

    return fish


def get_all_fish_with_aquariums(owner_id, base_url, cursor):
    with client.transaction():
        query = client.query(kind=constants.fish)
        query.add_filter('ownerId', '=', owner_id)
        fish, next_cursor = get_page(query, 5, cursor)
        return [add_attributes_to_fish(
            add_attributes(f, constants.fish, base_url), base_url)
                   for f in fish], next_cursor


def get_fish_with_aquarium(fish_id, base_url):
    with client.transaction():
        fish = get_by_id(constants.fish, fish_id, base_url)
        if fish is None:
            return fish

        return add_attributes_to_fish(fish, base_url)


def put_fish_in_aquarium(owner_id, fish_id, aquarium_id, base_url):
    with client.transaction():
        fish = get_by_id(constants.fish, fish_id, base_url)
        aquarium = get_by_id(constants.aquarium, aquarium_id, base_url)

        if fish['ownerId'] != owner_id or aquarium['ownerId'] != owner_id:
            return 401
        if fish is None or aquarium is None:
            return 404
        if 'aquariumId' in fish and fish['aquariumId'] is not None:
            return 403
        fish['aquariumId'] = aquarium.key.id

        del fish['id']
        del fish['self']
        client.put(fish)
    return 204


def delete_fish_from_aquarium(owner_id, fish_id, aquarium_id, base_url):
    with client.transaction():
        fish = get_by_id(constants.fish, fish_id, base_url)
        aquarium = get_by_id(constants.aquarium, aquarium_id, base_url)

        if fish['ownerId'] != owner_id or aquarium['ownerId'] != owner_id:
            return 401
        if fish is None or aquarium is None or ('aquariumId' in fish and fish['aquariumId'] != aquarium.key.id):
            return 404

        del fish['aquariumId']
        del fish['id']
        del fish['self']
        client.put(fish)
    return 204


def delete_if_owned(kind, _id, owner_id):
    with client.transaction():
        key = client.key(kind, _id)
        obj = client.get(key)
        if obj is None:
            return 404
        if obj['ownerId'] != owner_id:
            return 401
        client.delete(key)
        return 204


def delete_aquarium_and_remove_fish_if_owned(_id, owner_id):
    with client.transaction():
        key = client.key(constants.aquarium, _id)
        obj = client.get(key)
        if obj is None:
            return 404
        if obj['ownerId'] != owner_id:
            return 401

        query = client.query(kind=constants.fish)
        query.add_filter('aquariumId', '=', _id)
        results = list(query.fetch())
        for fish in results:
            del fish['aquariumId']
            client.put(fish)

        client.delete(key)
        return 204
