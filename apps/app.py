
from flask import (
    Flask,
    render_template,
    make_response,
    url_for,
    request,
    redirect
)
from flask_oidc import OpenIDConnect
from keycloak import KeycloakOpenID

import json
import requests


app = Flask(__name__)


app.config.update({
    'SECRET_KEY': 'qrGdiQcH5KJbEK6jSHTTm66sELgcKhCH',
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    # 'OIDC_RESOURCE_CHECK_AUD': True,
    # 'OIDC_TOKEN_TYPE_HINT': 'access_token'
})

oidc = OpenIDConnect(app)

with open("client_secrets.json", "rb") as file:
    keycloak_params = json.load(file)

# Konfigurasi Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="https://sso.datains.id/",
    client_id=keycloak_params["web"]["client_id"],
    realm_name="development",
    client_secret_key=keycloak_params["web"]["client_secret"],
    verify=True
)


@app.route('/signout')
def logout():
    if oidc.user_loggedin:
        refresh_token = oidc.get_refresh_token()
        keycloak_openid.logout(refresh_token)
        oidc.logout()

        # flush cookies
        response = make_response(
            redirect(url_for('index'))
        )
        cookies_to_delete = request.cookies.keys()
        for cookie in cookies_to_delete:
            response.set_cookie(cookie, '', expires=0)

        return response
    else:
        return 'Not logged in'


@app.route('/')
def index():
    # print(request.json)
    return render_template("index.html", oidc=oidc)


@app.route('/login')
def login():
    return oidc.redirect_to_auth_server()

@app.route('/oidc_callback')
def oidc_callback():
    oidc.handle_callback()
    token = oidc.get_access_token()
    response = make_response(redirect(url_for('index')))
    response.set_cookie('access_token', token, httponly=True, secure=True)
    return response


@app.route('/protected')
@oidc.require_login
def protected():
    access_token = request.cookies.get('access_token')
    if access_token:
        return 'Access token: ' + access_token
    else:
        return redirect(url_for('index'))


@app.route('/home')
@oidc.require_login
def home():
    return {}
