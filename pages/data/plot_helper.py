import io
import seaborn as sns
from matplotlib import pyplot as plt
from pages.data.helper_functions import get_ordered_half_years, add_days_between_column
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

    #  plot
    fig = plt.figure(figsize=(10, 8))
    ax1 = sns.barplot(x='engaged_month', y='generic_makers', data=agg_active_makers, color='skyblue',
                      label='Non-Results Makers')
    ax2 = sns.barplot(x='engaged_month', y='results_makers', data=agg_active_makers, color='coral',
                      label='Results Makers')

    plt.title('Number of Active Makers per Month')
    plt.ylabel('Number of Makers')
    plt.xlabel('Month')

    for x, y in zip(agg_active_makers['engaged_month'], agg_active_makers['generic_makers']):
        plt.text(x, y, f'{int(y)}', color='black', ha='center', va='bottom')
    for x, y in zip(agg_active_makers['engaged_month'], agg_active_makers['results_makers']):
        plt.text(x, y - 120, f'{int(y)}', color='white', ha='center', va='bottom')
    for x, y in zip(agg_active_makers['engaged_month'], agg_active_makers['non_results_makers']):
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
        plt.text(x, y - 4, f'{int(y)}', color='black', ha='center', va='top')

    plt.title('Average Engagement Time per Maker per Month')
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

    # prepare aggregated data for stacked row chart
    num_makers_arr = df.groupby(['account_arr_binned']).agg(
        number_of_makers=('maker_id', 'nunique')).reset_index()

    fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [8, 1]})

    # bar plot
    sns.barplot(data=avg_engage_arr, x='half_year_period', y='avg_engaged_time_in_m', hue='account_arr_binned',
                palette='Set2', order=ordered_half_years, ax=ax[0])
    ax[0].set_title('Average Engagement Time by Account ARR')
    ax[0].set_xlabel('Six-month Period')
    ax[0].set_ylabel('Average Engagement Time (m)')

    for m in range(len(avg_engage_arr['account_arr_binned'].value_counts())):
        ax[0].bar_label(ax[0].containers[m])

    ax[0].legend(title="Account ARR")

    # stacked row chart
    num_makers = num_makers_arr['number_of_makers']
    total = sum(num_makers)

    palette = sns.color_palette("Set2", n_colors=len(num_makers_arr['account_arr_binned']))

    ax[1].barh(y=0, width=num_makers[0], left=0, color=palette[0], label='<50k')
    ax[1].barh(y=0, width=num_makers[1], left=num_makers[0], color=palette[1], label='50-100k')
    ax[1].barh(y=0, width=num_makers[2], left=num_makers[0] + num_makers[1], color=palette[2], label='100k+')

    ax[1].text(x=num_makers[0] / 2, y=0, s=f"{num_makers[0] / total * 100:.1f}%", va='center', ha='center',
               color='white')
    ax[1].text(x=num_makers[0] + num_makers[1] / 2, y=0, s=f"{num_makers[1] / total * 100:.1f}%", va='center',
               ha='center', color='white')
    ax[1].text(x=num_makers[0] + num_makers[1] + num_makers[2] / 2, y=0, s=f"{num_makers[2] / total * 100:.1f}%",
               va='center', ha='center', color='white')

    ax[1].set_yticks([])
    ax[1].grid(False)
    for spine in ax[1].spines.values():
        spine.set_visible(False)
    ax[1].set_title('Proportion of Makers by Account ARR')

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

    plt.title('Average Number of Days per Month a Maker Visits the Platform')
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

    # prepare aggregated data for stacked row chart
    num_makers_arr = df.groupby(['account_arr_binned']).agg(
        number_of_makers=('maker_id', 'nunique')).reset_index()

    # bar plot
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [4, 1]})

    sns.barplot(data=avg_days_arr, x='half_year_period', y='engaged_days', hue='account_arr_binned', palette='Set2',
                order=ordered_half_years, ax=ax[0])
    ax[0].set_title('Average Number of Days Visited by Account ARR')
    ax[0].set_xlabel('Six-month Period')
    ax[0].set_ylabel('Average Number of Days')

    for m in range(len(avg_days_arr['account_arr_binned'].value_counts())):
        ax[0].bar_label(ax[0].containers[m])

    ax[0].legend(title="Account ARR", loc='lower right')

    # stacked row chart
    num_makers = num_makers_arr['number_of_makers']
    total = sum(num_makers)

    palette = sns.color_palette("Set2", n_colors=len(num_makers_arr['account_arr_binned']))

    ax[1].barh(y=0, width=num_makers[0], left=0, color=palette[0], label='<50k')
    ax[1].barh(y=0, width=num_makers[1], left=num_makers[0], color=palette[1], label='50-100k')
    ax[1].barh(y=0, width=num_makers[2], left=num_makers[0] + num_makers[1], color=palette[2], label='100k+')

    ax[1].text(x=num_makers[0] / 2, y=0, s=f"{num_makers[0] / total * 100:.1f}%", va='center', ha='center',
               color='white')
    ax[1].text(x=num_makers[0] + num_makers[1] / 2, y=0, s=f"{num_makers[1] / total * 100:.1f}%", va='center',
               ha='center', color='white')
    ax[1].text(x=num_makers[0] + num_makers[1] + num_makers[2] / 2, y=0, s=f"{num_makers[2] / total * 100:.1f}%",
               va='center', ha='center', color='white')

    ax[1].set_yticks([])
    ax[1].grid(False)
    for spine in ax[1].spines.values():
        spine.set_visible(False)
    ax[1].set_title('Proportion of Makers by Account ARR')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


# Survey purchase frequencies
def plot_num_survey(df: DataFrame):
    """
    :param df: the survey
    :return: a line plot of Average Number of Survey purchased
    """
    survey_freq_acct = df.drop(['maker_id', 'purchase_day'], axis=1).drop_duplicates()
    avg_survey_acct = survey_freq_acct.groupby(['purchase_month'])['monthly_total_survey'].mean().round(2).reset_index()

    fig = plt.figure(figsize=(14, 4))
    ax = sns.lineplot(data=avg_survey_acct, x='purchase_month', y='monthly_total_survey', marker='o')

    plt.fill_between(avg_survey_acct['purchase_month'], avg_survey_acct['monthly_total_survey'], color='steelblue',
                     alpha=0.4)

    for x, y in zip(avg_survey_acct['purchase_month'], avg_survey_acct['monthly_total_survey']):
        plt.text(x, y - 0.4, f'{y:.2f}', color='black', ha='center', va='top')

    plt.title('Average Number of Survey Purchased per Account per Month')
    plt.ylabel('Number of Survey')
    plt.xlabel('Month')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def plot_arr_num_survey(df: DataFrame):
    """
    :param df: the survey df
    :return: a bar plot for Number of Survey Purchased across ARR brackets, with a stacked row chart showing the
    proportion of accounts by ARR.
    """
    # get a sorted list of half year periods
    ordered_half_years = get_ordered_half_years(df)

    # prepare aggregated data for bar plot
    survey_freq_acct = df.drop(['maker_id', 'purchase_day'], axis=1).drop_duplicates()
    survey_freq_arr = survey_freq_acct.groupby(['account_arr_binned', 'half_year_period'])[
        'monthly_total_survey'].mean().round(2).reset_index()

    # prepare aggregated data for stacked row chart
    num_accts_arr = survey_freq_acct.groupby(['account_arr_binned']).agg(
        number_of_accts=('account_id', 'nunique')).reset_index()

    # bar plot
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [6, 1]})

    sns.barplot(data=survey_freq_arr, x='half_year_period', y='monthly_total_survey', hue='account_arr_binned',
                palette='Set2', order=ordered_half_years, ax=ax[0])
    ax[0].set_title('Average Number of Survey Purchased by Account ARR')
    ax[0].set_xlabel('Six-month Period')
    ax[0].set_ylabel('Number of Survey')

    for m in range(len(survey_freq_arr['account_arr_binned'].value_counts())):
        ax[0].bar_label(ax[0].containers[m])

    ax[0].legend(title="Account ARR", loc='lower right')

    # stacked row
    num_accts = num_accts_arr['number_of_accts']
    total = sum(num_accts)

    palette = sns.color_palette("Set2", n_colors=len(num_accts_arr['account_arr_binned']))

    ax[1].barh(y=0, width=num_accts[0], left=0, color=palette[0], label='<50k')
    ax[1].barh(y=0, width=num_accts[1], left=num_accts[0], color=palette[1], label='50-100k')
    ax[1].barh(y=0, width=num_accts[2], left=num_accts[0] + num_accts[1], color=palette[2], label='100k+')

    ax[1].text(x=num_accts[0] / 2, y=0, s=f"{num_accts[0] / total * 100:.1f}%", va='center', ha='center', color='white')
    ax[1].text(x=num_accts[0] + num_accts[1] / 2, y=0, s=f"{num_accts[1] / total * 100:.1f}%", va='center', ha='center',
               color='white')
    ax[1].text(x=num_accts[0] + num_accts[1] + num_accts[2] / 2, y=0, s=f"{num_accts[2] / total * 100:.1f}%",
               va='center', ha='center', color='white')

    ax[1].set_yticks([])
    ax[1].grid(False)
    for spine in ax[1].spines.values():
        spine.set_visible(False)
    ax[1].set_title('Proportion of Accounts by Account ARR')

    plt.tight_layout()

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

    fig, ax = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [4, 1, 1]})

    # bar plot
    sns.barplot(data=avg_between, x='purchase_year', y='days_from_previous', hue='account_arr_binned', palette='Set2',
                order=['2022', '2023'], ax=ax[0])
    ax[0].set_title('Average Days Between Survey Purchasing by Account ARR')
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Days Between Survey Purchasing')

    for m in range(len(avg_between['account_arr_binned'].value_counts())):
        ax[0].bar_label(ax[0].containers[m])

    ax[0].legend(title="Account ARR", loc='lower right')

    # stacked row chart for makers proportion
    makers_arr_year = df_days.groupby(['purchase_year', 'account_arr_binned']).agg(
        number_of_makers=('maker_id', 'nunique'))
    makers_arr_tab = makers_arr_year.groupby(['purchase_year', 'account_arr_binned']).sum().unstack(fill_value=0)
    makers_arr_tab = makers_arr_tab.div(makers_arr_tab.sum(axis=1), axis=0) * 100
    makers_arr_tab.index = makers_arr_tab.index.astype('str')

    labels = ['<50k', '50-100k', '100k+']
    palette = sns.color_palette("Set2", n_colors=len(labels))

    previous_width = [0, 0]
    for idx, (cols, col_data) in enumerate(makers_arr_tab.items()):
        ax[1].barh(makers_arr_tab.index, col_data, color=palette[idx], left=previous_width, label=labels[idx])
        previous_width += col_data
    for i, (year, row) in enumerate(makers_arr_tab.iterrows()):
        cumulative_width = 0
        for j, (col, val) in enumerate(row.items()):
            ax[1].text(x=cumulative_width + val / 2, y=year, s=f"{val:.1f}%", va='center', ha='center', color='white',
                       fontsize=10)
            cumulative_width += val

    ax[1].set_xlim(0, 100)
    ax[1].set_xticks([])

    ax[1].set_title('Proportion of Makers by Account ARR')

    # stacked row chart for accounts proportion
    accts_arr_year = df_days.groupby(['purchase_year', 'account_arr_binned']).agg(
        number_of_accounts=('account_id', 'nunique'))
    accts_arr_tab = accts_arr_year.groupby(['purchase_year', 'account_arr_binned']).sum().unstack(fill_value=0)
    accts_arr_tab = accts_arr_tab.div(accts_arr_tab.sum(axis=1), axis=0) * 100
    accts_arr_tab.index = accts_arr_tab.index.astype('str')

    previous_width = [0, 0]
    labels = ['<50k', '50-100k', '100k+']
    palette = sns.color_palette("Set2", n_colors=len(labels))

    for idx, (cols, col_data) in enumerate(accts_arr_tab.items()):
        ax[2].barh(accts_arr_tab.index, col_data, color=palette[idx], left=previous_width, label=labels[idx])
        previous_width += col_data
    for i, (year, row) in enumerate(accts_arr_tab.iterrows()):
        cumulative_width = 0
        for j, (col, val) in enumerate(row.items()):
            ax[2].text(x=cumulative_width + val / 2, y=year, s=f"{val:.1f}%", va='center', ha='center', color='white',
                       fontsize=10)
            cumulative_width += val

    ax[2].set_xlim(0, 100)
    ax[2].set_xticks([])
    ax[2].set_title('Proportion of Accounts by Account ARR')

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    buf_read = buf.read()
    plt.close()

    return fig, buf_read


def run_interaction_plotting_pipeline(df: DataFrame, arr_df: DataFrame):
    """
    This pipeline function runs all the functions necessary to get the interaction metrics plots.

    Args:
        df (DataFrame): interaction_df, the input dataframe for active makers and engagement metrics.
        arr_df (DataFrame): arr_interaction_df, the input dataframe for arr plots, which only include entire half years.
    Returns:
        A dictionary of all the figure object (fig) to be plotted and a buffer (buf_read)
        which is used for downloading the figures.
    """

    # sorted_date = df[LAUNCH_MONTH_COL_NAME].sort_values().unique()

    # surveys_df, size_df = prep_dataframe_for_plotting(df, cur_col)

    # If the selected time frame does not contain at least one entire half year period, the ARR plots are done with the
    # default time frame
    if arr_df.empty:
        arr_df = df
    else:
        arr_df = arr_df

    # interaction metrics
    fig1, img1 = plot_active_makers(df)
    fig2, img2 = plot_engaged_time(df)
    fig3, img3 = plot_arr_engaged_time(arr_df)
    fig4, img4 = plot_days_engaged(df)
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


def run_survey_plotting_pipeline(orig_df: DataFrame, df: DataFrame, arr_df: DataFrame):
    """
    This pipeline function runs all the functions necessary to get all the plots.

    Args:
        df (DataFrame): survey_df, the input dataframe for survey frequency metrics.
        arr_df (DataFrame): arr_survey_df, the input dataframe for arr plots, which only include entire half years.
        orig_df:
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

    # survey freq metrics
    fig1, img1 = plot_num_survey(df)
    fig2, img2 = plot_arr_num_survey(arr_df)
    fig3, img3 = plot_arr_days_between(orig_df)

    final_dic = dict(
        {
            "fig1": fig1,
            "img1": img1,
            "fig2": fig2,
            "img2": img2,
            "fig3": fig3,
            "img3": img3
        }
    )

    return final_dic
