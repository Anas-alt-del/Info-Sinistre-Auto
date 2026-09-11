'''
Ce service reçoit les données entrantes (lat + long + date + heure +
numéro de réclamation) et coordonne Service_DAO et Service_Collecte afin
de vérifier si un enregistrement existe déjà, collecter les données et
les enregistrer (le cas échéant)
'''
from flask import Flask, request
import requests
import json

app = Flask(__name__)


@app.route('/data', methods=['GET'])
def get_data():
    # Appel à Service_DAO pour vérifier si un document correspondant
    # aux données utilisateur existe déjà (GET)
    input = request.get_json()
    lat = input["lat"]
    long = input["long"]
    date = input["date"]
    heure = input["heure"]
    id_reclamation = input["id_reclamation"]

    URI_SERV_DAO = ''
    # Appel à Service_Collecte si Service_DAO ne trouve pas un document
    # correspondant
    URI_SERV_COLLECTE = 'http://127.0.0.1:5020/collecte_data'
    info_meteo = requests.get(URI_SERV_COLLECTE, json={
        "lat": lat,
        "long": long,
        "date": date,
        "heure": heure
    }).json()

    # Consolidation des données utilisateur et des informations
    # collectées dans un document JSON
    info_sinistre = {'info_dossier': input,
                     'info_meteo':info_meteo}

    # Envoi du document à Service_DAO afin de l'insérer dans la
    # collection (POST)

    # Réponse à la requête entrante avec le document JSON
    return (info_sinistre)


if __name__ == '__main__':
    app.run(debug=True, port=5010)
