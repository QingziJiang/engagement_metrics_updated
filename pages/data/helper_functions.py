import pandas as pd
from pandas import DataFrame
import numpy as np


# helper functions
def get_binned_arr(df: DataFrame):
    """
    Get the account_ARR_binned column for visualisations for metrics across ARR brackets.
    The ARR brackets are ['<0k', '50-100k', '100k+']

    :param df: the input dataframe.
    :return: the column of account ARR discretized into the above brackets.
    """

    bins = [-float('inf'), 50000, 100000, float('inf')]
    labels = ['<50k', '50-100k', '100k+']
    binned_arr = pd.cut(df['total_account_arr'], bins=bins, labels=labels, include_lowest=True)

    return binned_arr


def half_year(date):
    """
    A helper function to get the corresponding half year period for dates.
    """
    # Slice year
    year = date[:4]
    # Slice month
    half = 'H1' if int(date[5:7]) <= 6 else 'H2'

    return f'{half} {year}'


def get_ordered_half_years(df: DataFrame):
    """
    A helper function to get an ordered list of all the unique half year periods that appeared in the df.
    To be used for the order input in barplots.
    :param df: df
    :return: lst or ordered half year periods
    """
    lst_ordered_half_years = df['half_year_period'].value_counts().index.tolist()
    lst_ordered_half_years = sorted(lst_ordered_half_years, key=lambda x: (int(x.split()[1]), x.split()[0]))

    return lst_ordered_half_years


def add_days_between_column(df: DataFrame):
    """
    :param df: the survey df
    :return: the survey df with an added column of days between surveys
    """
    df_days = df.sort_values(by=['maker_id', 'account_id', 'purchase_day'])
    df_days['previous_date'] = df_days.groupby(['account_id', 'maker_id'])['purchase_day'].shift(1)

    # Calculate days_from previous within each year
    df_days['days_from_previous'] = np.where(df_days['purchase_day'].dt.year == df_days['previous_date'].dt.year,
                                             (df_days['purchase_day'] - df_days['previous_date']).dt.days,
                                             np.nan)

    # Drop temporary column
    df_days.drop(['previous_date'], axis=1, inplace=True)
    # DID NOT DROP MAKERS WITH SINGLE PURCHASES HERE.

    return df_days


def adjusted_start_month(month):
    year = int(month[:4])
    month_num = int(month[5:])
    if month_num == 1:
        return f"{year}-01"
    elif month_num <= 7:
        return f"{year}-07"
    else:
        return f"{year+1}-01"


def adjusted_end_month(month):
    year = int(month[:4])
    month_num = int(month[5:])
    if month_num == 12:
        return f"{year}-12"
    if month_num >= 6:
        return f"{year}-06"
    else:
        return f"{year-1}-12"
