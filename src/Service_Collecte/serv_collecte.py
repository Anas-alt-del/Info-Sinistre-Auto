'''
Ce service reçoit les données entrantes (lat + long +
date + heure) depuis Service_Data, collecte les données météo depuis leur source,
les traite et les renvoie à Service_Data au format JSON
'''

import os
from shapely.geometry import shape, Point

from datetime import datetime, timedelta
from operator import concat

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)

CORS(app)


@app.route('/collecte_data', methods=['GET'])
def collect_data():
    request_payload = request.get_json()
    print(request_payload)  # Affiche les données reçues.
    latitude = request_payload["latitude"]
    longitude = request_payload["longitude"]
    incident_datetime = f'{request_payload["date"]}T{request_payload["heure"]}'  # Format attendu par l'API.
    # Convertit la date en datetime.date afin de pouvoir effectuer
    # une opération sur la date (soustraire un jour).
    incident_date = datetime.strptime(incident_datetime, "%Y-%m-%dT%H:%M").date()

    # Appel à l'API Open-Meteo.
    WEATHER_SERVICE_URL = (f'https://archive-api.open-meteo.com/v1/archive?'
                      f'latitude={latitude}&'
                      f'longitude={longitude}&'
                      f'start_date={incident_date - timedelta(days=1)}&'
                      f'end_date={incident_date}&'
                      'daily=sunrise,sunset&'
                      'hourly=temperature_2m,rain,snowfall,cloud_cover,'
                      'wind_speed_10m,wind_direction_10m,weather_code&'
                      'timezone=auto')

    weather_data = requests.get(WEATHER_SERVICE_URL).json()

    # Transformations des données.
    # a. Ne conserver que les 24 heures précédant le sinistre pour l'analyse.
    # Arrondit l'heure de l'incident au début de l'heure (remplace les deux
    # derniers caractères par 00).
    rounded_incident_datetime = concat(incident_datetime[:-2], '00')
    available_hours = weather_data["hourly"]["time"]  # liste des heures correspondant aux points de données
    hour_index = available_hours.index(rounded_incident_datetime)

    # Données des 24h pertinentes
    temperatures = weather_data["hourly"]["temperature_2m"][(hour_index - 23):(hour_index + 1)]
    rainfall = weather_data["hourly"]["rain"][(hour_index - 23):(hour_index + 1)]
    snowfall = weather_data["hourly"]["snowfall"][(hour_index - 23):(hour_index + 1)]

    # b. Calculer le min/max de température, l'accumulation de pluie et de neige
    minimum_temperature = min(temperatures)
    maximum_temperature = max(temperatures)
    rainfall_24h = sum(rainfall)
    snowfall_24h = sum(snowfall)

    # Zone de dégel.
    # Charge le fichier GeoJSON.
    THAW_ZONE_SERVICE_URL = ('https://ws.mapserver.transports.gouv.qc.ca/swtq?'
                      'service=wfs&'
                      'version=2.0.0&'
                      'request=getfeature&'
                      'typename=ms:zone_degel&'
                      'outfile=ZoneDegel&'
                      'srsname=EPSG:4326&'
                      'outputformat=geojson')
    thaw_zone_data = requests.get(THAW_ZONE_SERVICE_URL).json()

    # Création d'un objet Point contenant les coordonnées de l'incident
    point = Point(longitude, latitude)

    # Teste chaque polygone du fichier GeoJSON pour déterminer s'il
    # contient les coordonnées renseignées, jusqu'à trouver le bon.
    found_zone = False
    for feature in thaw_zone_data['features']:
        if not found_zone:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                thaw_zone = feature['properties']['zone']
                thaw_period = f'{feature['properties']['dat_debut_zone']} - {feature['properties']['dat_fin_zone']}'
                found_zone = True

    # Si aucun polygone ne contient les coordonnées, celles-ci sont hors Québec.
    if not found_zone:
        thaw_zone = thaw_period = 'N/A'

    # Document JSON retourné par le service
    weather_info = {
        'horaire': {
            'temperature_C': weather_data["hourly"]["temperature_2m"][hour_index],
            'pluie_mm': weather_data["hourly"]["rain"][hour_index],
            'neige_cm': weather_data["hourly"]["snowfall"][hour_index],
            'couverture_nuageuse_pct': weather_data["hourly"]["cloud_cover"][hour_index],
            'vitesse_vent_kmh': weather_data["hourly"]["wind_speed_10m"][hour_index],
            'direction_vent_deg': weather_data["hourly"]["wind_direction_10m"][hour_index],
            'code_WMO': weather_data["hourly"]["weather_code"][hour_index]
        },
        'journalier': {
            'temperature_min_C': minimum_temperature,
            'temperature_max_C': maximum_temperature,
            'pluie_24h_mm': rainfall_24h,
            'neige_24h_cm': snowfall_24h,
            'lever_soleil': weather_data["daily"]["sunrise"][-1],
            'coucher_soleil': weather_data["daily"]["sunset"][-1],
            'zone_degel': thaw_zone,
            'periode_degel': thaw_period
        }
    }
    return weather_info

# Route utilisée pour maintenir les services déployés actifs (arrêt
# automatique par défaut).
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5020))
    app.run(debug=True, port=port, host='0.0.0.0')
