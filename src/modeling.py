import logging
from typing import List
import joblib
import pandas as pd
import numpy as np
from kmodes.kmodes import KModes
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def kmodes_modeling(filename: str,
                    k_start: int,
                    k_end: int,
                    init: str,
                    n_init: int,
                    random_state: int,
                    pngpath: str,
                    model_path: str,
                    n_cluster:str) -> None:
    try:
        df = pd.read_csv(filename)
        logging.info("The dataset path %s is loaded and it has %i columns.", filename, df.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename)
    cost = []
    K = range(k_start, k_end)
    for num_clusters in list(K):
        logger.info("running n_cluster = %i", num_clusters)
        kmode = KModes(n_clusters = num_clusters, init = init, n_init = n_init, random_state=random_state)
        kmode.fit_predict(df)
        cost.append(kmode.cost_)
    logger.info("Finished the training process. Saving a plot to %s", pngpath)
    plt.plot(K, cost, 'bx-')
    plt.xlabel('No. of clusters')
    plt.ylabel('Cost')
    plt.title('Elbow Method For Optimal k')
    plt.savefig(pngpath)
    final_model = kmode = KModes(n_clusters=n_cluster, init = init, n_init = n_init, random_state=random_state)
    joblib.dump(final_model, model_path)

def recommendation(filename: str,
                drop_list: List,
                model_path: str,
                recommendation_path: str) -> None:
    try:
        df = pd.read_csv(filename)
        logger.info("The dataset path %s is loaded and it has %i columns.", filename, df.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename)
    kmode = joblib.load(model_path)
    clusters = kmode.fit_predict(df)
    logger.debug('Kmode modeling finished!')
    df.insert(0, "Cluster", clusters, True)
    joined = df.merge(df, how='outer', on='Cluster', 
                      suffixes = ['_villager', ''])
    joined.drop(columns=drop_list, inplace=True)
    joined = joined[joined.Name_villager!=joined.Name]

    index_str = [str(x) for x in np.arange(0,joined.shape[0])]
    joined['Unique_id'] = index_str

    joined.to_csv(recommendation_path, index = False)
    logger.info("The table with clustering information is written to %s", recommendation_path)
