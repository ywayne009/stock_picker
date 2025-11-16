"""
Strategy Module

Provides the core strategy framework including:
- Base Strategy class
- Strategy types and metadata
- Strategy factory for easy instantiation
- Strategy registry for discovery
"""

# Core base class
from .base_strategy import Strategy

# Strategy types and metadata
from .strategy_types import (
    StrategyType,
    StrategyCategory,
    MarketRegime,
    TimeFrame,
    StrategyMetadata,
    PRESET_METADATA
)

# Factory pattern
from .strategy_factory import (
    StrategyFactory,
    get_factory,
    create_strategy,
    list_strategies,
    register_strategy
)

# Legacy registry (for backward compatibility)
from .registry import (
    StrategyRegistry,
    get_registry,
    get_strategy as get_strategy_legacy
)

# Technical indicators
from . import indicators

__all__ = [
    # Base
    'Strategy',

    # Types and metadata
    'StrategyType',
    'StrategyCategory',
    'MarketRegime',
    'TimeFrame',
    'StrategyMetadata',
    'PRESET_METADATA',

    # Factory
    'StrategyFactory',
    'get_factory',
    'create_strategy',
    'list_strategies',
    'register_strategy',

    # Legacy
    'StrategyRegistry',
    'get_registry',
    'get_strategy_legacy',

    # Indicators
    'indicators'
]
