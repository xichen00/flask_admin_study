import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel
from config import Config

db = SQLAlchemy()
babel = Babel()


def create_app(config_class=Config, debug=None, testing=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    if testing:
        app.config['TESTING'] = True
    db.init_app(app)
    babel.init_app(app)
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/iq_update.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('IQUpdate startup')
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from iqupdate import models
