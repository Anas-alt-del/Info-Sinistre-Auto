"""
Web App qui collecte les inputs (date, localisation) et sert les données
 collectée par le service d'intégration à l'utilisateur via un dashboard
"""
#Main entry point for the Flask application.
from routes import app
import os

if __name__ == '__main__':
    # This condition ensures the app only runs when this file is executed directly,
    # not when it's imported as a module in another file
    port = int(os.environ.get('PORT'))
    app.run(debug=True, port=port, host='0.0.0.0')
