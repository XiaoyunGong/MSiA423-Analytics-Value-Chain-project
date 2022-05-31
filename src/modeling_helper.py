"""
This module includes functions called in the modeling module.
"""
import logging
from typing import List
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def create_rec_table(df: pd.DataFrame,
                     clusters: np.array,
                     drop_list: List) -> pd.DataFrame:
    """Create the recommendation table. Needs to join two df's together.

    Args:
        df (pd.DataFrame): the original dataframe
        clusters (np.array): the clustering result
        drop_list (List): the items that are not needed in the end result

    Raises:
        ValueError: if the nrow of df doesn't match with the lenth of the cluter

    Returns:
        pd.DataFrame: the final rec result
    """

    # check if the nrow of the df is the same as the length of the clustering array
    df_nrows = df.shape[0]
    cluster_length = len(clusters)

    if df_nrows == cluster_length:
        df.insert(0, "Cluster", clusters, True)
    else:
        logger.error("nrow of df doesn't match with the lenth of the clutersing result.")
        raise ValueError("nrow of the df doesn't match length of the array.")

    # perform merging
    joined = df.merge(df, how="outer", on="Cluster",
                    suffixes = ["_villager", ""])
    joined.drop(columns=drop_list, inplace=True)
    joined = joined[joined.Name_villager!=joined.Name]

    # set a unique index for further use in creating the SQL table
    index_str = [int(x) for x in np.arange(0,joined.shape[0])]
    joined["Unique_id"] = index_str

    return joined
