'''
Ce service reçoit les données entrantes (lat + long +
date + heure), collecte les données météo depuis leur source,
les traite et les renvoie au service Data au format JSON
'''

import json

from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

@app.route('/CollecteData', methods=['GET'])
def get_data():

    input = request.get_json()
    print(input) # imprimer payload

    # Appel à l'API open-meteo
    URI_SERV_METEO = 'fakeURI'
    data_meteo = requests.get(URI_SERV_METEO, json = input)
    # Transformations
    # a. Ne conserver que les 24h précédant le sinistre pour l'analyse
    # b. Calculer le min/max de température, l'accumulation de pluie et
    # de neige + les inclure dans le document JSON


    # Zone de dégel
    # Chargement du fichier geoJSON
    URI_ZONE_DEGEL = ''
    data_degel = requests.get(URI_ZONE_DEGEL)
    # Détermination de la zone correspondant aux coordonnées renseignées
    pass

    # Inclure la zone de dégel dans data_meteo


    return jsonify(data_meteo)
if __name__ == '__main__':
    app.run(debug=True)