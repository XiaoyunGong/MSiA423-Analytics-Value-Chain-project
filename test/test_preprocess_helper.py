## This is the unit testing file for all the functions in the preprocess_helper module.

## import packages
import pandas as pd
import pytest

import src.preprocess_helper

def test_grouping():
    """This is the happy path to the grouping function
    """
    # define df_in
    df_in_values = [["g1", 2, 2],
                    ["g2", 4, 4],
                    ["a1", 6, 10],
                    ["a2", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Name", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # define grouping_dict, grouping column, and grouping_new_name
    grouping_dict = {"a":["a1", "a2"], "g": ["g1", "g2"]}
    grouping_column = "Name"
    grouping_new_name = "group_name"
    # define df_true
    df_true_values = [["g1", 2, 2, "g"],
                    ["g2", 4, 4, "g"],
                    ["a1", 6, 10, "a"],
                    ["a2", 6, 10, "a"]]
    df_true_index = [0, 1, 2, 3]
    df_true_col = ["Name", "col1", "col2", "group_name"]
    df_true = pd.DataFrame(df_true_values, index=df_true_index, columns=df_true_col)

    df_test = src.preprocess_helper.grouping(df_in, grouping_dict, grouping_column, grouping_new_name)

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_test, check_column_type = False)

def test_grouping_no_column():
    """This is the unhappy path to the grouping function
    """
    # define df_in
    df_in_values = [["g1", 2, 2],
                    ["g2", 4, 4],
                    ["a1", 6, 10],
                    ["a2", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Name", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # define grouping_dict, grouping column, and grouping_new_name
    grouping_dict = {"a":["a1", "a2"], "g": ["g1", "g2"]}
    grouping_column = "wrong_name"
    grouping_new_name = "group_name"
    with pytest.raises(KeyError):
        src.preprocess_helper.grouping(df_in, grouping_dict, grouping_column, grouping_new_name)

def test_trimming():
    """This is the happy path for the trimming function
    """
    # define df_in
    df_in_values = [["19-Aug", 2, 2],
                    ["20-May", 4, 4],
                    ["21-May", 6, 10],
                    ["09-Apr", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Date", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # define trim column, new column name, and trim by 
    trim_column = "Date"
    trim_new_name = "new_col_name"
    trim_by = -3
    # define df_true
    df_true_values = [["19-Aug", 2, 2, "Aug"],
                    ["20-May", 4, 4, "May"],
                    ["21-May", 6, 10, "May"],
                    ["09-Apr", 6, 10, "Apr"]]
    df_true_index = [0, 1, 2, 3]
    df_true_col = ["Date", "col1", "col2", "new_col_name"]
    df_true = pd.DataFrame(df_true_values, index=df_true_index, columns=df_true_col)

    df_test = src.preprocess_helper.trimming(df_in, trim_column, trim_by, trim_new_name)

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_test)

def test_trimming_no_col():
    """This is the unhappy path for the trimming function
    """
    # define df_in
    df_in_values = [["19-Aug", 2, 2],
                    ["20-May", 4, 4],
                    ["21-May", 6, 10],
                    ["09-Apr", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Date", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # define trim column, new column name, and trim by 
    trim_column = "wrong_col"
    trim_new_name = "new_col_name"
    trim_by = -3
    with pytest.raises(KeyError):
        src.preprocess_helper.trimming(df_in, trim_column, trim_by, trim_new_name)
