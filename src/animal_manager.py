"""Creates, ingests data into, and enables querying of a table of
 songs for the PennyLane app to query from and display results to the user."""
# mypy: plugins = sqlmypy, plugins = flasksqlamypy

import logging
import typing

import pandas as pd
import flask
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

Base = declarative_base()

class Villagers(Base):
    """Creates a data model for the database to be set up for capturing villagers."""

    __tablename__ = "villagers"

    Unique_Entry_ID = sqlalchemy.Column(sqlalchemy.String(100), primary_key=True)
    Name = sqlalchemy.Column(sqlalchemy.String(100), unique=True, nullable=False)
    Species = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Gender = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Personality = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Hobby = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Birthday = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Catchphrase = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Favorite_Song = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Style_1 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Style_2 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Color_1 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Color_2 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Wallpaper = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Flooring = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Furniture_List = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Filename = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<Animal Name %r>' % self.Name

class Recommendations(Base):
    """Creates a data model for the database to be set up for capturing villagers."""

    __tablename__ = "recommendations"
    Name_villager = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Name = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Species = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Gender = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Personality = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Hobby = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Birthday = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Style_1 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Style_2 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Color_1 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Color_2 = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Unique_id = sqlalchemy.Column(sqlalchemy.String(100), primary_key=True)

    def __repr__(self):
        return '<Animal Name %r>' % self.Name

class AnimalManager:
    """Creates a SQLAlchemy connection to the Apps table.

    Args:
        app (:obj:`flask.app.Flask`): Flask app object for when connecting from
            within a Flask app. Optional.
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to. Follows the format
    """
    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None):
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize")

    def ingest_from_csv(self, input_path: str) -> None:
        """
        Add all the data in a csv file into the database
        Args:
            input_path: the path of the csv file
        Returns: None
        """

        session = self.session
        data_list = pd.read_csv(input_path).to_dict(orient='records')

        persist_list = []
        for data in data_list:
            persist_list.append(Villagers(**data))

        try:
            session.add_all(persist_list)
            session.commit()
        except sqlalchemy.exc.OperationalError:
            my_message = ('You might have connection error. Have you configured \n'
                          'SQLALCHEMY_DATABASE_URI variable correctly and connect to Northwestern VPN?')
            logger.error(f"{my_message} \n The original error message is: ", exc_info=True)
        except sqlalchemy.exc.IntegrityError:
            my_message = ('Have you already inserted the same record into the database before? \n'
                          'This database does not allow duplicate in the input-recommendation pair')
            logger.error(f"{my_message} \n The original error message is: ", exc_info=True)
        else:
            logger.info('%i records from %s were added to the table',len(persist_list), input_path)

    def close(self) -> None:
        """Closes SQLAlchemy session

        Returns: None

        """
        self.session.close()

def create_db(engine_string: str) -> None:
    """Create database from provided engine string
    Args:
        engine_string (str): Engine string
    Returns: None
    """
    engine = sqlalchemy.create_engine(engine_string)
    logger.debug("the engine_str is %s", engine_string)
    try:
        Base.metadata.create_all(engine)
    except sqlalchemy.exc.OperationalError as e:
        my_message = ('You might have connection error. Have you configured \n'
                      'SQLALCHEMY_DATABASE_URI variable correctly and connect to Northwestern VPN?')
        logger.error(f'The original error is: {e}')
        logger.error(f"{my_message}")
    else:
        logger.info("Database created.")

class RecommendationManager:
    """Creates a SQLAlchemy connection to the Apps table.

    Args:
        app (:obj:`flask.app.Flask`): Flask app object for when connecting from
            within a Flask app. Optional.
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to. Follows the format
    """
    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None):
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize")

    def ingest_from_csv_rec(self, input_path: str) -> None:
        """
        Add all the data in a csv file into the database
        Args:
            input_path: the path of the csv file
        Returns: None
        """

        session = self.session

        data_list = pd.read_csv(input_path).to_dict(orient='records')

        persist_list = []
        for data in data_list:
            persist_list.append(Recommendations(**data))

        try:
            session.add_all(persist_list)
            session.commit()
        except sqlalchemy.exc.OperationalError:
            my_message = ('You might have connection error. Have you configured \n'
                          'SQLALCHEMY_DATABASE_URI variable correctly and connect to Northwestern VPN?')
            logger.error(f"{my_message} \n The original error message is: ", exc_info=True)
        except sqlalchemy.exc.IntegrityError:
            my_message = ('Have you already inserted the same record into the database before? \n'
                          'This database does not allow duplicate in the input-recommendation pair')
            logger.error(f"{my_message} \n The original error message is: ", exc_info=True)
        else:
            logger.info('%i records from %s were added to the table',len(persist_list), input_path)

    def close(self) -> None:
        """Closes SQLAlchemy session

        Returns: None

        """
        self.session.close()

# def create_db(engine_string: str) -> None:

#     # find SQLALCHEMY_DATABASE_URI from environment and set as engine.
#     engine_string = os.getenv("SQLALCHEMY_DATABASE_URI")
#     logger.debug("The engine string is set to be %s", SQLALCHEMY_DATABASE_URI)
#     if engine_string is None:
#         logger.error("SQLALCHEMY_DATABASE_URI environment variable not set.")
#         raise RuntimeError("SQLALCHEMY_DATABASE_URI environment variable not set; exiting")
#     engine = sql.create_engine(engine_string)

#     try:
#         engine.connect()
#     except sqlalchemy.exc.OperationalError as e:
#         logger.error("Could not connect to database!")
#         logger.debug("Database URI: %s", )
#         raise e
#     except sqlalchemy.exe.OperationalError as e1:
#         logger.error("Can't connect to MySQL server.")
#         logger.debug("It is possible that user is not connected to NU VPN.")
#         raise e1

#     # create the villagers table
#     Base.metadata.create_all(engine)

#     # create a db session
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     session.commit()
#     logger.info("Database created with table villagers and recommendation added.")
#     session.close()


