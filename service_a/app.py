from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Konfigurasi Keycloak
app.config['KEYCLOAK_SERVER_URL'] = 'http://sso.datains.id'
app.config['KEYCLOAK_REALM'] = 'development'
app.config['KEYCLOAK_CLIENT_ID'] = 'app-a'
app.config['KEYCLOAK_CLIENT_SECRET'] = 'lIrZXb4hrEUGHKy1GG93EARgCFnDdq6A'
app.config['KEYCLOAK_REDIRECT_URI'] = 'http://localhost:1234/callback'

oauth = OAuth(app)
keycloak = oauth.register(
    name='keycloak',
    client_id=app.config['KEYCLOAK_CLIENT_ID'],
    client_secret=app.config['KEYCLOAK_CLIENT_SECRET'],
    server_metadata_url=f"{app.config['KEYCLOAK_SERVER_URL']}/realms/{app.config['KEYCLOAK_REALM']}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid profile email'},
)


def login_required(f):
    def wrap(*args, **kwargs):
        if 'profile' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
def index():
    if 'profile' in session:
        return f'Hello {session["profile"]["preferred_username"]}!'
    return '(App A) You are not logged in! <a href="/login">Login</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    nonce = os.urandom(24).hex()
    state = os.urandom(24).hex()
    session['nonce'] = nonce
    session['state'] = state
    return keycloak.authorize_redirect(redirect_uri, state=state, nonce=nonce)

@app.route('/callback')
def callback():
    token = keycloak.authorize_access_token()
    state = session.pop('state', None)
    nonce = session.pop('nonce', None)
    if state is None or nonce is None:
        return "Error: state or nonce not found in session", 400
    if state != request.args.get('state'):
        return "Error: state mismatch", 400
    session['profile'] = keycloak.parse_id_token(token, nonce=nonce)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    keycloak_server_url = app.config['KEYCLOAK_SERVER_URL']
    realm = app.config['KEYCLOAK_REALM']
    client_id = app.config['KEYCLOAK_CLIENT_ID']
    # redirect_uri = url_for('index', _external=True)
    redirect_uri = "http://localhost:1234"
    logout_url = f"{keycloak_server_url}/realms/{realm}/protocol/openid-connect/logout?redirect_uri={redirect_uri}"
    
    session.clear()
    return redirect(logout_url)

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected page. You are logged in as ' + session['profile']['preferred_username']


if __name__ == '__main__':
    app.run(debug=True)
