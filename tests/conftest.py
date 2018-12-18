import os
import tempfile
import pytest

from config import Config
from iqupdate import db, views
from iqupdate.example_database import init_example_database
from iqupdate import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app(Config(True, 'sqlite:///' + db_path))
    views.init_views(app)
    # create the db and load test data
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_example_database(app)
    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='admin', password='admin'):
        return self._client.post(
            '/admin/login',
            data={'email': email, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/admin/logout/')


@pytest.fixture
def auth(client):
    return AuthActions(client)
