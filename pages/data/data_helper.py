import streamlit as st
import pandas as pd
from kyber_dwh import DataWarehouse
from pages.data.queries import interaction_query, survey_query
from pages.data.helper_functions import get_binned_arr, half_year

st.cache(allow_output_mutation=True)


def get_dwh():
    return DataWarehouse(use_realtime_prod_data=True)


@st.cache_resource  # This prevents from reloading the data needlessly
def get_data_for_interaction_metrics():
    st.write("LOADING DATA")
    print("LOADING DATA")
    dwh = get_dwh()
    query = interaction_query
    df = dwh.read_sql_query(query)

    # Add binned arr
    df['account_arr_binned'] = get_binned_arr(df)
    # Add half year periods
    df['half_year_period'] = df['engaged_month'].apply(half_year)
    return df


@st.cache_resource  # This prevents from reloading the data needlessly
def get_data_for_survey_frequency_metrics():
    dwh = get_dwh()
    query = survey_query
    df = dwh.read_sql_query(query)

    # Handle dates
    df['purchase_day'] = pd.to_datetime(df['purchase_day'])
    # Add binned arr
    df['account_arr_binned'] = get_binned_arr(df)
    # Add half year periods
    df['half_year_period'] = df['purchase_month'].apply(half_year)

    return df
