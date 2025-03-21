import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable

from ...utils.formatting import format_currency

def filter_transactions(
    transactions: List[Dict[str, Any]],
    start_date: datetime = None,
    end_date: datetime = None,
    category: str = None,
    notebook_id: str = None,
    transaction_type: str = None
) -> List[Dict[str, Any]]:
    """Filter transactions based on various criteria"""
    filtered = transactions.copy()
    
    if start_date:
        filtered = [
            t for t in filtered
            if datetime.strptime(t["date"], "%Y-%m-%d") >= start_date
        ]
    
    if end_date:
        filtered = [
            t for t in filtered
            if datetime.strptime(t["date"], "%Y-%m-%d") <= end_date
        ]
    
    if category:
        filtered = [t for t in filtered if t["category"] == category]
    
    if notebook_id:
        filtered = [t for t in filtered if t.get("notebook_id") == notebook_id]
    
    if transaction_type:
        if transaction_type == "Expense":
            filtered = [t for t in filtered if t["amount"] < 0]
        elif transaction_type == "Income":
            filtered = [t for t in filtered if t["amount"] > 0]
    
    return filtered

def display_transactions_tab(
    transactions: List[Dict[str, Any]],
    notebooks: List[Dict[str, Any]],
    categories: List[str],
    on_edit_transaction: Callable[[Dict[str, Any]], None],
    on_delete_transaction: Callable[[str], None]
):
    """Display the transactions tab content"""
    # Filter controls
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            start_date = st.date_input(
                "Start Date",
                value=(datetime.now() - timedelta(days=30)).date(),
                max_value=datetime.now().date()
            )
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                min_value=start_date
            )
        
        with col2:
            # Category filter
            selected_category = st.selectbox(
                "Category",
                ["All"] + categories,
                index=0
            )
            
            # Transaction type filter
            transaction_type = st.selectbox(
                "Type",
                ["All", "Expense", "Income"],
                index=0
            )
        
        with col3:
            # Notebook filter
            notebook_options = ["All"] + [n["name"] for n in notebooks]
            selected_notebook_name = st.selectbox(
                "Notebook",
                notebook_options,
                index=0
            )
            
            # Search filter
            search_query = st.text_input("Search", "")
    
    # Apply filters
    filtered_transactions = filter_transactions(
        transactions,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        category=None if selected_category == "All" else selected_category,
        notebook_id=None if selected_notebook_name == "All" else next(
            (n["id"] for n in notebooks if n["name"] == selected_notebook_name),
            None
        ),
        transaction_type=None if transaction_type == "All" else transaction_type
    )
    
    # Apply search filter if provided
    if search_query:
        filtered_transactions = [
            t for t in filtered_transactions
            if search_query.lower() in t["description"].lower()
        ]
    
    # Display transactions
    if filtered_transactions:
        # Convert to DataFrame for better display
        df = pd.DataFrame(filtered_transactions)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["amount"] = df["amount"].apply(format_currency)
        
        # Add notebook names
        notebook_map = {n["id"]: n["name"] for n in notebooks}
        df["notebook"] = df["notebook_id"].map(notebook_map)
        
        # Reorder and rename columns
        display_df = df[[
            "date",
            "description",
            "category",
            "amount",
            "notebook",
            "recurring"
        ]].rename(columns={
            "date": "Date",
            "description": "Description",
            "category": "Category",
            "amount": "Amount",
            "notebook": "Notebook",
            "recurring": "Recurring"
        })
        
        # Display as table with action buttons
        for index, row in display_df.iterrows():
            with st.container():
                cols = st.columns([2, 3, 2, 2, 2, 1, 1])
                
                # Display transaction details
                cols[0].write(str(row["Date"]))
                cols[1].write(row["Description"])
                cols[2].write(row["Category"])
                cols[3].write(row["Amount"])
                cols[4].write(row["Notebook"])
                cols[5].write("🔄" if row["Recurring"] else "")
                
                # Action buttons
                with cols[6]:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️", key=f"edit_{filtered_transactions[index]['id']}"):
                            on_edit_transaction(filtered_transactions[index])
                    with col2:
                        if st.button("🗑️", key=f"delete_{filtered_transactions[index]['id']}"):
                            on_delete_transaction(filtered_transactions[index]["id"])
            
            st.divider()
    else:
        st.info("No transactions found")
