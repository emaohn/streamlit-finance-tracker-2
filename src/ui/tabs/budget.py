import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Callable

from ...utils.formatting import format_currency

def calculate_budget_progress(expenses: List[Dict[str, Any]], budget: float) -> float:
    """Calculate the progress towards a budget"""
    total_spent = sum(abs(expense["amount"]) for expense in expenses)
    return (total_spent / budget * 100) if budget > 0 else 0

def render_budget_progress(category: str, spent: float, budget: float, on_edit_budget: Callable[[Dict[str, Any]], None]):
    """Render a budget progress bar for a category"""
    progress = (spent / budget * 100) if budget > 0 else 0
    over_budget = spent > budget
    
    # Display category name and amounts
    col1, col2, col3 = st.columns([3, 1, 0.5])
    with col1:
        st.write(f"**{category}**")
        progress_color = "red" if over_budget else "green"
        st.progress(min(progress, 100) / 100, text=f"{progress:.1f}%")
    with col2:
        st.write(f"{format_currency(spent)} / {format_currency(budget)}")
    with col3:
        st.button("✏️", key=f"edit_budget_{category}", on_click=lambda: on_edit_budget({"category": category}))

def display_budget_tab(
    transactions: List[Dict[str, Any]], 
    budgets: Dict[str, Any],
    on_add_budget: Callable[[], None],
    on_edit_budget: Callable[[Dict[str, Any]], None]
):
    """Display the budget tab content"""
    # Add budget button
    st.button("➕ Add Budget", on_click=on_add_budget, type="primary")
    
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
                key="budget_date_range"
            )
    else:
        # Calculate date range based on timeframe
        now = datetime.now()
        if timeframe == "Current Month":
            start_date = date(now.year, now.month, 1)
            end_date = date.today()
            current_budgets = budgets.get("monthly", {}).get("categories", {})
            total_budget = budgets.get("monthly", {}).get("total", 0)
        elif timeframe == "Current Week":
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = date.today()
            # Use prorated monthly budget for the week
            current_budgets = {
                category: budget / 4  # Approximate week as month/4
                for category, budget in budgets.get("monthly", {}).get("categories", {}).items()
            }
            total_budget = budgets.get("monthly", {}).get("total", 0) / 4
        else:  # YTD
            start_date = date(now.year, 1, 1)
            end_date = date.today()
            current_budgets = budgets.get("annual", {}).get("categories", {})
            total_budget = budgets.get("annual", {}).get("total", 0)
    
    filtered_transactions = [
        t for t in transactions
        if start_date <= datetime.strptime(t["date"], "%Y-%m-%d").date() <= end_date
        and t["amount"] < 0  # Only expenses
    ]
    
    # Group expenses by category
    category_expenses = {}
    for transaction in filtered_transactions:
        category = transaction["category"]
        amount = abs(transaction["amount"])
        category_expenses[category] = category_expenses.get(category, 0) + amount
    
    if not current_budgets:
        st.info("No budgets set yet. Click the button above to set your first budget!")
        return
    
    # Display overall budget progress
    st.subheader("Overall Budget")
    total_spent = sum(category_expenses.values())
    render_budget_progress("Total", total_spent, total_budget, on_edit_budget)
    
    # Display category budgets
    st.subheader("Category Budgets")
    for category, budget in current_budgets.items():
        spent = category_expenses.get(category, 0)
        render_budget_progress(category, spent, budget, on_edit_budget)
    
    # Budget vs Actual chart
    st.subheader("Budget vs Actual")
    chart_data = []
    for category, budget in current_budgets.items():
        spent = category_expenses.get(category, 0)
        chart_data.extend([
            {"category": category, "type": "Budget", "amount": budget},
            {"category": category, "type": "Actual", "amount": spent}
        ])
    
    if chart_data:
        df = pd.DataFrame(chart_data)
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("amount:Q", title="Amount"),
            color=alt.Color(
                "type:N", 
                scale=alt.Scale(
                    domain=["Budget", "Actual"],
                    range=["#4CAF50", "#2196F3"]
                )
            ),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("type:N", title="Type"),
                alt.Tooltip("amount:Q", title="Amount", format="$,.2f")
            ]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No budget data to display")
