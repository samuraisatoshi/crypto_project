"""
Binance client for data download.
"""
import pandas as pd
from datetime import datetime
from binance.client import Client
from typing import Optional

class BinanceClient:
    """Client for downloading data from Binance."""
    
    def __init__(self):
        """Initialize client."""
        self.client = Client()
    
    def download_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Download historical klines data."""
        try:
            # Convert timeframe to interval
            interval = self._get_interval(timeframe)
            
            # Download klines
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_date.strftime('%Y-%m-%d'),
                end_str=end_date.strftime('%Y-%m-%d')
            )
            
            if not klines:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Set index
            df.set_index('timestamp', inplace=True)
            
            # Add symbol and timeframe
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            
            return df
            
        except Exception as e:
            raise Exception(f"Error downloading data: {str(e)}")
    
    def _get_interval(self, timeframe: str) -> str:
        """Convert timeframe to Binance interval."""
        intervals = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '1d': Client.KLINE_INTERVAL_1DAY
        }
        
        if timeframe not in intervals:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        return intervals[timeframe]
