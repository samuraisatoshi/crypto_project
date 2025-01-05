"""
File utility functions.
"""
import os
import pandas as pd

def get_available_files(directory, formats=None):
    """
    Get list of files in directory with specified formats.
    
    Args:
        directory: Directory to search
        formats: List of file extensions (e.g., ['.csv', '.parquet']). If None, defaults to ['.csv']
    
    Returns:
        List of filenames that match the specified formats
    """
    if not os.path.exists(directory):
        return []
    
    if formats is None:
        formats = ['.csv']
    
    return [f for f in os.listdir(directory) 
            if any(f.endswith(fmt) for fmt in formats)]

def ensure_directory_exists(directory):
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path to check/create
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_standardized_filename(symbol, timeframe, start_date, end_date, format_type, file_format='.csv'):
    """
    Create standardized filename for data files.
    
    Args:
        symbol: Trading pair or symbol string
        timeframe: Timeframe string (e.g., '1h', '4h', '1d')
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        format_type: Type of data format (e.g., 'native', 'finrl')
        file_format: File extension (default: '.csv')
    
    Returns:
        Standardized filename string
    """
    prefix = 'finrl_' if format_type == 'finrl' else ''
    return f"{prefix}{symbol}_{timeframe}_{start_date}_{end_date}_{format_type}{file_format}"

def parse_filename(filename):
    """
    Parse information from standardized filename.
    
    Args:
        filename: Filename to parse
    
    Returns:
        Dictionary containing parsed information (symbol, timeframe, dates, format)
    """
    # Remove file extension
    name = filename.rsplit('.', 1)[0]
    parts = name.split('_')
    
    # Handle finrl format
    if parts[0] == 'finrl':
        # Find timeframe index
        timeframe_idx = next(i for i, part in enumerate(parts) 
                           if part in ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'])
        return {
            'symbol': '_'.join(parts[1:timeframe_idx]),
            'timeframe': parts[timeframe_idx],
            'start_date': parts[timeframe_idx + 1],
            'end_date': parts[timeframe_idx + 2],
            'format': parts[-1]
        }
    else:
        # Native format
        return {
            'symbol': parts[0],
            'timeframe': parts[1],
            'start_date': parts[2],
            'end_date': parts[3],
            'format': parts[-1]
        }

def load_data_file(file_path):
    """
    Load data from file based on extension.
    
    Args:
        file_path: Path to data file
    
    Returns:
        Pandas DataFrame with loaded data
    """
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    else:  # csv
        df = pd.read_csv(file_path)
    
    # Ensure timestamp column exists and is datetime
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()
        df = df.rename(columns={'index': 'timestamp'})
    
    if 'timestamp' not in df.columns:
        df = df.reset_index()
        df = df.rename(columns={'index': 'timestamp'})
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df
