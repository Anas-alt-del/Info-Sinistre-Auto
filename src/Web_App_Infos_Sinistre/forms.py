from asyncio.windows_events import NULL

from flask_wtf import FlaskForm  # Base class for all Flask forms
from wtforms import (SubmitField, IntegerField, FloatField,
                     DateField, TimeField, StringField)  # Field types
from wtforms.validators import DataRequired  # Validation rules


class InfosInputForm(FlaskForm):
    """
    Formulaire d'insertion de données:
    -id_reclamation (nullable)
    -Date (nullable)
    -Heure (nullable)
    -Lat (nullable)
    -Long (nullable)
    -Niveau de zoom (default 15)
    """
    id_reclamation = StringField("Identifiant de réclamation", default=None)

    date = DateField("Date", default=None)
    heure = TimeField("Heure", default=None)

    lat = FloatField("Latitude", default=None)
    long = FloatField("Longitude", default=None)

    submit = SubmitField("Sauvegarder")

class FormAjoutReclamation(FlaskForm):
    """
    Formulaire donnant l'option à l'utilisateur d'ajouter la réclamation
    """
    pass

class FormCollecteDonnees(FlaskForm):
    pass