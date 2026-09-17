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

URI_SERV_DAO = {
    'chercher_incident': 'http://127.0.0.1:5601/dao/incidents',
    'creer_incident': 'http://127.0.0.1:5601/dao/incidents',
    'modifier_incident': 'http://127.0.0.1:5601/dao/incidents',
    'ajouter_reclamation': 'http://127.0.0.1:5601/dao/incidents'
}

URI_SERV_COLLECTE = 'http://127.0.0.1:5020/collecte_data'


@app.route('/data', methods=['GET'])
def get_data():
    # Appel à Service_DAO pour vérifier si un document correspondant
    # aux données utilisateur existe déjà (GET)
    input = request.get_json()
    recherche, code = requests.get(URI_SERV_DAO['chercher_incident'], json=input)

    if code == 200:
        # incident trouvé avec id_reclamation
        return (recherche)
    elif code == 210:
        # incident non trouvé avec id_reclamation mais trouvé avec heure/lieu
        # requête PUT afin d'ajouter le id à la liste
        requests.put(URI_SERV_DAO['ajouter_reclamation'], json=recherche)
        return (recherche)

    else:

        # Appel à Service_Collecte si Service_DAO ne trouve pas un document
        # correspondant
        latitude = input["lat"]
        longitude = input["long"]
        date = input["date"]
        heure = input["heure"]
        id_reclamation = input["id_reclamation"]

        info_meteo = requests.get(URI_SERV_COLLECTE, json={
            "latitude": latitude,
            "longitude": longitude,
            "date": date,
            "heure": heure
        }).json()

        # Consolidation des données utilisateur et des informations
        # collectées dans un document JSON
        info_sinistre = {'info_dossier': input,
                         'info_meteo': info_meteo}

        # Envoi du document à Service_DAO afin de l'insérer dans la
        # collection (POST)
        requests.post(URI_SERV_DAO['creer_incident'], json=info_sinistre)

        # Réponse à la requête entrante avec le document JSON
        return (info_sinistre)


if __name__ == '__main__':
    app.run(debug=True, port=5010)
