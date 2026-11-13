# Info-Sinistre-Auto

**Français** · [English](#english)

## Présentation

Info-Sinistre-Auto est un prototype d’intégration de données pour l’évaluation de réclamations automobiles. Les évaluateurs doivent souvent consulter plusieurs sources pour comprendre les circonstances d’un sinistre. L’application regroupe ces recherches en collectant des données météo et des informations sur les zones de dégel à partir de la date, de l’heure et des coordonnées de l’incident.

## Fonctionnalités

- Interface Web bilingue (français et anglais) pour rechercher un sinistre, collecter des données et associer des numéros de réclamation.
- API REST pour rechercher, créer et modifier les dossiers d’incident.
- Données météo historiques par heure et résumé des 24 heures précédant l’incident, via Open-Meteo.
- Identification de la zone et de la période de dégel à partir des données GeoJSON du gouvernement du Québec.
- Authentification par jeton JWT.
- Persistance dans MongoDB ou, par défaut, dans un fichier JSON local.
- Documentation Swagger pour les services d’authentification et de données.

## Technologies

Python, Flask, Flask-WTF, Flask-CORS, PyJWT, Flasgger/Swagger, Requests, Shapely, PyMongo, MongoDB et les API Open-Meteo et du gouvernement du Québec. L’interface Web utilise des modèles Jinja.

## Architecture simplifiée

L’application Web communique avec les services d’authentification et de données. Le service de données orchestre les appels au service de collecte et au DAO. Le service de collecte interroge les sources externes; le DAO lit et écrit les dossiers dans MongoDB ou dans le fichier JSON local.

![Schéma simplifié de l’architecture Info-Sinistre-Auto](docs/architecture.PNG)

## Démarrage local

Prérequis : Python 3.12 ou plus récent et un accès Internet pour la collecte météo et les données de zones de dégel. Le workflow CI vérifie la syntaxe du code sous Python 3.12 et 3.13. MongoDB est facultatif; sans connexion MongoDB, le DAO utilise `src/Service_DAO/db_incidents.json`.

Chaque composant possède son propre `requirements.txt` et doit être lancé dans un terminal séparé. Pour chacun des cinq composants ci-dessous, ouvrez un terminal à la racine du dépôt, puis exécutez les commandes de préparation en remplaçant `Service_Auth` par le dossier voulu :

```powershell
Set-Location src\Service_Auth
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloque l’activation de l’environnement virtuel, utilisez un terminal autorisant l’exécution du script ou appelez directement `.\.venv\Scripts\python.exe`.

Lancez ensuite chaque application dans son propre terminal :

| Composant | Dossier | Commande | Port local |
|---|---|---|---:|
| Authentification | `src/Service_Auth` | `python serv_auth.py` | 5602 |
| Collecte | `src/Service_Collecte` | `python serv_collecte.py` | 5020 |
| DAO | `src/Service_DAO` | `python serv_dao.py` | 5601 |
| Données | `src/Service_Data` | `python serv_data.py` | 5010 |
| Application Web | `src/web_app_info_sinistre` | `python web_app_main.py` | 5000 |

Le projet peut être déployé localement ou sur le cloud. En local, les services utilisent ces ports par défaut et la configuration référence `127.0.0.1`. Démarrez les services d’authentification, de collecte, de DAO et de données avant l’application Web. Ouvrez ensuite [http://127.0.0.1:5000](http://127.0.0.1:5000). Les documentations Swagger sont disponibles à [http://127.0.0.1:5010/apidocs](http://127.0.0.1:5010/apidocs) et [http://127.0.0.1:5602/apidocs](http://127.0.0.1:5602/apidocs).

Sur le cloud, définissez les variables d’environnement `SERV_AUTH_URL`, `SERV_COLLECTE_URL`, `SERV_DAO_URL` et `SERV_DATA_URL` avec les URL des services correspondants afin de configurer leurs communications. Pour déclencher le workflow `keep-alive.yml` depuis la page d’accueil (au maximum une fois toutes les cinq minutes), configurez aussi `GITHUB_TOKEN` dans l’environnement de l’application Web avec un jeton GitHub limité au dépôt et doté de la permission Actions « Read and write ». Le jeton reste côté serveur; sans lui, la page s’affiche normalement, mais le déclenchement est ignoré et consigné dans les logs. Pour utiliser MongoDB, connectez-le depuis l’interface Web avec une URI valide; sinon le stockage JSON local est utilisé.

## Limites connues

- Il s’agit d’un prototype : les identifiants de démonstration et certaines clés secrètes sont codés en dur. Ne pas exposer tel quel en production; configurer des secrets robustes et une authentification adaptée.
- Les données dépendent de la disponibilité et de la couverture des sources externes. La collecte des zones de dégel concerne le Québec; une coordonnée hors des zones connues retourne `N/A`.
- Le fichier JSON local est adapté au développement et à la démonstration, pas à l’accès concurrent ou à une persistance de production.
- La gestion des erreurs, la validation des entrées, les délais d’attente et les tests automatisés restent à renforcer, en particulier lors des appels aux API externes.
- Les services API démarrent en mode debug dans leur configuration locale; ce mode doit être désactivé pour tout déploiement réel.

## Sources de données, attribution et licences

| Source | Données utilisées et traitement | Attribution et licence |
|---|---|---|
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), endpoint [Archive API](https://archive-api.open-meteo.com/v1/archive) | Pour les coordonnées et la date/heure de l’incident : température, pluie, neige, couverture nuageuse, vent et code météo horaires; lever et coucher du soleil quotidiens. L’application affiche les valeurs de l’heure de l’incident et calcule les minimums, maximums et cumuls des 24 heures précédentes. Le modèle/source météorologique est laissé à la sélection par défaut de l’API (aucun modèle n’est fixé dans la requête); la disponibilité historique dépend donc de l’API. Documentation consultée le 7 novembre 2026. | Les données de l’API sont sous [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution : « Données météo par [Open-Meteo.com](https://open-meteo.com/), adaptées (résumés calculés sur 24 h) », avec un lien vers la licence. Citation du logiciel : Zippenfenig, P. (2023). *Open-Meteo.com Weather API* [logiciel]. Zenodo. [https://doi.org/10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649). |
| Ministère des Transports et de la Mobilité durable du Québec, [Zone de dégel](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel), consulté par le [service WFS GeoJSON](https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:zone_degel&outfile=ZoneDegel&srsname=EPSG:4326&outputformat=geojson) | Polygones des zones 1–3 et propriétés de période de dégel; l’application repère le polygone contenant les coordonnées de l’incident et affiche sa zone et ses dates. Couverture : Québec. Le jeu est mis à jour au besoin; sa propriété `dat_maj` indique la date de mise à jour des données. Métadonnées consultées le 7 novembre 2026. | Le catalogue [Données Québec](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel) indique la licence [CC BY 4.0](https://www.donneesquebec.ca/licence/#cc-by). Citation : Ministère des Transports et de la Mobilité durable du Québec. (s. d.). *Zone de dégel* [jeu de données]. Données Québec. |

Les données proviennent de services en ligne et peuvent évoluer ou être indisponibles. Pour reproduire une collecte, consigner la date d’accès, les paramètres de requête et les dates de mise à jour des sources. La licence des données ne détermine pas celle du code de ce projet.

---

<a id="english"></a>

## English

Info-Sinistre-Auto is a data-integration prototype for motor-claim assessment. Claims adjusters often need to consult several sources to understand the circumstances of an accident. This application brings those searches together by collecting weather and thaw-zone information from the incident’s date, time, and coordinates.

### Features

- Bilingual (French and English) web interface to search incidents, collect data, and associate claim numbers.
- REST API to search, create, and update incident records.
- Hourly historical weather and a summary of the 24 hours before the incident, using Open-Meteo.
- Thaw-zone and period lookup using GeoJSON data from the Government of Québec.
- JWT-based authentication.
- MongoDB persistence or, by default, a local JSON file.
- Swagger documentation for the authentication and data services.

### Technologies

Python, Flask, Flask-WTF, Flask-CORS, PyJWT, Flasgger/Swagger, Requests, Shapely, PyMongo, MongoDB, the Open-Meteo API, and Québec government data. The web interface uses Jinja templates.

### Simplified architecture

The web app communicates with the authentication and data services. The data service orchestrates calls to the collection service and DAO. The collection service queries external sources; the DAO reads and writes incident records to MongoDB or the local JSON file.

![Simplified Info-Sinistre-Auto architecture diagram](docs/architecture.PNG)

### Getting started locally

Prerequisites: Python 3.12 or later and Internet access for weather and thaw-zone data. The CI workflow checks source syntax on Python 3.12 and 3.13. MongoDB is optional; without a MongoDB connection, the DAO uses `src/Service_DAO/db_incidents.json`.

Each component has its own `requirements.txt` and must run in a separate terminal. For each of the five components below, open a terminal at the repository root and run the setup commands, replacing `Service_Auth` with the component’s folder:

```powershell
Set-Location src\Service_Auth
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual-environment activation, use a terminal that allows script execution or call `.\.venv\Scripts\python.exe` directly.

Then start each application in its own terminal:

| Component | Folder | Command | Local port |
|---|---|---|---:|
| Authentication | `src/Service_Auth` | `python serv_auth.py` | 5602 |
| Collection | `src/Service_Collecte` | `python serv_collecte.py` | 5020 |
| DAO | `src/Service_DAO` | `python serv_dao.py` | 5601 |
| Data | `src/Service_Data` | `python serv_data.py` | 5010 |
| Web app | `src/web_app_info_sinistre` | `python web_app_main.py` | 5000 |

The project can be deployed locally or in the cloud. For local deployment, the services use these ports by default, and configuration points to `127.0.0.1`. Start authentication, collection, DAO, and data services before the web app. Then open [http://127.0.0.1:5000](http://127.0.0.1:5000). Swagger documentation is available at [http://127.0.0.1:5010/apidocs](http://127.0.0.1:5010/apidocs) and [http://127.0.0.1:5602/apidocs](http://127.0.0.1:5602/apidocs).

For cloud deployment, set the `SERV_AUTH_URL`, `SERV_COLLECTE_URL`, `SERV_DAO_URL`, and `SERV_DATA_URL` environment variables to the corresponding service URLs to configure inter-service communication. To dispatch `keep-alive.yml` from the home page (at most once every five minutes), also configure `GITHUB_TOKEN` in the web app's environment with a GitHub token restricted to this repository and the Actions “Read and write” permission. The token stays server-side; without it, the page still loads normally, but dispatch is skipped and logged. To use MongoDB, connect it from the web interface with a valid URI; otherwise, local JSON storage is used.

### Known limitations

- This is a prototype: demo credentials and some secret keys are hard-coded. Do not expose it as-is in production; configure strong secrets and suitable authentication.
- Data availability and coverage depend on external providers. Thaw-zone data covers Québec; coordinates outside known zones return `N/A`.
- Local JSON storage is intended for development and demonstration, not concurrent access or production persistence.
- Error handling, input validation, timeouts, and automated tests need improvement, particularly around external API calls.
- The API services start in debug mode in their local configuration; disable it before any real deployment.

### Data sources, attribution and licenses

| Source | Data used and processing | Attribution and license |
|---|---|---|
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), [Archive API endpoint](https://archive-api.open-meteo.com/v1/archive) | For the incident’s coordinates and date/time: hourly temperature, rain, snowfall, cloud cover, wind, and weather code; daily sunrise and sunset. The app displays values for the incident hour and calculates minimums, maximums, and totals for the preceding 24 hours. The weather model/source is left to the API’s default selection (the request does not pin a model), so historical availability depends on the API. Documentation accessed November 7, 2026. | API data are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: “Weather data by [Open-Meteo.com](https://open-meteo.com/), adapted (24-hour summaries calculated),” with a link to the license. Software citation: Zippenfenig, P. (2023). *Open-Meteo.com Weather API* [Computer software]. Zenodo. [https://doi.org/10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649). |
| Québec Ministère des Transports et de la Mobilité durable, [Zone de dégel](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel), accessed through the [WFS GeoJSON service](https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:zone_degel&outfile=ZoneDegel&srsname=EPSG:4326&outputformat=geojson) | Polygons for thaw zones 1–3 and their thaw-period properties; the app finds the polygon containing the incident coordinates and displays its zone and dates. Coverage: Québec. The dataset is updated as needed; its `dat_maj` property records the data update date. Metadata accessed November 7, 2026. | The [Données Québec catalog](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel) identifies the license as [CC BY 4.0](https://www.donneesquebec.ca/licence/#cc-by). Citation: Ministère des Transports et de la Mobilité durable du Québec. (n.d.). *Zone de dégel* [Data set]. Données Québec. |

These sources are online services and may change or become unavailable. To reproduce a collection, record the access date, query parameters, and source update dates. The data licenses do not determine the license for this project’s code.
