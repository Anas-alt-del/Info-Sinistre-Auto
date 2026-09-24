"""
URL routing and request handling for the Flask application.

Routes are URLs that users can visit (like /index or /form_projet_input).
Each route has a function that decides what to display when someone visits that URL.

Routes are like "addresses" for your web application!
"""
import json

from flask import Flask, render_template, flash, redirect
# Flask: The main framework
# render_template: Converts HTML template files into complete web pages
# flash: Displays temporary messages to users (like "Success!" or "Error!")
# redirect: Sends users to a different URL after an action (like after form submission)

import requests
# HTTP framework

# from forms import ProjetForm  # Import the project form we defined
from config import Config  # Import configuration settings
from forms import InfosInputForm,FormAjoutReclamation,FormCollecteDonnees

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


@app.route('/infos_sinistre', methods=['GET','POST'])
def form_info_sinistre():
    inputForm = InfosInputForm()
    if inputForm.validate_on_submit():
        # A faire: validation des inputs
        # 1. si id_reclamation est égal à None alors on doit avoir la date, l'heure et les coordonnées
        # 2. si la date, l'heure et les coordonnées sont égales à None alors on doit avoir id_reclamation

        if inputForm.date.data:
            date = inputForm.date.data.strftime("%Y-%m-%d")
        else:
            date =  None

        if inputForm.heure.data:
            heure = inputForm.heure.data.strftime("%H:%M")
        else:
            heure =  None

        payload = {
            "id_reclamation": inputForm.id_reclamation.data,
            "date": date,
            "heure": heure,
            "latitude": inputForm.lat.data,
            "longitude": inputForm.long.data
        }
        print(payload)
        # envoi de la requête GET à serv_data
        response= requests.get(URI_SERV_DATA['chercher_incident'], json = payload)
        resultat = response.json()
        print(resultat)
        code= response.status_code
        print(code)
        # Si code 200 : retourner l'incident
        if code == 200:
            return render_template('infos_output.html', data=resultat), code

        # Si code 210 : proposer à l'utilisateur d'ajouter le id_reclamation à l'incident trouvé (PATCH)
        if code == 210:
            form_ajout_reclamation = FormAjoutReclamation()
            # Afficher le formulaire proposant d'ajouter le id_réclamation à l'incident

            if form_ajout_reclamation.validate_on_submit():
                # option sélectionnée dans le formulaire
                option = form_ajout_reclamation.options.data
                if option == 'Ajouter':
                    # si oui: requete PATCH à serv_data
                    payload.update({"id_incident": resultat["id_incident"]})
                    requests.patch(URI_SERV_DATA['ajouter_reclamation'], json=payload)
                # Dans tous les cas: afficher l'incident à la fin
                return render_template('infos_output.html', data=resultat)
            else:
                # Afficher le formulaire si pas encore soumis
                return render_template('form_ajout_reclamation.html', form=form_ajout_reclamation), code



        # # Si code 404 : proposer à l'utilisateur de collecter les données (POST)
        # if code == 404:
        #     form_collecte_donnees = FormCollecteDonnees()
        #     return render_template('collecte_données.html', form= form_collecte_donnees)
        #     if form_collecte_donnees.validate_on_submit():
        #         # si oui: requete POST à serv_data
        #         # si non: re-charger la route
        #         return redirect('/infos_sinistre')
        #         pass

    return render_template('form_infos_input.html',
                    form=inputForm)
