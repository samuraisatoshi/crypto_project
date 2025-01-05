"""
Streamlit application entry point.
"""
import streamlit as st

from app import (
    render_backtest_page,
    render_download_page,
    render_enrich_page,
    render_storage_config_page
)

def main():
    """Main application."""
    st.set_page_config(
        page_title="Crypto Trading",
        page_icon="📈",
        layout="wide"
    )
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Download", "Enrich", "Backtest", "Storage"],
        format_func=lambda x: f"{x} Data" if x in ["Download", "Enrich"] else 
                   f"{x} Configuration" if x == "Storage" else x
    )
    
    # Render selected page
    if page == "Download":
        render_download_page()
    elif page == "Enrich":
        render_enrich_page()
    elif page == "Storage":
        render_storage_config_page()
    else:  # Backtest
        render_backtest_page()

if __name__ == "__main__":
    main()
