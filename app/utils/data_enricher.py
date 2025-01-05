import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
from .indicators import add_indicators_and_oscillators, add_advanced_indicators
from .temporal import add_temporal_features
from .market_regime import add_market_regime
from .liquidity_metrics import add_liquidity_metrics
from .volatility_metrics import add_volatility_metrics
from .market_value import add_market_value_metrics
from .patterns import add_candlestick_patterns

class DataEnricher:
    def __init__(self, df):
        self.df = df.copy()
        self.logger = logging.getLogger(__name__)
        self.total_steps = 8  # Total number of enrichment steps (basic indicators, advanced indicators, and 6 other steps)
        self.current_step = 0

    def log_progress(self, message):
        # Calculate progress as percentage of completed steps
        progress = ((self.current_step + 1) / self.total_steps) * 100
        # Ensure progress never exceeds 100%
        progress = min(100, progress)
        # Log with consistent format
        self.logger.info(f"Progress:{progress:.0f}% - {message}")
        # Increment step counter after logging
        self.current_step += 1

    def enrich(self):
        """
        Enrich the dataframe with various features
        """
        try:
            # Reset progress for new enrichment
            self.current_step = 0
            
            # Add basic technical indicators
            self.log_progress("Adicionando indicadores técnicos básicos...")
            self.df = add_indicators_and_oscillators(self.df)
            
            # Add advanced technical indicators
            self.log_progress("Adicionando indicadores técnicos avançados...")
            self.df = add_advanced_indicators(self.df)
            
            # Add temporal features
            self.log_progress("Adicionando características temporais...")
            self.df = add_temporal_features(self.df)
            
            # Add market regime features
            self.log_progress("Adicionando regime de mercado...")
            self.df = add_market_regime(self.df)
            
            # Add liquidity metrics
            self.log_progress("Adicionando métricas de liquidez...")
            self.df = add_liquidity_metrics(self.df)
            
            # Add volatility metrics
            self.log_progress("Adicionando métricas de volatilidade...")
            self.df = add_volatility_metrics(self.df)
            
            # Add market value metrics
            self.log_progress("Adicionando métricas de valor de mercado...")
            self.df = add_market_value_metrics(self.df)
            
            # Add candlestick patterns
            self.log_progress("Adicionando padrões de candlestick...")
            self.df = add_candlestick_patterns(self.df)
            
            return self.df

        except Exception as e:
            self.logger.error(f"Erro durante o enriquecimento: {str(e)}")
            raise

    def save_enriched_data(self, pair: str, timeframe: str, source_type: str, output_dir: str, file_format: str = 'parquet'):
        """
        Save enriched data with standardized filename format.
        
        Args:
            pair: Trading pair or symbol (e.g., 'BTCUSDT' or 'BTC_ETH_BNB')
            timeframe: Data timeframe (e.g., '1h', '4h', '1d')
            source_type: Data source type ('native' or 'finrl')
            output_dir: Directory to save enriched file
            file_format: Output file format ('parquet' or 'csv')
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename
        filename = f"enriched_{pair}_{timeframe}_{source_type}_{timestamp}.{file_format}"
        output_path = os.path.join(output_dir, filename)
        
        self.logger.info(f"\nSaving enriched data:")
        self.logger.info(f"Pair: {pair}")
        self.logger.info(f"Timeframe: {timeframe}")
        self.logger.info(f"Source: {source_type}")
        self.logger.info(f"Format: {file_format}")
        self.logger.info(f"Path: {output_path}")
        
        # Save based on format
        if file_format == 'parquet':
            self.df.to_parquet(output_path)
        else:  # csv
            self.df.to_csv(output_path, index=False)
        
        # Verify file was saved
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            self.logger.info(f"File saved successfully ({file_size:,} bytes)")
            return output_path
        else:
            raise IOError(f"Failed to save file to {output_path}")
