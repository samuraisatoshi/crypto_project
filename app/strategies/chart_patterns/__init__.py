"""
Chart pattern detection module.
"""
from .base_pattern import BasePattern
from .head_and_shoulders import HeadAndShouldersPattern
from .triangle_patterns import (
    AscendingTriangle,
    DescendingTriangle,
    SymmetricalTriangle
)
from .flag_patterns import BullFlag, BearFlag
from .wedge_patterns import RisingWedge, FallingWedge
from .multiple_tops_bottoms import DoubleTop, DoubleBottom

# Available pattern detectors
PATTERNS = [
    HeadAndShouldersPattern,
    AscendingTriangle,
    DescendingTriangle,
    SymmetricalTriangle,
    BullFlag,
    BearFlag,
    RisingWedge,
    FallingWedge,
    DoubleTop,
    DoubleBottom
]

__all__ = [
    'BasePattern',
    'HeadAndShouldersPattern',
    'AscendingTriangle',
    'DescendingTriangle',
    'SymmetricalTriangle',
    'BullFlag',
    'BearFlag',
    'RisingWedge',
    'FallingWedge',
    'DoubleTop',
    'DoubleBottom',
    'PATTERNS'
]
