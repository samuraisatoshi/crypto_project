"""
Trading strategies package.
"""
from .base import BaseStrategy
from .pattern_strategy import PatternStrategy
from .pattern_orchestrator import PatternOrchestrator
from .ema_trend_strategy import EMATrendStrategy

__all__ = [
    'BaseStrategy',
    'PatternStrategy',
    'PatternOrchestrator',
    'EMATrendStrategy'
]
