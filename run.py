"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config
import yaml
from src.animal_manager import AnimalManager, RecommendationManager, create_db
from src.modeling import form_final_model, get_metric, kmodes_modeling, recommendation
from src.s3 import upload_file_to_s3, download_file_from_s3
from src.preprocess import drop_cols, load_dataset, feature_engineering, save_df
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

# add logging configuration
logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("run.py")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="The main parser for the animal crossing recommender")

    subparsers = parser.add_subparsers(dest="subparser_name")

    # Sub-parser for uploading data to s3
    sp_upload = subparsers.add_parser("upload_file_to_s3", help="Upload raw data to s3")
    sp_upload.add_argument("--s3_path",
                           default="s3://2022-msia423-gong-xiaoyun/data/external/villagers.csv",
                           help="S3 data path to the data")
    sp_upload.add_argument("--local_path", default="data/external/villagers.csv",
                           help="local path to the data")

    # Sub-parser for downloading data from s3 (optional)
    sp_download = subparsers.add_parser("download_file_from_s3", help="Download raw data from s3")
    sp_download.add_argument("--s3_path",
                             default="s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv",
                             help="S3 data path to the data")
    sp_download.add_argument("--local_path", default="data/raw/villagers.csv",
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
    sp_train.add_argument("--clean_path", default="data/interim/clean.csv",
                          help="the input path for the cleaned data.")
    sp_train.add_argument("--png_path", default="figures/cost_plot_kmodes.png",
                          help="the output path for the cost plot.")
    sp_train.add_argument("--result_path", default="deliverables/kmodes_result.csv",
                          help="the output path for the kmode results.")
    sp_train.add_argument("--df_model_path", default="data/interim/for_model.csv",
                          help="the output path for the csv for model uses.")
    sp_train.add_argument("--model_path", default="models/kmodes.joblib",
                          help="the output path for the final model.")
    sp_train.add_argument("--config",
                          default="config/model_config.yaml",
                          help="Path to configuration file")

    # Sub-parser for generating the recommendation result
    sp_recommendation = subparsers.add_parser("recommendation", help="generate the recommendation result")
    sp_recommendation.add_argument("--df_model_path", default="data/interim/for_model.csv",
                          help="the input path for the data used for modeling.")
    sp_recommendation.add_argument("--clean_path", default="data/interim/clean.csv",
                          help="the input path for the cleaned data.")
    sp_recommendation.add_argument("--model_path", default="models/kmodes.joblib",
                          help="the input path for the final model.")
    sp_recommendation.add_argument("--rec_path", default="data/final/recommendation.csv",
                          help="the output path for the recommendation.")
    sp_recommendation.add_argument("--config",
                        default="config/model_config.yaml",
                        help="Path to configuration file")

    # Sub-parser for generating the metric
    sp_get_metric = subparsers.add_parser("get_metric", help="generate the recommendation result")
    sp_get_metric.add_argument("--df_model_path", default="data/interim/for_model.csv",
                          help="the input path for the data used for modeling.")
    sp_get_metric.add_argument("--model_path", default="models/kmodes.joblib",
                          help="the input path for the final model.")
    sp_get_metric.add_argument("--metric_path", default="deliverables/metric.csv",
                          help="the output path for the metric.")
    sp_get_metric.add_argument("--config",
                        default="config/model_config.yaml",
                        help="Path to configuration file")

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

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
    sp_ingest_rec.add_argument("--input_path", default="data/final/recommendation.csv",
                               help="Recommendation table ingestion.")

    args = parser.parse_args()
    sp_used = args.subparser_name

    if sp_used == "upload_file_to_s3":
        upload_file_to_s3(args.local_path, args.s3_path)

    elif sp_used == "download_file_from_s3":
        download_file_from_s3(args.local_path, args.s3_path)

    elif sp_used == "preprocess":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s", args.config)
        data = load_dataset(filename=args.raw_path)
        data_dropped = drop_cols(data, **config["preprocess"]["drop_cols"])
        data_cleaned = feature_engineering(data_dropped, **config["preprocess"]["feature_engineering"])
        save_df(data_cleaned, output_path=args.clean_path)

    elif sp_used == "train":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s", args.config)
        kmodes_modeling(**config["modeling"]["kmodes_modeling"],
                        filename=args.clean_path,
                        pngpath=args.png_path,
                        df_model_path=args.df_model_path,
                        result_path = args.result_path
                        )
        form_final_model(**config["modeling"]["form_final_model"],
                         model_path=args.model_path)

    elif sp_used == "recommendation":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s", args.config)
        recommendation(**config["modeling"]["recommendation"],
                       filename_model=args.df_model_path,
                       filename_clean=args.clean_path,
                       model_path=args.model_path,
                       recommendation_path=args.rec_path)
    elif sp_used =="get_metric":
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info("Configuration file loaded from %s", args.config)
        get_metric(**config["modeling"]["get_metric"],
                       filename_model=args.df_model_path,
                       model_path=args.model_path,
                       metric_path=args.metric_path)

    elif sp_used == "create_db":
        create_db(args.engine_string)

    elif sp_used == "ingest_raw":
        am = AnimalManager(engine_string=args.engine_string)
        am.ingest_from_csv(input_path=args.input_path)
        am.close()

    elif sp_used == "ingest_rec":
        am = RecommendationManager(engine_string=args.engine_string)
        am.ingest_from_csv_rec(input_path=args.input_path)
        am.close()
    else:
        parser.print_help()
