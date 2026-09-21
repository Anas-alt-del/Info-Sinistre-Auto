
# Service DAO


from flask import Flask, jsonify, request
import json, os

app = Flask(__name__)
DB_URI = 'db_incidents.json'
DB_COLLECTION = 'incidents'



##### FONCTIONS UTILITAIRES

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


# Chercher un incident à partir du id_reclamation
def select_id_reclamation(info_dossier):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # collecter les inputs du nouveau document
    u_id_reclamation = info_dossier.get("id_reclamation")[0]

    # trouver le id_reclamation dans la bd
    for doc in documents:
        doc_id_reclamation = doc.get("info_dossier").get("id_reclamation")
        if u_id_reclamation in doc_id_reclamation:
            return doc

    # id_reclamation non trouvé
    return None


# Chercher un incident à partir des champs date + heure + latitude + longitude
def select_incident(info_dossier):
    # récupérer le data de la base de données
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # trouver l'incident dans la bd
    for doc in documents:
        dossier = doc.get("info_dossier", {})
        # vérifier si la combinaison (date + heure + latitude + longitude) existe déjà
        if (
            dossier.get("date") == info_dossier.get("date") and
            dossier.get("heure") == info_dossier.get("heure") and
            dossier.get("latitude") == info_dossier.get("latitude") and
            dossier.get("longitude") == info_dossier.get("longitude")
        ):
            return doc

    # retourner None s'il n'existe pas
    return None


# Insérer un nouvel incident à la bd
def insert_incident(nouvel_incident):
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


# Modifier un incident déjà existant de la bd
def update_incident(id_incident, incident):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # retirer le document existant de la bd
    documents = [doc for doc in documents if doc.get("id_incident") != id_incident]

    # ajouter le document modifié dans la collection
    documents.append(incident)

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)


# Ajouter un id_réclamation à un incident déjà existant
def update_reclamation(id_incident, id_reclamation):
    incident_modifie = None

    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    documents = data.get(DB_COLLECTION, [])

    # ajouter le id_reclamation à l'incident correspondant
    for doc in documents:
        if doc.get("id_incident") == id_incident:
            dossier = doc["info_dossier"]
            dossier["id_reclamation"].append(id_reclamation[0])
            incident_modifie = doc
            break

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)

    return incident_modifie



##### ROUTES


# Chercher un incident à partir des infos "info_dossier"
@app.route('/dao/incidents', methods=['GET'])
def chercher_incident():
    # récupérer le payload info_dossier
    info_dossier = request.get_json()

    # si le id_réclamation fourni existe déjà, retourner l'incident correspondant
    incident = select_id_reclamation(info_dossier)
    if incident is not None:
        return jsonify(incident), 200

    # si l'incident existe déjà, retourner l'incident correspondant
    incident = select_incident(info_dossier)
    print(incident)
    if incident is not None:
        return jsonify(incident), 210

    return jsonify({"erreur": "404 - incident non trouvé"}), 404


# Ajouter un incident à la bd
@app.route('/dao/incidents', methods=['POST'])
def creer_incident():
    # récupérer le payload
    jsondata = request.get_json()

    # insérer le nouveau document dans la db
    #       (le #id est auto-généré et assigné)
    insert_incident(jsondata)
    # retourner le nouveau document avec le code de succès 201
    return jsonify(jsondata), 201


# Modifier un incident existant à la bd
@app.route('/dao/incidents/<int:id_incident>', methods=['PUT'])
def modifier_incident(id_incident):
    # récupérer le payload
    jsondata = request.get_json()

    # modifier le document existant dans la db
    update_incident(id_incident, jsondata)

    # retourner le nouveau document avec le code de succès 201
    return jsonify(jsondata), 201


# Ajouter un id_reclamation à un incident existant à la bd
@app.route('/dao/incidents/<int:id_incident>/reclamation', methods=['PATCH'])
def ajouter_reclamation(id_incident):
    # récupérer le payload
    id_reclamation = request.get_json()

    # modifier le document existant dans la db, uniquement pour ajouter un id_reclamation
    incident = update_reclamation(id_incident, id_reclamation)

    # retourner le nouveau document avec le code de succès 201
    return jsonify(incident), 201



if __name__ == '__main__':
    initialiser_db()
    app.run(debug=True, port=5601)
