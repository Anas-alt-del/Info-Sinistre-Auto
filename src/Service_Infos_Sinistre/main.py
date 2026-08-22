import json

from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

@app.route('/InfosSinistreAuto', methods=['POST'])
def get_infos():

    input = request.get_json()
    print(input) # imprimer payload
    URI_SERV_INTEGRATION = 'fakeURI'
    # Appel à l'API d'intégration
    #reponse = requests.post(URI_SERV_INTEGRATION, json = input)

    # Fausses données pour tester
    with open('Données_json_projet.json') as donnees_json:
        reponse = json.load(donnees_json)
        print(reponse)

    return jsonify(reponse)
if __name__ == '__main__':
    app.run(debug=True)