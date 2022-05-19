import logging.config
import sqlite3
import traceback

import sqlalchemy.exc
from flask import Flask, render_template, request, redirect, url_for

# For setting up the Flask-SQLAlchemy database session
from src.animal_manager import RecommendationManager, Recommendations
from src.modeling import recommendation

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates",
            static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5000:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config["HOST"]
    , app.config["PORT"])

# Initialize the database session
recommendation_manager = RecommendationManager(app)
#logger.info('The database dialect is %s', app.config['SQLALCHEMY_DATABASE_URI'].split(':')[0])
logger.info('The database dialect is %s', app.config['SQLALCHEMY_DATABASE_URI'])

@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the app/templates/index.html template.

    Returns:
        Rendered html template

    """
    return render_template('index.html')


@app.route('/', methods=['POST'])
def data():
    if request.method == 'POST':
        user_input = request.form.to_dict()['Name']
        try:
            recommendations = recommendation_manager.session.query(Recommendations).filter_by(Name_villager=user_input).limit(
                app.config["MAX_ROWS_SHOW"]).all()
            if len(recommendations) == 0:
                return render_template('not_found.html', user_input=user_input)
            return render_template('result.html', recommendations=recommendations, user_input=user_input)
        except sqlalchemy.exc.OperationalError:
            traceback.print_exc()
            logger.warning("Not able to display villagers, error page returned")
            return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"],
            host=app.config["HOST"])
