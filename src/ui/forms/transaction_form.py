import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Callable

def transaction_form(
    notebooks: List[Dict[str, Any]],
    categories: List[str],
    existing_data: Optional[Dict[str, Any]],
    on_submit: Callable[[Optional[Dict[str, Any]]], None]
):
    """Form for adding/editing a transaction"""
    st.markdown("""
    <div class="modal-overlay">
    <div class="modal-content">
    """, unsafe_allow_html=True)
    
    st.subheader("Transaction Details")
    
    with st.form("transaction_form"):
        # Description
        description = st.text_input(
            "Description",
            value=existing_data.get("description", "") if existing_data else "",
            placeholder="e.g., Groceries at Trader Joe's"
        ).strip()
        
        # Amount and type
        col1, col2 = st.columns([2, 1])
        with col1:
            amount = st.number_input(
                "Amount",
                value=abs(existing_data.get("amount", 0)) if existing_data else 0.0,
                min_value=0.0,
                format="%.2f"
            )
        with col2:
            is_expense = st.radio(
                "Type",
                ["Expense", "Earning"],
                index=0 if existing_data and existing_data.get("amount", 0) < 0 else 1,
                horizontal=True
            ) == "Expense"
        
        # Date
        date_value = st.date_input(
            "Date",
            value=datetime.strptime(existing_data.get("date", str(date.today())), "%Y-%m-%d").date() if existing_data else date.today()
        )
        
        # Category
        category_options = [""] + categories if categories else [""]
        category = st.selectbox(
            "Category",
            options=category_options,
            index=category_options.index(existing_data.get("category", "")) if existing_data and existing_data.get("category") in category_options else 0,
        )
        
        # New category input if empty is selected
        if not category:
            category = st.text_input("New Category", placeholder="Enter a new category")
        
        # Notebook selection
        if notebooks:
            notebook_options = [""] + [n["name"] for n in notebooks]
            selected_notebook = st.selectbox(
                "Add to Notebook (optional)",
                notebook_options,
                index=notebook_options.index(next((n["name"] for n in notebooks if n["id"] == existing_data.get("notebook_id")), "")) if existing_data and existing_data.get("notebook_id") else 0
            )
            
            if selected_notebook:
                notebook = next(n for n in notebooks if n["name"] == selected_notebook)
                notebook_id = notebook["id"]
                
                # Auto-fill notebook category if not set
                if not category:
                    category = notebook.get("category", "")
        
        # Notes
        notes = st.text_area(
            "Notes (optional)",
            value=existing_data.get("notes", "") if existing_data else "",
            placeholder="Add any additional details"
        ).strip()
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save"):
                if not description:
                    st.error("Please enter a description")
                    return
                if not category:
                    st.error("Please select or enter a category")
                    return
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                    return
                
                # Prepare transaction data
                transaction_data = {
                    "description": description,
                    "amount": -amount if is_expense else amount,
                    "date": date_value.strftime("%Y-%m-%d"),
                    "category": category,
                    "notes": notes
                }
                
                # Add notebook if selected
                if notebooks and selected_notebook:
                    transaction_data["notebook_id"] = notebook_id
                
                on_submit(transaction_data)
        
        with col2:
            if st.form_submit_button("Cancel"):
                on_submit(None)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
