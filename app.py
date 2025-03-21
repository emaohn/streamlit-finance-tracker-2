import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any, List

from src.services.firebase import get_firebase_instance
from src.services.auth import render_auth_ui
from src.models.transaction import Transaction
from src.models.notebook import Notebook
from src.ui.dashboard import (
    render_sidebar_dashboard,
    display_overview_tab,
    display_budget_tab,
    display_transactions_tab,
    display_assets_tab
)
from src.ui.forms import transaction_form, notebook_form, budget_form, asset_form

# Initialize Firebase
try:
    firebase = get_firebase_instance()
except Exception as e:
    st.error(f"Failed to initialize Firebase: {str(e)}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Finance Tracker",
    page_icon="",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .stProgress .st-bp {
        background-color: #f0f2f6;
    }
    div[data-testid="stSidebarNav"] {
        background-image: none;
        padding-top: 2rem;
    }
    .st-emotion-cache-1cypcdb {
        background: rgba(255, 255, 255, 0.95);
    }
    /* Modal form styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0,0,0,0.4);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .modal-content {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 600px;
        margin: 2rem;
        position: relative;
    }
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "show_transaction_form" not in st.session_state:
    st.session_state.show_transaction_form = False
if "show_notebook_form" not in st.session_state:
    st.session_state.show_notebook_form = False
if "show_budget_form" not in st.session_state:
    st.session_state.show_budget_form = False
if "show_asset_form" not in st.session_state:
    st.session_state.show_asset_form = False
if "edit_transaction" not in st.session_state:
    st.session_state.edit_transaction = None
if "edit_notebook" not in st.session_state:
    st.session_state.edit_notebook = None
if "edit_budget" not in st.session_state:
    st.session_state.edit_budget = None
if "edit_asset" not in st.session_state:
    st.session_state.edit_asset = None

def load_data() -> Dict[str, Any]:
    """Load all required data from Firebase"""
    try:
        transactions = firebase.fetch_transactions()
        notebooks = firebase.fetch_notebooks()
        categories = firebase.fetch_categories()
        budgets = firebase.fetch_budgets()
        assets = firebase.fetch_assets()
        
        return {
            "transactions": transactions,
            "notebooks": notebooks,
            "categories": categories,
            "budgets": budgets or {},
            "assets": assets or []
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def handle_transaction_form(data: Optional[Dict[str, Any]], notebooks: List[Dict[str, Any]], categories: List[str]):
    """Handle transaction form submission"""
    if not data:
        st.session_state.show_transaction_form = False
        return
    
    try:
        transaction_id = st.session_state.edit_transaction.get("id") if st.session_state.edit_transaction else None
        
        if transaction_id:
            success = firebase.update_transaction(transaction_id, data)
        else:
            transaction_id = firebase.add_transaction(data)
            success = bool(transaction_id)
        
        if success:
            st.success("Transaction saved successfully!")
            
            # Update categories if new one was added
            if data["category"] not in categories:
                firebase.update_categories(categories + [data["category"]])
            
            st.session_state.show_transaction_form = False
            st.session_state.edit_transaction = None
            st.rerun()
        else:
            st.error("Failed to save transaction")
    except Exception as e:
        st.error(f"Error saving transaction: {str(e)}")

def handle_notebook_form(data: Optional[Dict[str, Any]], categories: List[str]):
    """Handle notebook form submission"""
    if not data:
        st.session_state.show_notebook_form = False
        return
    
    try:
        notebook_id = st.session_state.edit_notebook.get("id") if st.session_state.edit_notebook else None
        
        if notebook_id:
            success = firebase.update_notebook(notebook_id, data)
        else:
            notebook_id = firebase.add_notebook(data)
            success = bool(notebook_id)
        
        if success:
            st.success("Notebook saved successfully!")
            
            # Update categories if new one was added
            if data["category"] not in categories:
                firebase.update_categories(categories + [data["category"]])
            
            st.session_state.show_notebook_form = False
            st.session_state.edit_notebook = None
            st.rerun()
        else:
            st.error("Failed to save notebook")
    except Exception as e:
        st.error(f"Error saving notebook: {str(e)}")

def handle_budget_form(data: Optional[Dict[str, Any]], current_budgets: Dict[str, Any]):
    """Handle budget form submission"""
    if not data:
        st.session_state.show_budget_form = False
        return
    
    try:
        # Initialize budget structure if not exists
        if "monthly" not in current_budgets:
            current_budgets["monthly"] = {"total": 0, "categories": {}}
        if "annual" not in current_budgets:
            current_budgets["annual"] = {"total": 0, "categories": {}}
        
        # Update budgets
        current_budgets["monthly"]["categories"][data["category"]] = data["monthly"]
        current_budgets["annual"]["categories"][data["category"]] = data["annual"]
        
        # Update totals
        current_budgets["monthly"]["total"] = sum(current_budgets["monthly"]["categories"].values())
        current_budgets["annual"]["total"] = sum(current_budgets["annual"]["categories"].values())
        
        if firebase.update_budgets(current_budgets):
            st.success("Budget saved successfully!")
            st.session_state.show_budget_form = False
            st.session_state.edit_budget = None
            st.rerun()
        else:
            st.error("Failed to save budget")
    except Exception as e:
        st.error(f"Error saving budget: {str(e)}")

def handle_asset_form(data: Optional[Dict[str, Any]], categories: List[str]):
    """Handle asset form submission"""
    if not data:
        st.session_state.show_asset_form = False
        return
    
    try:
        asset_id = st.session_state.edit_asset.get("id") if st.session_state.edit_asset else None
        
        if asset_id:
            success = firebase.update_asset(asset_id, data)
        else:
            asset_id = firebase.add_asset(data)
            success = bool(asset_id)
        
        if success:
            st.success("Asset saved successfully!")
            
            # Update categories if new one was added
            if data["category"] not in categories:
                firebase.update_categories(categories + [data["category"]])
            
            st.session_state.show_asset_form = False
            st.session_state.edit_asset = None
            st.rerun()
        else:
            st.error("Failed to save asset")
    except Exception as e:
        st.error(f"Error saving asset: {str(e)}")

def delete_notebook(notebook_id: str):
    """Delete a notebook and its transactions"""
    try:
        if firebase.delete_notebook(notebook_id):
            st.success("Notebook deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete notebook")
    except Exception as e:
        st.error(f"Error deleting notebook: {str(e)}")

def main():
    """Main application function"""
    # Render authentication UI
    render_auth_ui()
    
    # Only show content for authenticated users
    if "user_id" not in st.session_state:
        return
    
    # Load data
    data = load_data()
    if not data:
        return
    
    # Render sidebar
    render_sidebar_dashboard(
        notebooks=data["notebooks"],
        on_add_transaction=lambda: setattr(st.session_state, "show_transaction_form", True),
        on_add_notebook=lambda: setattr(st.session_state, "show_notebook_form", True),
        on_edit_notebook=lambda n: setattr(st.session_state, "edit_notebook", n),
        on_delete_notebook=delete_notebook
    )
    
    # Handle forms
    if st.session_state.show_transaction_form:
        transaction_form(
            data["notebooks"],
            data["categories"],
            st.session_state.edit_transaction,
            lambda form_data: handle_transaction_form(form_data, data["notebooks"], data["categories"])
        )
    
    if st.session_state.show_notebook_form:
        notebook_form(
            data["categories"],
            st.session_state.edit_notebook,
            lambda form_data: handle_notebook_form(form_data, data["categories"])
        )
    
    if st.session_state.show_budget_form:
        budget_form(
            data["categories"],
            data["budgets"],
            st.session_state.edit_budget,
            lambda form_data: handle_budget_form(form_data, data["budgets"])
        )
    
    if st.session_state.show_asset_form:
        asset_form(
            data["categories"],
            st.session_state.edit_asset,
            lambda form_data: handle_asset_form(form_data, data["categories"])
        )
    
    # Display tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Budget", "Assets", "Transactions"])
    
    with tab1:
        display_overview_tab(
            data["transactions"],
            data["notebooks"],
            data["budgets"]
        )
    
    with tab2:
        display_budget_tab(
            data["transactions"],
            data["budgets"],
            lambda: setattr(st.session_state, "show_budget_form", True),
            lambda b: setattr(st.session_state, "edit_budget", b)
        )
    
    with tab3:
        display_assets_tab(
            data["assets"],
            data["categories"],
            lambda: setattr(st.session_state, "show_asset_form", True),
            lambda a: setattr(st.session_state, "edit_asset", a),
            lambda a: firebase.delete_asset(a["id"])
        )
    
    with tab4:
        display_transactions_tab(
            data["transactions"],
            data["notebooks"],
            data["categories"],
            lambda transaction: firebase.delete_transaction(transaction["id"]),
            lambda transaction: setattr(st.session_state, "edit_transaction", transaction)
        )

if __name__ == "__main__":
    main()
