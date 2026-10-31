import os

# URI dynamiques : si l'URI n'existe pas dans les variables d'environnement
# (définies manuellement dans l'environnement virtuel de Render) alors
# utiliser localhost et port définis dans le service
dao_service_root = os.getenv("SERV_DAO_RENDER", "http://127.0.0.1:5601")
collection_service_root = os.getenv("SERV_COLLECTE_RENDER", "http://127.0.0.1:5020")

DAO_SERVICE_ENDPOINTS = {
    'find_incident': f'{dao_service_root}/dao/incidents',
    'create_incident': f'{dao_service_root}/dao/incidents',
    'add_claim': f'{dao_service_root}/dao/incidents/''{}''/reclamation',
    'update_incident': f'{dao_service_root}/dao/incidents',
    'database_status': f'{dao_service_root}/dao/database/status',
    'database_connect': f'{dao_service_root}/dao/database/connect',
    'database_disconnect': f'{dao_service_root}/dao/database/disconnect'
}
DATA_COLLECTION_URL = f'{collection_service_root}/collecte_data'