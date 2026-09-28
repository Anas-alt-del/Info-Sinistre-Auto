

from flask import Flask, request, jsonify, redirect
import jwt, datetime
from flasgger import Swagger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'le bonheur est dans le pré'
swagger = Swagger(app)

DELAI_EXPIRATION_MIN = 60  # >>> Le token expire après x minutes.


# FONCTIONS UTILITAIRES

def verifier_login(username, password):
    if username.lower() == 'alain' and password.lower() == 'flouflou':
        return True
    return False

def generer_token():
    expiration_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=DELAI_EXPIRATION_MIN))
    token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
    return token


# ROUTES

@app.route('/')
@app.route('/index')
def index():
    return redirect('/apidocs')

@app.route('/auth/login', methods=['POST'])
def login():
    """
    Valider les informations de connexion et retourner un jeton de connexion
    ---
    parameters:
      - in: body
        name: payload
        description: Les informations de connexion (username, password)
        schema:
            type: object
            properties:
                username:
                    type: string
                    example: "alain"
                password:
                    type: string
                    example: "flouflou"
    responses:
        200:
            description: Informations de connexion valides. Token retourné. Valide pour 60 minutes
        401:
            description: Non-autorisé. Informations de connexion invalides
    """

    # récupérer le payload username + password
    info_auth = request.get_json()

    if verifier_login(info_auth.get('username'), info_auth.get('password')):
        return jsonify({
            "token": generer_token()
        }), 200
    else:
        return jsonify({
            "message": "Erreur 401 - Non autorisé. Le username ou le password est invalide"
        }), 401



if __name__ == '__main__':
    app.run(debug=True, port=5602)