"""
Enrich manager for handling data enrichment operations.
"""
from typing import Optional, Dict, Any, List, Union, Tuple
import streamlit as st
import pandas as pd
import os
from datetime import datetime

from utils.data_enricher import DataEnricher
from utils.file_utils import load_data, save_data
from utils.logging_helper import LoggingHelper
from .storage_manager import StorageManager

class EnrichManager:
    """Manager for handling data enrichment operations."""
    
    def __init__(self, storage_manager: Optional[StorageManager] = None):
        """
        Initialize enrich manager.
        
        Args:
            storage_manager: Optional storage manager instance
        """
        self.enricher = DataEnricher()
        self.storage = storage_manager or StorageManager()
    
    def set_storage(self, storage_info: Optional[Dict[str, str]]):
        """Set storage configuration."""
        self.storage.set_storage(storage_info)
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List available datasets from configured storage."""
        return self.storage.list_files(
            pattern='*.{csv,parquet}'
        )
    
    def load_dataset(self, dataset_info: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Load dataset from storage."""
        try:
            file_path = self.storage.load_file(
                dataset_info['path'],
                is_remote=dataset_info['storage'] == 'external'
            )
            if file_path:
                LoggingHelper.log(f"Loading dataset from {file_path}")
                return load_data(file_path)
            LoggingHelper.log("Failed to load dataset: File path not found")
            return None
        except Exception as e:
            LoggingHelper.log(f"Error loading dataset: {str(e)}")
            return None
    
    def enrich_data(
        self,
        df: pd.DataFrame,
        enrichments: List[Union[str, Tuple[str, Dict]]],
        save_path: Optional[str] = None,
        format: str = 'csv'
    ) -> Optional[Dict[str, Any]]:
        """Enrich dataset with selected indicators."""
        # Add symbol and timeframe if not present
        df = df.copy()
        if 'symbol' not in df.columns:
            LoggingHelper.log("Adding default 'symbol' column")
            df['symbol'] = 'UNKNOWN'
        if 'timeframe' not in df.columns:
            LoggingHelper.log("Adding default 'timeframe' column")
            df['timeframe'] = '1d'
        
        # Store original symbol and timeframe
        original_symbol = df['symbol'].iloc[0]
        original_timeframe = df['timeframe'].iloc[0]
        
        LoggingHelper.log(f"Processing data for {original_symbol} ({original_timeframe})")
        
        # Apply enrichments (cached)
        # Generate cache key from enrichments and data shape
        cache_key = str(hash(f"{str(enrichments)}_{df.shape}"))
        
        result = self._enrich_data_impl(
            df.copy(),  # Pass copy to avoid modifying original
            enrichments,  # Pass enrichments directly
            cache_key  # Pass cache key
        )
        
        if result is None:
            return None
            
        # Ensure symbol and timeframe are preserved
        result['df']['symbol'] = original_symbol
        result['df']['timeframe'] = original_timeframe
        
        # Save if path provided
        if save_path:
            result['filename'] = self._save_enriched_data(
                result['df'],
                df,
                save_path,
                format
            )
        
        return result
    
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def _enrich_data_impl(
        _df: pd.DataFrame,
        _enrichments: List[Union[str, Tuple[str, Dict]]],
        _cache_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Apply enrichments to dataset."""
        try:
            enricher = DataEnricher()
            # Generate cache key from enrichments
            if _cache_key is None:
                _cache_key = str(hash(str(_enrichments)))
            
            # Log enrichments before processing
            LoggingHelper.log("Processing enrichments")
            for e in _enrichments:
                if isinstance(e, tuple):
                    name, config = e
                    LoggingHelper.log(f"- {name}: {config}")
                else:
                    LoggingHelper.log(f"- {e}")
            
            result = enricher.enrich_data(_df, _enrichments)
            
            # Log result info
            if result:
                LoggingHelper.log("Enrichment result")
                LoggingHelper.log(f"Added columns: {result['info']['columns']}")
            
            return result
        except Exception as e:
            st.error(f"Error enriching data: {str(e)}")
            return None
    
    def _save_enriched_data(
        self,
        enriched_df: pd.DataFrame,
        original_df: pd.DataFrame,
        save_path: str,
        format: str = 'csv'
    ) -> str:
        """Save enriched data to storage."""
        # Get metadata from original DataFrame
        symbol = original_df['symbol'].iloc[0]
        timeframe = original_df['timeframe'].iloc[0]
        
        # Get date range
        if isinstance(enriched_df.index, pd.DatetimeIndex):
            start_date = enriched_df.index[0]
            end_date = enriched_df.index[-1]
        elif 'date' in enriched_df.columns:
            start_date = pd.to_datetime(enriched_df['date'].iloc[0])
            end_date = pd.to_datetime(enriched_df['date'].iloc[-1])
        else:
            raise ValueError("Enriched data must have a DatetimeIndex or 'date' column")
        
        # Format dates
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        try:
            # Save locally first
            LoggingHelper.log("Saving enriched data locally")
            local_filename = save_data(
                enriched_df,
                symbol=symbol,
                timeframe=timeframe,
                prefix='Enriched',
                suffix=f"{start_str}_{end_str}",
                format=format,
                directory='data/dataset'
            )
            
            # Save to external storage if configured
            if self.storage.has_external_storage:
                LoggingHelper.log("Saving to external storage")
                remote_path = f"enriched/{os.path.basename(local_filename)}"
                return self.storage.save_file(local_filename, remote_path)
            
            return local_filename
        except Exception as e:
            LoggingHelper.log(f"Error saving enriched data: {str(e)}")
            raise
