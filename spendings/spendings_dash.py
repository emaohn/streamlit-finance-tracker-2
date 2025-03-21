import streamlit as st

import pandas as pd
import altair as alt

def display_spendings_dash(expenses):
    left, right = st.columns([0.7, 0.3])
    with right:
        option = st.selectbox(
            "Timeframe",
            ("December 2024", "November 2024", "September 2024"),
        )
    col1, col2 = st.columns(2, border=False, vertical_alignment="center")
    with col1:
        st.title("$840")
        st.markdown("spent this month")

    with col2:
        progress_text = "Total Budget Remaining"
        my_bar = st.progress(67, text=progress_text)

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.subheader("Spending Categories")
        source = pd.DataFrame({"category": ["Liquid", "CDs", "Retirement", "Investments"], "value": [30000, 45000, 100000, 100000]})

        chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
        )

        st.altair_chart(chart, theme="streamlit", use_container_width=True)

    with col2: 
        st.markdown("Monthly Budget")
        
        progress_text = "Grocery"
        my_bar = st.progress(67, text=progress_text)

        progress_text = "Shopping"
        my_bar = st.progress(67, text=progress_text)

        progress_text = "Transportation"
        my_bar = st.progress(67, text=progress_text)

        st.divider()
        st.markdown("Annual Budget")
        progress_text = "Travel"
        my_bar = st.progress(67, text=progress_text)

        progress_text = "Pet"
        my_bar = st.progress(67, text=progress_text)

        progress_text = "Home"
        my_bar = st.progress(67, text=progress_text)

            

    display_spendings_df(expenses)

def display_spendings_df(expenses):
    df = pd.DataFrame(
        expenses
    )
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", 
        hide_index=True, 
        use_container_width=True,
        column_config={
        "command": "Streamlit Command",
        "amount": st.column_config.NumberColumn(
            "Amount",
            help="$ spent",
            format="$%d",
        ),
    },
    )
