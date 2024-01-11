import streamlit as st
from pages.data.data_helper import get_data_for_survey_frequency_metrics
from pages.data.helper_functions import add_days_between_column
from pages.data.plot_helper import run_survey_plotting_pipeline
from pages.data.helper_functions import adjusted_start_month, adjusted_end_month
import pandas as pd
from datetime import datetime, timedelta

# create date range and default dates
default_start_month = pd.to_datetime('2022-01-01')
default_end_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
date_range = pd.date_range(default_start_month, default_end_month, freq='MS').strftime('%Y-%m')

# initialise session state for start and end dates
if 'start_month' not in st.session_state or 'end_month' not in st.session_state:
    st.session_state.start_month = date_range[0]
    st.session_state.end_month = date_range[-1]

# sidebar for date selection
st.sidebar.title('Please select dates')
st.sidebar.write('**Data dates back to 2022-01')
start_month = st.sidebar.selectbox('Start Month', date_range[:-1], index=0)
end_month = st.sidebar.selectbox('End Month', date_range[1:], len(date_range[1:]) - 1)
if start_month != st.session_state.start_month:
    st.session_state.start_month = start_month
if end_month != st.session_state.end_month:
    st.session_state.end_month = end_month

if st.session_state.end_month < st.session_state.start_month:
    st.sidebar.error('End date cannot be earlier than start date. Please select again.')
    st.session_state.start_month = default_start_month.strftime('%Y-%m')
    st.session_state.end_month = default_end_month


def main_pipeline_p2():
    orig_survey_df = get_data_for_survey_frequency_metrics()
    survey_df = orig_survey_df[(orig_survey_df['purchase_month'] >= st.session_state.start_month)
                          & (orig_survey_df['purchase_month'] <= st.session_state.end_month)]
    arr_start_month = adjusted_start_month(st.session_state.start_month)
    arr_end_month = adjusted_end_month(st.session_state.end_month)
    arr_survey_df = survey_df[(survey_df['purchase_month'] >= arr_start_month)
                          & (survey_df['purchase_month'] <= arr_end_month)]

    final_dic = run_survey_plotting_pipeline(orig_survey_df, survey_df, arr_survey_df)

    st.header(
        f"""🗓️ Survey Frequency Metrics"""
    )
    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.header("Number of Survey Purchased")

    st.write('Number of makers who purchased a survey:', len(survey_df['maker_id'].value_counts()))
    st.write('Number of accounts that purchased a survey:', len(survey_df['account_id'].value_counts()))

    total_survey = survey_df[['maker_id', 'purchase_month', 'monthly_total_survey']].drop_duplicates()
    st.write('Total number of surveys purchased:', total_survey['monthly_total_survey'].sum())
    st.write("***since", start_month)

    st.markdown("""---""")

    st.write('Number of Accounts:')
    st.write('-that purchased a survey in 2022:',
             len(orig_survey_df[orig_survey_df['purchase_year'] == '2022']['account_id'].value_counts()))
    st.write('-that purchased a survey in 2023:',
             len(orig_survey_df[orig_survey_df['purchase_year'] == '2023']['account_id'].value_counts()))

    st.markdown("""---""")

    fig1 = final_dic["fig1"]
    img1 = final_dic["img1"]

    st.write("The Average Number of Survey Purchased at the Account Level by Month")

    st.pyplot(fig1)

    btn1 = st.download_button(
        label="Download plot of Number of Survey Purchased",
        data=img1,
        file_name=f"fig1_num_survey_purchased.png",
        mime="image/png",
        key="btn1",
    )

    st.markdown("""---""")

    fig2 = final_dic["fig2"]
    img2 = final_dic["img2"]

    st.write(
        f"""Plot of *Average Number of Survey Purchased* per Account across Account ARR."""
    )

    if arr_survey_df.empty:
        st.error('The selected time frame does not contain at least one entire half year period, the ARR plots are done'
                 ' with the default time frame')

    st.pyplot(fig2)

    st.write(
        f"""The percentage of Accounts across ARR brackets is shown in a stacked row here for reference."""
    )

    btn2 = st.download_button(
        label="Download plot of Number pf Survey Purchased by ARR",
        data=img2,
        file_name=f"fig2_num_survey_arr.png",
        mime="image/png",
        key="btn2",
    )

    with st.expander("The percentages of Accounts across ARR brackets:", expanded=True):

        fig4 = final_dic["fig4"]
        img4 = final_dic["img4"]
        st.pyplot(fig4)

        btn4 = st.download_button(
            label="Download plot of Account% by ARR",
            data=img4,
            file_name=f"fig4_acct_by_arr.png",
            mime="image/png",
            key="btn4",
        )

    st.markdown("""---""")

    st.header("Days Between Purchases")

    # Get some numbers of makers
    df_all = add_days_between_column(survey_df)
    df_multiple = df_all.drop(df_all[df_all['days_from_previous'].isna()].index)

    num_single_makers = len(df_all.groupby('maker_id').filter(lambda x: len(x) == 1))
    single_2022 = len(df_all[df_all['purchase_year'] == '2022'].groupby('maker_id').filter(lambda x: len(x) == 1))
    single_2023 = len(df_all[df_all['purchase_year'] == '2023'].groupby('maker_id').filter(lambda x: len(x) == 1))

    num_multiple_makers = len(df_multiple['maker_id'].value_counts())
    multiple_2022 = len(df_multiple[df_multiple['purchase_year'] == '2022']['maker_id'].value_counts())
    multiple_2023 = len(df_multiple[df_multiple['purchase_year'] == '2023']['maker_id'].value_counts())

    st.write('Number of Makers with *single* survey purchases:', num_single_makers)
    st.write('Number of Makers with *multiple* survey purchases:', num_multiple_makers)

    tbl = pd.DataFrame({'Single Purchasers': [single_2022, single_2023],
                        'Multiple Purchasers': [multiple_2022, multiple_2023]},
                       index=['2022', '2023'])
    tbl['Total'] = tbl.sum(axis=1)

    st.write('Number of Makers:')
    st.table(tbl)

    st.write(
        f"""Plot of *Average Days Between Purchases* by account ARR."""
    )
    st.write('***Only the makers who have purchased multiple surveys are included for this metric')

    fig3 = final_dic["fig3"]
    img3 = final_dic["img3"]

    st.pyplot(fig3)

    st.write(
        f"""The percentages of Maker and Account across ARR brackets is shown in stacked rows here for reference."""
    )

    btn3 = st.download_button(
        label="Download Days Between by ARR",
        data=img3,
        file_name=f"fig3_days_between_arr.png",
        mime="image/png",
        key="btn3",
    )

    with st.expander("The percentages of Makers and Accounts across ARR brackets:", expanded=True):

        fig5 = final_dic["fig5"]
        img5 = final_dic["img5"]
        st.pyplot(fig5)

        btn5 = st.download_button(
            label="Download plot of Maker% and Account% by ARR",
            data=img5,
            file_name=f"fig5_maker_and_acct_by_arr.png",
            mime="image/png",
            key="btn5",
        )


main_pipeline_p2()
