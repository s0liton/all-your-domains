from flask import Flask, render_template, url_for, redirect, session, json, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from utils import access_token_valid, id_token_valid, configuration
from user import User
import requests
import base64
from domains import Domains

app = Flask(__name__)
app.config.update({'SECRET_KEY': 'SomeReallySecretShit'})

login_manager = LoginManager()
login_manager.init_app(app)

# Static Params
APP_STATE = 'ApplicationState+CSRFProtection'
NONCE = 'SampleNonce'
apikey = ''
url = 'https://api.freenom.com/v2'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/login")
def login():
    bu = configuration['issuer'].split('/oauth2')[0]
    cid = configuration['client_id']
    audience = configuration['audience']
    return render_template('login.html',
                           baseUri=bu,
                           clientId=cid,
                           state=APP_STATE,
                           nonce=NONCE,
                           audience=audience)


@app.route("/authorization-code/callback")
def callback():
    if request.args.get("state") != APP_STATE:
        return "The state is unexpected.", 403
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        configuration["token_uri"],
        headers=headers,
        data=query_params,
        auth=(configuration["client_id"], configuration["client_secret"]),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]
    audience = configuration["audience"]

    # Tokens do not some to validate no matter what....will use introspect API in prod to validate.
    # if not access_token_valid(access_token, configuration["issuer"], audience):
    #    return "Access token is invalid", 403

    # if not id_token_valid(id_token, configuration["issuer"], configuration["client_id"], NONCE, audience):
    #    return "ID token is invalid", 403

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(configuration["userinfo_uri"],
                                     headers={'Authorization': f'Bearer {access_token}'}).json()

    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = userinfo_response["given_name"]

    user = User(
        id_=unique_id, name=user_name, email=user_email
    )

    if not User.get(unique_id):
        User.create(unique_id, user_name, user_email)

    login_user(user)

    return redirect(url_for("domains"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/domains")
def domain_manager():
    user_domain = request.form.get("domainname")
    x = Domains(url, apikey)
    x.search_domain(user_domain)
    return render_template("domains.html", user=current_user)


def base64_to_str(data):
    return str(base64.b64encode(json.dumps(data).encode('utf-8')), 'utf-8')


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
