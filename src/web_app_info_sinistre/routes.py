"""Routage des URL et traitement des requêtes de l'application Flask."""
import json
import os
from threading import Lock
from time import monotonic

from flask import Flask, render_template, flash, redirect, session, request
# Flask est le framework principal.
# render_template transforme les modèles HTML en pages Web.
# flash affiche des messages temporaires à l'utilisateur.
# redirect redirige l'utilisateur après une action, comme l'envoi d'un formulaire.
from flask_cors import CORS

from datetime import datetime, timedelta
from functools import wraps

import requests
# Bibliothèque pour les requêtes HTTP.
from urllib.parse import urlsplit

from config import (
    AUTH_SERVICE_LOGIN_URL,
    DATA_SERVICE_ENDPOINTS,
    Config,
    auth_service_root,
    data_service_root,
)
from forms import ClaimAdditionForm, DataCollectionForm, IncidentSearchForm
from util import has_valid_search_inputs, build_search_payload
from dictionary import get_active_language, translate_text

# Crée l'application Flask.
app = Flask(__name__)

# Charge SECRET_KEY et les autres paramètres de configuration.
app.config.from_object(Config)

CORS(app)

KEEP_ALIVE_WORKFLOW_URL = (
    'https://api.github.com/repos/Anas-alt-del/Info-Sinistre-Auto/'
    'actions/workflows/keep-alive.yml/dispatches'
)
KEEP_ALIVE_DISPATCH_INTERVAL_SECONDS = 5 * 60
_keep_alive_dispatch_lock = Lock()
_last_keep_alive_dispatch = None


@app.context_processor
def inject_translations():
    """Rend la langue active et la fonction de traduction accessibles aux modèles."""
    return {"_": translate_text, "active_language": get_active_language()}


# Décorateur qui vérifie que l'utilisateur possède un jeton valide.
def token_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'auth_token' not in session:
            flash(translate_text("Veuillez d'abord vous connecter."), 'warning')
            return redirect('/login')
        return view_function(*args, **kwargs)

    return decorated_function


def trigger_keep_alive_workflow():
    """Déclenche le workflow au plus une fois toutes les cinq minutes."""
    global _last_keep_alive_dispatch

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        # La page reste accessible même si aucun jeton GitHub n'est configuré.
        app.logger.warning("GITHUB_TOKEN is not configured; keep-alive dispatch skipped.")
        return

    # Le verrou empêche deux requêtes simultanées de lancer deux workflows.
    with _keep_alive_dispatch_lock:
        # L'horloge monotone n'est pas affectée par les changements d'heure système.
        now = monotonic()
        if (
            _last_keep_alive_dispatch is not None
            and now - _last_keep_alive_dispatch < KEEP_ALIVE_DISPATCH_INTERVAL_SECONDS
        ):
            # Les visites pendant la fenêtre de cinq minutes ne relancent pas le workflow.
            return

        # Le délai commence à la tentative, même si l'appel à GitHub échoue.
        _last_keep_alive_dispatch = now
        try:
            response = requests.post(
                KEEP_ALIVE_WORKFLOW_URL,
                headers={
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {token}',
                    'X-GitHub-Api-Version': '2022-11-28',
                },
                json={'ref': 'main'},
                timeout=5,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            # L'erreur est journalisée sans bloquer l'affichage de la page d'accueil.
            app.logger.exception("Unable to dispatch the keep-alive workflow.")


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    """Route d'accueil - affiche les options de login ou recherche"""
    flash(translate_text(
        "Si certaines fonctionnalités ne sont pas disponibles, veuillez réessayer dans une minute : "
        "les services Web sont en cours de démarrage."
    ), 'info')
    trigger_keep_alive_workflow()
    try:
        response = requests.get(DATA_SERVICE_ENDPOINTS['database_status'], timeout=8)
        database_status = response.json() if response.ok else None
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de récupérer le statut de la base.")
        database_status = None
    return render_template('index.html', api_docs_url=data_service_root,
                           api_auth_docs_url=auth_service_root,
                           database_status=database_status)


@app.route('/language/<language_code>', methods=['GET'])
def change_language(language_code):
    """Mémorise la langue et revient à la page d'où vient l'utilisateur."""
    if language_code not in ('fr', 'en'):
        return redirect('/')
    session['langue'] = language_code
    referrer = request.referrer
    if referrer:
        parsed = urlsplit(referrer)
        if parsed.netloc == request.host and parsed.path.startswith('/') and not parsed.path.startswith('//'):
            return redirect(parsed.path + (f'?{parsed.query}' if parsed.query else ''))
    return redirect('/')


@app.route('/database/connect', methods=['POST'])
def connect_database():
    """Transmet l'URI au service de données sans la conserver côté Web."""
    uri = request.form.get('connection_string', '')
    if not uri.strip():
        flash(translate_text("Veuillez saisir une URI MongoDB."), 'warning')
        return redirect('/')

    try:
        response = requests.post(
            DATA_SERVICE_ENDPOINTS['database_connect'],
            json={'connection_string': uri},
            timeout=10
        )
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de joindre le service de données pour MongoDB.")
        flash(translate_text("Le service DAO est indisponible."), 'danger')
        return redirect('/')

    if response.ok:
        flash(translate_text("Connexion MongoDB réussie."), 'success')
    else:
        flash(translate_text(
            "Connexion MongoDB impossible. Vérifiez l'URI et la disponibilité du serveur."
        ), 'danger')
    return redirect('/')


@app.route('/database/disconnect', methods=['POST'])
def disconnect_database():
    """Demande au service de données de rétablir le stockage JSON local."""
    try:
        response = requests.post(
            DATA_SERVICE_ENDPOINTS['database_disconnect'], timeout=10
        )
    except requests.exceptions.RequestException:
        app.logger.exception("Impossible de joindre le service de données pour la déconnexion.")
        flash(translate_text("Le service DAO est indisponible."), 'danger')
        return redirect('/')

    if response.ok:
        flash(translate_text(
            "Déconnexion MongoDB réussie. Le fichier JSON local est utilisé."
        ), 'success')
    else:
        flash(translate_text("Le service DAO est indisponible."), 'danger')
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion - envoie les identifiants au service d'auth"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validation basique
        if not username or not password:
            flash(translate_text("Nom d'utilisateur et mot de passe requis."), 'danger')
            return redirect('/login')

        try:
            # Envoi des identifiants au service d'authentification
            auth_payload = {
                'username': username,
                'password': password
            }
            auth_response = requests.post(AUTH_SERVICE_LOGIN_URL, json=auth_payload)

            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                token = auth_data.get('token')

                if token:
                    # Stockage du token en session
                    session['auth_token'] = token
                    session['username'] = username
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(hours=24)

                    flash(translate_text("Bienvenue {username}!").format(username=username), 'success')
                    return redirect('/infos_sinistre')
                else:
                    flash(translate_text("Identifiants invalides."), 'danger')

        except requests.exceptions.RequestException as error:
            flash(translate_text(
                "Erreur de connexion au service d'authentification: {error}"
            ).format(error=str(error)), 'danger')

        return redirect('/login')

    return render_template('login.html')


@app.route('/infos_sinistre', methods=['GET', 'POST'])
@token_required
def incident_search_form():
    """Route de recherche d'incident - affiche le formulaire de recherche"""
    search_form = IncidentSearchForm()
    if search_form.validate_on_submit():
        # Valide les données selon les règles métier.
        if not has_valid_search_inputs(search_form):
            flash(translate_text(
                "Vous devez fournir soit un ID de réclamation, soit (date + heure + coordonnées)."
            ), 'danger')
            return render_template('form_infos_input.html', form=search_form)

        # Prépare les données de recherche.
        payload = build_search_payload(search_form)

        # Stocke temporairement les données de recherche dans la session.
        session['search_payload'] = payload

        try:
            # Envoie la requête GET au service de données avec le jeton.
            headers = {'Authorization': f'Bearer {session.get("auth_token")}'}
            response = requests.get(
                DATA_SERVICE_ENDPOINTS['find_incident'],
                json=payload,
                headers=headers
            )

            # Traite le code de réponse.
            if response.status_code == 200 or (response.status_code == 210 and payload['id_reclamation'] is None):
                # Incident trouvé et complet
                result = response.json()
                # Stockage temporaire du résultat de la recherche en session
                session['incident_data'] = result
                return redirect('/afficher_resultat')

            elif response.status_code == 210:
                # Incident trouvé mais ID réclamation manquant
                result = response.json()
                session['incident_data'] = result
                return redirect('/ajouter_reclamation')

            elif response.status_code == 404:
                # Incident non trouvé - proposer la création
                return redirect('/collecter_donnees')

            else:
                flash(translate_text("Erreur serveur (code {status}).").format(
                    status=response.status_code
                ), 'danger')

        except requests.exceptions.RequestException as e:
            flash(translate_text("Erreur de connexion à serv_data: {error}").format(
                error=str(e)
            ), 'danger')

    return render_template('form_infos_input.html', form=search_form)


@app.route('/afficher_resultat', methods=['GET'])
@token_required
def display_results():
    """Route pour afficher les résultats d'une recherche/création"""
    incident_data = session.get('incident_data')

    if not incident_data:
        flash(translate_text(
            'Aucune donnée à afficher. Veuillez rechercher à nouveau.'
        ), 'warning')
        return redirect('/infos_sinistre')

    return render_template('infos_output.html', data=incident_data)


@app.route('/ajouter_reclamation', methods=['GET', 'POST'])
@token_required
def add_claim():
    """Route pour ajouter un ID réclamation à un incident existant"""
    incident_data = session.get('incident_data')
    search_payload = session.get('search_payload')

    if not incident_data or not search_payload:
        flash(translate_text('Données manquantes. Veuillez rechercher à nouveau.'), 'warning')
        return redirect('/infos_sinistre')

    form = ClaimAdditionForm()

    if form.validate_on_submit():
        selected_option = form.options.data

        # Ajoute l'identifiant de réclamation à l'incident si
        # l'utilisateur choisit cette option.
        if selected_option == 'Ajouter':
            try:
                # Prépare les données et l'en-tête de la requête PATCH.
                patch_payload = {
                    **search_payload,
                    'id_incident': incident_data.get('id_incident')
                }
                headers = {'Authorization': f'Bearer {session.get("auth_token")}'}

                # Envoi de la requête PATCH
                patch_response = requests.patch(
                    DATA_SERVICE_ENDPOINTS['add_claim'],
                    json=patch_payload,
                    headers=headers
                )

                # Gestion des codes de réponse
                if patch_response.status_code == 200:
                    flash(translate_text('ID réclamation ajouté avec succès.'), 'success')
                    session['incident_data'] = patch_response.json()
                else:
                    flash(translate_text("Erreur lors de l'ajout (code {status}).").format(
                        status=patch_response.status_code
                    ), 'danger')

            except requests.exceptions.RequestException as e:
                flash(translate_text('Erreur de connexion: {error}').format(error=str(e)), 'danger')

        # Affiche le résultat dans tous les cas.
        return redirect('/afficher_resultat')

    return render_template('form_ajout_reclamation.html',
                           form=form,
                           id_reclamation=search_payload["id_reclamation"],
                           id_incident = incident_data.get('id_incident'))


@app.route('/collecter_donnees', methods=['GET', 'POST'])
@token_required
def collect_data():
    """Route pour collecter les données d'un nouvel incident"""
    search_payload = session.get('search_payload')
    if not search_payload:
        flash(translate_text('Données manquantes. Veuillez rechercher à nouveau.'), 'warning')
        return redirect('/infos_sinistre')

    form = DataCollectionForm()

    if form.validate_on_submit():
        selected_option = form.options.data

        if selected_option == 'Oui' and None not in search_payload.values():
            try:
                # Envoi de la requête POST pour créer l'incident
                headers = {'Authorization': f'Bearer {session.get("auth_token")}'}
                post_response = requests.post(
                    DATA_SERVICE_ENDPOINTS['create_incident'],
                    json=search_payload,
                    headers=headers
                )

                if post_response.status_code == 201:
                    result = post_response.json()
                    session['incident_data'] = result
                    flash(translate_text('Incident créé et données collectées.'), 'success')
                    return redirect('/afficher_resultat')
                else:
                    flash(translate_text("Erreur lors de la création (code {status}).").format(
                        status=post_response.status_code
                    ), 'danger')

            except requests.exceptions.RequestException as e:
                flash(translate_text('Erreur de connexion: {error}').format(error=str(e)), 'danger')

        elif None in search_payload.values():
            # Valeurs manquantes dans le formulaire de recherche
            flash(translate_text('Valeurs manquantes dans le formulaire de recherche.'), 'info')
            return redirect('/infos_sinistre')
        else:
            # L'utilisateur a choisi "Non"
            flash(translate_text('Opération annulée.'), 'info')
            return redirect('/infos_sinistre')

    return render_template('form_collecte_donnees.html', form=form)

# Route utilisée pour maintenir les services déployés actifs (arrêt
# automatique par défaut).
@app.route('/health', methods=['GET'])
def health():
    return 'ok', 200
