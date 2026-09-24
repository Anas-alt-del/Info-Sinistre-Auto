

from flask import Flask, render_template, flash, jsonify, request
from werkzeug.utils import redirect
from app.forms import LoginForm
import jwt, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'le bonheur est dans le pré'

#AUTH_DB = 'auth.json'
DELAI_EXPIRATION_MIN = 1


# FONCTIONS UTILITAIRES

def verifier_login(username, password):
    if username.lower() == 'alain' and password.lower() == 'flouflou':
        return True
    return False

def generer_token():
    expiration_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=DELAI_EXPIRATION_MIN))
    token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
    return token


# ROUTES

@app.get('/')
@app.get('/index')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        if verifier_login(login_form.username.data, login_form.password.data):
            flash(f'Authentification réussie. Token = {generer_token()}')
        else:
            flash('Erreur: username ou password invalide')
        return redirect('/login')

    return render_template('login.html', form=login_form)

