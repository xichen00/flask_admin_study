from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel

app = Flask(__name__)
babel = Babel(app)
app.config.from_pyfile('iq_update_config.py')
db = SQLAlchemy(app)

