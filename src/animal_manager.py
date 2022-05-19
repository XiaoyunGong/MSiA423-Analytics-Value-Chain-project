"""Creates, ingests data into, and enables querying of a table of
 songs for the PennyLane app to query from and display results to the user."""
# mypy: plugins = sqlmypy, plugins = flasksqlamypy
import os
import argparse
import logging.config
import sqlite3
#from tkinter.ttk import Style
import typing

import flask
from sklearn import cluster
import sqlalchemy as sql
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

logger = logging.getLogger(__name__)

#Base: typing.Any = declarative_base()
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

def create_db(engine_string: str) -> None:

    # find SQLALCHEMY_DATABASE_URI from environment and set as engine.
    engine_string = os.getenv("SQLALCHEMY_DATABASE_URI")
    if engine_string is None:
        logger.error("SQLALCHEMY_DATABASE_URI environment variable not set.")
        raise RuntimeError("SQLALCHEMY_DATABASE_URI environment variable not set; exiting")
    engine = sql.create_engine(engine_string)

    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("Could not connect to database!")
        logger.debug("Database URI: %s", )
        raise e
    except sqlalchemy.exe.OperationalError as e1:
        logger.error("Can't connect to MySQL server.")
        logger.debug("It is possible that user is not connected to NU VPN.")
        raise e1

    # create the villagers table
    Base.metadata.create_all(engine)

    # create a db session
    Session = sessionmaker(bind=engine)
    session = Session()

    session.commit()
    logger.info("Database created with table villagers and recommendation added.")
    session.close()


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
        # Make the dataframe to a list of dictionaries to pass the data into the Pokemon class easily
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

    def add_animal(
        self,
        Unique_Entry_ID: str,
        Name: str,
        Species: str,
        Gender: str,
        Personality: str,
        Hobby: str,
        Birthday: str,
        Catchphrase: str,
        Favorite_Song: str,
        Style_1: str,
        Style_2: str,
        Color_1: str,
        Color_2: str,
        Wallpaper: str,
        Flooring: str,
        Furniture_List: str,
        Filename: str) -> None:
        """Seeds an existing database with additional animal.

        Args:
            !!! TO DO !!!!

        Returns:
            None
        """
        try:
            session = self.session
            animal = Villagers(
                Unique_Entry_ID=Unique_Entry_ID,
                Name=Name,
                Species=Species,
                Gender=Gender,
                Personality=Personality,
                Hobby=Hobby,
                Birthday=Birthday,
                Catchphrase=Catchphrase,
                Favorite_Song=Favorite_Song,
                Style_1=Style_1,
                Style_2=Style_2,
                Color_1=Color_1,
                Color_2=Color_2,
                Wallpaper=Wallpaper,
                Flooring=Flooring,
                Furniture_List=Furniture_List,
                Filename=Filename
                )
            session.add(animal)
            session.commit()
            logger.info("New animal %s added to the database", Name)
        except sqlalchemy.exc.OperationalError:
            logger.error('Failed to connect to server. '
                         'Please check if you are connected to Northwestern VPN')

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
        # Make the dataframe to a list of dictionaries to pass the data into the Pokemon class easily
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
