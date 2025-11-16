"""
ADX Trend Strength Filter Strategy

A trend-following strategy that only trades when the ADX (Average Directional Index)
indicates a strong trend is present.

Strategy Logic:
- BUY when ADX > threshold (strong trend) AND +DI > -DI (uptrend)
- SELL when ADX > threshold AND +DI < -DI (downtrend)
- EXIT when ADX falls below threshold (weak trend)

The ADX measures trend strength on a scale of 0-100:
- 0-25: Absent or weak trend
- 25-50: Strong trend
- 50-75: Very strong trend
- 75-100: Extremely strong trend

Performance Notes:
- Works best in trending markets (breakouts, momentum)
- Avoids losses in choppy/ranging markets
- May miss early trend entries (ADX lags)
- Reduces trading frequency but increases win rate
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import adx, atr
from ..strategy_types import (
    StrategyType,
    StrategyCategory,
    MarketRegime,
    TimeFrame,
    StrategyMetadata
)
from ..strategy_factory import register_strategy


# Define metadata for ADX strategy
ADX_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.TREND_FOLLOWING,
    best_market_regime=[MarketRegime.TRENDING, MarketRegime.VOLATILE],
    typical_timeframe=TimeFrame.SWING,
    complexity="intermediate",
    requires_indicators=['ADX', '+DI', '-DI', 'ATR'],
    min_data_points=50,
    suitable_for_beginners=True,
    description="Trend-following strategy that only trades during strong trends identified by ADX",
    pros=[
        "Filters out choppy markets effectively",
        "High win rate in trending conditions",
        "Clear trend strength measurement",
        "Reduces whipsaws significantly"
    ],
    cons=[
        "Misses early trend entries (lagging)",
        "Very few trades in ranging markets",
        "Requires strong directional moves",
        "Can be slow to exit trends"
    ],
    tags=["adx", "trend_following", "directional_movement", "trend_strength", "filter"],
    author="System",
    version="1.0.0"
)


class ADXTrendStrength(Strategy):
    """
    ADX Trend Strength Filter Strategy.

    Uses the Average Directional Index (ADX) to identify strong trends and the
    Directional Indicators (+DI/-DI) to determine trend direction.

    Parameters:
        adx_period (int): Period for ADX calculation (default: 14)
        adx_threshold (float): ADX level above which trend is considered strong (default: 25)
        di_period (int): Period for +DI/-DI calculation (default: 14, typically same as ADX)
        use_atr_stop (bool): Use ATR-based trailing stop (default: False)
        atr_multiplier (float): ATR multiplier for stops if enabled (default: 2.0)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'ADX Trend 25',
        ...     'parameters': {
        ...         'adx_period': 14,
        ...         'adx_threshold': 25,
        ...         'use_atr_stop': True
        ...     }
        ... }
        >>> strategy = ADXTrendStrength(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ADX Trend Strength strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.adx_period = self.parameters.get('adx_period', 14)
        self.adx_threshold = self.parameters.get('adx_threshold', 25)
        self.di_period = self.parameters.get('di_period', self.adx_period)
        self.use_atr_stop = self.parameters.get('use_atr_stop', False)
        self.atr_multiplier = self.parameters.get('atr_multiplier', 2.0)

        # Validate parameters
        if self.adx_period < 2:
            raise ValueError(f"ADX period must be at least 2, got {self.adx_period}")

        if not (0 <= self.adx_threshold <= 100):
            raise ValueError(f"ADX threshold must be between 0 and 100, got {self.adx_threshold}")

        if self.di_period < 2:
            raise ValueError(f"DI period must be at least 2, got {self.di_period}")

        if self.use_atr_stop and self.atr_multiplier <= 0:
            raise ValueError(f"ATR multiplier must be positive, got {self.atr_multiplier}")

        # Set indicators list for tracking
        self.indicators = [f'ADX_{self.adx_period}', '+DI', '-DI']
        if self.use_atr_stop:
            self.indicators.append(f'ATR_{self.adx_period}')

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

        # ADX requires high, low, close columns
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Calculate minimum required data points
        # ADX needs double the period due to smoothing
        min_required = self.adx_period * 3

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: ADX strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def _calculate_directional_indicators(self, data: pd.DataFrame) -> tuple:
        """
        Calculate +DI and -DI indicators.

        Args:
            data: OHLCV DataFrame

        Returns:
            Tuple of (+DI, -DI) Series
        """
        high = data['high']
        low = data['low']
        close = data['close']
        period = self.di_period

        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # Calculate ATR
        atr_values = atr(high, low, close, period)

        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr_values)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr_values)

        return plus_di, minus_di

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on ADX trend strength.

        Args:
            data: OHLCV DataFrame with 'high', 'low', 'close' columns

        Returns:
            DataFrame with added columns:
                - adx_value: ADX values
                - plus_di: +DI values
                - minus_di: -DI values
                - atr_value: ATR values (if use_atr_stop=True)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            - BUY when ADX > threshold AND +DI > -DI (strong uptrend)
            - SELL when ADX > threshold AND +DI < -DI (strong downtrend)
            - EXIT when ADX < threshold (weak trend) or directional change
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate ADX
        df['adx_value'] = adx(df['high'], df['low'], df['close'], self.adx_period)

        # Calculate Directional Indicators
        df['plus_di'], df['minus_di'] = self._calculate_directional_indicators(df)

        # Calculate ATR if using ATR stops
        if self.use_atr_stop:
            df['atr_value'] = atr(df['high'], df['low'], df['close'], self.adx_period)

        # Initialize signal and position columns
        df['signal'] = 0
        df['position'] = 0

        # Strong uptrend: ADX > threshold AND +DI > -DI
        strong_uptrend = (df['adx_value'] > self.adx_threshold) & (df['plus_di'] > df['minus_di'])

        # Strong downtrend: ADX > threshold AND +DI < -DI
        strong_downtrend = (df['adx_value'] > self.adx_threshold) & (df['plus_di'] < df['minus_di'])

        # Weak trend: ADX < threshold
        weak_trend = df['adx_value'] <= self.adx_threshold

        # Detect crossovers for entry signals
        df['prev_plus_di'] = df['plus_di'].shift(1)
        df['prev_minus_di'] = df['minus_di'].shift(1)

        # Buy signal: +DI crosses above -DI while ADX > threshold
        di_bullish_cross = (df['prev_plus_di'] <= df['prev_minus_di']) & (df['plus_di'] > df['minus_di'])
        df.loc[di_bullish_cross & (df['adx_value'] > self.adx_threshold), 'signal'] = 1

        # Sell signal: -DI crosses above +DI while ADX > threshold
        di_bearish_cross = (df['prev_plus_di'] >= df['prev_minus_di']) & (df['plus_di'] < df['minus_di'])
        df.loc[di_bearish_cross & (df['adx_value'] > self.adx_threshold), 'signal'] = -1

        # Forward fill signals to maintain positions
        start_idx = self.adx_period * 3

        for i in range(start_idx, len(df)):
            current_idx = df.index[i]
            prev_position = df['position'].iloc[i-1]

            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1

            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0

            elif prev_position == 1:
                # Check exit conditions for long positions
                # Exit if trend weakens
                if df['adx_value'].iloc[i] <= self.adx_threshold:
                    df.loc[df.index[i:], 'position'] = 0
                # Exit if directional indicators flip
                elif df['plus_di'].iloc[i] < df['minus_di'].iloc[i]:
                    df.loc[df.index[i:], 'position'] = 0
                # Otherwise maintain position
                else:
                    df.loc[current_idx, 'position'] = 1

        # Clean up temporary columns
        df.drop(['prev_plus_di', 'prev_minus_di'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (ADX period * 3 + buffer for smoothing)
        """
        return self.adx_period * 3 + 20

    def __repr__(self) -> str:
        """String representation of the strategy."""
        atr_str = f", ATR_stop={self.atr_multiplier}x" if self.use_atr_stop else ""
        return (
            f"ADXTrendStrength(period={self.adx_period}, "
            f"threshold={self.adx_threshold}{atr_str})"
        )


class ADX25(ADXTrendStrength):
    """
    Standard ADX strategy using 25 threshold (classic strong trend definition).

    This is the most common ADX setup:
    - ADX > 25 = Strong trend
    - +DI > -DI = Uptrend
    - +DI < -DI = Downtrend
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with default threshold of 25."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'ADX Trend 25'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['adx_period'] = config['parameters'].get('adx_period', 14)
        config['parameters']['adx_threshold'] = config['parameters'].get('adx_threshold', 25)

        super().__init__(config)


class ADX30Conservative(ADXTrendStrength):
    """
    Conservative ADX strategy using 30 threshold (very strong trends only).

    Generates fewer signals but higher quality:
    - ADX > 30 = Very strong trend
    - Filters out moderate trends
    - Higher win rate, lower frequency
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with conservative threshold of 30."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'ADX Trend 30 Conservative'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['adx_period'] = config['parameters'].get('adx_period', 14)
        config['parameters']['adx_threshold'] = config['parameters'].get('adx_threshold', 30)

        super().__init__(config)


class ADX20Aggressive(ADXTrendStrength):
    """
    Aggressive ADX strategy using 20 threshold (moderate trends).

    Generates more signals with lower trend requirements:
    - ADX > 20 = Moderate to strong trend
    - More trading opportunities
    - Lower win rate, higher frequency
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with aggressive threshold of 20."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'ADX Trend 20 Aggressive'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['adx_period'] = config['parameters'].get('adx_period', 14)
        config['parameters']['adx_threshold'] = config['parameters'].get('adx_threshold', 20)

        super().__init__(config)


# Register with factory
register_strategy('adx', ADX_METADATA)(ADXTrendStrength)
register_strategy('adx_25', ADX_METADATA)(ADX25)
register_strategy('adx_30', ADX_METADATA)(ADX30Conservative)
register_strategy('adx_20', ADX_METADATA)(ADX20Aggressive)
