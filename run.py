"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

# from config.flaskconfig import SQLALCHEMY_DATABASE_URI
import yaml
from src.animal_manager import AnimalManager, Villagers, create_db
from src.s3 import upload_file_to_s3, download_file_from_s3
from src.preprocess import load_dataset, feature_engineering, save_df
#from src.RDS import create_db;

# add configuration
logging.config.fileConfig('config/logging/local.conf')
from config.flaskconfig import SQLALCHEMY_DATABASE_URI
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add the main parser for create and/or add data to the database.
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    # parser.add_argument('--config',
    #                     default='config/model_config.yaml',
    #                     help='Path to configuration file')

    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for uploading data to s3
    sp_upload = subparsers.add_parser("upload_file_to_s3", help="Upload raw data to s3")
    sp_upload.add_argument('--s3_path',
                           default='s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv',
                           help="S3 data path to the data")
    sp_upload.add_argument('--local_path', default='data/raw/villagers.csv',
                           help="local path to the data")
    
    # Sub-parser for downloading data from s3 (optional)
    sp_download = subparsers.add_parser("download_file_from_s3", help="Download raw data from s3")
    sp_download.add_argument('--s3_path',
                           default='s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv',
                           help="S3 data path to the data")
    sp_download.add_argument('--local_path', default='data/download/villagers.csv',
                           help="local path to the data")

    # Sub-parser for preprocess the data
    sp_preprocess = subparsers.add_parser("preprocess", help="preprocess the raw data for modeling")
    sp_preprocess.add_argument('--config',
                        default='config/model_config.yaml',
                        help='Path to configuration file')

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sp_ingest = subparsers.add_parser("ingest",
                                      description="Add data to database")
    # sp_ingest.add_argument("--Unique_Entry_ID", help="ID of the new animal")
    # sp_ingest.add_argument("--Name", help="Name of the animal")
    # sp_ingest.add_argument("--Species", help="Species of the animal")
    # sp_ingest.add_argument("--Gender", help="Gender of the animal")
    # sp_ingest.add_argument("--Personality", help="Personality of the animal")
    # sp_ingest.add_argument("--Hobby", help="Hobby of the animal")
    # sp_ingest.add_argument("--Birthday", help="Birthday of the animal")
    # sp_ingest.add_argument("--Catchphrase", help="Catchphrase of the animal")
    # sp_ingest.add_argument("--Favorite_Song", help="Favorate song of the animal")
    # sp_ingest.add_argument("--Style_1", help="The first favorite style of the animal")
    # sp_ingest.add_argument("--Style_2", help="The second favorite style of the animal")
    # sp_ingest.add_argument("--Color_1", help="The first favorite color of the animal")
    # sp_ingest.add_argument("--Color_2", help="The second favorite color of the animal")
    # sp_ingest.add_argument("--Wallpaper", help="The wallpaper of the animal's house")
    # sp_ingest.add_argument("--Flooring", help="The wallpaper of the animal's house")
    # sp_ingest.add_argument("--Furniture_List", help="The list of furniture(IDs) in the animal's house")
    # sp_ingest.add_argument("--Filename", help="The Filename of the animal")   
    sp_ingest.add_argument("--engine_string",
                           default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sp_ingest.add_argument("--input_path", default="data/raw/villagers.csv", help="Name of villagers to be added")

    args = parser.parse_args()
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Configuration file loaded from %s" % args.config)

    sp_used = args.subparser_name

    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        am = AnimalManager(engine_string=args.engine_string)
        am.ingest_from_csv(input_path=args.input_path)
        am.close()
    elif sp_used == 'upload_file_to_s3':
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == 'download_file_from_s3':
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'preprocess':
        data = load_dataset(**config['preprocess']['load_dataset'])
        data_cleaned = feature_engineering(data, **config['preprocess']['feature_engineering'])
        save_df(data_cleaned, **config['preprocess']['save_df'])
    else:
        parser.print_help()
