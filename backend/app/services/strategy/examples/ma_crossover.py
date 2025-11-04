"""
Moving Average Crossover Strategy

A classic trend-following strategy that generates signals when two moving averages cross.

Strategy Logic:
- BUY when fast MA crosses above slow MA (golden cross)
- SELL when fast MA crosses below slow MA (death cross)

This strategy works well in trending markets but may generate false signals in ranging markets.
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import sma, ema


class MovingAverageCrossover(Strategy):
    """
    Moving Average Crossover Strategy.

    Generates buy signals when a fast moving average crosses above a slow moving average,
    and sell signals when it crosses below.

    Parameters:
        fast_period (int): Period for fast moving average (default: 20)
        slow_period (int): Period for slow moving average (default: 50)
        ma_type (str): Type of moving average - 'sma' or 'ema' (default: 'sma')
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'MA Crossover 20/50',
        ...     'parameters': {
        ...         'fast_period': 20,
        ...         'slow_period': 50,
        ...         'ma_type': 'sma'
        ...     }
        ... }
        >>> strategy = MovingAverageCrossover(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Moving Average Crossover strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.fast_period = self.parameters.get('fast_period', 20)
        self.slow_period = self.parameters.get('slow_period', 50)
        self.ma_type = self.parameters.get('ma_type', 'sma').lower()

        # Validate parameters
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"Fast period ({self.fast_period}) must be less than "
                f"slow period ({self.slow_period})"
            )

        if self.ma_type not in ['sma', 'ema']:
            raise ValueError(f"ma_type must be 'sma' or 'ema', got '{self.ma_type}'")

        # Set indicators list for tracking
        self.indicators = [
            f'{self.ma_type.upper()}_{self.fast_period}',
            f'{self.ma_type.upper()}_{self.slow_period}'
        ]

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

        # Additional validation for this strategy
        if len(data) < self.slow_period:
            raise ValueError(
                f"Insufficient data: strategy requires at least {self.slow_period} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on moving average crossovers.

        Args:
            data: OHLCV DataFrame with at least 'close' column

        Returns:
            DataFrame with added columns:
                - fast_ma: Fast moving average
                - slow_ma: Slow moving average
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat, -1=short)

        Signal Logic:
            - Generate BUY (1) when fast_ma crosses above slow_ma
            - Generate SELL (-1) when fast_ma crosses below slow_ma
            - Otherwise HOLD (0)
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate moving averages
        if self.ma_type == 'sma':
            df['fast_ma'] = sma(df['close'], self.fast_period)
            df['slow_ma'] = sma(df['close'], self.slow_period)
        else:  # ema
            df['fast_ma'] = ema(df['close'], self.fast_period)
            df['slow_ma'] = ema(df['close'], self.slow_period)

        # Initialize signal column
        df['signal'] = 0

        # Detect crossovers
        # Golden cross: fast MA crosses above slow MA (bullish)
        df['prev_fast'] = df['fast_ma'].shift(1)
        df['prev_slow'] = df['slow_ma'].shift(1)

        # Buy signal: fast was below slow, now it's above
        golden_cross = (df['prev_fast'] <= df['prev_slow']) & (df['fast_ma'] > df['slow_ma'])
        df.loc[golden_cross, 'signal'] = 1

        # Sell signal: fast was above slow, now it's below
        death_cross = (df['prev_fast'] >= df['prev_slow']) & (df['fast_ma'] < df['slow_ma'])
        df.loc[death_cross, 'signal'] = -1

        # Calculate position (持仓状态)
        # Start with no position
        df['position'] = 0

        # Forward fill signals to maintain positions
        # When we get a buy signal, we're long until we get a sell signal
        for i in range(self.slow_period, len(df)):
            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0

        # Clean up temporary columns
        df.drop(['prev_fast', 'prev_slow'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (slow_period + buffer)
        """
        return self.slow_period + 10  # Add buffer for stability

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return (
            f"MovingAverageCrossover(fast={self.fast_period}, slow={self.slow_period}, "
            f"type={self.ma_type.upper()})"
        )


class GoldenCross50_200(MovingAverageCrossover):
    """
    Classic Golden Cross strategy using 50-day and 200-day moving averages.

    This is a popular long-term trend-following strategy used by institutional investors.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with default 50/200 day parameters."""
        if config is None:
            config = {}

        # Set default parameters for golden cross
        if 'name' not in config:
            config['name'] = 'Golden Cross 50/200'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['fast_period'] = config['parameters'].get('fast_period', 50)
        config['parameters']['slow_period'] = config['parameters'].get('slow_period', 200)
        config['parameters']['ma_type'] = config['parameters'].get('ma_type', 'sma')

        super().__init__(config)


class FastMACrossover(MovingAverageCrossover):
    """
    Fast Moving Average Crossover using 10-day and 30-day EMAs.

    This is a more responsive strategy suitable for day trading or swing trading.
    Generates more signals but may have more false positives.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with default 10/30 day EMA parameters."""
        if config is None:
            config = {}

        # Set default parameters for fast crossover
        if 'name' not in config:
            config['name'] = 'Fast MA Crossover 10/30'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['fast_period'] = config['parameters'].get('fast_period', 10)
        config['parameters']['slow_period'] = config['parameters'].get('slow_period', 30)
        config['parameters']['ma_type'] = config['parameters'].get('ma_type', 'ema')

        super().__init__(config)
