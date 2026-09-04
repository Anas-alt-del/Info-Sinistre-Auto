from flask_wtf import FlaskForm  # Base class for all Flask forms
from wtforms import SubmitField, IntegerField, FloatField  # Field types
from wtforms.validators import DataRequired  # Validation rules

class InfosInputForm(FlaskForm):
    """
    Formulaire d'insertion de données:
    -Date
    -Heure
    -Lat
    -Long
    -Niveau de zoom (default 15)
    """

    Lat =   FloatField("Latitude", validators=[DataRequired()])
    Long =  FloatField("Longitude", validators=[DataRequired()])

    zoom =  IntegerField("Niveau de zoom", validators=[DataRequired()])
    submit = SubmitField("Sauvegarder")
