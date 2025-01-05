import pandas as pd
import numpy as np

class TrendAnalysis:
    """
    Classe utilitária para análise de tendências.
    Fornece métodos comuns que podem ser usados por diferentes estratégias.
    """
    @staticmethod
    def detect_trend(df: pd.DataFrame, 
                    ema_short: int = 8,
                    ema_medium: int = 21,
                    ema_long: int = 200,
                    strict: bool = False) -> pd.Series:
        """
        Detecta tendência usando EMAs.
        
        Args:
            df: DataFrame com dados OHLCV e EMAs
            ema_short: Período da EMA curta
            ema_medium: Período da EMA média
            ema_long: Período da EMA longa
            strict: Se True, usa critérios mais estritos
            
        Returns:
            pd.Series: 1 (alta), -1 (baixa), 0 (neutro)
        """
        trend = pd.Series(0, index=df.index)
        
        if strict:
            # Critérios estritos: EMAs alinhadas em ordem
            uptrend = (df[f'ema_{ema_short}'] > df[f'ema_{ema_medium}']) & \
                     (df[f'ema_{ema_medium}'] > df[f'ema_{ema_long}']) & \
                     (df['close'] > df[f'ema_{ema_long}'])
                     
            downtrend = (df[f'ema_{ema_short}'] < df[f'ema_{ema_medium}']) & \
                       (df[f'ema_{ema_medium}'] < df[f'ema_{ema_long}']) & \
                       (df['close'] < df[f'ema_{ema_long}'])
        else:
            # Critérios flexíveis: EMA curta e preço apenas
            uptrend = (df[f'ema_{ema_short}'] > df[f'ema_{ema_medium}']) & \
                     (df['close'] > df[f'ema_{ema_long}'])
                     
            downtrend = (df[f'ema_{ema_short}'] < df[f'ema_{ema_medium}']) & \
                       (df['close'] < df[f'ema_{ema_long}'])
        
        trend[uptrend] = 1
        trend[downtrend] = -1
        
        return trend
    
    @staticmethod
    def detect_swing_points(df: pd.DataFrame, 
                          lookback: int = 5,
                          price_col: str = 'close') -> tuple:
        """
        Detecta pontos de swing (pivôs) no preço.
        
        Args:
            df: DataFrame com dados OHLCV
            lookback: Número de barras para olhar para cada lado
            price_col: Coluna de preço a usar
            
        Returns:
            tuple: (swing_highs, swing_lows) Series booleanas
        """
        highs = pd.Series(False, index=df.index)
        lows = pd.Series(False, index=df.index)
        
        for i in range(lookback, len(df) - lookback):
            price_window = df[price_col].iloc[i-lookback:i+lookback+1]
            center_price = price_window.iloc[lookback]
            
            # Swing high
            if center_price > price_window.iloc[:lookback].max() and \
               center_price > price_window.iloc[lookback+1:].max():
                highs.iloc[i] = True
            
            # Swing low
            if center_price < price_window.iloc[:lookback].min() and \
               center_price < price_window.iloc[lookback+1:].min():
                lows.iloc[i] = True
                
        return highs, lows
    
    @staticmethod
    def calculate_momentum(df: pd.DataFrame,
                         col: str = 'close',
                         period: int = 14) -> pd.Series:
        """
        Calcula momentum do preço.
        
        Args:
            df: DataFrame com dados
            col: Coluna para calcular momentum
            period: Período do momentum
            
        Returns:
            pd.Series: Momentum normalizado (-1 a 1)
        """
        # Calcular variação percentual
        momentum = df[col].pct_change(period)
        
        # Normalizar entre -1 e 1
        momentum = momentum / momentum.abs().rolling(period*2).max()
        
        return momentum
