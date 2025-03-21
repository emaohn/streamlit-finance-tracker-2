import streamlit as st
from typing import List, Dict, Any, Callable

from .tabs.overview import display_overview_tab
from .tabs.budget import display_budget_tab
from .tabs.transactions import display_transactions_tab
from .tabs.assets import display_assets_tab

__all__ = [
    "render_sidebar_dashboard",
    "display_overview_tab",
    "display_budget_tab",
    "display_transactions_tab",
    "display_assets_tab",
    "render_dashboard"
]

def render_sidebar_dashboard(
    notebooks: List[Dict[str, Any]],
    on_add_transaction: Callable[[], None],
    on_add_notebook: Callable[[], None],
    on_edit_notebook: Callable[[Dict[str, Any]], None],
    on_delete_notebook: Callable[[str], None]
):
    """Render the sidebar dashboard"""
    # Quick Actions
    with st.sidebar:
        st.subheader("Quick Actions")
        st.button("➕ Add Transaction", on_click=on_add_transaction, type="primary")
        st.button("📓 Add Notebook", on_click=on_add_notebook)
        
        # Notebooks
        if notebooks:
            st.subheader("Notebooks")
            for notebook in notebooks:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(notebook["name"])
                with col2:
                    st.button(
                        "✏️",
                        key=f"edit_notebook_{notebook['id']}",
                        on_click=lambda n=notebook: on_edit_notebook(n)
                    )
                with col3:
                    st.button(
                        "🗑️",
                        key=f"delete_notebook_{notebook['id']}",
                        on_click=lambda n=notebook: on_delete_notebook(n["id"])
                    )

def render_dashboard(
    transactions: List[Dict[str, Any]],
    notebooks: List[Dict[str, Any]],
    categories: List[str],
    assets: List[Dict[str, Any]],
    budgets: Dict[str, Any],
    on_edit_transaction: Callable[[Dict[str, Any]], None],
    on_delete_transaction: Callable[[str], None],
    on_add_transaction: Callable[[], None]
):
    """Render the main dashboard content"""
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["Overview", "Budget", "Transactions"])
    
    # Overview tab
    with tab1:
        display_overview_tab(transactions, assets, budgets)
    
    # Budget tab
    with tab2:
        display_budget_tab(transactions, budgets, on_edit_transaction)
    
    # Transactions tab
    with tab3:
        display_transactions_tab(
            transactions,
            on_add_transaction,
            on_edit_transaction,
            on_delete_transaction
        )
