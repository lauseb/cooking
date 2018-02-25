import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "it's a secret !"
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOW_USER_REGISTRATION = os.environ.get("ALLOW_USER_REGISTRATION") or False
    RECIPES_PER_PAGE = os.environ.get("RECIPES_PER_PAGE") or 10

    BOOTSTRAP_SERVE_LOCAL = True

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
