"""
Candlestick pattern detection module.
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from utils.logging_helper import LoggingHelper

def is_doji(open_price: float, high: float, low: float, close: float, threshold: float = 0.1) -> bool:
    """
    Check if candle is a doji pattern.
    
    Args:
        open_price: Opening price
        high: High price
        low: Low price
        close: Closing price
        threshold: Maximum body/wick ratio to consider as doji
        
    Returns:
        bool: True if candle is a doji
    """
    body = abs(close - open_price)
    upper_wick = high - max(open_price, close)
    lower_wick = min(open_price, close) - low
    
    if body == 0:
        return True
        
    body_to_wick_ratio = body / (upper_wick + lower_wick) if (upper_wick + lower_wick) > 0 else float('inf')
    return body_to_wick_ratio <= threshold

def is_hammer(open_price: float, high: float, low: float, close: float) -> bool:
    """
    Check if candle is a hammer pattern.
    
    Args:
        open_price: Opening price
        high: High price
        low: Low price
        close: Closing price
        
    Returns:
        bool: True if candle is a hammer
    """
    body = abs(close - open_price)
    upper_wick = high - max(open_price, close)
    lower_wick = min(open_price, close) - low
    
    if body == 0:
        return False
        
    # Lower wick should be at least 2x the body
    if lower_wick < body * 2:
        return False
        
    # Upper wick should be small
    if upper_wick > body * 0.5:
        return False
        
    return True

def is_shooting_star(open_price: float, high: float, low: float, close: float) -> bool:
    """
    Check if candle is a shooting star pattern.
    
    Args:
        open_price: Opening price
        high: High price
        low: Low price
        close: Closing price
        
    Returns:
        bool: True if candle is a shooting star
    """
    body = abs(close - open_price)
    upper_wick = high - max(open_price, close)
    lower_wick = min(open_price, close) - low
    
    if body == 0:
        return False
        
    # Upper wick should be at least 2x the body
    if upper_wick < body * 2:
        return False
        
    # Lower wick should be small
    if lower_wick > body * 0.5:
        return False
        
    return True

def is_engulfing(current: Dict[str, float], previous: Dict[str, float]) -> Optional[str]:
    """
    Check if current candle engulfs previous candle.
    
    Args:
        current: Current candle OHLC prices
        previous: Previous candle OHLC prices
        
    Returns:
        str: 'bullish', 'bearish', or None
    """
    current_body = current['close'] - current['open']
    previous_body = previous['close'] - previous['open']
    
    # Must be opposite colors
    if (current_body * previous_body >= 0):
        return None
        
    if current_body > 0:  # Current is bullish
        if (current['open'] <= previous['close'] and
            current['close'] >= previous['open']):
            return 'bullish'
    else:  # Current is bearish
        if (current['open'] >= previous['close'] and
            current['close'] <= previous['open']):
            return 'bearish'
            
    return None

def find_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find candlestick patterns in price data.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with pattern columns added
    """
    LoggingHelper.log("Finding candlestick patterns...")
    
    # Add pattern columns
    df['doji'] = df.apply(lambda x: is_doji(x['open'], x['high'], x['low'], x['close']), axis=1)
    df['hammer'] = df.apply(lambda x: is_hammer(x['open'], x['high'], x['low'], x['close']), axis=1)
    df['shooting_star'] = df.apply(lambda x: is_shooting_star(x['open'], x['high'], x['low'], x['close']), axis=1)
    
    # Find engulfing patterns
    engulfing = []
    for i in range(len(df)):
        if i == 0:
            engulfing.append(None)
            continue
            
        current = {
            'open': df.iloc[i]['open'],
            'high': df.iloc[i]['high'],
            'low': df.iloc[i]['low'],
            'close': df.iloc[i]['close']
        }
        
        previous = {
            'open': df.iloc[i-1]['open'],
            'high': df.iloc[i-1]['high'],
            'low': df.iloc[i-1]['low'],
            'close': df.iloc[i-1]['close']
        }
        
        engulfing.append(is_engulfing(current, previous))
    
    df['engulfing'] = engulfing
    
    LoggingHelper.log("Found patterns:")
    LoggingHelper.log(f"Doji: {df['doji'].sum()}")
    LoggingHelper.log(f"Hammer: {df['hammer'].sum()}")
    LoggingHelper.log(f"Shooting Star: {df['shooting_star'].sum()}")
    LoggingHelper.log(f"Engulfing: {df['engulfing'].count()}")
    
    return df

def get_pattern_signals(df: pd.DataFrame) -> List[Dict]:
    """
    Generate trading signals from candlestick patterns.
    
    Args:
        df: DataFrame with pattern columns
        
    Returns:
        List of signal dictionaries
    """
    signals = []
    
    # Check latest candle
    current = df.iloc[-1]
    
    # Bullish signals
    if current['hammer']:
        signals.append({
            'type': 'long',
            'confidence': 0.6,
            'price': current['close'],
            'pattern': 'hammer'
        })
        
    if current['engulfing'] == 'bullish':
        signals.append({
            'type': 'long', 
            'confidence': 0.7,
            'price': current['close'],
            'pattern': 'bullish_engulfing'
        })
        
    # Bearish signals
    if current['shooting_star']:
        signals.append({
            'type': 'short',
            'confidence': 0.6,
            'price': current['close'],
            'pattern': 'shooting_star'
        })
        
    if current['engulfing'] == 'bearish':
        signals.append({
            'type': 'short',
            'confidence': 0.7,
            'price': current['close'],
            'pattern': 'bearish_engulfing'
        })
        
    # Doji signals depend on trend
    if current['doji']:
        # Check trend using last 5 candles
        trend = 'up' if df['close'].tail(5).is_monotonic_increasing else 'down'
        
        if trend == 'up':
            signals.append({
                'type': 'short',
                'confidence': 0.5,
                'price': current['close'],
                'pattern': 'doji_top'
            })
        else:
            signals.append({
                'type': 'long',
                'confidence': 0.5,
                'price': current['close'],
                'pattern': 'doji_bottom'
            })
            
    return signals
