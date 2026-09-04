"""
URL routing and request handling for the Flask application.

Routes are URLs that users can visit (like /index or /form_projet_input).
Each route has a function that decides what to display when someone visits that URL.

Routes are like "addresses" for your web application!
"""

from flask import Flask, render_template, flash, redirect
# Flask: The main framework
# render_template: Converts HTML template files into complete web pages
# flash: Displays temporary messages to users (like "Success!" or "Error!")
# redirect: Sends users to a different URL after an action (like after form submission)

# from forms import ProjetForm  # Import the project form we defined
from config import Config  # Import configuration settings
from forms import InfosInputForm

# Create the Flask application object
# This object represents your entire web application
app = Flask(__name__)

# Tell Flask to use our Config class for settings
# This loads SECRET_KEY and other configuration values
app.config.from_object(Config)


@app.route('/infos_sinistre', methods=['GET', 'POST'])
def form_info_sinistre():
    inputForm = InfosInputForm()
    if inputForm.validate_on_submit():
        # If we reach here, the form data is valid!
        inputs = {
            "lat": inputForm.lat.data,
            "long": inputForm.long.data,
            "zoom": inputForm.zoom.data
        }

        return render_template('infos_output.html', data=inputs)

    return render_template('form_infos_input.html',
                           form=inputForm)
