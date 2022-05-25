"""This module includes three functions that is associated with preprocessing the data.
After these three steps, user should get a cleaned dataset.
"""
import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

def load_dataset(filename: str, features: List) -> pd.DataFrame:
    """load the dataset from the data folder, and keep only the useful features

    Args:
        filename (str): The location of the input .csv file
        features (List): List of useful features

    Returns:
        pd.DataFrame: The dataframe with only useful features
    """ 
    try:
        df = pd.read_csv(filename)
        logger.info("The dataset path %s is loaded and it has %i columns.", filename, df.shape[1])
    except FileNotFoundError:
        logger.error("Cannot find %s", filename)

    # check if all elements in the features list exist in the df
    all_cols = df.columns.values.tolist()
    if all(elem in all_cols for elem in features):
        # save the useful features only
        df_use = df[features]
    else:
        logger.error("Some columns in the columns input is not in the dataset. Check again!")
        raise KeyError("Some columns in the columns input is not in the dataset. Check again!")
   
    logger.info("The shape of the data with useful features only is %s", str(df_use.shape))
    return df_use

def feature_engineering(df: pd.DataFrame,
                        grouping_column: str,
                        grouping_dict: Dict,
                        grouping_new_name: str,
                        trim_column: str,
                        trim_by: int,
                        trim_new_name:str,
                        index_column:str) -> pd.DataFrame:
    """This function will regroup the animal species column using the grouping dictionary
        in the configuration file. Then, the birthday column will be replaced by a month only value.
        Afterwards, the name column is set as the index.

    Args:
        df (pd.DataFrame): output pandas df from load_dataset
        grouping_column (str): the column that needs to be grouped
        grouping_dict (Dict): a dictionary with information of the grouping rules for the grouping column
        grouping_new_name (str): the name of the new column after grouping
        trim_column (str): The column to trim
        trim_by (int): The number to trim the trim_column by
        trim_new_name (str): The name for the new column after trimming
        index_column (str): The new index column 

    Returns:
        pd.DataFrame: a df after feature enginnering
    """
    # check if the pass in value is a pd.dataframe
    if not isinstance(df, pd.DataFrame):
        logger.error("Provided argument `df` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")

    # regroup the animals by species
    for key in grouping_dict.keys():
        lst = grouping_dict.get(key)
        df.loc[df[grouping_column].isin(lst), grouping_new_name] = key

    logger.info("Animals are re-grouped into %i groups (%s).", 
                len(grouping_dict.keys()), 
                str(grouping_dict.keys()))

    # get the last three characters of the birthday column and save it as birthday_month
    df[trim_new_name] = df[trim_column].str[trim_by:]

    logger.info("The %s column was trimmed by %i.", trim_column, trim_by)

    # reset the index
    df.set_index(index_column)
    logger.info("The index column is set to be the %s column", index_column)
    return df

def save_df(df: pd.DataFrame, output_path: str) -> None:
    """This function will save the preprocessed data to the output path location.

    Args:
        df (pd.DataFrame): preprocessed data.
        output_path (str): intented location.
    """
    # check if the readin is a pd.DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error("Provided argument `df` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")

    # save the df to csv
    df.to_csv(output_path, index=False)
    logger.info("The preprocessed data is saved to %s", output_path)
