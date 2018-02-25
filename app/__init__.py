import os
import sys
import logging
import traceback

from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
bootstrap = Bootstrap()

class ReverseProxied:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    if not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
                "logs/cooking.log", maxBytes=1024**2, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        if app.debug:
            file_handler.setLevel(logging.DEBUG)
            app.logger.setLevel(logging.DEBUG)

            db_log = logging.getLogger("sqlalchemy.engine")
            db_log.setLevel(logging.DEBUG)
            db_log.addHandler(file_handler)
        else:
            file_handler.setLevel(logging.INFO)
            app.logger.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.info("Cooking starting")

        def logging_excepthook(exc_type, value, tb):
            app.logger.critical(
                    "".join(traceback.format_exception(exc_type, value, tb)))

        sys.excepthook = logging_excepthook

    return app

from app import models
