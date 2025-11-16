"""
Donchian Channel Breakout Strategy (Turtle Trader System)

A classic trend-following breakout strategy that trades price movements beyond
the highest high or lowest low over a lookback period.

Strategy Logic:
- BUY when price breaks above the upper channel (highest high of N periods)
- SELL when price breaks below the lower channel (lowest low of N periods)
- Optional: Exit on opposite channel break or middle channel touch

The Donchian Channel is defined as:
- Upper Channel: Highest high over N periods
- Middle Channel: (Upper + Lower) / 2
- Lower Channel: Lowest low over N periods

This strategy was famously used by the Turtle Traders in the 1980s.

Performance Notes:
- Works best in trending markets with clear breakouts
- Generates many false signals in choppy/ranging markets
- Classic trend-following: cuts losses short, lets profits run
- Simple and robust across different markets and timeframes
- Can have long drawdowns in non-trending periods
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import donchian_channel, atr
from ..strategy_types import (
    StrategyType,
    StrategyCategory,
    MarketRegime,
    TimeFrame,
    StrategyMetadata
)
from ..strategy_factory import register_strategy


# Define metadata for Donchian strategy
DONCHIAN_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.TREND_FOLLOWING,
    best_market_regime=[MarketRegime.TRENDING, MarketRegime.VOLATILE],
    typical_timeframe=TimeFrame.SWING,
    complexity="simple",
    requires_indicators=['Donchian Channel'],
    min_data_points=30,
    suitable_for_beginners=True,
    description="Classic trend-following breakout strategy using Donchian Channels (Turtle Trader)",
    pros=[
        "Simple and objective entry/exit rules",
        "Captures strong trends effectively",
        "Used successfully by Turtle Traders",
        "Robust across markets and timeframes",
        "Pure price action (no lagging indicators)"
    ],
    cons=[
        "Many false breakouts in choppy markets",
        "Can have extended drawdown periods",
        "Late entries after trend already started",
        "Requires discipline to trade mechanically"
    ],
    tags=["donchian", "breakout", "trend_following", "turtle_trader", "price_channel"],
    author="System",
    version="1.0.0"
)


class DonchianBreakout(Strategy):
    """
    Donchian Channel Breakout Strategy (Turtle Trader).

    Generates buy signals on breakouts above the upper channel and sell signals
    on breakdowns below the lower channel.

    Parameters:
        entry_period (int): Period for entry breakout calculation (default: 20)
        exit_period (int): Period for exit breakout calculation (default: 10)
        exit_on_middle (bool): Exit position when price touches middle channel (default: False)
        use_atr_stop (bool): Use ATR-based trailing stop (default: False)
        atr_period (int): Period for ATR calculation (default: 14)
        atr_multiplier (float): ATR multiplier for stops (default: 2.0)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'Donchian 20/10',
        ...     'parameters': {
        ...         'entry_period': 20,
        ...         'exit_period': 10,
        ...         'exit_on_middle': False
        ...     }
        ... }
        >>> strategy = DonchianBreakout(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Donchian Breakout strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.entry_period = self.parameters.get('entry_period', 20)
        self.exit_period = self.parameters.get('exit_period', 10)
        self.exit_on_middle = self.parameters.get('exit_on_middle', False)
        self.use_atr_stop = self.parameters.get('use_atr_stop', False)
        self.atr_period = self.parameters.get('atr_period', 14)
        self.atr_multiplier = self.parameters.get('atr_multiplier', 2.0)

        # Validate parameters
        if self.entry_period < 2:
            raise ValueError(f"Entry period must be at least 2, got {self.entry_period}")

        if self.exit_period < 1:
            raise ValueError(f"Exit period must be at least 1, got {self.exit_period}")

        if self.exit_period >= self.entry_period:
            raise ValueError(
                f"Exit period ({self.exit_period}) should be less than "
                f"entry period ({self.entry_period}) for optimal performance"
            )

        if self.use_atr_stop and self.atr_multiplier <= 0:
            raise ValueError(f"ATR multiplier must be positive, got {self.atr_multiplier}")

        # Set indicators list for tracking
        self.indicators = [f'Donchian_{self.entry_period}']
        if self.use_atr_stop:
            self.indicators.append(f'ATR_{self.atr_period}')

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

        # Donchian Channel requires high, low, close columns
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Calculate minimum required data points
        min_required = self.entry_period + 1

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Donchian Channel breakouts.

        Args:
            data: OHLCV DataFrame with 'high', 'low', 'close' columns

        Returns:
            DataFrame with added columns:
                - entry_upper: Entry channel upper band
                - entry_middle: Entry channel middle band
                - entry_lower: Entry channel lower band
                - exit_upper: Exit channel upper band (if different period)
                - exit_lower: Exit channel lower band (if different period)
                - atr_value: ATR values (if use_atr_stop=True)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            Entry:
            - BUY when close > entry_upper (breakout above highest high)
            - Position opened at next bar's open

            Exit (multiple conditions):
            - Close < exit_lower (breakdown below lowest low)
            - OR close touches middle channel (if exit_on_middle=True)
            - OR ATR trailing stop hit (if use_atr_stop=True)
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate entry Donchian Channel
        df['entry_upper'], df['entry_middle'], df['entry_lower'] = donchian_channel(
            df['high'], df['low'], self.entry_period
        )

        # Calculate exit Donchian Channel (if different period)
        if self.exit_period != self.entry_period:
            df['exit_upper'], _, df['exit_lower'] = donchian_channel(
                df['high'], df['low'], self.exit_period
            )
        else:
            df['exit_upper'] = df['entry_upper']
            df['exit_lower'] = df['entry_lower']

        # Calculate ATR if using ATR stops
        if self.use_atr_stop:
            df['atr_value'] = atr(df['high'], df['low'], df['close'], self.atr_period)

        # Initialize signal and position columns
        df['signal'] = 0
        df['position'] = 0

        # Detect breakouts
        # Buy signal: close breaks above upper channel
        upper_breakout = df['close'] > df['entry_upper'].shift(1)

        # Sell signal: close breaks below lower channel
        lower_breakdown = df['close'] < df['exit_lower'].shift(1)

        # Mark entry signals
        df.loc[upper_breakout, 'signal'] = 1
        df.loc[lower_breakdown, 'signal'] = -1

        # Forward fill signals to maintain positions
        start_idx = self.entry_period + 1
        entry_price = None
        stop_loss = None

        for i in range(start_idx, len(df)):
            current_idx = df.index[i]
            prev_position = df['position'].iloc[i-1]
            current_close = df['close'].iloc[i]

            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1
                entry_price = current_close

                # Set ATR stop if enabled
                if self.use_atr_stop and not pd.isna(df['atr_value'].iloc[i]):
                    stop_loss = entry_price - (self.atr_multiplier * df['atr_value'].iloc[i])

            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0
                entry_price = None
                stop_loss = None

            elif prev_position == 1:
                # Check exit conditions for long positions
                should_exit = False

                # Exit condition 1: Price breaks below exit channel
                if current_close < df['exit_lower'].iloc[i-1]:
                    should_exit = True

                # Exit condition 2: Price touches middle channel (optional)
                elif self.exit_on_middle and current_close <= df['entry_middle'].iloc[i]:
                    should_exit = True

                # Exit condition 3: ATR trailing stop (optional)
                elif self.use_atr_stop and stop_loss is not None and current_close < stop_loss:
                    should_exit = True
                # Update trailing stop if using ATR
                elif self.use_atr_stop and not pd.isna(df['atr_value'].iloc[i]):
                    new_stop = current_close - (self.atr_multiplier * df['atr_value'].iloc[i])
                    if stop_loss is None or new_stop > stop_loss:
                        stop_loss = new_stop

                if should_exit:
                    df.loc[df.index[i:], 'position'] = 0
                    entry_price = None
                    stop_loss = None
                else:
                    df.loc[current_idx, 'position'] = 1

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (entry period + buffer)
        """
        return self.entry_period + 20

    def __repr__(self) -> str:
        """String representation of the strategy."""
        atr_str = f", ATR_stop={self.atr_multiplier}x" if self.use_atr_stop else ""
        middle_str = ", exit_on_middle" if self.exit_on_middle else ""
        return (
            f"DonchianBreakout(entry={self.entry_period}, "
            f"exit={self.exit_period}{atr_str}{middle_str})"
        )


class Donchian20_10(DonchianBreakout):
    """
    Classic Turtle Trader Donchian strategy (20-day entry, 10-day exit).

    This is the exact setup used by the original Turtle Traders:
    - Entry: 20-day high breakout
    - Exit: 10-day low breakdown
    - Simple and proven over decades
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with classic Turtle Trader parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Donchian 20/10 (Turtle)'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['entry_period'] = config['parameters'].get('entry_period', 20)
        config['parameters']['exit_period'] = config['parameters'].get('exit_period', 10)
        config['parameters']['exit_on_middle'] = config['parameters'].get('exit_on_middle', False)

        super().__init__(config)


class Donchian50_25(DonchianBreakout):
    """
    Longer-term Donchian strategy (50-day entry, 25-day exit).

    For swing and position traders:
    - Entry: 50-day high breakout
    - Exit: 25-day low breakdown
    - Captures longer-term trends
    - Fewer trades, longer holding periods
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with longer-term parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Donchian 50/25 Long-term'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['entry_period'] = config['parameters'].get('entry_period', 50)
        config['parameters']['exit_period'] = config['parameters'].get('exit_period', 25)
        config['parameters']['exit_on_middle'] = config['parameters'].get('exit_on_middle', False)

        super().__init__(config)


class Donchian10_5Fast(DonchianBreakout):
    """
    Fast Donchian strategy (10-day entry, 5-day exit).

    For active traders:
    - Entry: 10-day high breakout
    - Exit: 5-day low breakdown
    - More frequent signals
    - Shorter holding periods
    - Higher turnover
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with fast parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'Donchian 10/5 Fast'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['entry_period'] = config['parameters'].get('entry_period', 10)
        config['parameters']['exit_period'] = config['parameters'].get('exit_period', 5)
        config['parameters']['exit_on_middle'] = config['parameters'].get('exit_on_middle', False)

        super().__init__(config)


# Register with factory
register_strategy('donchian', DONCHIAN_METADATA)(DonchianBreakout)
register_strategy('donchian_20_10', DONCHIAN_METADATA)(Donchian20_10)
register_strategy('donchian_50_25', DONCHIAN_METADATA)(Donchian50_25)
register_strategy('donchian_10_5', DONCHIAN_METADATA)(Donchian10_5Fast)
