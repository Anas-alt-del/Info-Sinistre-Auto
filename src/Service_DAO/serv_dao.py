
from flask import Flask, jsonify, request, Response
import json, os
from modeles import Incident, Localisation, MeteoHourly, MeteoDaily

app = Flask(__name__)
DB_URI = 'incidents.json'

def initialiser_db():
    # si la db n'existe pas, la créer
    if not os.path.exists(DB_URI) or os.path.getsize(DB_URI) == 0:
        data = { "documents": [] }
        with open(DB_URI, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, indent=4)
    print("Base de données initialisée")

def valider_incident(jsondata):
    return True
    # à faire plus tard

def insert_incident(obj):
    # récupérer le data de la collection
    with open(DB_URI, 'r', encoding='utf-8') as fin:
        data = json.load(fin)

    # trouver le prochain id
    next_id = get_next_id(data)
    obj.id_incident = next_id

    # ajouter le nouveau document dans la collection
    data.get("documents").append(obj.to_dict())

    # commit le changement à la collection
    with open(DB_URI, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)

def get_next_id(data):
    # chercher dans le json pour le dernier id_incident et ajouter 1
    # s'il n'y a aucun document enregistré, retourner 0
    documents = data.get("documents", [])
    id_list = [doc.get("id_incident") for doc in documents if doc.get("id_incident") is not None]
    next_id = max(id_list) + 1 if id_list else 0
    return next_id

@app.route('/dao/incidents', methods=['POST'])
def creer_incidents():
    # récupérer le payload
    jsondata = request.get_json()

    # valider le payload. si le document n'est pas conforme, retourner code d'erreur 400
    if not valider_incident(jsondata):
        return jsonify({'error': 'Bad request'}), 400

    # créer le nouveau document
    incident = Incident(
        id_reclamation=jsondata.get('id_reclamation'),
        date=jsondata.get('date'),
        heure=jsondata.get('heure'),
        localisation=Localisation(
            latitude=jsondata.get('localisation').get('latitude'),
            longitude=jsondata.get('localisation').get('longitude')),
        meteo_hourly=MeteoHourly(
            temperature=jsondata.get('meteo_hourly').get('temperature'),
            rain=jsondata.get('meteo_hourly').get('rain'),
            snow=jsondata.get('meteo_hourly').get('snow'),
            cloud=jsondata.get('meteo_hourly').get('cloud'),
            wind_speed=jsondata.get('meteo_hourly').get('wind_speed'),
            wind_direction=jsondata.get('meteo_hourly').get('wind_direction'),
            weather_code=jsondata.get('meteo_hourly').get('weather_code'),
        ),
        meteo_daily=MeteoDaily(
            jsondata.get('meteo_daily').get('temperature_min_24h'),
            jsondata.get('meteo_daily').get('temperature_max_24h'),
            jsondata.get('meteo_daily').get('rain_24h'),
            jsondata.get('meteo_daily').get('snow_24h'),
            jsondata.get('meteo_daily').get('sunrise'),
            jsondata.get('meteo_daily').get('sunset')
        ),
        zone_degel=jsondata.get('zone_degel')
    )

    # insérer le nouveau document dans la db
    #       (le #id est auto-généré et assigné)
    insert_incident(incident)

    # retourner le nouveau document avec le code de succès 201
    return Response(
        json.dumps(incident, default=vars, indent=4),
        status=201,
        mimetype='application/json'
    )

if __name__ == '__main__':
    initialiser_db()
    app.run(debug=True, port=5601)