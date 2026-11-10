"""
Web App qui collecte les inputs (date, heure, localisation) et affiche
les données collectées par le service d'intégration à l'utilisateur
via un dashboard
"""
from routes import app
import os

from apscheduler.schedulers.background import BackgroundScheduler
import requests

if __name__ == '__main__':
    # En déploiement cloud, appeler les services périodiquement pour éviter
    # qu'ils ne se désactivent.
    if os.getenv("SERV_DATA_URL"):

        def keep_warm():
            for uri in ["SERV_AUTH_URL",
                        "SERV_COLLECTE_URL",
                        "SERV_DAO_URL",
                        "SERV_DATA_URL"]:
                try:
                    # Récupère l'adresse depuis la variable d'environnement correspondante.
                    requests.get(f"{os.getenv(uri)}/health", timeout=30)
                except:
                    pass

        keep_warm()
        scheduler = BackgroundScheduler()
        scheduler.add_job(keep_warm, 'interval', minutes=5)
        scheduler.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
