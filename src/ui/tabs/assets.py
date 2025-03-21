import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict, Any, Callable
from ...utils.formatting import format_currency

def display_assets_tab(
    assets: List[Dict[str, Any]],
    categories: List[str],
    on_add_asset: Callable[[], None],
    on_edit_asset: Callable[[Dict[str, Any]], None],
    on_delete_asset: Callable[[Dict[str, Any]], None]
):
    """Display the assets tab content"""
    # Add asset button
    st.button("➕ Add Asset", on_click=on_add_asset, type="primary")
    
    if not assets:
        st.info("No assets added yet. Click the button above to add your first asset!")
        return
    
    # Group assets by category
    assets_by_category = {}
    total_value = 0
    
    for asset in assets:
        category = asset.get("category", "Uncategorized")
        if category not in assets_by_category:
            assets_by_category[category] = []
        assets_by_category[category].append(asset)
        total_value += asset.get("value", 0)
    
    # Display total value
    st.metric("Total Assets Value", format_currency(total_value))
    
    # Asset distribution chart
    st.subheader("Asset Distribution")
    chart_data = []
    for category, category_assets in assets_by_category.items():
        category_value = sum(a.get("value", 0) for a in category_assets)
        chart_data.append({
            "category": category,
            "value": category_value,
            "percentage": (category_value / total_value * 100) if total_value > 0 else 0
        })
    
    if chart_data:
        df = pd.DataFrame(chart_data)
        
        # Pie chart
        pie_chart = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q", title="Value", format="$,.2f"),
                alt.Tooltip("percentage:Q", title="Percentage", format=".1f")
            ]
        ).properties(width=400, height=400)
        
        st.altair_chart(pie_chart, use_container_width=True)
    
    # Display assets by category
    st.subheader("Assets by Category")
    for category, category_assets in assets_by_category.items():
        with st.expander(f"{category} ({len(category_assets)} assets)"):
            for asset in category_assets:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{asset['name']}**")
                    if asset.get("description"):
                        st.write(asset["description"])
                with col2:
                    st.write(format_currency(asset.get("value", 0)))
                with col3:
                    col3_1, col3_2 = st.columns(2)
                    with col3_1:
                        st.button("✏️", key=f"edit_asset_{asset['id']}", on_click=lambda a=asset: on_edit_asset(a))
                    with col3_2:
                        st.button("🗑️", key=f"delete_asset_{asset['id']}", on_click=lambda a=asset: on_delete_asset(a))
