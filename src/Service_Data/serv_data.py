'''
Ce service reçoit les données entrantes (lat + long + date + heure +
numéro de réclamation) et coordonne Service_DAO et Service_Collecte afin
de vérifier si un enregistrement existe déjà, collecter les données et
les enregistrer (le cas échéant)
'''
from flask import Flask, request
import requests

app = Flask(__name__)

URI_SERV_DAO = {
    'chercher_incident': 'http://127.0.0.1:5601/dao/incidents',
    'creer_incident': 'http://127.0.0.1:5601/dao/incidents',
    'ajouter_reclamation': 'http://127.0.0.1:5601/dao/incidents/{}/reclamation'
}

URI_SERV_COLLECTE = 'http://127.0.0.1:5020/collecte_data'


@app.route('/data', methods=['GET'])
def chercher_incident():
    # Appel à Service_DAO pour vérifier si un document correspondant
    # aux données utilisateur existe déjà (GET)
    input = request.get_json()
    recherche, code = requests.get(URI_SERV_DAO['chercher_incident'], json=input)

    return recherche, code

@app.route('/data/reclamation', methods=['PATCH'])
def ajouter_reclamation():
    input = request.get_json()
    id_reclamation = input["id_reclamation"]
    id_incident = input["id_incident"]

    # incident non trouvé avec id_reclamation mais trouvé avec heure/lieu
    # requête PATCH afin d'ajouter le id à la liste
    confirmation = requests.patch(URI_SERV_DAO['ajouter_reclamation'].format(id_incident),
                                  json={"id_reclamation":id_reclamation}) #la méthode format insère id_incident dans le placeholder {}
    return confirmation

@app.route('/data', methods=['POST'])
def creer_incident():
    """Appel à Service_Collecte si Service_DAO ne trouve pas un document
    correspondant"""

    # inputs utilisateur
    payload = request.get_json()  # >>>  j'ai changé le nom 'input' à 'payload', pcq input est une instruction python

    latitude = payload["lat"]
    longitude = payload["long"]
    date = payload["date"]
    heure = payload["heure"]
    # id_reclamation = payload["id_reclamation"]  >>> (variable qui n'est pas utilisé)

    # Appel au service de collecte de données
    info_meteo = requests.get(URI_SERV_COLLECTE, json={
        "latitude": latitude,
        "longitude": longitude,
        "date": date,
        "heure": heure
    }).json()

    # Consolidation des données utilisateur et des informations
    # collectées dans un document JSON
    info_sinistre = {'info_dossier': payload,
                     'info_meteo': info_meteo}

    # Envoi du document à Service_DAO afin de l'insérer dans la
    # collection (POST)
    requests.post(URI_SERV_DAO['creer_incident'], json=info_sinistre)

    # Réponse à la requête entrante avec le document JSON
    return info_sinistre


if __name__ == '__main__':
    app.run(debug=True, port=5010)
