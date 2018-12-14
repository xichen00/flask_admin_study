from iqupdate import create_app, views
from config import Config

application = create_app(Config)

views.init_views(application)

if __name__ == '__main__':
    # Start application
    application.run(host='0.0.0.0', port=5000, debug=True)
