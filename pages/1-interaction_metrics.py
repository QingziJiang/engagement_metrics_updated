import streamlit as st
from pages.data.data_helper import get_data_for_interaction_metrics
from pages.data.plot_helper import run_interaction_plotting_pipeline


def main_pipeline_p1():
    interaction_df = get_data_for_interaction_metrics()

    final_dic = run_interaction_plotting_pipeline(interaction_df)

    st.header(
        f"""💫 Platform Interaction Metrics""", divider='rainbow'
    )

    st.header("Active Makers/ Active Results Makers")
    st.write("A maker is defined as active if they have done ≥ 5 interactions & have viewed a page ≥ 5 mins.")

    # Active maker filters
    active_makers = interaction_df[
        (interaction_df['total_engaged_time_in_m'] >= 5) & (interaction_df['num_unique_interactions'] >= 5)]
    results_makers = active_makers[active_makers['results_active_maker']]

    st.write("Number of Active Makers:", len(active_makers['maker_id'].value_counts()))
    st.write("Number of Active Results Makers:", len(results_makers['maker_id'].value_counts()))
    st.write("***since 2022-10-01")

    fig1 = final_dic["fig1"]
    img1 = final_dic["img1"]

    st.pyplot(fig1)

    btn1 = st.download_button(
        label="Download plot of Active Makers/ Active Results Makers",
        data=img1,
        file_name=f"fig1_active_makers.png",
        mime="image/png",
        key="btn1",
    )

    st.markdown("""---""")

    st.header("""Engagement Time""")

    fig2 = final_dic["fig2"]
    img2 = final_dic["img2"]

    st.write(
        f"""Plot of *Average Engagement Time* per Maker by Month."""
    )

    st.pyplot(fig2)

    st.write(
        """All makers who has had an active subscription (since 2022-10-01) are included for this metric for the
        duration while their subscription was active."""
    )

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

    fig3 = final_dic["fig3"]
    img3 = final_dic["img3"]

    st.pyplot(fig3)

    st.write(
        f"""The percentages of Maker across ARR brackets is shown in a stacked row here for reference."""
    )

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

    fig4 = final_dic["fig4"]
    img4 = final_dic["img4"]

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

    fig5 = final_dic["fig5"]
    img5 = final_dic["img5"]

    st.pyplot(fig5)

    btn5 = st.download_button(
        label="Download Days Engaged by ARR",
        data=img5,
        file_name=f"fig5_days_engaged_arr.png",
        mime="image/png",
        key="btn5",
    )

    st.write(
        f"""The percentage of Makers across ARR brackets is shown in a stacked row here for reference."""
    )


main_pipeline_p1()
