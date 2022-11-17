def required_attributes_error(content):
    expected = {'name', 'species', 'gender', 'color'}

    for key in expected:
        if key not in content or key is None:
            return {
                'Error': 'The request object is missing at least one of the required attributes.'
            }
    return None


def not_found_error(fish):
    if fish is None:
        return {
                'Error': 'No fish with this fish_id exists.'
            }
    return None
