"""
Stochastic Oscillator Strategy

A mean-reversion momentum oscillator strategy that identifies overbought and oversold conditions
using the relationship between current price and the price range over a period.

Strategy Logic:
- BUY when %K crosses above %D in oversold zone (below 20)
- SELL when %K crosses below %D in overbought zone (above 80)
- EXIT when opposite signal occurs

The Stochastic Oscillator compares the current close price to its price range over a period:
- %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
- %D = 3-period SMA of %K (signal line)

Zones:
- 0-20: Oversold (potential buy)
- 20-80: Neutral
- 80-100: Overbought (potential sell)

Performance Notes:
- Works best in ranging/oscillating markets
- Generates many false signals in strong trends
- %K/%D crossover provides better entries than raw levels
- Can stay overbought/oversold for extended periods in trends
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import stochastic, sma
from ..strategy_types import (
    StrategyType,
    StrategyCategory,
    MarketRegime,
    TimeFrame,
    StrategyMetadata
)
from ..strategy_factory import register_strategy


# Define metadata for Stochastic strategy
STOCHASTIC_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.MEAN_REVERSION,
    best_market_regime=[MarketRegime.RANGING, MarketRegime.LOW_VOLATILITY],
    typical_timeframe=TimeFrame.SWING,
    complexity="intermediate",
    requires_indicators=['Stochastic %K', 'Stochastic %D'],
    min_data_points=20,
    suitable_for_beginners=True,
    description="Mean reversion strategy using Stochastic Oscillator crossovers in extreme zones",
    pros=[
        "Effective in range-bound markets",
        "Clear overbought/oversold signals",
        "Crossover reduces false signals",
        "Well-known and widely used"
    ],
    cons=[
        "Many whipsaws in trending markets",
        "Can stay overbought/oversold in strong trends",
        "Requires zone filtering to reduce noise",
        "Best combined with trend filter"
    ],
    tags=["stochastic", "mean_reversion", "oscillator", "momentum", "oversold", "overbought"],
    author="System",
    version="1.0.0"
)


class StochasticOscillator(Strategy):
    """
    Stochastic Oscillator Strategy.

    Generates buy signals when %K crosses above %D in oversold territory and
    sell signals when %K crosses below %D in overbought territory.

    Parameters:
        k_period (int): Period for %K calculation (default: 14)
        d_period (int): Period for %D smoothing (default: 3)
        oversold_level (float): Level below which asset is oversold (default: 20)
        overbought_level (float): Level above which asset is overbought (default: 80)
        use_trend_filter (bool): Only take signals aligned with trend (default: False)
        trend_period (int): Period for trend SMA if using filter (default: 200)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'Stochastic 14,3',
        ...     'parameters': {
        ...         'k_period': 14,
        ...         'd_period': 3,
        ...         'oversold_level': 20,
        ...         'overbought_level': 80
        ...     }
        ... }
        >>> strategy = StochasticOscillator(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Stochastic Oscillator strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.k_period = self.parameters.get('k_period', 14)
        self.d_period = self.parameters.get('d_period', 3)
        self.oversold_level = self.parameters.get('oversold_level', 20)
        self.overbought_level = self.parameters.get('overbought_level', 80)
        self.use_trend_filter = self.parameters.get('use_trend_filter', False)
        self.trend_period = self.parameters.get('trend_period', 200)

        # Validate parameters
        if self.k_period < 2:
            raise ValueError(f"K period must be at least 2, got {self.k_period}")

        if self.d_period < 1:
            raise ValueError(f"D period must be at least 1, got {self.d_period}")

        if not (0 <= self.oversold_level <= 100):
            raise ValueError(f"Oversold level must be between 0 and 100, got {self.oversold_level}")

        if not (0 <= self.overbought_level <= 100):
            raise ValueError(f"Overbought level must be between 0 and 100, got {self.overbought_level}")

        if self.oversold_level >= self.overbought_level:
            raise ValueError(
                f"Oversold level ({self.oversold_level}) must be less than "
                f"overbought level ({self.overbought_level})"
            )

        # Set indicators list for tracking
        self.indicators = [f'Stochastic_{self.k_period}_{self.d_period}']
        if self.use_trend_filter:
            self.indicators.append(f'SMA_{self.trend_period}')

    def setup(self, data: pd.DataFrame) -> None:
        """
        Setup the strategy with initial data validation.

        Args:
            data: OHLCV DataFrame

        Raises:
            ValueError: If data is insufficient for strategy requirements
        """
        # Validate data
        self.validate_data(data)

        # Stochastic requires high, low, close columns
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Calculate minimum required data points
        min_required = self.k_period + self.d_period + 1
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period)

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Stochastic Oscillator crossovers.

        Args:
            data: OHLCV DataFrame with 'high', 'low', 'close' columns

        Returns:
            DataFrame with added columns:
                - stoch_k: %K values
                - stoch_d: %D values
                - trend_sma: Trend filter SMA (if enabled)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            Without trend filter:
            - BUY when %K crosses above %D AND both are below oversold level
            - SELL when %K crosses below %D AND both are above overbought level

            With trend filter:
            - BUY when %K crosses above %D in oversold zone AND price > trend SMA
            - SELL when %K crosses below %D in overbought zone OR price < trend SMA
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = stochastic(
            df['high'], df['low'], df['close'],
            self.k_period, self.d_period
        )

        # Calculate trend filter if enabled
        if self.use_trend_filter:
            df['trend_sma'] = sma(df['close'], self.trend_period)

        # Initialize signal and position columns
        df['signal'] = 0
        df['position'] = 0

        # Detect crossovers
        df['prev_k'] = df['stoch_k'].shift(1)
        df['prev_d'] = df['stoch_d'].shift(1)

        # Bullish crossover: %K crosses above %D
        bullish_cross = (df['prev_k'] <= df['prev_d']) & (df['stoch_k'] > df['stoch_d'])

        # Bearish crossover: %K crosses below %D
        bearish_cross = (df['prev_k'] >= df['prev_d']) & (df['stoch_k'] < df['stoch_d'])

        # In oversold zone
        in_oversold = (df['stoch_k'] < self.oversold_level) | (df['prev_k'] < self.oversold_level)

        # In overbought zone
        in_overbought = (df['stoch_k'] > self.overbought_level) | (df['prev_k'] > self.overbought_level)

        if self.use_trend_filter:
            # Only buy in uptrend
            uptrend = df['close'] > df['trend_sma']
            downtrend = df['close'] < df['trend_sma']

            # Buy: bullish crossover in oversold zone during uptrend
            df.loc[bullish_cross & in_oversold & uptrend, 'signal'] = 1

            # Sell: bearish crossover in overbought zone OR trend breaks down
            df.loc[bearish_cross & in_overbought, 'signal'] = -1
        else:
            # Buy: bullish crossover in oversold zone
            df.loc[bullish_cross & in_oversold, 'signal'] = 1

            # Sell: bearish crossover in overbought zone
            df.loc[bearish_cross & in_overbought, 'signal'] = -1

        # Forward fill signals to maintain positions
        start_idx = self.k_period + self.d_period + 1
        if self.use_trend_filter:
            start_idx = max(start_idx, self.trend_period)

        for i in range(start_idx, len(df)):
            current_idx = df.index[i]
            prev_position = df['position'].iloc[i-1]

            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1

            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0

            elif prev_position == 1:
                # Check if we should exit due to trend break (only if trend filter enabled)
                if self.use_trend_filter and df['close'].iloc[i] < df['trend_sma'].iloc[i]:
                    df.loc[df.index[i:], 'position'] = 0
                # Check if we get a bearish crossover
                elif df['prev_k'].iloc[i] >= df['prev_d'].iloc[i] and df['stoch_k'].iloc[i] < df['stoch_d'].iloc[i]:
                    df.loc[df.index[i:], 'position'] = 0
                else:
                    df.loc[current_idx, 'position'] = 1

        # Clean up temporary columns
        df.drop(['prev_k', 'prev_d'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (max of stochastic period and trend period + buffer)
        """
        min_required = self.k_period + self.d_period + 10
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period + 10)
        return min_required

    def __repr__(self) -> str:
        """String representation of the strategy."""
        trend_str = f", trend_filter=SMA{self.trend_period}" if self.use_trend_filter else ""
        return (
            f"StochasticOscillator(k={self.k_period}, d={self.d_period}, "
            f"oversold={self.oversold_level}, overbought={self.overbought_level}"
            f"{trend_str})"
        )


class Stochastic14_3(StochasticOscillator):
    """
    Classic Stochastic strategy using 14,3 periods with 20/80 zones.

    This is the most common Stochastic setup:
    - %K period: 14
    - %D period: 3
    - Oversold: 20
    - Overbought: 80
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with classic 14,3 parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Stochastic 14,3'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['k_period'] = config['parameters'].get('k_period', 14)
        config['parameters']['d_period'] = config['parameters'].get('d_period', 3)
        config['parameters']['oversold_level'] = config['parameters'].get('oversold_level', 20)
        config['parameters']['overbought_level'] = config['parameters'].get('overbought_level', 80)

        super().__init__(config)


class StochasticSlow(StochasticOscillator):
    """
    Slow Stochastic strategy using 14,3,3 (additional smoothing).

    Uses slower %D for reduced noise:
    - %K period: 14
    - %D period: 3
    - %D smoothing: 3 (applied twice)
    - Oversold: 20
    - Overbought: 80
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with slow stochastic parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Stochastic Slow 14,3,3'

        if 'parameters' not in config:
            config['parameters'] = {}

        # Slow stochastic uses longer D period for additional smoothing
        config['parameters']['k_period'] = config['parameters'].get('k_period', 14)
        config['parameters']['d_period'] = config['parameters'].get('d_period', 6)  # Effectively 3+3
        config['parameters']['oversold_level'] = config['parameters'].get('oversold_level', 20)
        config['parameters']['overbought_level'] = config['parameters'].get('overbought_level', 80)

        super().__init__(config)


class StochasticFast(StochasticOscillator):
    """
    Fast Stochastic strategy using 5,3 (more responsive).

    Generates more signals with faster periods:
    - %K period: 5
    - %D period: 3
    - Oversold: 20
    - Overbought: 80
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with fast stochastic parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Stochastic Fast 5,3'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['k_period'] = config['parameters'].get('k_period', 5)
        config['parameters']['d_period'] = config['parameters'].get('d_period', 3)
        config['parameters']['oversold_level'] = config['parameters'].get('oversold_level', 20)
        config['parameters']['overbought_level'] = config['parameters'].get('overbought_level', 80)

        super().__init__(config)


# Register with factory
register_strategy('stochastic', STOCHASTIC_METADATA)(StochasticOscillator)
register_strategy('stochastic_14_3', STOCHASTIC_METADATA)(Stochastic14_3)
register_strategy('stochastic_slow', STOCHASTIC_METADATA)(StochasticSlow)
register_strategy('stochastic_fast', STOCHASTIC_METADATA)(StochasticFast)
