"""
Data source selector component.
"""
import streamlit as st
from typing import Optional, Dict, Any
import pandas as pd
import os

from utils.file_utils import load_data
from app.managers import StorageManager

def render_data_source_selector(storage_manager: Optional[StorageManager] = None) -> Optional[pd.DataFrame]:
    """
    Render data source selection component.
    
    Args:
        storage_manager: Optional storage manager instance
        
    Returns:
        Selected DataFrame or None if no selection
    """
    # Initialize storage manager if needed
    if storage_manager is None:
        storage_manager = StorageManager()
    
    # Source selection
    source = st.radio(
        "Data Source",
        options=['Local Storage', 'Cloud Storage', 'Upload File', 'URL'],
        help="Select where to load data from"
    )
    
    selected_df = None
    selected_file = None
    
    if source == 'Local Storage':
        # List all files first to check available types
        all_files = storage_manager.list_files(
            path='data/dataset',  # Project's data directory
            pattern='*.csv,*.parquet',  # List both CSV and Parquet files
            include_local=True
        )
        
        if not all_files:
            st.warning("No data files found in data/dataset directory")
            return None
        
        # Filter out enriched files
        available_files = [f for f in all_files if not f['name'].startswith('Enriched_')]
        
        if not available_files:
            st.warning("No raw data files found")
            return None
        
        # Determine available file types
        file_types = []
        if any(f['name'].endswith('.csv') for f in available_files):
            file_types.append('CSV')
        if any(f['name'].endswith('.parquet') for f in available_files):
            file_types.append('Parquet')
        
        if not file_types:
            st.warning("No CSV or Parquet files found")
            return None
        
        # File type selection
        st.subheader("Select File Type")
        selected_type = st.radio(
            "Available file types",
            options=file_types,
            help="Select the type of file to load",
            horizontal=True
        )
        
        # Filter files by selected type
        files_to_show = [
            f for f in available_files 
            if f['name'].endswith(f".{selected_type.lower()}")
        ]
        
        # Format file options
        def format_file_option(file_info: Dict[str, Any]) -> str:
            size_mb = file_info['size'] / (1024 * 1024)
            name = file_info['name']
            
            # Extract metadata from filename
            # Expected format: Type_Symbol_Timeframe_StartDate_EndDate.ext
            try:
                name_without_ext = os.path.splitext(name)[0]
                parts = name_without_ext.split('_')
                if len(parts) >= 5:
                    data_type = parts[0]
                    symbol = parts[1]
                    timeframe = parts[2]
                    start_date = parts[3]
                    end_date = parts[4]
                    return f"{data_type} - {symbol} ({timeframe}) | {start_date} to {end_date} | {size_mb:.1f}MB"
            except Exception:
                pass
            
            # Fallback format if filename doesn't match expected pattern
            return f"{name} | {size_mb:.1f}MB"
        
        # File selection
        st.subheader("Select Data File")
        selected_file = st.selectbox(
            f"Available {selected_type} files",
            options=files_to_show,
            format_func=format_file_option,
            help="Choose a data file to load"
        )
        
        if selected_file:
            try:
                selected_df = load_data(selected_file['path'])
                
                # Show detailed success message
                name = selected_file['name']
                try:
                    name_without_ext = os.path.splitext(name)[0]
                    parts = name_without_ext.split('_')
                    if len(parts) >= 5:
                        data_type = parts[0]
                        symbol = parts[1]
                        timeframe = parts[2]
                        st.success(f"Loaded {data_type} data for {symbol} ({timeframe}) - {len(selected_df)} rows")
                    else:
                        st.success(f"Loaded {len(selected_df)} rows from {name}")
                except Exception:
                    st.success(f"Loaded {len(selected_df)} rows from {name}")
                    
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    elif source == 'Cloud Storage':
        if not storage_manager.has_external_storage:
            st.warning("No cloud storage configured. Please configure storage settings first.")
            if st.button("Go to Storage Configuration"):
                st.session_state['page'] = "Storage"
                st.rerun()
            return None
        
        # List cloud files
        cloud_files = storage_manager.list_files(
            pattern='*.csv,*.parquet',
            include_local=False
        )
        
        if not cloud_files:
            st.warning("No data files found in cloud storage")
            return None
        
        # Format file options
        def format_file_option(file_info: Dict[str, Any]) -> str:
            size_mb = file_info['size'] / (1024 * 1024)
            return f"{file_info['name']} ({size_mb:.1f}MB) - {file_info['modified'].strftime('%Y-%m-%d %H:%M')}"
        
        # File selection
        selected_file = st.selectbox(
            "Select File",
            options=cloud_files,
            format_func=format_file_option
        )
        
        if selected_file:
            try:
                # Download and load file
                local_path = storage_manager.load_file(
                    selected_file['path'],
                    is_remote=True
                )
                if local_path:
                    selected_df = load_data(local_path)
                    st.success(f"Loaded {len(selected_df)} rows from {selected_file['name']}")
                else:
                    st.error("Failed to download file from cloud storage")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    elif source == 'Upload File':
        uploaded_file = st.file_uploader(
            "Upload Data File",
            type=['csv', 'parquet'],
            help="Upload a CSV or Parquet file"
        )
        
        if uploaded_file:
            try:
                # Save uploaded file temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(
                    suffix=os.path.splitext(uploaded_file.name)[1],
                    delete=False
                ) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    
                # Load data
                selected_df = load_data(tmp.name)
                st.success(f"Loaded {len(selected_df)} rows from {uploaded_file.name}")
                
                # Clean up temp file
                os.unlink(tmp.name)
                
            except Exception as e:
                st.error(f"Error loading uploaded file: {str(e)}")
    
    else:  # URL
        st.info("For GitHub URLs, make sure to use the 'Raw' file URL")
        url = st.text_input(
            "Dataset URL",
            help="Enter the URL of a CSV or Parquet file (e.g., https://raw.githubusercontent.com/...)"
        )
        
        if url:
            # Validate URL
            if not url.lower().endswith(('.csv', '.parquet')):
                st.error("URL must point to a CSV or Parquet file")
                return None
                
            try:
                import requests
                import tempfile
                
                # Convert GitHub URLs to raw format if needed
                if 'github.com' in url and '/raw/' not in url:
                    url = url.replace('github.com', 'raw.githubusercontent.com')
                    url = url.replace('/blob/', '/')
                
                # Download file
                with st.spinner("Downloading file..."):
                    response = requests.get(url)
                    response.raise_for_status()  # Raise error for bad status codes
                    
                    # Get file extension from URL
                    file_ext = '.csv' if url.lower().endswith('.csv') else '.parquet'
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                        tmp.write(response.content)
                        
                    # Load data
                    selected_df = load_data(tmp.name)
                    st.success(f"Loaded {len(selected_df)} rows from URL")
                    
                    # Clean up temp file
                    os.unlink(tmp.name)
                    
            except requests.RequestException as e:
                st.error(f"Error downloading file: {str(e)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    return selected_df
