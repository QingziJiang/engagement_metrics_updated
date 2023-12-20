import streamlit as st

st.set_page_config(
    page_title="Product Engagement Metric",
    page_icon="🧲",
    initial_sidebar_state="expanded",
)

st.write("# Welcome to Attest Product Engagement Metric Page ")

st.sidebar.success("Select an option from above.")

st.markdown(
    """    
    Measuring user engagement on our platform is essential for understanding how effectively our product is meeting 
    user needs.
    
    **👈👈👈**

    - **Interaction**: These metrics give you a closer look on users' active usage and time spent on the platform
        - Active user/Active results user
        - Engaged time
    - **Survey Frequency**: This page gives you the metrics for users' purchasing frequency
        - Number of Survey purchased
        - Number of days between surveys 
        
    All charts are downloadable! 🤗
"""
)
