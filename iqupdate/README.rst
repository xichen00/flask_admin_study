To run this application:

1. Clone the repository::

    git clone https://github.com/xichen00/flask_admin_study.git
    cd iqupdate

2. Create and activate a virtual environment::

    virtualenv venv
    source venv/bin/activate

3. Install requirements:

    **Install with command**::

        pip install -r 'deployment/requirements/prod.txt'

    **If there are some errors in installing mysqlclient, try this command**::

        pip install --only-binary :all: mysqlclient

4. Before first time run this application change config SQLALCHEMY_DATABASE_URI in iq_update_config.py and run::

    python iqupdate/iq_update_example_data.py

5. Run the application::

    python iqupdate/iq_update.py

6. The default account:

    Administrator

        **Email:** admin **Password:** admin

    Release manager

        **Email:** release **Password:** release

7. Translations update:

    **If any new filed in html or py files:**

        *Step1: Recreate translation template in ./ run shell command*::

            pybabel extract -F babel.cfg -o messages.pot .

        *Step2: Recreate translate './translations/zh/LC_MESSAGES/message.po' file with shell commant*::

            pybabel init -i messages.pot -d translations -l zh

        *Step3: Recompile all .po files in dir ./translations into .mo files with shell command*::

            pybabel compile -d translations

    **If only translation change:**

        *Step1: When there are only translation contents updates, run following command*::

            pybabel update -i messages.pot -d translations

        *Step2: Recompile all .po files in dir ./translations into .mo files with shell command*::

            pybabel compile -d translations

