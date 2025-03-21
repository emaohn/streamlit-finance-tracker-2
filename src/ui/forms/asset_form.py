import streamlit as st
from typing import List, Dict, Any, Optional, Callable

def asset_form(
    categories: List[str],
    existing_data: Optional[Dict[str, Any]],
    on_submit: Callable[[Dict[str, Any]], None]
):
    """Form for adding/editing an asset"""
    st.markdown("""
    <div class="modal-overlay">
    <div class="modal-content">
    """, unsafe_allow_html=True)
    
    st.subheader("Asset Details")
    
    with st.form("asset_form"):
        # Asset name
        name = st.text_input(
            "Name",
            value=existing_data.get("name", "") if existing_data else "",
            placeholder="e.g., Car, House, Stocks"
        )
        
        # Asset value
        value = st.number_input(
            "Value",
            value=float(existing_data.get("value", 0)) if existing_data else 0.0,
            min_value=0.0,
            format="%.2f",
            help="Current value of the asset"
        )
        
        # Asset category
        category_options = [""] + categories if categories else [""]
        category = st.selectbox(
            "Category",
            options=category_options,
            index=category_options.index(existing_data.get("category", "")) if existing_data and existing_data.get("category") in category_options else 0,
        )
        
        # New category input if "Other" is selected
        if not category:
            category = st.text_input("New Category", placeholder="Enter a new category")
        
        # Description
        description = st.text_area(
            "Description",
            value=existing_data.get("description", "") if existing_data else "",
            placeholder="Add any additional details about the asset"
        )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save"):
                if not name:
                    st.error("Please enter an asset name")
                    return
                if not category:
                    st.error("Please select or enter a category")
                    return
                
                asset_data = {
                    "name": name,
                    "value": value,
                    "category": category,
                    "description": description
                }
                on_submit(asset_data)
        
        with col2:
            if st.form_submit_button("Cancel"):
                on_submit(None)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
