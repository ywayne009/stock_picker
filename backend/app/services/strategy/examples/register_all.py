"""
Auto-register all strategies with the factory.

This module ensures all strategy classes are registered when the examples package is imported.
"""

# Import all strategy modules to trigger registration
# Phase 1: Core Signal Strategies
from . import rsi_strategy
from . import macd_strategy
from . import bollinger_strategy
from . import ma_crossover

# Phase 2: Advanced Signal Strategies
from . import adx_strategy
from . import stochastic_strategy
from . import donchian_strategy

# Ensure all imports happen
__all__ = [
    # Phase 1
    'rsi_strategy',
    'macd_strategy',
    'bollinger_strategy',
    'ma_crossover',
    # Phase 2
    'adx_strategy',
    'stochastic_strategy',
    'donchian_strategy',
]
