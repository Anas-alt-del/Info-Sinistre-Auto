import os

# URI dynamiques : utilise les variables d'environnement lorsqu'elles sont
# définies, sinon localhost et le port définis dans le service.
dao_service_root = os.getenv("SERV_DAO_URL", "http://127.0.0.1:5601")
collection_service_root = os.getenv("SERV_COLLECTE_URL", "http://127.0.0.1:5020")

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