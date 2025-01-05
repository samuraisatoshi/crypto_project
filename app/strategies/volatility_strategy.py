"""
Volatility-based trading strategy implementation.
"""
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from utils.indicators import calculate_atr, calculate_bollinger_bands
from utils.volatility_metrics import calculate_volatility_ratio
from utils.logging_helper import LoggingHelper
from .base import BaseStrategy

class VolatilityStrategy(BaseStrategy):
    def __init__(self,
                atr_period: int = 14,
                bb_period: int = 20,
                bb_std: float = 2.0,
                vol_lookback: int = 20,
                vol_threshold: float = 1.5,  # Threshold para expansão de volatilidade
                range_threshold: float = 0.8,  # % do ATR para considerar range significativo
                confidence_threshold: float = 0.6):
        """
        Initialize Volatility strategy.
        
        Args:
            atr_period: Period for ATR calculation
            bb_period: Period for Bollinger Bands
            bb_std: Standard deviations for Bollinger Bands
            vol_lookback: Lookback period for volatility comparison
            vol_threshold: Minimum volatility expansion ratio
            range_threshold: Minimum candle range as % of ATR
            confidence_threshold: Minimum confidence level for signals
        """
        super().__init__()
        self.atr_period = atr_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.vol_lookback = vol_lookback
        self.vol_threshold = vol_threshold
        self.range_threshold = range_threshold
        self.confidence_threshold = confidence_threshold
        
        LoggingHelper.log(f"Initialized Volatility Strategy with parameters:")
        LoggingHelper.log(f"ATR Period: {atr_period}")
        LoggingHelper.log(f"BB Period: {bb_period}")
        LoggingHelper.log(f"BB Std: {bb_std}")
        LoggingHelper.log(f"Volatility Lookback: {vol_lookback}")
        LoggingHelper.log(f"Volatility Threshold: {vol_threshold}")
        LoggingHelper.log(f"Range Threshold: {range_threshold}")
        LoggingHelper.log(f"Confidence Threshold: {confidence_threshold}")

    def analyze_volatility(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze current volatility conditions.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            Dictionary with volatility metrics
        """
        # Calcular razão de volatilidade atual/histórica
        current_vol = df['atr'].iloc[-1]
        historical_vol = df['atr'].tail(self.vol_lookback).mean()
        vol_ratio = current_vol / historical_vol
        
        # Calcular range da vela atual como % do ATR
        current = df.iloc[-1]
        candle_range = current['high'] - current['low']
        range_ratio = candle_range / current_vol
        
        # Verificar posição em relação às Bollinger Bands
        bb_position = (current['close'] - current['bb_lower']) / (current['bb_upper'] - current['bb_lower'])
        
        # Detectar squeeze das Bollinger Bands
        bb_width = (current['bb_upper'] - current['bb_lower']) / current['bb_middle']
        historical_width = ((df['bb_upper'] - df['bb_lower']) / df['bb_middle']).tail(self.vol_lookback).mean()
        squeeze_ratio = bb_width / historical_width
        
        return {
            'vol_ratio': vol_ratio,
            'range_ratio': range_ratio,
            'bb_position': bb_position,
            'squeeze_ratio': squeeze_ratio,
            'is_high_vol': vol_ratio > self.vol_threshold,
            'is_significant_range': range_ratio > self.range_threshold
        }

    def detect_breakout(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect potential breakout direction.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            str: 'up', 'down', or None
        """
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Verificar rompimento das Bollinger Bands
        if current['close'] > current['bb_upper'] and previous['close'] <= previous['bb_upper']:
            return 'up'
        elif current['close'] < current['bb_lower'] and previous['close'] >= previous['bb_lower']:
            return 'down'
            
        return None

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate trading signals based on volatility analysis.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Calculate indicators
        df['atr'] = calculate_atr(df['high'], df['low'], df['close'], self.atr_period)
        bb_data = calculate_bollinger_bands(df['close'], self.bb_period, self.bb_std)
        df['bb_upper'] = bb_data['bb_upper']
        df['bb_middle'] = bb_data['bb_middle']
        df['bb_lower'] = bb_data['bb_lower']
        
        # Get current values
        current = df.iloc[-1]
        
        # Analyze volatility conditions
        vol_analysis = self.analyze_volatility(df)
        
        # Detect breakout
        breakout = self.detect_breakout(df)
        
        # Calculate base confidence from volatility
        base_confidence = min(vol_analysis['vol_ratio'] / self.vol_threshold, 1.0)
        
        # Adjust confidence based on range and squeeze
        if vol_analysis['is_significant_range']:
            base_confidence *= 1.2
        if vol_analysis['squeeze_ratio'] < 0.8:  # Squeeze setup
            base_confidence *= 1.1
            
        confidence = min(base_confidence, 1.0)
        
        # Generate signals based on volatility and breakouts
        if breakout == 'up' and vol_analysis['is_high_vol']:
            if confidence >= self.confidence_threshold:
                signals.append({
                    'type': 'long',
                    'confidence': confidence,
                    'price': current['close'],
                    'pattern': 'volatility_breakout_up',
                    'atr': current['atr']
                })
                LoggingHelper.log(f"Generated bullish breakout signal with confidence {confidence:.2f}")
                
        elif breakout == 'down' and vol_analysis['is_high_vol']:
            if confidence >= self.confidence_threshold:
                signals.append({
                    'type': 'short',
                    'confidence': confidence,
                    'price': current['close'],
                    'pattern': 'volatility_breakout_down',
                    'atr': current['atr']
                })
                LoggingHelper.log(f"Generated bearish breakout signal with confidence {confidence:.2f}")
        
        # Gerar sinais de mean reversion em condições específicas
        elif vol_analysis['squeeze_ratio'] < 0.7:  # Forte squeeze
            if vol_analysis['bb_position'] > 0.9:  # Próximo à banda superior
                signals.append({
                    'type': 'short',
                    'confidence': confidence * 0.8,  # Reduzir confiança para mean reversion
                    'price': current['close'],
                    'pattern': 'volatility_mean_reversion_high',
                    'atr': current['atr']
                })
                LoggingHelper.log(f"Generated mean reversion short signal with confidence {confidence*0.8:.2f}")
                
            elif vol_analysis['bb_position'] < 0.1:  # Próximo à banda inferior
                signals.append({
                    'type': 'long',
                    'confidence': confidence * 0.8,
                    'price': current['close'],
                    'pattern': 'volatility_mean_reversion_low',
                    'atr': current['atr']
                })
                LoggingHelper.log(f"Generated mean reversion long signal with confidence {confidence*0.8:.2f}")
        
        return signals

    def should_exit(self, df: pd.DataFrame, current_idx: int, position: Dict) -> bool:
        """
        Determine if current position should be exited based on volatility.
        
        Args:
            df: DataFrame with price data
            current_idx: Current index in DataFrame
            position: Current position information
            
        Returns:
            bool: True if position should be exited
        """
        if current_idx < 1:
            return False
            
        current = df.iloc[current_idx]
        
        # Analyze current volatility
        vol_analysis = self.analyze_volatility(
            df.iloc[:current_idx + 1]
        )
        
        # Exit long position
        if position['type'] == 'long':
            # Exit on volatility contraction ou mean reversion
            if (vol_analysis['vol_ratio'] < 0.7 or  # Contração significativa
                current['close'] < current['bb_middle']):  # Abaixo da média
                LoggingHelper.log("Exiting long position on volatility contraction")
                return True
                
        # Exit short position
        elif position['type'] == 'short':
            # Exit on volatility contraction ou mean reversion
            if (vol_analysis['vol_ratio'] < 0.7 or  # Contração significativa
                current['close'] > current['bb_middle']):  # Acima da média
                LoggingHelper.log("Exiting short position on volatility contraction")
                return True
        
        return False

    def calculate_position_size(self, df: pd.DataFrame, signal: Dict) -> float:
        """
        Calculate position size based on volatility and signal confidence.
        
        Args:
            df: DataFrame with price data
            signal: Signal dictionary with confidence level
            
        Returns:
            float: Position size multiplier (0.0 to 1.0)
        """
        # Base size from signal confidence
        base_size = 0.5
        
        # Analyze volatility
        vol_analysis = self.analyze_volatility(df)
        
        # Adjust based on volatility conditions
        vol_multiplier = 1.0
        if vol_analysis['vol_ratio'] > self.vol_threshold:
            vol_multiplier = 0.8  # Reduzir exposição em alta volatilidade
        elif vol_analysis['squeeze_ratio'] < 0.8:
            vol_multiplier = 1.2  # Aumentar exposição em squeeze
            
        # Adjust based on range significance
        range_multiplier = 1.2 if vol_analysis['is_significant_range'] else 0.8
        
        return min(base_size * vol_multiplier * range_multiplier * signal['confidence'], 1.0)
