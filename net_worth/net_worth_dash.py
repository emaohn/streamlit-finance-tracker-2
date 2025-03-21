import streamlit as st
import pandas as pd
import altair as alt

def display_net_worth_dash(assets):
    net_worth_display, timeframe_selector = st.columns([0.55, 0.45])
    with net_worth_display:
        st.metric(label="Current Net Worth", value="$350,000", delta="$2,300")


    with timeframe_selector:
        timeframes = ["1W", "1M", "YTD", "1Y", "3Y"]
        selection = st.radio(
            "", timeframes, horizontal=True
        )


    df_net_worth = pd.DataFrame(
        [
            {"Date": "2024-01-01", "Net Worth": 100000},
            {"Date": "2024-02-01", "Net Worth": 200000},
            {"Date": "2024-03-01", "Net Worth": 275000},
        ]
    )
    st.line_chart(df_net_worth, x="Date", y="Net Worth")

    asset_list, asset_chart = st.columns([0.5, 0.5])
    
    with asset_list:
        st.header("Assets")
        options = st.multiselect(
            "Filter Assets",
            ["Certificats of Deposit", "Taxable Investments", "Liquid", "Retirement"],
            ["Certificats of Deposit", "Taxable Investments", "Liquid", "Retirement"],
        )
        assets_container = st.container()
        with assets_container:
            for asset in assets:
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.text(asset["asset_name"])
                    st.text(asset["asset_type"])
                    st.text(asset["company"])
                with col2:
                    st.text(f"${asset['account_value']}")
                st.divider()

    with asset_chart:
        source = pd.DataFrame({"category": ["Liquid", "CDs", "Retirement", "Investments"], "value": [30000, 45000, 100000, 100000]})

        chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
        )

        st.altair_chart(chart, theme="streamlit", use_container_width=True)