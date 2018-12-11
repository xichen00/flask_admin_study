# Create dummy secrey key so we can use sessions
SECRET_KEY = 'This is a secret key for IQUpdate@Apis'

# Create in-memory database
SQLALCHEMY_DATABASE_URI = 'mysql://xichen00:6DCzRR00@localhost:3306/iqupdate'
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "This is a password salt for IQUpdate@Apis"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"

# Bable default config
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'