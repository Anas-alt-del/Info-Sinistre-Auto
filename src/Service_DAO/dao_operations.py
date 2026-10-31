"""Opérations de persistance JSON et MongoDB du service DAO."""

import json
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError


JSON_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "db_incidents.json")
DATABASE_NAME = "info_sinistre_auto"
DATABASE_COLLECTION = "incidents"

_mongo_client = None
_mongodb = None


def is_mongodb_connected():
    """Indique si une connexion MongoDB est actuellement active."""
    return _mongo_client is not None


def connect_to_mongodb(uri):
    """Valide la connexion, crée la collection si nécessaire et l'active."""
    global _mongo_client, _mongodb

    new_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        new_client.admin.command("ping")
        base = new_client[DATABASE_NAME]
        if DATABASE_COLLECTION not in base.list_collection_names():
            base.create_collection(DATABASE_COLLECTION)
    except PyMongoError:
        new_client.close()
        raise

    previous_client = _mongo_client
    _mongo_client = new_client
    _mongodb = base[DATABASE_COLLECTION]
    if previous_client is not None:
        previous_client.close()


def disconnect_from_mongodb():
    """Ferme la connexion active et rétablit le stockage JSON."""
    global _mongo_client, _mongodb

    previous_client = _mongo_client
    _mongo_client = None
    _mongodb = None
    if previous_client is not None:
        previous_client.close()


def initialize_json_database():
    """Crée le fichier local s'il est absent ou vide."""
    if not os.path.exists(JSON_DATABASE_PATH) or os.path.getsize(JSON_DATABASE_PATH) == 0:
        with open(JSON_DATABASE_PATH, "w", encoding="utf-8") as file:
            json.dump({DATABASE_COLLECTION: []}, file, indent=4)


def get_next_json_id(documents):
    """Calcule le prochain identifiant disponible dans les documents JSON."""
    identifiers = [
        document.get("id_incident")
        for document in documents
        if document.get("id_incident") is not None
    ]
    return max(identifiers) + 1 if identifiers else 0


def find_json_incident_by_claim_id(claim_details):
    """Recherche un incident JSON à partir de son identifiant de réclamation."""
    identifier = claim_details.get("id_reclamation")
    if identifier is None:
        return None

    with open(JSON_DATABASE_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file).get(DATABASE_COLLECTION, [])
    for document in documents:
        claim_details = document.get("info_dossier", {})
        if identifier in claim_details.get("id_reclamation", []):
            return document
    return None


def find_json_incident_by_details(claim_details):
    """Recherche un incident JSON par date, heure et coordonnées."""
    with open(JSON_DATABASE_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file).get(DATABASE_COLLECTION, [])
    for document in documents:
        stored_claim_details = document.get("info_dossier", {})
        if all(
            stored_claim_details.get(field_name) == claim_details.get(field_name)
            for field_name in ("date", "heure", "latitude", "longitude")
        ):
            return document
    return None


def insert_json_incident(new_incident):
    """Ajoute un incident au fichier JSON et lui attribue un identifiant."""
    with open(JSON_DATABASE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    documents = data.get(DATABASE_COLLECTION, [])
    new_incident["id_incident"] = get_next_json_id(documents)
    documents.append(new_incident)
    data[DATABASE_COLLECTION] = documents
    with open(JSON_DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    return new_incident


def update_json_incident(incident):
    """Remplace un incident dans le fichier JSON."""
    with open(JSON_DATABASE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    documents = data.get(DATABASE_COLLECTION, [])
    data[DATABASE_COLLECTION] = [
        document for document in documents
        if document.get("id_incident") != incident["id_incident"]
    ] + [incident]
    with open(JSON_DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    return incident


def add_claim_id_to_json_incident(incident_id, claim_data):
    """Ajoute un identifiant de réclamation à un incident JSON."""
    with open(JSON_DATABASE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    updated_incident = None
    for document in data.get(DATABASE_COLLECTION, []):
        if document.get("id_incident") == incident_id:
            claim_details = document.setdefault("info_dossier", {})
            claim_details.setdefault("id_reclamation", []).append(
                claim_data["id_reclamation"]
            )
            updated_incident = document
            break
    with open(JSON_DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    return updated_incident


def get_next_mongodb_id():
    """Calcule le prochain identifiant d'incident MongoDB."""
    identifiers = [
        document["id_incident"]
        for document in _mongodb.find({}, {"id_incident": 1, "_id": 0})
        if "id_incident" in document
    ]
    return max(identifiers) + 1 if identifiers else 0


def find_mongodb_incident_by_claim_id(claim_details):
    """Recherche un incident MongoDB par identifiant de réclamation."""
    identifier = claim_details.get("id_reclamation")
    if identifier is None:
        return None
    for document in _mongodb.find({}, {"_id": 0}):
        stored_claim_details = document.get("info_dossier", {})
        if identifier in stored_claim_details.get("id_reclamation", []):
            return document
    return None


def find_mongodb_incident_by_details(claim_details):
    """Recherche un incident MongoDB par date, heure et coordonnées."""
    query = {
        f"info_dossier.{field_name}": claim_details[field_name]
        for field_name in ("date", "heure", "latitude", "longitude")
    }
    return _mongodb.find_one(query, {"_id": 0})


def insert_mongodb_incident(new_incident):
    """Insère un incident dans MongoDB et lui attribue un identifiant."""
    new_incident["id_incident"] = get_next_mongodb_id()
    _mongodb.insert_one(new_incident)
    new_incident.pop("_id", None)
    return new_incident


def update_mongodb_incident(incident):
    """Remplace un incident dans MongoDB."""
    _mongodb.replace_one({"id_incident": incident["id_incident"]}, incident)
    return incident


def add_claim_id_to_mongodb_incident(incident_id, claim_data):
    """Ajoute un identifiant de réclamation à un incident MongoDB."""
    result = _mongodb.update_one(
        {"id_incident": incident_id},
        {"$push": {"info_dossier.id_reclamation": claim_data["id_reclamation"]}},
    )
    if result.modified_count == 1:
        return find_mongodb_incident_by_claim_id(claim_data)
    return None
