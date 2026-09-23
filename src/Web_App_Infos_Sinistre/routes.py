"""
URL routing and request handling for the Flask application.

Routes are URLs that users can visit (like /index or /form_projet_input).
Each route has a function that decides what to display when someone visits that URL.

Routes are like "addresses" for your web application!
"""

from flask import Flask, render_template, flash, redirect
# Flask: The main framework
# render_template: Converts HTML template files into complete web pages
# flash: Displays temporary messages to users (like "Success!" or "Error!")
# redirect: Sends users to a different URL after an action (like after form submission)

import requests
# HTTP framework

# from forms import ProjetForm  # Import the project form we defined
from config import Config  # Import configuration settings
from forms import InfosInputForm

# Create the Flask application object
# This object represents your entire web application
app = Flask(__name__)

# Tell Flask to use our Config class for settings
# This loads SECRET_KEY and other configuration values
app.config.from_object(Config)

URI_SERV_DATA = {
    'chercher_incident': 'http://127.0.0.1:5010/data',
    'creer_incident': 'http://127.0.0.1:5010/data',
    'ajouter_reclamation': 'hhttp://127.0.0.1:5010/data/reclamation'
}


@app.route('/infos_sinistre', methods=['GET'])
def form_info_sinistre():
    inputForm = InfosInputForm()
    if inputForm.validate_on_submit():
        # A faire: validation des inputs
        # 1. si id_reclamation est égal à None alors on doit avoir la date, l'heure et les coordonnées
        # 2. si la date, l'heure et les coordonnées sont égales à None alors on doit avoir id_reclamation

        inputs = {
            "id_reclamation": inputForm.id_reclamation.data,
            "date": inputForm.date.data,
            "heure": inputForm.heure.data,
            "lat": inputForm.lat.data,
            "long": inputForm.long.data
        }

        # envoi de la requête GET à serv_data
        resultat, code = requests.get(URI_SERV_DATA['chercher_incident'])

        # Si code 200 : retourner l'incident
        if code == 200:
            return render_template('infos_output.html', data=resultat)

        # Si code 210 : proposer à l'utilisateur d'ajouter le id_reclamation à l'incident trouvé (PATCH)
        if code == 210:
            form_ajout_reclamation = FormAjoutReclamation()
            return render_template('ajout_reclamation.html', form = form_ajout_reclamation, data=resultat)
            if form_ajout_reclamation.validate_on_submit():
            # si oui: requete PATCH à serv_data
            # si non: afficher l'incident
                return render_template('infos_output.html', data=resultat)
                pass

        # Si code 404 : proposer à l'utilisateur de collecter les données (POST)
        if code == 404:
            form_collecte_donnees = FormCollecteDonnees()
            return render_template('collecte_données.html', form= form_collecte_donnees)
            if form_collecte_donnees.validate_on_submit():
                # si oui: requete POST à serv_data
                # si non: re-charger la route
                return redirect('/infos_sinistre')
                pass

    return render_template('form_infos_input.html',
                           form=inputForm)
