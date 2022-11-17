def required_attributes_error(content):
    expected = {'name', 'waterType', 'size', 'material'}

    for key in expected:
        if key not in content or key is None:
            return {
                'Error': 'The request object is missing at least one of the required attributes.'
            }
    return None


def not_found_error(aquarium):
    if aquarium is None:
        return {
                'Error': 'No aquarium with this aquarium_id exists.'
            }
    return None
