"""
Storage selection component.
"""
import streamlit as st
from typing import Optional, Dict

def render_storage_selector() -> Optional[Dict[str, str]]:
    """
    Render storage selection component.
    
    Returns:
        Dict with storage configuration or None if using local storage:
        {
            'provider': Storage provider type ('google_drive', 'onedrive', or 's3')
            'path': Storage path where files will be saved
        }
    """
    use_external = st.checkbox(
        "Use External Storage",
        help="Save data to external storage provider instead of local storage"
    )
    
    if use_external:
        if 'storage_provider' not in st.session_state:
            st.warning("No storage provider configured. Please configure storage settings first.")
            if st.button("Configure Storage"):
                # Update navigation in parent page
                st.session_state['page'] = "Storage"
                st.rerun()
            return None
            
        # Show current storage info
        provider = st.session_state.storage_provider
        st.info(f"Using {provider.title()} storage")
        
        # Let user choose storage path
        if provider == 'google_drive':
            path = st.text_input(
                "Google Drive Folder",
                value="MLTrade/Data",
                help="Path to Google Drive folder (folders will be created if they don't exist)"
            )
        elif provider == 'onedrive':
            path = st.text_input(
                "OneDrive Folder",
                value="MLTrade/Data",
                help="Path to OneDrive folder (folders will be created if they don't exist)"
            )
        else:  # S3
            path = st.text_input(
                "S3 Path",
                value="mltrade/data",
                help="Path in S3 bucket (folders will be created if they don't exist)"
            )
        
        return {
            'provider': provider,
            'path': path.strip('/')
        }
    
    return None
