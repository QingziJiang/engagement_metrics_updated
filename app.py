import streamlit as st
from data.data_helper import get_data_for_interaction_metrics, get_data_for_survey_frequency_metrics
from data.plot_helper import run_interaction_plotting_pipeline, run_survey_plotting_pipeline
from data.helper_functions import adjusted_start_month, adjusted_end_month, add_days_between_column
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Product Engagement Metric",
    page_icon="🧲",
    initial_sidebar_state="expanded",
)

st.write("# Welcome to Attest Product Engagement Metric Page ")

st.markdown("""    
Measuring user engagement on our platform is essential for understanding how effectively our product is meeting 
user needs.

All charts are downloadable! 🤗
"""
            )

with st.expander("Outline", expanded=True):

    st.markdown("""    
    - **Platform Engagement**: 
        - Engaged Time
        - Number of Days Engaged
    - **Number of Active Makers**
    - **Survey Frequencies** 
        - Number of Days Between Purchases
        """
                )

st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

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


def main_pipeline():
    interaction_df = get_data_for_interaction_metrics()
    interaction_df = interaction_df[(interaction_df['engaged_month'] >= st.session_state.start_month)
                                    & (interaction_df['engaged_month'] <= st.session_state.end_month)]
    arr_start_month = adjusted_start_month(st.session_state.start_month)
    arr_end_month = adjusted_end_month(st.session_state.end_month)
    arr_interaction_df = interaction_df[(interaction_df['engaged_month'] >= arr_start_month)
                                        & (interaction_df['engaged_month'] <= arr_end_month)]

    st.header(
        f"""💫 Platform Engagement""")
    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.header("""Engagement Time""")

    st.write(
        f"""Plot of *Average Engagement Time* per Maker by Month."""
    )

    with st.expander("Definition of Engagement"):
        st.markdown("""   
    Duration of ALL generic interactions is included in the ***engagement time.***
    """)
        st.markdown("""(All makers who have had an active subscription (since 2022-01-01) are included for this metric 
                    for the duration while their subscription was active.)""")

    # initialize session state variables if they don't exist
    if 'selected_account_name' not in st.session_state:
        st.session_state['selected_account_name'] = ''
    if 'clear_selection_triggered' not in st.session_state:
        st.session_state['clear_selection_triggered'] = False

    # define the list of options for the selectbox, including a default placeholder
    options = ['Select an account'] + sorted(interaction_df['account_name'].unique())

    # define a callback function to update the session state based on selection
    def on_account_selected():
        # updates the session state with the selected account name
        st.session_state['selected_account_name'] = st.session_state['account_name_temp']
        # reset the clear selection trigger
        st.session_state['clear_selection_triggered'] = False

    # account selection selectbox
    # use the index to control the default selection
    default_index = 0 if st.session_state['clear_selection_triggered'] else options.index(
        st.session_state['selected_account_name']) if st.session_state['selected_account_name'] in options else 0
    selected_account_name = st.selectbox(
        "Display Overall Engagement Time OR (Optional)",
        options=options,
        index=default_index,
        key='account_name_temp',  # temp key for the selectbox
        on_change=on_account_selected
    )

    # button to clear the selection
    if st.session_state.selected_account_name and st.session_state.selected_account_name != 'Select an account':
        if st.button('Clear Selection '):
            # reset the selected account name and trigger a rerun
            st.session_state['selected_account_name'] = 'Select an account'
            st.session_state['clear_selection_triggered'] = True
            st.experimental_rerun()

    # filter the df based on the selection (if not the placeholder)
    if st.session_state['selected_account_name'] and st.session_state['selected_account_name'] != 'Select an account':
        account_df = interaction_df[interaction_df['account_name'] == st.session_state['selected_account_name']]
    else:
        account_df = interaction_df

    # generate and display charts
    final_dic_engage = run_interaction_plotting_pipeline(interaction_df, arr_interaction_df, account_df)

    fig2 = final_dic_engage["fig2"]
    img2 = final_dic_engage["img2"]

    st.pyplot(fig2)

    btn2 = st.download_button(
        label="Download plot of Engagement Time",
        data=img2,
        file_name=f"fig2_engagement_time.png",
        mime="image/png",
        key="btn2",
    )

    st.markdown("""---""")

    st.write(
        f"""Plot of *Average Engagement Time* by Account ARR."""
    )
    if arr_interaction_df.empty:
        st.error('The selected time frame does not contain at least one entire half year period, the ARR plots are done'
                 ' with the default time frame')

    fig3 = final_dic_engage["fig3"]
    img3 = final_dic_engage["img3"]

    st.pyplot(fig3)

    btn3 = st.download_button(
        label="Download Engagement Time by ARR",
        data=img3,
        file_name=f"fig3_engagement_time_arr.png",
        mime="image/png",
        key="btn3",
    )

    st.markdown("""---""")

    st.header("Number of Days Engaged")

    st.write(
        f"""The Average Number of Days per month a Maker Visits the Platform"""
    )

    # indicate the current selection near the second line chart
    if st.session_state.selected_account_name and st.session_state.selected_account_name != 'Select an account':
        st.write(f"Chart selected for: {st.session_state.selected_account_name}")
        # button to clear selection here as well
        if st.button('Clear Selection'):
            st.session_state.selected_account_name = ''  # clear the selection
            st.experimental_rerun()  # rerun the app
    else:
        st.write("Showing charts for all accounts.")

    fig4 = final_dic_engage["fig4"]
    img4 = final_dic_engage["img4"]

    st.pyplot(fig4)

    btn4 = st.download_button(
        label="Download Days Engaged",
        data=img4,
        file_name=f"fig4_days_engaged.png",
        mime="image/png",
        key="btn4",
    )

    st.markdown("""---""")

    st.write(
        f"""The Average Number of Days Engaged by Account ARR"""
    )

    if arr_interaction_df.empty:
        st.error('The selected time frame does not contain at least one entire half year period, the ARR plots are done'
                 ' with the default time frame')

    fig5 = final_dic_engage["fig5"]
    img5 = final_dic_engage["img5"]

    st.pyplot(fig5)

    btn5 = st.download_button(
        label="Download Days Engaged by ARR",
        data=img5,
        file_name=f"fig5_days_engaged_arr.png",
        mime="image/png",
        key="btn5",
    )

    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.header("🪩 Number of Active Makers")
    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    with st.expander("Definition of Active Makers/ Active Results Makers"):
        st.markdown("""   
    - Generic Interaction: any activity on the platform is included for ***generic interactions***.
    - Results Interactions: ***results interactions*** are filtered only for results pages; not very ‘engaging’ 
    interactions like downloading, showing/collapsing panels, are excluded.

    ### Active Makers             
     - A maker is defined as active if they have done ≥ 5 ***generic interactions*** & have viewed a page ≥ 5 mins

     ### Active Results Makers
     - All active makers who have had ANY ***results interactions*** are deemed Active Results Makers.

    """)

    # Active maker filters
    fig1 = final_dic_engage["fig1"]
    img1 = final_dic_engage["img1"]

    st.pyplot(fig1)

    btn1 = st.download_button(
        label="Download plot of Active Makers/ Active Results Makers",
        data=img1,
        file_name=f"fig1_active_makers.png",
        mime="image/png",
        key="btn1",
    )

    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.header(
        f"""🗓️ Survey Frequencies"""
    )
    st.markdown("""<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    orig_survey_df = get_data_for_survey_frequency_metrics()
    survey_df = orig_survey_df[(orig_survey_df['purchase_month'] >= st.session_state.start_month)
                          & (orig_survey_df['purchase_month'] <= st.session_state.end_month)]

    final_dic_survey = run_survey_plotting_pipeline(orig_survey_df, survey_df)

    # Get some numbers of makers
    df_all = add_days_between_column(orig_survey_df)
    df_multiple = df_all.drop(df_all[df_all['days_from_previous'].isna()].index)

    single_2022 = len(df_all[df_all['purchase_year'] == '2022'].groupby('maker_id').filter(lambda x: len(x) == 1))
    single_2023 = len(df_all[df_all['purchase_year'] == '2023'].groupby('maker_id').filter(lambda x: len(x) == 1))

    multiple_2022 = len(df_multiple[df_multiple['purchase_year'] == '2022']['maker_id'].value_counts())
    multiple_2023 = len(df_multiple[df_multiple['purchase_year'] == '2023']['maker_id'].value_counts())

    st.write("**Average Days Between Purchases - 2022:**", int(df_multiple[df_multiple['purchase_year'] == '2022']['days_from_previous'].mean().round()), "days")
    st.write("**Average Days Between Purchases - 2023:**", int(df_multiple[df_multiple['purchase_year'] == '2023']['days_from_previous'].mean().round()), "days")

    st.write("**Note:** This metric only includes the makers who have purchased multiple surveys within the year.")

    tbl = pd.DataFrame({'Single Purchasers': [single_2022, single_2023],
                        'Multiple Purchasers': [multiple_2022, multiple_2023]},
                       index=['2022', '2023'])
    tbl['Ratio'] = tbl['Single Purchasers'] / (tbl['Single Purchasers'] + tbl['Multiple Purchasers'])

    with st.expander("The ratio between Single Purchasers and Multiple Purchasers", expanded=True):
        st.table(tbl)

    st.header("Days Between Purchases")

    fig6 = final_dic_survey["fig6"]
    img6 = final_dic_survey["img6"]

    st.pyplot(fig6)

    btn6 = st.download_button(
        label="Download Days Between by ARR",
        data=img6,
        file_name=f"fig6_days_between_arr.png",
        mime="image/png",
        key="btn6",
    )

    with st.expander("The percentages of Makers and Accounts across ARR brackets", expanded=False):
        st.write(
            f"""The percentages of Maker and Account across ARR brackets is shown in stacked rows here for reference."""
        )

        fig7 = final_dic_survey["fig7"]
        img7 = final_dic_survey["img7"]

        st.pyplot(fig7)

        btn7 = st.download_button(
            label="Download plot of Maker% and Account% by ARR",
            data=img7,
            file_name=f"fig7_maker_and_acct_by_arr.png",
            mime="image/png",
            key="btn7",
        )


main_pipeline()
