from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import jwt, datetime, os
from flasgger import Swagger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'le bonheur est dans le pré'
app.config['SWAGGER'] = {
    'title' : 'Info-Sinistre-Auto - Service autentification',
    'version' : '1.0'
}
swagger = Swagger(app)
CORS(app)


TOKEN_EXPIRATION_MINUTES = 60  # >>> Le token expire après x minutes.


# Fonctions utilitaires

def verify_login(username, password):
    if username.lower() == 'alain' and password.lower() == 'flouflou':
        return True
    return False

def generate_token():
    expiration_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES))
    token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
    return token


# Routes

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

    # Récupère le nom d'utilisateur et le mot de passe transmis.
    authentication_data = request.get_json()

    if verify_login(authentication_data.get('username'), authentication_data.get('password')):
        return jsonify({
            "token": generate_token()
        }), 200
    else:
        return jsonify({
            "message": "Erreur 401 - Non autorisé. Le username ou le password est invalide"
        }), 401

# Route utilisée pour maintenir les services déployés actifs (arrêt
# automatique par défaut).
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5602))
    app.run(debug=True, port=port, host='0.0.0.0')
