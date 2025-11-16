"""
Strategy Type Definitions and Metadata

This module provides enums and metadata classes for categorizing and describing strategies.
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class StrategyType(Enum):
    """
    Enumeration of strategy types based on taxonomy.

    Categories:
    - SIGNAL: Discrete buy/sell signals for single asset
    - PORTFOLIO: Multi-asset portfolio weight allocation
    - PAIR_TRADING: Spread-based strategies on correlated pairs
    - OPTIONS: Option contract strategies (spreads, straddles, etc.)
    - MARKET_MAKING: Provide liquidity via bid/ask quotes
    - STATISTICAL_ARBITRAGE: Statistical edge-based strategies
    - ML_BASED: Machine learning / AI-driven strategies
    """
    SIGNAL = "signal"                           # Type 1: Single-asset signals
    PORTFOLIO = "portfolio"                     # Type 2: Multi-asset weights
    PAIR_TRADING = "pair_trading"              # Type 3: Pair spreads
    OPTIONS = "options"                         # Type 4: Options strategies
    MARKET_MAKING = "market_making"            # Type 5: Market making
    STATISTICAL_ARBITRAGE = "stat_arb"         # Type 6: Statistical arbitrage
    ML_BASED = "ml_based"                      # Type 7: ML/AI strategies


class StrategyCategory(Enum):
    """
    Sub-categories for signal-based strategies.

    These categories help organize strategies by their primary trading logic.
    """
    # Trend Following
    TREND_FOLLOWING = "trend_following"

    # Mean Reversion
    MEAN_REVERSION = "mean_reversion"

    # Momentum
    MOMENTUM = "momentum"

    # Volatility
    VOLATILITY = "volatility"

    # Volume
    VOLUME = "volume"

    # Multi-Indicator
    MULTI_INDICATOR = "multi_indicator"

    # Pattern Recognition
    PATTERN = "pattern"

    # Other
    OTHER = "other"


class MarketRegime(Enum):
    """Market conditions where strategies perform best."""
    TRENDING = "trending"           # Strong directional movement
    RANGING = "ranging"             # Sideways/choppy markets
    VOLATILE = "volatile"           # High volatility periods
    LOW_VOLATILITY = "low_vol"      # Quiet markets
    BULL = "bull"                   # Rising markets
    BEAR = "bear"                   # Falling markets
    ALL = "all"                     # Works in all conditions


class TimeFrame(Enum):
    """Typical time horizons for strategies."""
    INTRADAY = "intraday"           # Minutes to hours
    SWING = "swing"                 # Days to weeks
    POSITION = "position"           # Weeks to months
    LONG_TERM = "long_term"         # Months to years


@dataclass
class StrategyMetadata:
    """
    Comprehensive metadata for a trading strategy.

    This provides a rich description of strategy characteristics,
    making it easier to search, filter, and understand strategies.

    Attributes:
        strategy_type: Primary strategy type (SIGNAL, PORTFOLIO, etc.)
        category: Sub-category (TREND_FOLLOWING, MEAN_REVERSION, etc.)
        best_market_regime: Market conditions where strategy excels
        typical_timeframe: Typical holding period
        complexity: Simple, Medium, Advanced, Expert
        requires_indicators: List of technical indicators used
        requires_features: List of special features needed (ML models, etc.)
        min_data_points: Minimum historical data required
        suitable_for_beginners: Whether beginners should use this
        tags: Free-form tags for searchability
        author: Strategy creator
        version: Version string
        created_at: Creation timestamp
        last_updated: Last modification timestamp
    """
    # Core classification
    strategy_type: StrategyType
    category: StrategyCategory

    # Performance characteristics
    best_market_regime: List[MarketRegime] = field(default_factory=lambda: [MarketRegime.ALL])
    typical_timeframe: TimeFrame = TimeFrame.SWING

    # Complexity and requirements
    complexity: str = "medium"  # simple, medium, advanced, expert
    requires_indicators: List[str] = field(default_factory=list)
    requires_features: List[str] = field(default_factory=list)
    min_data_points: int = 50

    # User guidance
    suitable_for_beginners: bool = False
    description: str = ""
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)
    author: str = "System"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'strategy_type': self.strategy_type.value,
            'category': self.category.value,
            'best_market_regime': [r.value for r in self.best_market_regime],
            'typical_timeframe': self.typical_timeframe.value,
            'complexity': self.complexity,
            'requires_indicators': self.requires_indicators,
            'requires_features': self.requires_features,
            'min_data_points': self.min_data_points,
            'suitable_for_beginners': self.suitable_for_beginners,
            'description': self.description,
            'pros': self.pros,
            'cons': self.cons,
            'tags': self.tags,
            'author': self.author,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyMetadata':
        """Create metadata from dictionary."""
        return cls(
            strategy_type=StrategyType(data['strategy_type']),
            category=StrategyCategory(data['category']),
            best_market_regime=[MarketRegime(r) for r in data.get('best_market_regime', [])],
            typical_timeframe=TimeFrame(data.get('typical_timeframe', 'swing')),
            complexity=data.get('complexity', 'medium'),
            requires_indicators=data.get('requires_indicators', []),
            requires_features=data.get('requires_features', []),
            min_data_points=data.get('min_data_points', 50),
            suitable_for_beginners=data.get('suitable_for_beginners', False),
            description=data.get('description', ''),
            pros=data.get('pros', []),
            cons=data.get('cons', []),
            tags=data.get('tags', []),
            author=data.get('author', 'System'),
            version=data.get('version', '1.0.0')
        )


# Preset metadata for common strategy types
PRESET_METADATA = {
    'trend_following': StrategyMetadata(
        strategy_type=StrategyType.SIGNAL,
        category=StrategyCategory.TREND_FOLLOWING,
        best_market_regime=[MarketRegime.TRENDING, MarketRegime.BULL, MarketRegime.BEAR],
        typical_timeframe=TimeFrame.SWING,
        complexity="simple",
        suitable_for_beginners=True,
        description="Trend-following strategies capture sustained directional moves",
        pros=["Works in strong trends", "Clear entry/exit rules", "Emotion-free trading"],
        cons=["Whipsaws in ranging markets", "Late entries", "Frequent small losses"],
        tags=["trend", "moving_average", "crossover"]
    ),

    'mean_reversion': StrategyMetadata(
        strategy_type=StrategyType.SIGNAL,
        category=StrategyCategory.MEAN_REVERSION,
        best_market_regime=[MarketRegime.RANGING, MarketRegime.LOW_VOLATILITY],
        typical_timeframe=TimeFrame.SWING,
        complexity="medium",
        suitable_for_beginners=False,
        description="Mean reversion strategies profit from price extremes returning to average",
        pros=["High win rate", "Works in ranging markets", "Defined entry points"],
        cons=["Fails in strong trends", "Can stay oversold/overbought", "Requires patience"],
        tags=["mean_reversion", "oscillator", "oversold", "overbought"]
    ),

    'momentum': StrategyMetadata(
        strategy_type=StrategyType.SIGNAL,
        category=StrategyCategory.MOMENTUM,
        best_market_regime=[MarketRegime.TRENDING, MarketRegime.VOLATILE],
        typical_timeframe=TimeFrame.SWING,
        complexity="medium",
        suitable_for_beginners=True,
        description="Momentum strategies ride the wave of strong price movements",
        pros=["Catches strong moves", "Combines trend and strength", "Widely used"],
        cons=["Lags in fast markets", "False signals in chop", "Requires confirmation"],
        tags=["momentum", "macd", "roc", "strength"]
    )
}
