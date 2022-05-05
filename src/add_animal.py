"""Creates, ingests data into, and enables querying of a table of
 songs for the PennyLane app to query from and display results to the user."""
# mypy: plugins = sqlmypy, plugins = flasksqlamypy
import argparse
import logging.config
import sqlite3
#from tkinter.ttk import Style
import typing

import flask
import sqlalchemy
import sqlalchemy.orm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

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
    
    # def __repr__(self):
    #     return f'<Track {self.Name}>'
    def __repr__(self):
        return '<Animal Name %r>' % self.Name
        
# def create_db(engine_string: str) -> None:
#     """Create database with Tracks() data model from provided engine string.

#     Args:
#         engine_string (str): SQLAlchemy engine string specifying which database to write to.

#     Returns: None

#     """
#     engine = sqlalchemy.create_engine(engine_string)

#     Base.metadata.create_all(engine)
#     logger.info("Database created.")

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
        


# def create_db(engine_string: str) -> None:
#     """Create database with Tracks() data model from provided engine string.

#     Args:
#         engine_string (str): SQLAlchemy engine string specifying which database
#             to write to

#     Returns: None

#     """
#     engine = sqlalchemy.create_engine(engine_string)

#     Base.metadata.create_all(engine)
#     logger.info("Database created.")


# def add_animal_f(args: argparse.Namespace) -> None:
#     """Parse command line arguments and add animal to database.

#     Args:
#         args (:obj:`argparse.Namespace`): object containing the following
#             fields:

#             - args.title (str): Title of song to add to database
#             - args.artist (str): Artist of song to add to database
#             - args.album (str): Album of song to add to database
#             - args.engine_string (str): SQLAlchemy engine string specifying
#               which database to write to

#     Returns:
#         None
#     """
#     App_manager = TrackManager(engine_string=args.engine_string)
#     try:
#         App_manager.add_App(args.title, args.artist, args.album)
#     except sqlite3.OperationalError as e:
#         logger.error(
#             "Error page returned. Not able to add song to local sqlite "
#             "database: %s. Is it the right path? Error: %s ",
#             args.engine_string, e)
#     except sqlalchemy.exc.OperationalError as e:
#         logger.error(
#             "Error page returned. Not able to add song to MySQL database.  "
#             "Please check engine string and VPN. Error: %s ", e)
#     App_manager.close()
