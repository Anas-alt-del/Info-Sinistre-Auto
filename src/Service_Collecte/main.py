'''
Ce service reçoit les données entrantes (lat + long +
date + heure), collecte les données météo depuis leur source,
les traite et les renvoie au service Data au format JSON
'''

import json

from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


@app.route('/CollecteData', methods=['GET'])
def get_data():
    input = request.get_json()
    print(input)  # imprimer payload
    lat = input["lat"]
    long = input["long"]
    date = datetime.strptime(input["date"], "%Y-%m-%d").date()
    heure = datetime.strptime(input["heure"], "%H:%M")

    # Appel à l'API open-meteo
    URI_SERV_METEO = (f'https://archive-api.open-meteo.com/v1/archive?'
                      f'latitude={lat}&'
                      f'longitude={long}&'
                      f'start_date={date - timedelta(days=1)}&'
                      f'end_date={date}&'
                      'daily=sunrise,sunset&'
                      'hourly=temperature_2m,rain,snowfall,cloud_cover,'
                      'wind_speed_10m,wind_direction_10m,weather_code&'
                      'timezone=auto')
    data_meteo = requests.get(URI_SERV_METEO).json()
    print(json.dumps(data_meteo, indent=4))
    # Transformations
    # a. Ne conserver que les 24h précédant le sinistre pour l'analyse
    # b. Calculer le min/max de température, l'accumulation de pluie et
    # de neige + les inclure dans le document JSON
    # Créer listes pour les températures et précipitations horaires
    # temp = []
    # rain = []
    # snow = []
    #
    # temp_min = min(temp)
    # temp_max = max(temp)
    # rain_24h = sum(rain)
    # snow_24h = sum(snow)
    #
    #
    # # Zone de dégel
    # # Chargement du fichier geoJSON
    # URI_ZONE_DEGEL = ('https://ws.mapserver.transports.gouv.qc.ca/swtq?'
    #                   'service=wfs&'
    #                   'version=2.0.0&'
    #                   'request=getfeature&'
    #                   'typename=ms:zone_degel&'
    #                   'outfile=ZoneDegel&'
    #                   'srsname=EPSG:4326&'
    #                   'outputformat=geojson')
    # data_degel = requests.get(URI_ZONE_DEGEL)
    # print(json.dumps(data_degel, indent = 3))
    # # Détermination de la zone correspondant aux coordonnées renseignées
    # pass

    # Inclure la zone de dégel dans data_meteo

    return(data_meteo)


if __name__ == '__main__':
    app.run(debug=True)
