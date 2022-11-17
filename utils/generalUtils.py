def get_json_from_content(content):
    res = {}

    for key in content:
        res[key] = content[key]

    return res


def validate_content_type(request):
    if 'application/json' not in request.content_type:
        return {
                   'Error': 'Only JSON content is accepted.'
               }
    else:
        return None
