import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date
from typing import List, Dict, Any

from ...utils.formatting import format_currency

def filter_transactions_by_timeframe(transactions: List[Dict[str, Any]], timeframe: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """Filter transactions based on the selected timeframe"""
    if timeframe == "Custom":
        return [t for t in transactions if start_date <= datetime.strptime(t["date"], "%Y-%m-%d").date() <= end_date]
    else:
        now = datetime.now()
        if timeframe == "Current Month":
            start_date = date(now.year, now.month, 1)
            end_date = date.today()
        elif timeframe == "Current Week":
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = date.today()
        else:  # YTD
            start_date = date(now.year, 1, 1)
            end_date = date.today()
        return [t for t in transactions if start_date <= datetime.strptime(t["date"], "%Y-%m-%d").date() <= end_date]

def render_spending_distribution(expenses: List[Dict[str, Any]]):
    """Render the spending distribution donut chart"""
    if not expenses:
        st.info("No expenses to display")
        return
    
    category_totals = {}
    for expense in expenses:
        category = expense["category"]
        category_totals[category] = category_totals.get(category, 0) + abs(expense["amount"])
    
    source = pd.DataFrame({
        "category": list(category_totals.keys()),
        "amount": list(category_totals.values())
    })
    
    chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="amount", type="quantitative"),
        color=alt.Color(field="category", type="nominal"),
        tooltip=["category", alt.Tooltip("amount", format="$,.2f")]
    )
    
    st.altair_chart(chart, use_container_width=True)

def render_spending_trends(expenses: List[Dict[str, Any]]):
    """Render the spending trends line chart"""
    if not expenses:
        st.info("No expenses to display")
        return
    
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].abs()
    
    # Group by date and category
    daily_by_category = df.groupby([df["date"].dt.date, "category"])["amount"].sum().reset_index()
    
    # Create line chart
    trend_chart = alt.Chart(daily_by_category).mark_line().encode(
        x="date:T",
        y="amount:Q",
        color="category:N",
        tooltip=["date", "category", alt.Tooltip("amount", format="$,.2f")]
    )
    
    st.altair_chart(trend_chart, use_container_width=True)

def render_top_expenses(expenses: List[Dict[str, Any]]):
    """Render the top expenses list"""
    if not expenses:
        st.info("No expenses to display")
        return
    
    sorted_expenses = sorted(expenses, key=lambda x: abs(x["amount"]), reverse=True)[:5]
    for expense in sorted_expenses:
        st.markdown(f"**{expense['description']}** - {format_currency(abs(expense['amount']))}")

def render_recurring_expenses(expenses: List[Dict[str, Any]]):
    """Render the recurring expenses list"""
    recurring = [expense for expense in expenses if expense.get("recurring", False)]
    if not recurring:
        st.info("No recurring expenses")
        return
    
    for expense in recurring:
        st.markdown(f"**{expense['description']}** - {format_currency(abs(expense['amount']))}/month")

def render_savings_analysis(earnings: List[Dict[str, Any]], expenses: List[Dict[str, Any]]):
    """Render the savings analysis chart"""
    if not earnings or not expenses:
        st.info("Not enough data for savings analysis")
        return
    
    # Calculate monthly savings rate trend
    df_earnings = pd.DataFrame(earnings)
    df_earnings["date"] = pd.to_datetime(df_earnings["date"])
    df_expenses = pd.DataFrame(expenses)
    df_expenses["date"] = pd.to_datetime(df_expenses["date"])
    
    # Group by month
    monthly_earnings = df_earnings.groupby(df_earnings["date"].dt.to_period("M"))["amount"].sum()
    monthly_expenses = df_expenses.groupby(df_expenses["date"].dt.to_period("M"))["amount"].sum().abs()
    monthly_savings_rate = ((monthly_earnings - monthly_expenses) / monthly_earnings * 100).round(1)
    
    # Display as a line chart
    savings_df = pd.DataFrame({
        "date": monthly_savings_rate.index.astype(str),
        "rate": monthly_savings_rate.values
    })
    
    savings_chart = alt.Chart(savings_df).mark_line(point=True).encode(
        x="date:T",
        y=alt.Y("rate:Q", title="Savings Rate (%)"),
        tooltip=["date", alt.Tooltip("rate", format=".1f")]
    )
    
    st.altair_chart(savings_chart, use_container_width=True)

def display_overview_tab(transactions: List[Dict[str, Any]], assets: List[Dict[str, Any]], budgets: Dict[str, Any]):
    """Display the overview tab content"""
    # Timeframe selector
    col1, col2 = st.columns([2, 3])
    with col1:
        timeframe = st.radio(
            "Timeframe",
            ["Current Month", "Current Week", "YTD", "Custom"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Date range selector for custom timeframe
    if timeframe == "Custom":
        with col2:
            start_date, end_date = st.date_input(
                "Date Range",
                value=(date.today().replace(day=1), date.today()),
                key="overview_date_range"
            )
    else:
        # Calculate date range based on timeframe
        now = datetime.now()
        if timeframe == "Current Month":
            start_date = date(now.year, now.month, 1)
            end_date = date.today()
        elif timeframe == "Current Week":
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = date.today()
        else:  # YTD
            start_date = date(now.year, 1, 1)
            end_date = date.today()
    
    # Filter transactions
    filtered_transactions = filter_transactions_by_timeframe(transactions, timeframe, start_date, end_date)
    
    # Calculate metrics
    total_expenses = sum(t["amount"] for t in filtered_transactions if t["amount"] < 0)
    total_earnings = sum(t["amount"] for t in filtered_transactions if t["amount"] > 0)
    net_savings = total_earnings + total_expenses  # total_expenses is negative
    savings_rate = (net_savings / total_earnings * 100) if total_earnings > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Expenses", format_currency(abs(total_expenses)))
    with col2:
        st.metric("Total Earnings", format_currency(total_earnings))
    with col3:
        st.metric("Net Savings", format_currency(net_savings))
    with col4:
        st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    # Overview content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spending Distribution")
        expenses = [t for t in filtered_transactions if t["amount"] < 0]
        render_spending_distribution(expenses)
        
        st.subheader("Spending Trends")
        render_spending_trends(expenses)
    
    with col2:
        st.subheader("Top Expenses")
        render_top_expenses(expenses)
        
        st.subheader("Recurring Expenses")
        render_recurring_expenses(expenses)
        
        st.subheader("Savings Analysis")
        earnings = [t for t in filtered_transactions if t["amount"] > 0]
        render_savings_analysis(earnings, expenses)
