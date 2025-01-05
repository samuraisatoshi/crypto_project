"""
Trading orders for backtesting.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Order:
    """Trading order."""
    type: str  # 'long', 'short', 'buy', 'sell'
    size: float
    price: float
    time: datetime
    pattern: Optional[str] = None
    confidence: Optional[float] = None
    
    def __post_init__(self):
        """Validate order after initialization."""
        # Validate order type
        valid_types = ['long', 'short', 'buy', 'sell']
        if self.type not in valid_types:
            raise ValueError(f"Invalid order type: {self.type}")
        
        # Validate size
        if self.size <= 0:
            raise ValueError(f"Invalid order size: {self.size}")
        
        # Validate price
        if self.price <= 0:
            raise ValueError(f"Invalid order price: {self.price}")
        
        # Validate time
        if not isinstance(self.time, datetime):
            raise ValueError(f"Invalid order time: {self.time}")
        
        # Validate confidence if provided
        if self.confidence is not None and not (0 <= self.confidence <= 1):
            raise ValueError(f"Invalid confidence value: {self.confidence}")
