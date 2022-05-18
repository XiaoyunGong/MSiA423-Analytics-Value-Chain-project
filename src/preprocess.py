import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

def load_dataset(filename: str, features: List) -> pd.DataFrame:
    """load the dataset from the data folder, and keep only the useful features.

    Args:
        filename (str): The location of the input .csv file.
        features (List): List of useful features.

    Returns:
        pd.DataFrame: The dataframe with only useful features.
    """ 
    try:
        df = pd.read_csv(filename)
        logging.info("The dataset path %s is loaded and it has %i columns.", filename, df.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename)

    df_use = df[features]
    logger.info(f'The shape of the data with useful features only is {df_use.shape}')
    return df_use

def feature_engineering(df: pd.DataFrame, grouping_dict: Dict) -> pd.DataFrame:
    """This function will regroup the animal species column using the grouping dictionary
        in the configuration file. Then, the birthday column will be replaced by a month only value.
        Afterwards, the name column is set as the index.

    Args:
        df (pd.DataFrame): output pandas df from load_dataset.
        grouping_dict (Dict): a dictionary with information of the grouping rules for the species column.

    Returns:
        pd.DataFrame: preprocessed dataframe.
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("Provided argument `df` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")

    for key in grouping_dict.keys():
        lst = grouping_dict.get(key)
        df.loc[df.Species.isin(lst), "Species"] = key
    
    logger.info("Animals are re-grouped into %i groups (%s).", 
                len(grouping_dict.keys()), 
                str(grouping_dict.keys()))
    
    df.Birthday = df.Birthday.str[-3:]

    logger.info("The birthday column was set to be month only.")
    df.set_index('Name')
    logger.info("The index column is set to be the name of the villagers.")
    return df

def save_df(df: pd.DataFrame, output_path: str) -> None:
    """This function will save the preprocessed data to the output path location.

    Args:
        df (pd.DataFrame): preprocessed data.
        output_path (str): intented location.
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("Provided argument `df` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")

    df.to_csv(output_path, index=False)
    logger.info('The preprocessed data is saved to %s', output_path)
