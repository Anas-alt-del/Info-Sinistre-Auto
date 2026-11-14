'''
Ce service reçoit les données entrantes (lat + long + date + heure +
numéro de réclamation) et coordonne Service_DAO et Service_Collecte afin
de vérifier si un enregistrement existe déjà, collecter les données et
les enregistrer (le cas échéant)
'''
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests, jwt, os
from flasgger import Swagger

from config import DATA_COLLECTION_URL, DAO_SERVICE_ENDPOINTS
app = Flask(__name__)
app.config['SECRET_KEY'] = 'le bonheur est dans le pré'
app.config['SWAGGER'] = {
    'title' : 'Info-Sinistre-Auto - Service Data',
    'version' : '1.0.1'
}
swagger = Swagger(app)

CORS(app)


# Fonctions utilitaires

def get_bearer_token():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]  # retourner uniquement le token
    return request.headers.get('token')

def is_token_valid(token):
    try:
        jwt.decode(token, key=app.config['SECRET_KEY'], algorithms='HS256')
        return True
    except jwt.InvalidTokenError:
        return False


# Routes
@app.route('/')
@app.route('/index')
def index():
    return redirect('/apidocs')

@app.route('/data', methods=['GET'])
def find_incident():
    """
    Recherche d'un document en fonction des informations du dossier
    ---
    parameters:
      - in: header
        name: token
        type: string
        required: true
        description: Clé d'autentification
      - in: query
        name: id_reclamation
        type: string
        required: false
        example: "ABC123"
      - in: query
        name: date
        type: string
        format: date
        required: false
        example: "2025-12-31"
      - in: query
        name: heure
        type: string
        required: false
        example: "19:15"
      - in: query
        name: latitude
        type: number
        format: float
        required: false
        example: 49.914
      - in: query
        name: longitude
        type: number
        format: float
        required: false
        example: 74.963
    responses:
        200:
            description: Dossier trouvé avec le id_reclamation
        210:
            description: Dossier trouvé avec les informations de l'incident (date, heure, latitude, longitude)
        401:
            description: Non-autorisé. Token manquant, invalide ou expiré
        404:
            description: Dossier non trouvé
    """

    # Vérifie le jeton d'authentification.
    token = get_bearer_token()
    if not is_token_valid(token):
        return jsonify({"message": "Erreur 401: Unauthorized. Token non fourni, invalide ou expiré"}), 401

    payload = {
        'id_reclamation': request.args.get('id_reclamation'),
        'date': request.args.get('date'),
        'heure': request.args.get('heure'),
    }
    for coordinate in ('latitude', 'longitude'):
        value = request.args.get(coordinate)
        try:
            payload[coordinate] = float(value) if value is not None else None
        except ValueError:
            return jsonify({"message": "Latitude et longitude doivent être numériques."}), 400

    response = requests.get(DAO_SERVICE_ENDPOINTS['find_incident'], params=payload)
    result = response.json()
    code = response.status_code
    return result, code

@app.route('/data/reclamation', methods=['PATCH'])
def add_claim():
    """
    Ajouter un id_reclamation à un incident existant
    ---
    parameters:
      - in: header
        name: token
        type: string
        required: true
        description: Clé d'autentification
      - in: body
        name: payload
        description: id_reclamation, id_incident
        schema:
            type: object
            properties:
                id_reclamation:
                    type: string
                    example: "ABC123"
                id_incident:
                    type: number
                    format: integer
                    example: 1
    responses:
        200:
            description: Id_reclamation ajouté à l'incident
        401:
            description: Non-autorisé. Token manquant, invalide ou expiré
    """

    """Requête PATCH à serv_DAO pour ajouter id_reclamation à l'incident
    correspondant (si l'incident n'est pas trouvé avec id_reclamation
    mais qu'il est trouvé avec date/heure/lieu) """

    # Vérifie le jeton d'authentification.
    token = get_bearer_token()
    if not is_token_valid(token):
        return jsonify({"message": "Erreur 401: Unauthorized. Token non fourni, invalide ou expiré"}), 401

    payload = request.get_json()
    claim_id = payload["id_reclamation"]
    incident_id = payload["id_incident"]

    # Envoie une requête PATCH pour ajouter l'identifiant à la liste.
    confirmation = requests.patch(DAO_SERVICE_ENDPOINTS['add_claim'].format(incident_id),
                                  json={"id_reclamation":claim_id}).json()  # Le format insère l'identifiant d'incident dans l'espace réservé.
    return confirmation, 200

@app.route('/data', methods=['POST'])
def create_incident():
    """
    Ajouté un nouveau document en fonction des informations du dossier
    ---
    parameters:
      - in: header
        name: token
        type: string
        required: true
        description: Clé d'autentification
      - in: body
        name: payload
        description: Les informations concernant le dossier (id_reclamation, date, heure, latitude, longitude)
        schema:
            type: object
            properties:
                id_reclamation:
                    type: string
                    example: "ABC123"
                date:
                    type: string
                    format: date
                    example: "2025-12-31"
                heure:
                    type: string
                    format: time
                    example: "19:15"
                latitude:
                    type: number
                    format: float
                    example: 49.914
                longitude:
                    type: number
                    format: float
                    example: 74.963
    responses:
        201:
            description: Dossier ajouté
        401:
            description: Non-autorisé. Token manquant, invalide ou expiré
    """

    # Vérifie le jeton d'authentification.
    token = get_bearer_token()
    if not is_token_valid(token):
        return jsonify({"message": "Erreur 401: Unauthorized. Token non fourni, invalide ou expiré"}), 401

    # Récupère les données saisies par l'utilisateur.
    payload = request.get_json()
    latitude = payload["latitude"]
    longitude = payload["longitude"]
    incident_date = payload["date"]
    incident_time = payload["heure"]

    # Appelle le service de collecte des données.
    weather_info = requests.get(DATA_COLLECTION_URL, json={
        "latitude": latitude,
        "longitude": longitude,
        "date": incident_date,
        "heure": incident_time
    }).json()

    # Regroupe les données utilisateur et les informations collectées
    # dans un document JSON.
    payload['id_reclamation'] = [payload['id_reclamation']]
    claim_record = {'info_dossier': payload,
                     'info_meteo': weather_info}

    # Envoie le document au service DAO pour l'insérer dans la collection.
    new_incident = requests.post(DAO_SERVICE_ENDPOINTS['create_incident'], json=claim_record).json()

    # Renvoie le document JSON en réponse à la requête.
    return new_incident, 201

@app.route('/data', methods=['PUT'])
def update_incident():
    """
    Modifier un document existant
    ---
    parameters:
      - in: header
        name: token
        type: string
        required: true
        description: Clé d'autentification
      - in: body
        name: payload
        description: Les informations concernant le dossier (id_reclamation, date, heure, latitude, longitude)
        schema:
            type: object
            properties:
                id_reclamation:
                    type: string
                    example: "ABC123"
                date:
                    type: string
                    format: date
                    example: "2025-12-31"
                heure:
                    type: string
                    format: time
                    example: "19:15"
                latitude:
                    type: number
                    format: float
                    example: 49.914
                longitude:
                    type: number
                    format: float
                    example: 74.963
    responses:
        201:
            description: Dossier modifié
        401:
            description: Non-autorisé. Token manquant, invalide ou expiré
    """

    # Vérifie le jeton d'authentification.
    token = get_bearer_token()
    if not is_token_valid(token):
        return jsonify({"message": "Erreur 401: Unauthorized. Token non fourni, invalide ou expiré"}), 401

    # Récupère les données saisies par l'utilisateur.
    payload = request.get_json()

    # Envoie le document au service DAO pour modifier un enregistrement existant.
    updated_incident = requests.put(DAO_SERVICE_ENDPOINTS['update_incident'], json=payload).json()

    # Renvoie le document JSON en réponse à la requête.
    return updated_incident, 201


@app.route('/database/status', methods=['GET'])
def database_status():
    """Relaye à l'interface le mode de stockage actif du DAO."""
    try:
        response = requests.get(DAO_SERVICE_ENDPOINTS['database_status'], timeout=8)
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de joindre le statut de la base DAO.")
        return jsonify({"message": "Le service DAO est indisponible."}), 503
    return jsonify(response.json()), response.status_code


@app.route('/database/connect', methods=['POST'])
def database_connect():
    """Transmet l'URI au DAO sans la conserver dans Service_Data."""
    payload = request.get_json(silent=True) or {}
    try:
        response = requests.post(
            DAO_SERVICE_ENDPOINTS['database_connect'], json=payload, timeout=8
        )
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de joindre le service DAO pour la connexion.")
        return jsonify({"message": "Le service DAO est indisponible."}), 503
    return jsonify(response.json()), response.status_code


@app.route('/database/disconnect', methods=['POST'])
def database_disconnect():
    """Demande au DAO de fermer MongoDB et de reprendre le stockage JSON."""
    try:
        response = requests.post(
            DAO_SERVICE_ENDPOINTS['database_disconnect'], timeout=8
        )
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de joindre le service DAO pour la déconnexion.")
        return jsonify({"message": "Le service DAO est indisponible."}), 503
    return jsonify(response.json()), response.status_code


# Route utilisée pour maintenir les services déployés actifs (arrêt
# automatique par défaut).
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(debug=True, port=port, host='0.0.0.0')
