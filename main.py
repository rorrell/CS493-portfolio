import json
import flask
import google_auth_oauthlib.flow
import requests
from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
from google.auth.transport import requests as req
from google.oauth2 import id_token
import constants
from blueprints import aquarium, user, fish
import auth

app = Flask(__name__)

CLIENT_SECRETS_FILE = 'client_secret.json'
secret_data = json.load(open(CLIENT_SECRETS_FILE))['web']
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']
API_SERVICE_NAME = 'people'
API_VERSION = 'v1'
client = datastore.Client()

app.register_blueprint(aquarium.bp)
app.register_blueprint(user.bp)
app.register_blueprint(fish.bp)


# This is adapted from:
# https://auth0.com/docs/quickstart/backend/python/01-authorization?_ga=2.46956069.349333901.1589042886-466012638.1589042885#create-the-jwt-validation-decorator
@app.errorhandler(auth.AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/send-to-oauth', methods=['GET'])
def send_to_oauth():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    data = {
        'value': state
    }

    with client.transaction():
        incomplete_key = client.key(constants.state)
        obj = datastore.Entity(key=incomplete_key)
        obj.update(data)
        client.put(obj)

    return flask.redirect(authorization_url)


@app.route('/oauth2callback', methods=['GET'])
def callback():
    args = request.args
    state_from_server = args.get('state')
    code = args.get('code')

    with client.transaction():
        query = client.query(kind=constants.state)
        query.add_filter("value", "=", state_from_server)
        results = list(query.fetch())

    if len(results) > 0:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state_from_server
        )
        flow.redirect_uri = flask.url_for('callback', _external=True)

        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        try:
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token,
                req.Request(),
                secret_data['client_id']
            )
            userid = idinfo['sub']
        except ValueError as e:
            return {
                "Error": e.args
            }, 401

        auth = {'Authorization': 'Bearer ' + credentials.token}

        r = requests.get(
            'https://people.googleapis.com/v1/people/me?personFields=names',
            headers=auth
        )
        if r.status_code == 200:
            names = r.json()['names'][0]

            data = {
                'name': names['displayName']
            }

            with client.transaction():
                query = client.query(kind=constants.user)
                query.add_filter("id", "=", userid)
                results = list(query.fetch())
                if len(results) == 0:
                    key = client.key(constants.user, userid)
                    obj = datastore.Entity(key=key)
                    obj.update(data)
                    client.put(obj)
            return render_template('results.html', data=names,
                                   jwt=credentials.id_token, id=userid)
    return {
        "Error": "Invalid code"
    }, 401


if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
