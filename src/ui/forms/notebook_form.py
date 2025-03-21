import streamlit as st
from typing import List, Dict, Any, Optional, Callable

def notebook_form(
    categories: List[str],
    existing_data: Optional[Dict[str, Any]],
    on_submit: Callable[[Optional[Dict[str, Any]]], None]
):
    """Form for adding/editing a notebook"""
    st.markdown("""
    <div class="modal-overlay">
    <div class="modal-content">
    """, unsafe_allow_html=True)
    
    st.subheader("Notebook Details")
    
    with st.form("notebook_form"):
        # Notebook name
        name = st.text_input(
            "Name",
            value=existing_data.get("name", "") if existing_data else "",
            placeholder="e.g., Vacation 2025, Home Renovation"
        ).strip()
        
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
        
        # Description
        description = st.text_area(
            "Description",
            value=existing_data.get("description", "") if existing_data else "",
            placeholder="Add details about this notebook"
        ).strip()
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save"):
                if not name:
                    st.error("Please enter a notebook name")
                    return
                if not category:
                    st.error("Please select or enter a category")
                    return
                
                notebook_data = {
                    "name": name,
                    "category": category,
                    "description": description
                }
                on_submit(notebook_data)
        
        with col2:
            if st.form_submit_button("Cancel"):
                on_submit(None)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
