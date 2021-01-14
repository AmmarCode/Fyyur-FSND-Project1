import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

database_path = os.environ['DATABASE_URL']
# DATABASE URL
SQLALCHEMY_DATABASE_URI = database_path