"""API du service DAO, avec sélection du stockage selon la connexion active."""

import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo.errors import PyMongoError

import dao_operations as operations


app = Flask(__name__)
CORS(app)

operations.initialize_json_database()


def find_incident_by_claim_id(claim_details):
    """Utilise la recherche adaptée au stockage actif."""
    operation = (
        operations.find_mongodb_incident_by_claim_id
        if operations.is_mongodb_connected()
        else operations.find_json_incident_by_claim_id
    )
    return operation(claim_details)


def find_incident_by_details(claim_details):
    """Utilise la recherche adaptée au stockage actif."""
    operation = (
        operations.find_mongodb_incident_by_details
        if operations.is_mongodb_connected()
        else operations.find_json_incident_by_details
    )
    return operation(claim_details)


def insert_incident(new_incident):
    """Insère un incident dans le stockage actif."""
    operation = (
        operations.insert_mongodb_incident
        if operations.is_mongodb_connected()
        else operations.insert_json_incident
    )
    return operation(new_incident)


def update_active_incident(incident):
    """Met à jour un incident dans le stockage actif."""
    operation = (
        operations.update_mongodb_incident
        if operations.is_mongodb_connected()
        else operations.update_json_incident
    )
    return operation(incident)


def add_claim_id_to_incident(incident_id, claim_data):
    """Ajoute une réclamation dans le stockage actif."""
    operation = (
        operations.add_claim_id_to_mongodb_incident
        if operations.is_mongodb_connected()
        else operations.add_claim_id_to_json_incident
    )
    return operation(incident_id, claim_data)


@app.route("/dao/database/status", methods=["GET"])
def database_status():
    """Retourne le mode de stockage sans exposer l'URI de connexion."""
    connected = operations.is_mongodb_connected()
    return jsonify({
        "connected": connected,
        "mode": "mongodb" if connected else "json",
    }), 200


@app.route("/dao/database/connect", methods=["POST"])
def database_connect():
    """Connecte MongoDB et crée la collection si elle est absente."""
    payload = request.get_json(silent=True) or {}
    uri = payload.get("connection_string", "")
    if not isinstance(uri, str) or not uri.strip():
        return jsonify({"message": "Une URI MongoDB est requise."}), 400

    try:
        operations.connect_to_mongodb(uri.strip())
    except PyMongoError:
        app.logger.error("Échec de la connexion MongoDB.")
        return jsonify({
            "message": "Connexion MongoDB impossible. Vérifiez l'URI et la disponibilité du serveur."
        }), 502

    return jsonify({
        "connected": True,
        "mode": "mongodb",
        "message": "Connexion MongoDB réussie.",
    }), 200


@app.route("/dao/database/disconnect", methods=["POST"])
def database_disconnect():
    """Ferme MongoDB pour repasser au fichier JSON local."""
    operations.disconnect_from_mongodb()
    return jsonify({
        "connected": False,
        "mode": "json",
        "message": "Déconnexion MongoDB réussie. Le fichier JSON local est utilisé.",
    }), 200


@app.route("/dao/incidents", methods=["GET"])
def find_incident():
    """Recherche un incident par réclamation ou informations de dossier."""
    claim_details = {
        "id_reclamation": request.args.get("id_reclamation"),
        "date": request.args.get("date"),
        "heure": request.args.get("heure"),
    }
    for coordinate in ("latitude", "longitude"):
        value = request.args.get(coordinate)
        try:
            claim_details[coordinate] = float(value) if value is not None else None
        except ValueError:
            return jsonify({"message": "Latitude et longitude doivent être numériques."}), 400

    incident = find_incident_by_claim_id(claim_details)
    if incident is not None:
        return jsonify(incident), 200

    incident = find_incident_by_details(claim_details)
    if incident is not None:
        return jsonify(incident), 210

    return jsonify({"erreur": "404 - Document non trouvé"}), 404


@app.route("/dao/incidents", methods=["POST"])
def create_incident():
    """Ajoute un nouvel incident dans le stockage actif."""
    request_data = request.get_json()
    new_incident = insert_incident(request_data)
    return jsonify(new_incident), 201


@app.route("/dao/incidents", methods=["PUT"])
def update_incident():
    """Modifie un incident existant dans le stockage actif."""
    request_data = request.get_json()
    updated_incident = update_active_incident(request_data)
    return jsonify(updated_incident), 201


@app.route("/dao/incidents/<int:incident_id>/reclamation", methods=["PATCH"])
def add_claim(incident_id):
    """Ajoute un identifiant de réclamation à un incident existant."""
    claim_data = request.get_json()
    incident = add_claim_id_to_incident(incident_id, claim_data)
    if incident is None:
        return jsonify({"erreur": "Incident non trouvé."}), 404
    return jsonify(incident), 200


@app.route("/health", methods=["GET"])
def health():
    """Vérifie que le service DAO répond."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5601))
    app.run(debug=True, port=port, host="0.0.0.0")
