from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from datetime import datetime

from iqupdate.example_database import init_example_database
from iqupdate.models import Role, User, ServicePack, ServicePackDetail
from iqupdate import create_app, db
from config import Config

application = create_app(Config)
# http://flask-sqlalchemy.pocoo.org/2.3/contexts/
# http://flask.pocoo.org/docs/1.0/appcontext/#creating-an-application-context
application.app_context().push()


def build_sample_db():
    db.drop_all()
    db.create_all()
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(application, user_datastore)
    init_example_database(application)
    return


if __name__ == '__main__':
    build_sample_db()
