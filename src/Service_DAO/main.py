
from flask import Flask, jsonify, request, Response
import json, os
#from modeles import Incident, Localisation, MeteoHourly, MeteoDaily

app = Flask(__name__)
DB_URI = 'incidents.json'


def initialiser_db():
    # si la db n'existe pas, la créer
    if not os.path.exists(DB_URI) or os.path.getsize(DB_URI) == 0:
        data = { "documents": [] }
        with open(DB_URI, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, indent=4)
    print("- Base de données initialisée")


def inserer_document(document):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)

    # trouver le prochain id
    next_id = get_next_id(data)
    document['id_incident'] = next_id

    # ajouter le nouveau document dans la collection
    data.get("documents").append(document)

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)


def get_next_id(data):
    # chercher dans les données pour le dernier id_incident et ajouter 1
    # s'il n'y a aucun document enregistré, retourner 0
    documents = data.get("documents", [])
    id_list = [doc.get("id_incident") for doc in documents if doc.get("id_incident") is not None]
    next_id = max(id_list) + 1 if id_list else 0
    return next_id


@app.route('/dao/incidents', methods=['POST'])
def creer_incident():
    # récupérer le payload
    jsondata = request.get_json()

    # insérer le nouveau document dans la db
    #       (le #id est auto-généré et assigné)
    inserer_document(jsondata)

    # retourner le nouveau document avec le code de succès 201
    return jsonify(jsondata), 201


if __name__ == '__main__':
    initialiser_db()
    app.run(debug=True, port=5601)
