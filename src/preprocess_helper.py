"""
This module includes functions called in the preprocess module.
"""

from typing import Dict
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def grouping(df:pd.DataFrame,
            grouping_dict: Dict,
            grouping_column: str,
            grouping_new_name: str) -> pd.DataFrame:
    """regroup entries in a given column

    Args:
        df (pd.DataFrame): the orginal dataframe
        grouping_dict (Dict): The dictionary with the grouping key and value
        grouping_column (str): the column that will be regrouped
        grouping_new_name (str): the column name of the new column (after regroup)

    Raises:
        KeyError: if grouping_column doesn't exist in the df.

    Returns:
        pd.DataFrame: the dataframe with the new column.
    """

    all_cols = df.columns.values.tolist()
    if grouping_column not in all_cols:
        logger.error("Can not find the column that user want to regroup.")
        raise KeyError("grouping_column is not in the dataset. Check again!")
    for key in grouping_dict.keys():
        lst = grouping_dict.get(key)
        df.loc[df[grouping_column].isin(lst), grouping_new_name] = key

    return df

def trimming(df:pd.DataFrame,
            trim_column: str,
            trim_by: int,
            trim_new_name: str) -> pd.DataFrame:
    """trim a column by certain length.

    Args:
        df (pd.DataFrame): the orginal dataframe
        trim_column (str): the column to trim
        trim_by (int): the number to trim
        trim_new_name (str): the name of the trimmed column

    Raises:
        KeyError: if the trim_column doesn't exist in the dataframe
        TypeError: if the trim_by value is not integer

    Returns:
        pd.DataFrame: new df with one column trimmed.
    """

    all_cols = df.columns.values.tolist()
    if trim_column not in all_cols:
        logger.error("Can not find the column that user want to trim.")
        raise KeyError("trim_column is not in the dataset. Check again!")
    if not isinstance(trim_by, int):
        logger.error("Provided argument `trim_by` is not an Integer.")
        raise TypeError("trim_by is not an interger.")
    df[trim_new_name] = df[trim_column].str[trim_by:]

    return df
