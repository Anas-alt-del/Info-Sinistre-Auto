"""Paramètres de configuration de l'application Flask."""

import os

# URI dynamiques : utilise les variables d'environnement lorsqu'elles sont
# définies, sinon localhost et le port définis dans le service.
data_service_root = os.getenv("SERV_DATA_URL", "http://127.0.0.1:5010")
auth_service_root = os.getenv("SERV_AUTH_URL", "http://127.0.0.1:5602")


DATA_SERVICE_ENDPOINTS = {
    'find_incident': f'{data_service_root}/data',
    'create_incident': f'{data_service_root}/data',
    'add_claim': f'{data_service_root}/data/reclamation',
    'database_status': f'{data_service_root}/database/status',
    'database_connect': f'{data_service_root}/database/connect',
    'database_disconnect': f'{data_service_root}/database/disconnect'
}

AUTH_SERVICE_LOGIN_URL = f'{auth_service_root}/auth/login'

class Config(object):
    """
    Classe principale de configuration de l'application Flask.

    Flask utilise cette classe au démarrage de l'application. D'autres classes
    peuvent être créées pour configurer différents environnements.
    """

    # SECRET_KEY chiffre les données sensibles, comme les jetons de formulaire.
    # La clé est d'abord récupérée dans les variables d'environnement.
    # À défaut, une valeur par défaut est utilisée (à ne pas conserver en production).
    # En production, ne jamais coder de secret en dur.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Le renard saute la barriere'
