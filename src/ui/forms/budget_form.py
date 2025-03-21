import streamlit as st
from typing import List, Dict, Any, Optional, Callable

def budget_form(
    categories: List[str],
    existing_budgets: Dict[str, Any],
    existing_data: Optional[Dict[str, Any]],
    on_submit: Callable[[Dict[str, Any]], None]
):
    """Form for adding/editing a budget"""
    st.markdown("""
    <div class="modal-overlay">
    <div class="modal-content">
    """, unsafe_allow_html=True)
    
    st.subheader("Budget Details")
    
    with st.form("budget_form"):
        # Category selection
        category_options = [""] + categories if categories else [""]
        selected_category = existing_data.get("category") if existing_data else ""
        category = st.selectbox(
            "Category",
            options=category_options,
            index=category_options.index(selected_category) if selected_category in category_options else 0,
        )
        
        # New category input if empty is selected
        if not category:
            category = st.text_input("New Category", placeholder="Enter a new category")
        
        # Monthly budget
        current_monthly = (
            existing_budgets.get("monthly", {})
            .get("categories", {})
            .get(selected_category, 0)
            if selected_category
            else 0
        )
        monthly = st.number_input(
            "Monthly Budget",
            value=float(current_monthly),
            min_value=0.0,
            format="%.2f",
            help="Set your monthly budget for this category"
        )
        
        # Annual budget
        current_annual = (
            existing_budgets.get("annual", {})
            .get("categories", {})
            .get(selected_category, 0)
            if selected_category
            else 0
        )
        annual = st.number_input(
            "Annual Budget",
            value=float(current_annual),
            min_value=0.0,
            format="%.2f",
            help="Set your annual budget for this category"
        )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save"):
                if not category:
                    st.error("Please select or enter a category")
                    return
                
                budget_data = {
                    "category": category,
                    "monthly": monthly,
                    "annual": annual
                }
                on_submit(budget_data)
        
        with col2:
            if st.form_submit_button("Cancel"):
                on_submit(None)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
