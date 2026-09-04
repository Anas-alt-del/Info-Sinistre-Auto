"""
Configuration settings for the Flask application.

This file stores settings that should be the same across your entire app,
like security keys and database connections. Keeping settings separate from
your main code is a best practice!
"""

import os


class Config(object):
    """
    Main configuration class for the Flask app.

    Flask uses this class to configure itself when the app starts.
    You can create different Config classes (like ConfigDev, ConfigProduction)
    for different environments (development vs. live servers).
    """

    # SECRET_KEY: A security token used to encrypt sensitive data (like form tokens)
    # It tries to get the key from your computer's environment variables first.
    # If not found, it uses the default string (not secure in production!).
    # In real projects, never hardcode secrets—always use environment variables.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Le renard saute la barriere'
