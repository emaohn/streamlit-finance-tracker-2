import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any, List

def transaction_form(
    categories: List[str],
    notebooks: List[Dict[str, Any]],
    existing_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Form for adding/editing a transaction"""
    
    # Initialize form data
    data = {}
    
    # Description
    data["description"] = st.text_input(
        "Description",
        value=existing_data.get("description", "") if existing_data else "",
        key="transaction_description"
    ).strip().lower()
    
    # Amount and type
    amount_col, type_col = st.columns([2, 1])
    with amount_col:
        data["amount"] = st.number_input(
            "Amount",
            min_value=-1000000.0,
            max_value=1000000.0,
            value=existing_data.get("amount", 0.0) if existing_data else 0.0,
            step=0.01,
            format="%.2f",
            key="transaction_amount"
        )
    
    with type_col:
        is_expense = st.radio(
            "Type",
            ["Expense", "Earning"],
            index=0 if existing_data and existing_data.get("amount", 0) < 0 else 1,
            key="transaction_type",
            horizontal=True
        ) == "Expense"
    
    # Date
    data["date"] = st.date_input(
        "Date",
        value=datetime.strptime(existing_data.get("date", str(date.today())), "%Y-%m-%d").date() if existing_data else date.today(),
        key="transaction_date"
    ).strftime("%Y-%m-%d")
    
    # Category with autocomplete
    category_input = st.text_input(
        "Category",
        value=existing_data.get("category", "") if existing_data else "",
        key="transaction_category"
    ).strip().lower()
    
    # Show category suggestions
    if category_input:
        suggestions = [c for c in categories if category_input in c.lower()]
        if suggestions:
            data["category"] = st.selectbox(
                "Select existing category",
                [""] + suggestions,
                index=suggestions.index(category_input) + 1 if category_input in suggestions else 0,
                key="category_suggestions"
            )
        else:
            data["category"] = category_input
    else:
        data["category"] = category_input
    
    # Notebook selection
    if notebooks:
        notebook_options = [""] + [n["name"] for n in notebooks]
        selected_notebook = st.selectbox(
            "Add to Notebook (optional)",
            notebook_options,
            index=notebook_options.index(next((n["name"] for n in notebooks if n["id"] == existing_data.get("notebook_id")), "")) if existing_data and existing_data.get("notebook_id") else 0,
            key="transaction_notebook"
        )
        
        if selected_notebook:
            notebook = next(n for n in notebooks if n["name"] == selected_notebook)
            data["notebook_id"] = notebook["id"]
            
            # Auto-fill notebook category if not set
            if not data["category"]:
                data["category"] = notebook.get("category", "")
    
    # Recurring flag
    data["recurring"] = st.checkbox(
        "Monthly recurring",
        value=existing_data.get("recurring", False) if existing_data else False,
        help="This transaction repeats monthly",
        key="transaction_recurring"
    )
    
    # Notes
    data["notes"] = st.text_area(
        "Notes (optional)",
        value=existing_data.get("notes", "") if existing_data else "",
        key="transaction_notes"
    ).strip()
    
    # Validate and submit
    if st.form_submit_button("Save Transaction"):
        if not data["description"]:
            st.error("Description is required")
            return None
        if data["amount"] == 0:
            st.error("Amount must not be zero")
            return None
        if not data["category"]:
            st.error("Category is required")
            return None
        
        # Set amount as negative for expenses
        if is_expense:
            data["amount"] = -data["amount"]
        
        return data
    
    return None

def budget_form(
    categories: List[str],
    existing_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Form for adding/editing a budget"""
    
    data = {}
    
    # Category with autocomplete
    category_input = st.text_input(
        "Category",
        value=existing_data.get("category", "") if existing_data else "",
        key="budget_category"
    ).strip().lower()
    
    # Show category suggestions
    if category_input:
        suggestions = [c for c in categories if category_input in c.lower()]
        if suggestions:
            data["category"] = st.selectbox(
                "Select existing category",
                [""] + suggestions,
                index=suggestions.index(category_input) + 1 if category_input in suggestions else 0,
                key="budget_category_suggestions"
            )
        else:
            data["category"] = category_input
    else:
        data["category"] = category_input
    
    # Budget type and amount
    budget_type = st.radio(
        "Budget Type",
        ["Monthly", "Annual"],
        horizontal=True,
        key="budget_type"
    )
    
    amount = st.number_input(
        f"{budget_type} Budget Amount",
        min_value=0.0,
        value=existing_data.get("amount", 0.0) if existing_data else 0.0,
        step=10.0,
        format="%.2f",
        key="budget_amount"
    )
    
    # Convert amount to both monthly and annual
    if budget_type == "Monthly":
        data["monthly"] = amount
        data["annual"] = amount * 12
    else:
        data["monthly"] = amount / 12
        data["annual"] = amount
    
    # Validate and submit
    if st.form_submit_button("Save Budget"):
        if not data["category"]:
            st.error("Category is required")
            return None
        if amount <= 0:
            st.error("Budget amount must be greater than 0")
            return None
        return data
    
    return None

def notebook_form(
    categories: List[str],
    existing_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Form for adding/editing a notebook"""
    
    data = {}
    
    # Name
    data["name"] = st.text_input(
        "Notebook Name",
        value=existing_data.get("name", "") if existing_data else "",
        key="notebook_name"
    ).strip()
    
    # Description
    data["description"] = st.text_area(
        "Description (optional)",
        value=existing_data.get("description", "") if existing_data else "",
        key="notebook_description"
    ).strip()
    
    # Category with autocomplete
    category_input = st.text_input(
        "Default Category",
        value=existing_data.get("category", "") if existing_data else "",
        help="This category will be auto-selected for new transactions in this notebook",
        key="notebook_category"
    ).strip().lower()
    
    # Show category suggestions
    if category_input:
        suggestions = [c for c in categories if category_input in c.lower()]
        if suggestions:
            data["category"] = st.selectbox(
                "Select existing category",
                [""] + suggestions,
                index=suggestions.index(category_input) + 1 if category_input in suggestions else 0,
                key="notebook_category_suggestions"
            )
        else:
            data["category"] = category_input
    else:
        data["category"] = category_input
    
    # Budget
    data["budget"] = st.number_input(
        "Budget (optional)",
        min_value=0.0,
        value=existing_data.get("budget", 0.0) if existing_data else 0.0,
        step=10.0,
        format="%.2f",
        help="Set a budget for this notebook",
        key="notebook_budget"
    )
    
    # Start and end dates
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        data["start_date"] = st.date_input(
            "Start Date (optional)",
            value=datetime.strptime(existing_data.get("start_date", str(date.today())), "%Y-%m-%d").date() if existing_data and existing_data.get("start_date") else None,
            key="notebook_start_date"
        ).strftime("%Y-%m-%d") if "start_date" in data else None
    
    with date_col2:
        data["end_date"] = st.date_input(
            "End Date (optional)",
            value=datetime.strptime(existing_data.get("end_date", str(date.today())), "%Y-%m-%d").date() if existing_data and existing_data.get("end_date") else None,
            key="notebook_end_date"
        ).strftime("%Y-%m-%d") if "end_date" in data else None
    
    # Validate and submit
    if st.form_submit_button("Save Notebook"):
        if not data["name"]:
            st.error("Name is required")
            return None
        if data["end_date"] and data["start_date"] and data["end_date"] < data["start_date"]:
            st.error("End date must be after start date")
            return None
        return data
    
    return None
