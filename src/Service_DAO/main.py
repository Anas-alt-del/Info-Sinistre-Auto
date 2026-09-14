
# Service DAO


from flask import Flask, jsonify, request, Response
import json, os
#from modeles import Incident, Localisation, MeteoHourly, MeteoDaily

app = Flask(__name__)
DB_URI = 'db_incidents.json'
DB_COLLECTION = 'incidents'



##### FONCTIONS UTILITAIRES


# Si id_reclamation existe déjà dans la bd
def existe_id_reclamation(jsondata):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # collecter les inputs du nouveau document
    u_dossier = jsondata.get("info_dossier", {})
    u_id_reclamation = u_dossier.get("id_reclamation")[0]

    # vérifier si le id_réclamation existe déjà dans la bd
    for doc in documents:
        dossier = doc.get("info_dossier", {})

        doc_id_reclamation = dossier.get("id_reclamation", [])
        if u_id_reclamation in doc_id_reclamation:
            return True

    # retourne False si non trouvé
    return False


# Si l'incident fourni existe déjà dans la bd
def existe_incident(jsondata):
    # récupérer le data de la base de données
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # collecter les infos du nouveau document fourni
    u_dossier = jsondata.get("info_dossier", {})
    u_date = u_dossier.get("date")
    u_heure = u_dossier.get("heure")
    u_lat = u_dossier.get("latitude")
    u_long = u_dossier.get("longitude")
    match_id_incident = None

    # vérifier l'occurrence des infos dans la bd
    for doc in documents:
        dossier = doc.get("info_dossier", {})
        # vérifier si la combinaison (date + heure + latitude + longitude) existe déjà
        if (
            dossier.get("date") == u_date and
            dossier.get("heure") == u_heure and
            dossier.get("latitude") == u_lat and
            dossier.get("longitude") == u_long
        ):
            match_id_incident = doc.get("id_incident")
            break

    # retourner le id_incident si l'incident existe déjà, ou None s'il n'existe pas
    return match_id_incident


# Récupérer le prochain id_incident à utiliser dans la bd
def get_next_id(documents):
    # chercher dans les données pour le dernier id_incident et ajouter 1
    # s'il n'y a aucun document enregistré, retourner 0
    id_list = [doc.get("id_incident") for doc in documents if doc.get("id_incident") is not None]
    next_id = max(id_list) + 1 if id_list else 0
    return next_id



##### FONCTIONS PRINCIPALES


# Initialisation de la base de données
def initialiser_db():
    # si la db n'existe pas, la créer
    if not os.path.exists(DB_URI) or os.path.getsize(DB_URI) == 0:
        data = { DB_COLLECTION: [] }
        with open(DB_URI, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, indent=4)
    print("- Base de données initialisée")


# Insérer un nouvel incident à la bd
def inserer_incident(nouvel_incident):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # trouver le prochain id
    next_id = get_next_id(documents)
    nouvel_incident['id_incident'] = next_id

    # ajouter le nouveau document dans la collection
    documents.append(nouvel_incident)

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)


# Ajouter un id_réclamation à un incident déjà existant
def inserer_reclamation(id_incident, incident):
    incident_existant = None

    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # récupérer le nouveau id_réclamation fourni
    nouveau_id_reclamation = incident.get("info_dossier").get("id_reclamation")[0]

    for doc in documents:
        if doc.get("id_incident") == id_incident:
            doc["info_dossier"]["id_reclamation"].append(nouveau_id_reclamation)
            incident_existant = doc
            break

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)

    return incident_existant



##### ROUTES


@app.route('/dao/incidents', methods=['POST'])
def creer_incident():
    # récupérer le payload
    jsondata = request.get_json()

    # vérifier si un id_réclamation existe déjà à partir du data fourni
    if existe_id_reclamation(jsondata):
        return jsonify({"erreur": "409 - id_reclamation déjà existant"}), 409  # conflict

    # vérifier si l'incident existe déjà à partir du data fourni
    id_incident = existe_incident(jsondata)
    print(id_incident)
    if id_incident is not None:
        # l'incident existe déjà, ajouter le id_réclamation seulement à l'incident
        jsondata = inserer_reclamation(id_incident, jsondata)
        # retourner le document modifié avec le code de succès 200
        return jsonify(jsondata), 200
    else:
        # l'incident n'existe pas, insérer le nouveau document dans la db (le #id est auto-généré et assigné)
        inserer_incident(jsondata)
        # retourner le nouveau document avec le code de succès 201
        return jsonify(jsondata), 201


if __name__ == '__main__':
    initialiser_db()
    app.run(debug=True, port=5601)
