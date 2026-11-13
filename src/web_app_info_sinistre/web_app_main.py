"""
Web App qui collecte les inputs (date, heure, localisation) et affiche
les données collectées par le service d'intégration à l'utilisateur
via un dashboard
"""
from routes import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
