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

@app.route('/Data', methods=['GET'])
def get_data():

    # Appel à Service_DAO pour vérifier si un document correspondant
    # aux données utilisateur existe déjà (GET)
    input = request.get_json()
    URI_SERV_DAO = ''
    # Appel à Service_Collecte si Service_DAO ne trouve pas un document
    # correspondant
    URI_SERV_COLLECTE = ''

    # Consolidation des données utilisateur et des informations
    # collectées dans un document JSON
    info_sinistre = {}
    
    # Envoi du document à Service_DAO afin de l'insérer dans la
    # collection (POST)

    # Réponse à la requête entrante avec le document JSON

    return(info_sinistre)

if __name__ == '__main__':
    app.run(debug=True, port=5010)
