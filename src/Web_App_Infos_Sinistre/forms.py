from asyncio.windows_events import NULL

from flask_wtf import FlaskForm  # Base class for all Flask forms
from wtforms import (SubmitField, IntegerField, FloatField, RadioField,
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
    id_reclamation = StringField("Identifiant de réclamation")
    date = DateField("Date")
    heure = TimeField("Heure")
    lat = FloatField("Latitude")
    long = FloatField("Longitude")

    submit = SubmitField("Sauvegarder")

class FormAjoutReclamation(FlaskForm):
    """
    Formulaire donnant l'option à l'utilisateur d'ajouter la réclamation
    """
    options = RadioField('Choose an option:', choices=[('Ajouter', 'Ajouter'), ('Ne pas ajouter', 'Ne pas ajouter')])
    submit = SubmitField("Sauvegarder")


class FormCollecteDonnees(FlaskForm):
    pass