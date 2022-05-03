"""Creates and ingests data into a table of villagers for the PennyLane."""
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
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__file__)

Base = declarative_base()


class Tracks(Base):
    """Creates a data model for the database to be set up for capturing songs."""

    __tablename__ = "tracks"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    album = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)

    def __repr__(self):
        return f"<Track {self.title}>"


if __name__ == "__main__":
    # set up mysql connection
    engine = sql.create_engine(engine_string)

    # test database connection
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

    # add a record/track
    track1 = Tracks(artist="Britney Spears", album="Circus", title="Radar")
    session.add(track1)
    session.commit()

    logger.info(
        "Database created with song added: Radar by Britney spears from the album, Circus"
    )
    track2 = Tracks(artist="Tayler Swift", album="Red", title="Red")
    session.add(track2)

    # To add multiple rows
    # session.add_all([track1, track2])

    session.commit()
    logger.info(
        "Database created with song added: Red by Tayler Swift from the album, Red"
    )

    # query records
    track_record = (
        session.query(Tracks.title, Tracks.album)
        .filter_by(artist="Britney Spears")
        .first()
    )
    print(track_record)

    query = "SELECT * FROM tracks WHERE artist LIKE '%%Britney%%'"
    result = session.execute(query)
    print(result.first().items())

    session.close()
