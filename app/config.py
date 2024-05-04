import os
from configparser import ConfigParser

config = ConfigParser()
config.read('config.cfg')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

SQLALCHEMY_DATABASE_URL= "sqlite:///./sql_app.db"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

API_KEY="9d207bf0"
# TODO MAKE THE BELOW CODE WORK
# SQLALCHEMY_DATABASE_URL= config.get('simulation', 'SQLALCHEMY_DATABASE_URL')
# SECRET_KEY = config.get('simulation', 'SECRET_KEY')
# ALGORITHM = config.get('simulation', 'ALGORITHM')

