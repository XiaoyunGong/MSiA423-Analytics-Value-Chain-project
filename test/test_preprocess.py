## This is the unit testing file for the drop_col function in the preprocess module.

## import packages
import pandas as pd
import pytest

import src.preprocess

def test_drop_cols():
    """happy path for the drop_cols function
    """
    # define df_in
    df_in_values = [["g1", 2, 2],
                    ["g2", 4, 4],
                    ["a1", 6, 10],
                    ["a2", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Name", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)

    features = ["Name", "col1"]

    # define df_true
    df_true_values = [["g1", 2],
                    ["g2", 4],
                    ["a1", 6],
                    ["a2", 6,]]
    df_true_index = [0, 1, 2, 3]
    df_true_col = ["Name", "col1"]
    df_true = pd.DataFrame(df_true_values, index=df_true_index, columns=df_true_col)

    df_test = src.preprocess.drop_cols(df_in, features)

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_test, check_column_type = False)

def test_drop_cols_no_col():
    """unhappy path for the drop_cols function
    """
    # define df_in
    df_in_values = [["g1", 2, 2],
                    ["g2", 4, 4],
                    ["a1", 6, 10],
                    ["a2", 6, 10]]
    df_in_index = [0, 1, 2, 3]
    df_in_col = ["Name", "col1", "col2"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)

    features = ["Name", "wrongcol"]

    with pytest.raises(KeyError):
        src.preprocess.drop_cols(df_in, features)
