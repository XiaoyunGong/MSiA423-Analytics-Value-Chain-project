import logging
import sys
from typing import List
import joblib
import pandas as pd
from kmodes.kmodes import KModes
import matplotlib.pyplot as plt

from src.modeling_helper import create_rec_table

logger = logging.getLogger(__name__)

def kmodes_modeling(filename: str,
                    feature_not_used: List,
                    k_start: int,
                    k_end: int,
                    init: str,
                    n_init: int,
                    random_state: int,
                    pngpath: str,
                    df_model_path: str,
                    result_path: str) -> None:
    """perform kmodes training, save a cost vs. cluster image and a final selected model.

    Args:
        filename (str): input csv file path
        feature_not_used (List): features that should not be included in the modeling
        k_start (int): start of k for the kmode model
        k_end (int): end of k for the kmode model
        init (str): init method (kmode param)
        n_init (int): number of items in each cluster at first (kmode param)
        random_state (int): random state for kmode
        pngpath (str): the path to save the png file
    """
    try:
        # read in the cleaned data
        df_all = pd.read_csv(filename)
        logger.info("The dataset path %s is loaded and it has %i columns.", filename, df_all.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename)
        sys.exit(1)
    
    # drop the features that are not used
    df = df_all.drop(columns = feature_not_used)
    logger.info("Columns used for kmodes clustering are %s", str(df.columns.values.tolist()))

    # save this df_model for further use.
    df.to_csv(df_model_path, index=False)

    # start the training process
    logger.debug("Kmodes training starts")
    cost = []
    K = range(k_start, k_end)
    for num_clusters in list(K):
        logger.debug("running n_cluster = %i", num_clusters)
        kmode = KModes(n_clusters = num_clusters, init = init, n_init = n_init, random_state=random_state)
        kmode.fit_predict(df)
        cost.append(kmode.cost_)
        logger.debug("The cost is %i", kmode.cost_)

    # plot the cost vs cluster plot
    logger.info("Finished the training process. Saving a plot to %s", pngpath)
    plt.plot(K, cost, "bx-")
    plt.xlabel("No. of clusters")
    plt.ylabel("Cost")
    plt.title("Elbow Method For Optimal k")
    plt.savefig(pngpath, transparent=True)

    # save the result kmodes K and cost table
    result_table = pd.DataFrame({"K": K, "cost": cost})
    result_table.to_csv(result_path, index=False)

def form_final_model(final_n_cluster: int,
                     init: str,
                     n_init: int,
                     random_state: int,
                     model_path: str):
    """this function will export the final model

    Args:
        init (str): init method (kmode param)
        n_init (int): init method (kmode param)
        random_state (int): random_state for this model
        model_path (str): the path to save the model
        final_n_cluster (str): number of clusters for the final model
    """
    logger.debug("entered the form final model step.")
    # save the final model
    final_model = KModes(n_clusters=final_n_cluster, init = init, n_init = n_init, random_state=random_state)
    joblib.dump(final_model, model_path)
    logger.info("The final model is saved to %s", model_path)

def recommendation(filename_model: str,
                   filename_clean: str,
                   drop_list: List,
                   model_path: str,
                   recommendation_path: str) -> None:
    """This function will create the recommendation file and save it to csv.

    Args:
        filename (str): input csv file path
        drop_list (List): the list of features that should not be included in the final recommendation
        model_path (str): the path to load the model
        recommendation_path (str): the path to save the final recommendation
    """
    # read in the csv file
    try:
        df_model = pd.read_csv(filename_model)
        logger.info("The dataset path %s is loaded and it has %i columns.", filename_model, df_model.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename_model)
    try:
        df_clean = pd.read_csv(filename_clean)
        logger.info("The dataset path %s is loaded and it has %i columns.", filename_clean, df_clean.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename_clean)

    # fit the final model
    kmode_final = joblib.load(model_path)

    clusters = kmode_final.fit_predict(df_model)
    logger.info("Kmode modeling finished! The cost is %i", kmode_final.cost_)

    # Create the recommendation table.
    joined = create_rec_table(df = df_clean, clusters = clusters, drop_list=drop_list)

    # export the recommendation table to a csv
    joined.to_csv(recommendation_path, index = False)
    logger.info("The table with clustering information is written to %s", recommendation_path)
