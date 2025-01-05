"""
Download data page.
"""
import streamlit as st
from datetime import datetime
import pytz

from app.managers import DownloadManager
from app.components.storage import render_storage_selector

def render():
    """Render download page."""
    st.title("Download Data")
    
    # Initialize manager in session state if needed
    if 'download_manager' not in st.session_state:
        st.session_state.download_manager = DownloadManager()
    
    # Format selection
    data_format = st.radio(
        "Data Format",
        options=['Native', 'FinRL'],
        help="Native: Single asset OHLCV format\nFinRL: Multi-asset format for reinforcement learning"
    )
    
    # Symbol input based on format
    if data_format == 'Native':
        symbol = st.text_input("Symbol", value="BTCUSDT")
        symbols = [symbol]
    else:
        symbols_text = st.text_area(
            "Symbols (one per line)",
            value="BTCUSDT\nETHUSDT\nBNBUSDT",
            help="Enter multiple symbols, one per line"
        )
        symbols = [s.strip() for s in symbols_text.split('\n') if s.strip()]
    
    # Timeframe selection
    timeframe = st.selectbox(
        "Timeframe",
        options=['1m', '5m', '15m', '1h', '4h', '1d'],
        index=2  # Default to 15m
    )
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2017, 10, 1).date(),
            help="Data download start date"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2024, 12, 31).date(),
            help="Data download end date"
        )
    
    # Storage selection
    storage_info = render_storage_selector()
    
    # Download button
    if st.button("Download Data"):
        # Configure storage
        st.session_state.download_manager.set_storage(storage_info)
        try:
            with st.spinner("Downloading data..."):
                if data_format == 'Native':
                    # Single symbol download
                    result = st.session_state.download_manager.download_data(
                        symbol=symbols[0],
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date,
                        format='native'
                    )
                else:
                    # Multi-symbol download
                    result = st.session_state.download_manager.download_multi_symbol(
                        symbols=symbols,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                
                if result:
                    # Store in session state
                    st.session_state['data'] = result['df']
                    
                    # Show success message
                    st.success(f"Data saved to {result['filename']}")
                    
                    # Show data preview
                    st.subheader("Data Preview")
                    st.dataframe(result['df'].head())
                    
                    # Show data info
                    st.subheader("Data Info")
                    st.write(f"Total rows: {result['info']['rows']}")
                    st.write(f"Date range: {result['info']['start_date']} to {result['info']['end_date']}")
                    
                    if data_format == 'FinRL':
                        st.write(f"Symbols: {', '.join(result['info']['symbols'])}")
                else:
                    st.error("No data found for the selected parameters")
                
        except Exception as e:
            st.error(f"Error downloading data: {str(e)}")
            st.exception(e)
