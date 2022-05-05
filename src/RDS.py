"""Creates and ingests data into a table of villagers in RDS."""
import os
import logging
import sqlalchemy as sql
import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData

engine_string = os.getenv("SQLALCHEMY_DATABASE_URI")
if engine_string is None:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI environment variable not set; exiting")
# engine_string = "mysql+pymysql://user:password@host:3306/msia423_db"

# set up looging config
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)

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
        return f"<villager {self.Name}>"

def create_db(engine_string: str) -> None:
    engine = sql.create_engine(engine_string)
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("Could not connect to database!")
        logger.debug("Database URI: %s", )
        raise e
    
    # create the tracks table
    Base.metadata.create_all(engine)

    # create a db session
    Session = sessionmaker(bind=engine)
    session = Session()

    session.commit()
    logger.info(
        "Database created with villagers added."
    )
    session.close()

# if __name__ == "__main__":
#     # set up mysql connection
#     engine = sql.create_engine(engine_string)

#     # test database connection
#     try:
#         engine.connect()
#     except sqlalchemy.exc.OperationalError as e:
#         logger.error("Could not connect to database!")
#         logger.debug("Database URI: %s", )
#         raise e

#     # create the tracks table
#     Base.metadata.create_all(engine)

#     # create a db session
#     Session = sessionmaker(bind=engine)
#     session = Session()
    

#     # # add a record/track
#     # track1 = Tracks(artist="Britney Spears", album="Circus", title="Radar")
#     # session.add(track1)
#     # session.commit()

#     # logger.info(
#     #     "Database created with song added: Radar by Britney spears from the album, Circus"
#     # )
#     # track2 = Tracks(artist="Tayler Swift", album="Red", title="Red")
#     # session.add(track2)

#     # # To add multiple rows
#     # # session.add_all([track1, track2])

#     session.commit()
#     logger.info(
#         "Database created with villagers added."
#     )

#     # query records
#     # track_record = (
#     #     session.query(Tracks.title, Tracks.album)
#     #     .filter_by(artist="Britney Spears")
#     #     .first()
#     # )
#     # print(track_record)

#     # query = "SELECT * FROM tracks WHERE artist LIKE '%%Britney%%'"
#     # result = session.execute(query)
#     # print(result.first().items())

#     session.close()
