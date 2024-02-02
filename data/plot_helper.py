import io
import seaborn as sns
from matplotlib import pyplot as plt
from data.helper_functions import get_ordered_half_years, add_days_between_column
from pandas import DataFrame


# Interactions
def plot_active_makers(df: DataFrame):
    """
    :param df: the interaction df
    :return: a stacked bar plot for number of Active Makers/ Active Results Makers
    """
    # filter and get aggregated data
    active_makers = df[
        (df['total_engaged_time_in_m'] >= 5) & (df['num_unique_interactions'] >= 5)]
    agg_active_makers = active_makers.groupby('engaged_month').agg(
        generic_makers=('generic_active_maker', 'sum'),
        results_makers=('results_active_maker', 'sum')
    ).reset_index()
    agg_active_makers['non_results_makers'] = agg_active_makers['generic_makers'] - agg_active_makers['results_makers']

    # plot
    fig = plt.figure(figsize=(10, 8))
    ax1 = sns.barplot(x='engaged_month', y='generic_makers', data=agg_active_makers, color='skyblue',
                      label='Non-Results Makers')
    ax2 = sns.barplot(x='engaged_month', y='results_makers', data=agg_active_makers, color='coral',
                      label='Results Makers')

    plt.title('Number of Active Makers per Month')
    plt.ylabel('Number of Makers')
    plt.xlabel('Month')

    # This chunk is add tho adjust to the older version of seaborn
    month_cate = agg_active_makers['engaged_month'].unique()
    month_indices = {month: index for index, month in enumerate(month_cate)}

    for month, y in zip(agg_active_makers['engaged_month'], agg_active_makers['generic_makers']):
        x = month_indices[month]
        plt.text(x, y, f'{int(y)}', color='black', ha='center', va='bottom')
    for month, y in zip(agg_active_makers['engaged_month'], agg_active_makers['results_makers']):
        x = month_indices[month]
        plt.text(x, y - 125, f'{int(y)}', color='white', ha='center', va='bottom')
    for month, y in zip(agg_active_makers['engaged_month'], agg_active_makers['non_results_makers']):
        x = month_indices[month]
        plt.text(x, y + 140, f'{int(y)}', color='white', ha='center', va='bottom')

    plt.xticks(rotation=45)
    plt.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_engaged_time(df: DataFrame):
    """
    :param df: the interaction df
    :return: a line plot for the Average Engaged Time per Maker per Month
    """
    avg_engage_m = df.groupby(['engaged_month'])['total_engaged_time_in_m'].mean().round().reset_index()

    fig = plt.figure(figsize=(10, 4))
    ax = sns.lineplot(data=avg_engage_m, x='engaged_month', y='total_engaged_time_in_m', marker='o')

    plt.fill_between(avg_engage_m['engaged_month'], avg_engage_m['total_engaged_time_in_m'], color='steelblue',
                     alpha=0.4)

    for x, y in zip(avg_engage_m['engaged_month'], avg_engage_m['total_engaged_time_in_m']):
        if y >= 6:
            plt.text(x, y-6, f'{int(y)}', color='black', ha='center', va='top')
        else:
            plt.text(x, y, f'{int(y)}', color='black', ha='center', va='top')

    plt.title('Average Engagement Time (in minutes) per Month - Maker level')
    plt.ylabel('Average Engagement Time (m)')
    plt.xlabel('Month')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_arr_engaged_time(df: DataFrame):
    """
    :param df: the interaction df
    :return: a bar plot for Average Engaged Time across ARR brackets, with a stacked row chart showing the proportion
    of makers by ARR.
    """
    # get a sorted list of half year periods
    ordered_half_years = get_ordered_half_years(df)

    # prepare aggregated data for bar plot
    avg_engage_arr = df.groupby(['account_arr_binned', 'half_year_period']).agg(
        avg_engaged_time_in_m=('total_engaged_time_in_m', lambda x: round(x.mean())),
        number_of_makers=('maker_id', 'nunique')
    ).reset_index()

    fig = plt.figure(figsize=(10, 6))

    ax = sns.barplot(data=avg_engage_arr, x='half_year_period', y='avg_engaged_time_in_m', hue='account_arr_binned',
                     palette='Set2', order=ordered_half_years)
    plt.title('Average Engagement Time (in minutes) by ARR - Maker level')
    plt.ylabel('Average Engagement Time (m)')
    plt.xlabel('Six-month Period')

    for m in range(len(avg_engage_arr['account_arr_binned'].value_counts())):
        ax.bar_label(ax.containers[m])

    ax.legend(title='ARR')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_days_engaged(df: DataFrame):
    """
    :param df: the interaction df
    :return: a line plot for Average Number of Days Engaged
    """

    avg_days_engaged = df.groupby(['engaged_month'])['engaged_days'].mean().round(2).reset_index()

    fig = plt.figure(figsize=(10, 4))
    ax = sns.lineplot(data=avg_days_engaged, x='engaged_month', y='engaged_days', marker='o')

    plt.fill_between(avg_days_engaged['engaged_month'], avg_days_engaged['engaged_days'], color='steelblue', alpha=0.4)

    for x, y in zip(avg_days_engaged['engaged_month'], avg_days_engaged['engaged_days']):
        plt.text(x, y - 0.5, f'{y:.2f}', color='black', ha='center', va='top')

    plt.title('Average Number of Days per Month a Maker Visits the Platform - Maker level')
    plt.ylabel('Number of Days')
    plt.xlabel('Month')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_arr_days_engaged(df: DataFrame):
    """
    :param df: the interaction df
    :return: a bar plot for Number of Days Engaged across ARR brackets, with a stacked row chart showing the proportion
    of makers by ARR.
    """
    # get a sorted list of half year periods
    ordered_half_years = get_ordered_half_years(df)

    # prepare aggregated data for bar plot
    avg_days_arr = df.groupby(['account_arr_binned', 'half_year_period'])['engaged_days'].mean().round(
        2).reset_index()

    # bar plot
    fig = plt.figure(figsize=(10, 6))

    ax = sns.barplot(data=avg_days_arr, x='half_year_period', y='engaged_days', hue='account_arr_binned',
                     palette='Set2',
                     order=ordered_half_years)
    ax.set_title('Average Number of Days Visited by ARR - Maker level')
    ax.set_xlabel('Six-month Period')
    ax.set_ylabel('Average Number of Days')

    for m in range(len(avg_days_arr['account_arr_binned'].value_counts())):
        ax.bar_label(ax.containers[m])

    ax.legend(title="Account ARR", loc='lower right')

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_arr_days_between(df: DataFrame):
    """
     :param df: the survey df
     :return: a bar plot for Average Days Between Purchased across ARR brackets, with a stacked row chart showing the
     proportion of makers by ARR, and a stacked row chart showing the proportion of accounts by ARR
     """
    df_days = add_days_between_column(df)
    # Only including multiple purchasers for this metric
    df_days = df_days.drop(df_days[df_days['days_from_previous'].isna()].index)

    avg_between = df_days.groupby(['purchase_year', 'account_arr_binned'])['days_from_previous'].mean().round(
        1).reset_index()

    fig = plt.figure(figsize=(8, 5))

    # bar plot
    ax = sns.barplot(data=avg_between, x='purchase_year', y='days_from_previous', hue='account_arr_binned',
                     palette='Set2', order=['2022', '2023'])
    ax.set_title('Average Days Between Survey Purchasing by ARR - Maker level')
    ax.set_xlabel('Year')
    ax.set_ylabel('Days Between Survey Purchasing')

    for m in range(len(avg_between['account_arr_binned'].value_counts())):
        ax.bar_label(ax.containers[m])

    ax.legend(title="Account ARR", loc='lower right')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_maker_and_acct_by_arr_year(df: DataFrame):
    fig, ax = plt.subplots(2, 1, figsize=(10, 4), gridspec_kw={'height_ratios': [1, 1]})

    # stacked row chart for makers proportion
    makers_arr_year = df.groupby(['purchase_year', 'account_arr_binned']).agg(
        number_of_makers=('maker_id', 'nunique'))
    makers_arr_tab = makers_arr_year.groupby(['purchase_year', 'account_arr_binned']).sum().unstack(fill_value=0)
    makers_arr_tab = makers_arr_tab.div(makers_arr_tab.sum(axis=1), axis=0) * 100
    makers_arr_tab.index = makers_arr_tab.index.astype('str')

    previous_width = [0] * len(makers_arr_tab.index)
    labels = ['<50k', '50-100k', '100k+']
    assert len(labels) == makers_arr_tab.shape[1], "Labels list must match the number of columns"

    palette = sns.color_palette("Set2", n_colors=makers_arr_tab.shape[1])

    for idx, (cols, col_data) in enumerate(makers_arr_tab.items()):
        ax[0].barh(makers_arr_tab.index, col_data, color=palette[idx], left=previous_width, label=labels[idx])
        for i, (bin, value) in enumerate(col_data.items()):
            ax[0].text(previous_width[i] + value / 2, i, f"{value:.1f}%", va='center', ha='center', color='white',
                       fontsize=10)
            previous_width[i] += value

    ax[0].set_xlim(0, 100)
    ax[0].set_xticks([])
    ax[0].set_title('% of Makers by ARR')

    # stacked row chart for accounts proportion
    accts_arr_year = df.groupby(['purchase_year', 'account_arr_binned']).agg(
        number_of_accounts=('account_id', 'nunique'))
    accts_arr_tab = accts_arr_year.groupby(['purchase_year', 'account_arr_binned']).sum().unstack(fill_value=0)
    accts_arr_tab = accts_arr_tab.div(accts_arr_tab.sum(axis=1), axis=0) * 100
    accts_arr_tab.index = accts_arr_tab.index.astype('str')

    previous_width = [0] * len(accts_arr_tab.index)
    assert len(labels) == accts_arr_tab.shape[1], "Labels list must match the number of columns"

    palette = sns.color_palette("Set2", n_colors=accts_arr_tab.shape[1])

    for idx, (cols, col_data) in enumerate(accts_arr_tab.items()):
        ax[1].barh(accts_arr_tab.index, col_data, color=palette[idx], left=previous_width, label=labels[idx])
        for i, (bin, value) in enumerate(col_data.items()):
            ax[1].text(previous_width[i] + value / 2, i, f"{value:.1f}%", va='center', ha='center', color='white',
                       fontsize=10)
            previous_width[i] += value

    ax[1].set_xlim(0, 100)
    ax[1].set_xticks([])
    ax[1].set_title('% of Accounts by ARR')
    ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def run_interaction_plotting_pipeline(df: DataFrame, arr_df: DataFrame, account_df: DataFrame):
    """
    This pipeline function runs all the functions necessary to get the interaction metrics plots.

    Args:
        df (DataFrame): interaction_df, the input dataframe for active makers and engagement metrics.
        arr_df (DataFrame): arr_interaction_df, the input dataframe for arr plots, which only include entire half years.
        account_df:
    Returns:
        A dictionary of all the figure object (fig) to be plotted and a buffer (buf_read)
        which is used for downloading the figures.
    """

    # If the selected time frame does not contain at least one entire half year period, the ARR plots are done with the
    # default time frame
    if arr_df.empty:
        arr_df = df
    else:
        arr_df = arr_df

    # interaction metrics
    fig1, img1 = plot_active_makers(df)
    fig2, img2 = plot_engaged_time(account_df)
    fig3, img3 = plot_arr_engaged_time(arr_df)
    fig4, img4 = plot_days_engaged(account_df)
    fig5, img5 = plot_arr_days_engaged(arr_df)

    final_dic = dict(
        {
            "fig1": fig1,
            "img1": img1,
            "fig2": fig2,
            "img2": img2,
            "fig3": fig3,
            "img3": img3,
            "fig4": fig4,
            "img4": img4,
            "fig5": fig5,
            "img5": img5
        }
    )

    return final_dic


def run_survey_plotting_pipeline(orig_df: DataFrame, df: DataFrame):
    """
    This pipeline function runs all the functions necessary to get all the plots.

    Args:
        df (DataFrame): survey_df, the input dataframe for survey frequency metrics.
        orig_df:
    Returns:
        A dictionary of all the figure object (fig) to be plotted and a buffer (buf_read)
        which is used for downloading the figures.
    """

    # survey freq metrics
    fig6, img6 = plot_arr_days_between(orig_df)
    fig7, img7 = plot_maker_and_acct_by_arr_year(df)

    final_dic = dict(
        {
            "fig6": fig6,
            "img6": img6,
            "fig7": fig7,
            "img7": img7
        }
    )

    return final_dic
