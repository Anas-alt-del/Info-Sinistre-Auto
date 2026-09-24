
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    password = StringField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Soumettre")

