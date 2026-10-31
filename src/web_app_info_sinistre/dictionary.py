"""Traductions françaises et anglaises de l'interface Web."""

from flask import has_request_context, session


TRANSLATIONS = {
    "Info-Sinistre-Auto": "Auto Claim Information",
    "Langue": "Language",
    "Tableau de bord sinistres": "Claims dashboard",
    "Bienvenue! Gérez et recherchez facilement les données concernant les sinistres automobiles.": (
        "Welcome! Easily manage and search automobile claim data."
    ),
    "Connexion": "Sign in",
    "Obtenir un token": "Get a token",
    "Recherche": "Search",
    "Chercher un incident": "Find an incident",
    "Fonctionnalités": "Features",
    "Recherchez un incident existant par ID de réclamation ou par date/heure/localisation": (
        "Find an existing incident by claim ID or by date, time, and location"
    ),
    "Créez un nouvel incident si celui-ci n'existe pas dans la base de données": (
        "Create a new incident if it does not exist in the database"
    ),
    "Ajoutez des IDs de réclamation à un incident existant": (
        "Add claim IDs to an existing incident"
    ),
    "Consultez les données météorologiques associées à chaque incident": (
        "View weather data associated with each incident"
    ),
    "Authentification sécurisée avec token": "Secure token-based authentication",
    "Développeurs": "Developers",
    "API Docs - Info-Sinistre-Auto": "API Docs - Info-Sinistre-Auto",
    "API Docs - Authentification (Info-Sinistre-Auto)": (
        "API Docs - Authentication (Info-Sinistre-Auto)"
    ),
    "Connexion à la base de données": "Database connection",
    "URI de connexion MongoDB (facultative)": "MongoDB connection URI (optional)",
    "Veuillez saisir une URI MongoDB.": "Please enter a MongoDB URI.",
    "Saisissez une URI MongoDB pour utiliser MongoDB. Laissez vide pour utiliser le fichier JSON local.": (
        "Enter a MongoDB URI to use MongoDB. Leave blank to use the local JSON file."
    ),
    "Se connecter à MongoDB": "Connect to MongoDB",
    "Se déconnecter": "Disconnect",
    "MongoDB connecté": "MongoDB connected",
    "Base JSON locale active": "Local JSON database active",
    "État de la base de données indisponible": "Database status unavailable",
    "Français": "French",
    "Anglais": "English",
    "Entrez vos identifiants pour accéder à l'application": (
        "Enter your credentials to access the application"
    ),
    "Nom d'utilisateur": "Username",
    "Entrez votre nom d'utilisateur": "Enter your username",
    "Mot de passe": "Password",
    "Entrez votre mot de passe": "Enter your password",
    "Se connecter": "Sign in",
    "Retour à l'accueil": "Back to home",
    "Saisie des informations du sinistre": "Enter claim information",
    "Identifiant de réclamation": "Claim ID",
    "Date": "Date",
    "Heure": "Time",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Sauvegarder": "Submit",
    "L'incident n'a pas été trouvé dans la base de données.": (
        "The incident was not found in the database."
    ),
    "Souhaitez-vous collecter les informations relatives à cet incident?": (
        "Would you like to collect information about this incident?"
    ),
    "L'incident correspondant a été trouvé mais il ne contient pas l'indentifiant de réclamation renseigné.": (
        "The matching incident was found, but it does not contain the specified claim ID."
    ),
    "Souhaitez-vous ajouter cet identifiant dans la fiche incident?": (
        "Would you like to add this ID to the incident record?"
    ),
    "Numéro d'incident": "Incident number",
    "Ajouter": "Add",
    "Ne pas ajouter": "Do not add",
    "Oui": "Yes",
    "Non": "No",
    "Résultats de la recherche - Analyse d'incident": (
        "Search results - Incident analysis"
    ),
    "Tableau de Bord": "Dashboard",
    "Informations du Dossier": "Claim Information",
    "ID Incident:": "Incident ID:",
    "Date:": "Date:",
    "Heure:": "Time:",
    "Latitude:": "Latitude:",
    "Longitude:": "Longitude:",
    "Réclamations:": "Claims:",
    "Conditions Actuelles (Horaire)": "Current Conditions (Hourly)",
    "Température:": "Temperature:",
    "Code WMO:": "WMO Code:",
    "Couverture Nuageuse:": "Cloud Cover:",
    "Vitesse du Vent:": "Wind Speed:",
    "Direction du Vent:": "Wind Direction:",
    "Pluie:": "Rain:",
    "Neige:": "Snow:",
    "Données Quotidiennes (24h)": "Daily Data (24h)",
    "Temp. Maximale:": "Maximum Temperature:",
    "Temp. Minimale:": "Minimum Temperature:",
    "Pluie (24h):": "Rain (24h):",
    "Neige (24h):": "Snow (24h):",
    "Lever du Soleil:": "Sunrise:",
    "Coucher du Soleil:": "Sunset:",
    "Zone Dégel:": "Thaw Zone:",
    "Période Dégel:": "Thaw Period:",
    "Localisation": "Location",
    "Veuillez d'abord vous connecter.": "Please sign in first.",
    "Nom d'utilisateur et mot de passe requis.": "Username and password are required.",
    "Bienvenue {username}!": "Welcome {username}!",
    "Identifiants invalides.": "Invalid credentials.",
    "Erreur de connexion au service d'authentification: {error}": (
        "Could not connect to the authentication service: {error}"
    ),
    "Vous devez fournir soit un ID de réclamation, soit (date + heure + coordonnées).": (
        "Provide either a claim ID or (date + time + coordinates)."
    ),
    "Erreur serveur (code {status}).": "Server error (code {status}).",
    "Erreur de connexion à serv_data: {error}": (
        "Could not connect to serv_data: {error}"
    ),
    "Aucune donnée à afficher. Veuillez rechercher à nouveau.": (
        "No data to display. Please search again."
    ),
    "Données manquantes. Veuillez rechercher à nouveau.": (
        "Missing data. Please search again."
    ),
    "ID réclamation ajouté avec succès.": "Claim ID added successfully.",
    "Erreur lors de l'ajout (code {status}).": "Error adding claim ID (code {status}).",
    "Erreur de connexion: {error}": "Connection error: {error}",
    "Incident créé et données collectées.": "Incident created and data collected.",
    "Erreur lors de la création (code {status}).": (
        "Error creating incident (code {status})."
    ),
    "Valeurs manquantes dans le formulaire de recherche.": (
        "Missing values in the search form."
    ),
    "Opération annulée.": "Operation cancelled.",
    "Connexion MongoDB réussie.": "MongoDB connection successful.",
    "Déconnexion MongoDB réussie. Le fichier JSON local est utilisé.": (
        "MongoDB disconnected successfully. The local JSON file is now in use."
    ),
    "Connexion MongoDB impossible. Vérifiez l'URI et la disponibilité du serveur.": (
        "Could not connect to MongoDB. Check the URI and server availability."
    ),
    "Le service DAO est indisponible.": "The DAO service is unavailable.",
}


def get_active_language():
    """Retourne la langue choisie, le français par défaut."""
    if has_request_context() and session.get("langue") in ("fr", "en"):
        return session["langue"]
    return "fr"


def translate_text(text):
    """Traduit une chaîne française lorsque l'anglais est sélectionné."""
    if get_active_language() == "en":
        return TRANSLATIONS.get(text, text)
    return text
