"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

# from config.flaskconfig import SQLALCHEMY_DATABASE_URI
import yaml
from src.animal_manager import AnimalManager, RecommendationManager, create_db
from src.modeling import kmodes_modeling, recommendation
from src.s3 import upload_file_to_s3, download_file_from_s3
from src.preprocess import load_dataset, feature_engineering, save_df
#from src.RDS import create_db;
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

# add configuration
logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("run.py")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="The main parser for the animal crossing recommender")

    subparsers = parser.add_subparsers(dest="subparser_name")

    # Sub-parser for uploading data to s3
    sp_upload = subparsers.add_parser("upload_file_to_s3", help="Upload raw data to s3")
    sp_upload.add_argument("--s3_path",
                           default="s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv",
                           help="S3 data path to the data")
    sp_upload.add_argument("--local_path", default="data/raw/villagers.csv",
                           help="local path to the data")
    
    # Sub-parser for downloading data from s3 (optional)
    sp_download = subparsers.add_parser("download_file_from_s3", help="Download raw data from s3")
    sp_download.add_argument("--s3_path",
                           default="s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv",
                           help="S3 data path to the data")
    sp_download.add_argument("--local_path", default="data/download/villagers.csv",
                           help="local path to the data")

    # Sub-parser for preprocess the data
    sp_preprocess = subparsers.add_parser("preprocess", help="preprocess the raw data for modeling")
    sp_preprocess.add_argument("--config",
                               default="config/model_config.yaml",
                               help="Path to configuration file")
    sp_preprocess.add_argument("--raw_path", default="data/raw/villagers.csv",
                               help="the input path of the raw data.")
    sp_preprocess.add_argument("--clean_path", default="data/interim/clean.csv",
                               help="the output path for the cleaned data.")

    # Sub-parser for training
    sp_train = subparsers.add_parser("train", help="train the model")
    sp_train.add_argument("--config",
                        default="config/model_config.yaml",
                        help="Path to configuration file")

    # Sub-parser for generating the recommendation result
    sp_recommendation = subparsers.add_parser("recommendation", help="generate the recommendation result")
    sp_recommendation.add_argument("--config",
                        default="config/model_config.yaml",
                        help="Path to configuration file")
    
    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting raw data
    sp_ingest_raw = subparsers.add_parser("ingest_raw",
                                      description="Add raw data to database")
    sp_ingest_raw.add_argument("--engine_string",
                           default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sp_ingest_raw.add_argument("--input_path", default="data/raw/villagers.csv", help="Raw datt ingestion.")

    # sub-parser for ingesting recommendation data
    sp_ingest_rec = subparsers.add_parser("ingest_rec",
                                      description="Add data to database")
    sp_ingest_rec.add_argument("--engine_string",
                           default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sp_ingest_rec.add_argument("--input_path", default="data/final/recommendation.csv", help="Recommendation table ingestion.")

    args = parser.parse_args()
    sp_used = args.subparser_name

    if sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)

    elif sp_used == "download_file_from_s3":
        download_file_from_s3(args.local_path, args.s3_path)

    elif sp_used == "preprocess":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s" % args.config)
        data = load_dataset(**config["preprocess"]["load_dataset"], filename=args.raw_path)
        data_cleaned = feature_engineering(data, **config["preprocess"]["feature_engineering"])
        save_df(data_cleaned, output_path=args.clean_path)

    elif sp_used == "create_db":
        create_db(args.engine_string)

    elif sp_used == "ingest_raw":
        am = AnimalManager(engine_string=args.engine_string)
        am.ingest_from_csv(input_path=args.input_path)
        am.close()


    elif sp_used =="train":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s" % args.config)
        kmodes_modeling(**config["modeling"]["kmodes_modeling"])
    elif sp_used == "recommendation":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s" % args.config)
        recommendation(**config["modeling"]["recommendation"])
    elif sp_used == "ingest_rec":
        am = RecommendationManager(engine_string=args.engine_string)
        am.ingest_from_csv_rec(input_path=args.input_path)
        am.close()
    else:
        parser.print_help()
