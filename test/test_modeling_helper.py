## This is the unit testing file for the create_rec_table function in the modeling_helper module.

## import packages
import pandas as pd
import numpy as np
import pytest

import src.modeling_helper

def test_create_rec_table():
    """happy path for create_rec_table
    """
    # create df_in
    df_in_values = [['a', 2, 2, 2, 1],
                    ['b', 4, 4, 7, 6],
                    ['c', 6, 10, 6, 9]]
    df_in_index = [0, 1, 2]
    df_in_col = ["Name", "col1", "col2", "col3", "col4"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # create cluster_in and drop_list
    cluster_in = np.array([2,2,4])
    drop_list_in = ['col1_villager', 'col2_villager', 'col3_villager', 'col4_villager', 'Cluster']
    # create df_true
    df_true_value = [['a', 'b', 4, 4, 7, 6, 0],
                     ['b', 'a', 2, 2, 2, 1, 1]]
    df_true_col= ["Name_villager", "Name", "col1", "col2", 'col3', "col4", "Unique_id"]
    df_true_index = [1, 2]

    df_true = pd.DataFrame(df_true_value, index=df_true_index, columns=df_true_col)
    df_test = src.modeling_helper.create_rec_table(df_in, cluster_in, drop_list_in)

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_test, check_column_type = False)

def test_create_rec_table_nrow_notmatch():
    """unhappy path for create_rec_table.
       Here, the number of rows are not matched with the length of the cluster array.
    """
    # create df_in
    df_in_values = [['a', 2, 2, 2, 1],
                    ['b', 4, 4, 7, 6],
                    ['c', 6, 10, 6, 9]]
    df_in_index = [0, 1, 2]
    df_in_col = ["Name", "col1", "col2", "col3", "col4"]
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_col)
    # create cluster_in and drop_list
    cluster_in = np.array([2,2])
    drop_list_in = ['col1_villager', 'col2_villager', 'col3_villager', 'col4_villager', 'Cluster']
    with pytest.raises(ValueError):
        src.modeling_helper.create_rec_table(df_in, cluster_in, drop_list_in)
