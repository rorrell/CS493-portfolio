import requests
from google.oauth2 import id_token
from google.auth.transport import requests as req
import json

CLIENT_SECRETS_FILE = 'client_secret.json'
secret_data = json.load(open(CLIENT_SECRETS_FILE))['web']


# This is adapted from:
# https://auth0.com/docs/quickstart/backend/python/01-authorization?_ga=2.46956069.349333901.1589042886-466012638.1589042885#create-the-jwt-validation-decorator
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_id_from_jwt(_request):
    if 'Authorization' in _request.headers:
        auth_header = _request.headers['Authorization'].split()
        token = auth_header[1]
        try:
            id_info = id_token.verify_oauth2_token(token, req.Request(),
                                                   secret_data['client_id'])
        except ValueError as e:
            err = {
                "Error": "You are not authorized."
            }
            raise AuthError(err, 401)
        return id_info['sub']
    else:
        err = {
            "Error": "You are not authorized."
        }
        raise AuthError(err, 401)
