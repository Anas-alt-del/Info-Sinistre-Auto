'''
Ce service reçoit les données entrantes (lat + long +
date + heure) depuis Service_Data, collecte les données météo depuis leur source,
les traite et les renvoie à Service_Data au format JSON
'''

import json

from shapely.geometry import shape, Point

from datetime import datetime, timedelta
from operator import concat

from flask import Flask, request
import requests

app = Flask(__name__)


@app.route('/CollecteData', methods=['GET'])
def collecte_data():
    input = request.get_json()
    print(input)  # imprimer payload
    lat = input["lat"]
    long = input["long"]
    date_heure = f'{input["date"]}T{input["heure"]}'  # Format utilisé par l'API
    # conversion de la date au format datetime.date afin de pouvoir
    # effectuer une opération sur la date (soustraire 1 jour)
    date = datetime.strptime(date_heure, "%Y-%m-%dT%H:%M").date()

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
    # Arrondir date_heure au début de l'heure (remplacer les 2
    # derniers caractères par 00)
    date_heure_arr = concat(date_heure[:-2], '00')
    heures = data_meteo["hourly"]["time"]
    index_heure = heures.index(date_heure_arr)

    # Données des 24h pertinentes
    temp = data_meteo["hourly"]["temperature_2m"][(index_heure - 23):(index_heure + 1)]
    pluie = data_meteo["hourly"]["rain"][(index_heure - 23):(index_heure + 1)]
    neige = data_meteo["hourly"]["snowfall"][(index_heure - 23):(index_heure + 1)]

    # b. Calculer le min/max de température, l'accumulation de pluie et de neige
    temp_min = min(temp)
    temp_max = max(temp)
    pluie_24h = sum(pluie)
    neige_24h = sum(neige)
    print(temp_min, temp_max, pluie_24h, neige_24h)

    # Zone de dégel
    # Chargement du fichier geoJSON
    URI_ZONE_DEGEL = ('https://ws.mapserver.transports.gouv.qc.ca/swtq?'
                      'service=wfs&'
                      'version=2.0.0&'
                      'request=getfeature&'
                      'typename=ms:zone_degel&'
                      'outfile=ZoneDegel&'
                      'srsname=EPSG:4326&'
                      'outputformat=geojson')
    data_degel = requests.get(URI_ZONE_DEGEL).json()

    point = Point(long, lat)

    # On teste chaque poygone contenu dans le fichier geoJSON pour
    # déterminer si il contient les coordonnées renseignées, tant qu'on
    # n'a pas trouvé le bon
    trouve = 0
    while trouve == 0:
        for feature in data_degel['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                zone_degel = feature['properties']['zone']
                periode_degel = f'{feature['properties']['dat_debut_zone']} - {feature['properties']['dat_fin_zone']}'
                trouve = 1


    info_meteo = {
        'temperature': data_meteo["hourly"]["temperature_2m"][index_heure],
        'pluie': data_meteo["hourly"]["rain"][index_heure],
        'neige': data_meteo["hourly"]["snowfall"][index_heure],
        'couverture_nuageuse': data_meteo["hourly"]["cloud_cover"][index_heure],
        'vitesse_vent': data_meteo["hourly"]["wind_speed_10m"][index_heure],
        'direction_vent': data_meteo["hourly"]["wind_direction_10m"][index_heure],
        'code_WMO': data_meteo["hourly"]["weather_code"][index_heure],
        'temperature_min': temp_min,
        'temperature_max': temp_max,
        'pluie_24h': pluie_24h,
        'neige_24h': neige_24h,
        'zone_degel': zone_degel,
        'periode_degel': periode_degel
    }

    return (info_meteo)


if __name__ == '__main__':
    app.run(debug=True)
