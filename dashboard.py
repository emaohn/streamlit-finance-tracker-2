import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

def format_currency(amount):
    """Format currency with K/M suffixes for large numbers"""
    if abs(amount) >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif abs(amount) >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:.2f}"

def display_dashboard(expenses, assets, earnings, budgets):
    # Timeframe selector as segments
    st.write("### Overview")
    timeframe_cols = st.columns([1, 3])  # Make the timeframe selector take up less space
    with timeframe_cols[0]:
        selected_timeframe = st.radio(
            "Timeframe",
            ["1W", "1M", "YTD", "12M"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Filter data based on timeframe
    filtered_expenses = calculate_timeframe_data(expenses, selected_timeframe)
    filtered_earnings = calculate_timeframe_data(earnings, selected_timeframe)
    
    # Summary metrics row - compact layout with minimal spacing
    st.write("")  # Add small space before metrics
    metrics_container = st.container()
    with metrics_container:
        # Use custom CSS to reduce spacing between metrics
        st.markdown("""
            <style>
            [data-testid="stMetricValue"] {
                font-size: 1.8rem;
            }
            [data-testid="stMetricDelta"] {
                font-size: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)
        
        cols = st.columns(4)  # Equal width columns, no spacers needed
        
        with cols[0]:  # Total Expenses
            total_expenses = abs(sum(expense["amount"] for expense in filtered_expenses))
            monthly_budget = budgets["monthly"]["total"]
            over_budget = total_expenses - monthly_budget if selected_timeframe == "1M" else None
            delta = format_currency(abs(over_budget)) if over_budget is not None else None
            st.metric("Total Expenses", format_currency(total_expenses), delta)
        
        with cols[1]:  # Total Earnings
            total_earnings = sum(earning["amount"] for earning in filtered_earnings)
            st.metric("Total Earnings", format_currency(total_earnings))
        
        with cols[2]:  # Savings
            savings = total_earnings - total_expenses
            savings_rate = (savings / total_earnings * 100) if total_earnings > 0 else 0
            st.metric("Savings", format_currency(savings), f"{savings_rate:.1f}%")
        
        with cols[3]:  # Net Worth
            net_worth = calculate_net_worth(assets)
            st.metric("Net Worth", format_currency(net_worth))
    
    # Overview content
    st.write("")  # Add small space after metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spending Distribution")
        # Create spending by category donut chart
        category_totals = {}
        for expense in filtered_expenses:
            category = expense["category"]
            category_totals[category] = category_totals.get(category, 0) + abs(expense["amount"])
        
        if category_totals:
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
        
        # Add spending trends
        st.subheader("Spending Trends")
        if filtered_expenses:
            df = pd.DataFrame(filtered_expenses)
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
    
    with col2:
        st.subheader("Top Expenses")
        sorted_expenses = sorted(filtered_expenses, key=lambda x: abs(x["amount"]), reverse=True)[:5]
        for expense in sorted_expenses:
            st.markdown(f"**{expense['description']}** - {format_currency(abs(expense['amount']))}")
        
        st.subheader("Recurring Expenses")
        recurring = [expense for expense in filtered_expenses if expense.get("recurring", False)]
        for expense in recurring:
            st.markdown(f"**{expense['description']}** - {format_currency(abs(expense['amount']))}/month")
        
        # Add savings analysis
        st.subheader("Savings Analysis")
        if filtered_earnings:
            # Calculate monthly savings rate trend
            df_earnings = pd.DataFrame(filtered_earnings)
            df_earnings["date"] = pd.to_datetime(df_earnings["date"])
            df_expenses = pd.DataFrame(filtered_expenses)
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

def display_budget_tab(expenses, budgets):
    """Display budget tracking information"""
    st.write("### Budget Tracking")
    
    # Timeframe selector as segments
    timeframe = st.radio(
        "View",
        ["Monthly", "Annual"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly/Annual budget progress
        budget_type = "monthly" if timeframe == "Monthly" else "annual"
        budget_data = budgets[budget_type]
        
        # Add budget button
        if st.button("➕ Add Budget Category"):
            st.session_state.show_edit_budget = True
            st.session_state.edit_budget = None
        
        for category, budget in budget_data["categories"].items():
            # Calculate expenses for this category
            category_expenses = sum(abs(expense["amount"]) for expense in expenses 
                                 if expense["category"] == category)
            
            # Scale budget based on timeframe
            if timeframe == "Monthly":
                annual_budget = budget * 12
                annual_expenses = category_expenses * 12
            else:  # Annual
                annual_budget = budget
                annual_expenses = category_expenses
            
            # Show progress
            progress = min(100, (category_expenses / budget) * 100)
            
            # Add edit button
            col1, col2 = st.columns([4, 1])
            with col1:
                st.progress(progress / 100, 
                           text=f"{category}: {format_currency(category_expenses)} / {format_currency(budget)}")
            with col2:
                if st.button("✏️", key=f"edit_budget_{category}"):
                    st.session_state.show_edit_budget = True
                    st.session_state.edit_budget = {
                        "category": category,
                        "amount": budget
                    }
    
    with col2:
        # Budget summary
        total_budget = budget_data["total"]
        total_expenses = sum(abs(expense["amount"]) for expense in expenses)
        remaining = total_budget - total_expenses
        
        st.metric(
            f"Total {timeframe} Budget",
            format_currency(total_budget),
            format_currency(remaining) + " remaining"
        )
        
        # Budget vs Actual chart
        source = pd.DataFrame({
            "type": ["Budget", "Spent"],
            "amount": [total_budget, total_expenses]
        })
        
        chart = alt.Chart(source).mark_bar().encode(
            x="type",
            y="amount",
            color=alt.Color("type", scale=alt.Scale(domain=["Budget", "Spent"], range=["#4CAF50", "#FF9800"]))
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Add budget analysis
        st.subheader("Budget Analysis")
        if expenses:
            df = pd.DataFrame(expenses)
            df["date"] = pd.to_datetime(df["date"])
            df["amount"] = df["amount"].abs()
            
            # Group by category and calculate stats
            category_stats = df.groupby("category").agg({
                "amount": ["sum", "mean", "count"]
            }).round(2)
            
            category_stats.columns = ["Total", "Average", "Count"]
            category_stats = category_stats.reset_index()
            
            # Format currency columns
            category_stats["Total"] = category_stats["Total"].apply(format_currency)
            category_stats["Average"] = category_stats["Average"].apply(format_currency)
            
            st.dataframe(
                category_stats,
                column_config={
                    "category": "Category",
                    "Total": "Total Spent",
                    "Average": "Avg per Transaction",
                    "Count": "# Transactions"
                },
                hide_index=True
            )

def display_assets_tab(assets):
    """Display assets information"""
    st.write("### Assets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Asset Distribution")
        # Group assets by type
        asset_by_type = {}
        for asset in assets:
            asset_type = asset["type"]
            asset_by_type[asset_type] = asset_by_type.get(asset_type, 0) + asset["value"]
        
        if asset_by_type:
            source = pd.DataFrame({
                "type": list(asset_by_type.keys()),
                "value": list(asset_by_type.values())
            })
            
            chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(field="type", type="nominal"),
                tooltip=["type", alt.Tooltip("value", format="$,.2f")]
            )
            
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Asset Details")
        for asset in sorted(assets, key=lambda x: x["value"], reverse=True):
            with st.expander(f"{asset['name']} - {format_currency(asset['value'])}"):
                st.write(f"Type: {asset['type']}")
                st.write(f"Company: {asset['company']}")
                if "interest_rate" in asset:
                    st.write(f"Interest Rate: {asset['interest_rate']}%")
                if "maturity_date" in asset:
                    st.write(f"Maturity Date: {asset['maturity_date']}")
                if "holdings" in asset:
                    st.write("Holdings:", asset["holdings"])
                if "account_type" in asset:
                    st.write(f"Account Type: {asset['account_type']}")
                if "contribution_limit" in asset:
                    st.write(f"Contribution Limit: {format_currency(asset['contribution_limit'])}")

def display_transactions_tab(transactions):
    """Display transactions information"""
    st.write("### Recent Transactions")
    
    # Add transaction button at the top
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Transaction", type="primary", use_container_width=True):
            st.session_state.show_add_transaction = True
            st.session_state.edit_transaction = None
    
    # Transactions table
    if transactions:
        df = pd.DataFrame(transactions)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=False)
        
        # Add action buttons
        df["actions"] = None
        for idx, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("✏️", key=f"edit_transaction_{row['id']}"):
                    st.session_state.edit_transaction = row
                    st.session_state.show_add_transaction = True
        
        # Show transactions table
        st.dataframe(
            df[["date", "description", "amount", "category", "recurring"]],
            column_config={
                "date": st.column_config.DateColumn("Date", width="small"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f",
                    width="small"
                ),
                "category": st.column_config.TextColumn("Category", width="medium"),
                "recurring": st.column_config.CheckboxColumn("Recurring", width="small", help="Monthly recurring expense")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Transaction Analysis
        st.write("### Transaction Analysis")
        
        # Time period selector
        analysis_timeframe = st.selectbox(
            "Analysis Period",
            ["Last 30 Days", "Last 3 Months", "Last 6 Months", "Last Year", "All Time"]
        )
        
        # Filter transactions based on selected period
        now = datetime.now()
        if analysis_timeframe == "Last 30 Days":
            start_date = now - timedelta(days=30)
        elif analysis_timeframe == "Last 3 Months":
            start_date = now - timedelta(days=90)
        elif analysis_timeframe == "Last 6 Months":
            start_date = now - timedelta(days=180)
        elif analysis_timeframe == "Last Year":
            start_date = now - timedelta(days=365)
        else:
            start_date = None
        
        analysis_df = df.copy()
        if start_date:
            analysis_df = analysis_df[analysis_df["date"] >= start_date]
        
        # Category analysis
        st.subheader("Category Analysis")
        category_analysis = analysis_df.groupby("category").agg({
            "amount": ["count", "sum", "mean"]
        }).round(2)
        
        category_analysis.columns = ["Count", "Total", "Average"]
        category_analysis = category_analysis.reset_index()
        category_analysis["Total"] = category_analysis["Total"].abs()
        category_analysis["Average"] = category_analysis["Average"].abs()
        
        # Sort by total amount
        category_analysis = category_analysis.sort_values("Total", ascending=False)
        
        # Format currency columns
        category_analysis["Total"] = category_analysis["Total"].apply(format_currency)
        category_analysis["Average"] = category_analysis["Average"].apply(format_currency)
        
        st.dataframe(
            category_analysis,
            column_config={
                "category": "Category",
                "Count": "# Transactions",
                "Total": "Total Amount",
                "Average": "Avg per Transaction"
            },
            hide_index=True
        )
        
        # Monthly trends
        st.subheader("Monthly Trends")
        monthly_df = analysis_df.copy()
        monthly_df["month"] = monthly_df["date"].dt.to_period("M")
        monthly_trends = monthly_df.groupby(["month", "category"])["amount"].sum().abs().reset_index()
        monthly_trends["month"] = monthly_trends["month"].astype(str)
        
        trend_chart = alt.Chart(monthly_trends).mark_line(point=True).encode(
            x="month:T",
            y="amount:Q",
            color="category:N",
            tooltip=["month", "category", alt.Tooltip("amount", format="$,.2f")]
        )
        
        st.altair_chart(trend_chart, use_container_width=True)

def calculate_timeframe_data(data, timeframe):
    """Calculate data for the selected timeframe"""
    now = datetime.now()
    
    if timeframe == "1W":
        start_date = now - timedelta(days=7)
    elif timeframe == "1M":
        start_date = now - timedelta(days=30)
    elif timeframe == "YTD":
        start_date = datetime(now.year, 1, 1)
    elif timeframe == "12M":
        start_date = now - timedelta(days=365)
    else:
        return data  # Return all data if timeframe not recognized
    
    # Filter data based on timeframe
    filtered_data = [d for d in data if datetime.strptime(d["date"], "%Y-%m-%d") >= start_date]
    return filtered_data

def calculate_net_worth(assets):
    """Calculate total net worth from assets"""
    return sum(asset["value"] for asset in assets)
