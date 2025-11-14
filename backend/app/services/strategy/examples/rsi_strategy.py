"""
RSI Overbought/Oversold Strategy

A mean-reversion strategy that generates signals based on RSI (Relative Strength Index) levels.

Strategy Logic:
- BUY when RSI crosses below oversold threshold (default: 30) - price is oversold
- SELL when RSI crosses above overbought threshold (default: 70) - price is overbought

The strategy can be enhanced with an optional trend filter to only take trades in the direction
of the trend.

Performance Notes:
- Works best in ranging/sideways markets
- Can generate losses in strong trending markets (price stays overbought/oversold)
- Adding trend filter improves performance but reduces trading frequency
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import rsi, sma


class RSIOverboughtOversold(Strategy):
    """
    RSI Overbought/Oversold Strategy.

    Generates buy signals when RSI enters oversold territory and sell signals when
    RSI enters overbought territory.

    Parameters:
        rsi_period (int): Period for RSI calculation (default: 14)
        oversold_threshold (float): RSI level below which asset is considered oversold (default: 30)
        overbought_threshold (float): RSI level above which asset is considered overbought (default: 70)
        use_trend_filter (bool): Whether to apply trend filter (default: False)
        trend_period (int): Period for trend SMA if using trend filter (default: 200)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'RSI 30/70',
        ...     'parameters': {
        ...         'rsi_period': 14,
        ...         'oversold_threshold': 30,
        ...         'overbought_threshold': 70,
        ...         'use_trend_filter': True,
        ...         'trend_period': 200
        ...     }
        ... }
        >>> strategy = RSIOverboughtOversold(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the RSI Overbought/Oversold strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.oversold_threshold = self.parameters.get('oversold_threshold', 30)
        self.overbought_threshold = self.parameters.get('overbought_threshold', 70)
        self.use_trend_filter = self.parameters.get('use_trend_filter', False)
        self.trend_period = self.parameters.get('trend_period', 200)

        # Validate parameters
        if self.oversold_threshold >= self.overbought_threshold:
            raise ValueError(
                f"Oversold threshold ({self.oversold_threshold}) must be less than "
                f"overbought threshold ({self.overbought_threshold})"
            )

        if not (0 <= self.oversold_threshold <= 100):
            raise ValueError(f"Oversold threshold must be between 0 and 100, got {self.oversold_threshold}")

        if not (0 <= self.overbought_threshold <= 100):
            raise ValueError(f"Overbought threshold must be between 0 and 100, got {self.overbought_threshold}")

        if self.rsi_period < 2:
            raise ValueError(f"RSI period must be at least 2, got {self.rsi_period}")

        # Set indicators list for tracking
        self.indicators = [f'RSI_{self.rsi_period}']
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

        # Calculate minimum required data points
        min_required = self.rsi_period + 1
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period)

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on RSI levels.

        Args:
            data: OHLCV DataFrame with at least 'close' column

        Returns:
            DataFrame with added columns:
                - rsi: RSI values
                - trend_sma: Trend filter SMA (if enabled)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            Without trend filter:
            - BUY when RSI crosses below oversold threshold
            - SELL when RSI crosses above overbought threshold

            With trend filter:
            - BUY when RSI crosses below oversold AND price > trend SMA (uptrend)
            - SELL when RSI crosses above overbought OR price < trend SMA (downtrend)
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate RSI
        df['rsi'] = rsi(df['close'], self.rsi_period)

        # Calculate trend filter if enabled
        if self.use_trend_filter:
            df['trend_sma'] = sma(df['close'], self.trend_period)

        # Initialize signal column
        df['signal'] = 0

        # Detect RSI crossovers
        df['prev_rsi'] = df['rsi'].shift(1)

        # Buy signal: RSI crosses below oversold threshold (was above, now below)
        oversold_cross = (df['prev_rsi'] >= self.oversold_threshold) & (df['rsi'] < self.oversold_threshold)

        # Sell signal: RSI crosses above overbought threshold (was below, now above)
        overbought_cross = (df['prev_rsi'] <= self.overbought_threshold) & (df['rsi'] > self.overbought_threshold)

        if self.use_trend_filter:
            # Only buy in uptrend (price above trend SMA)
            uptrend = df['close'] > df['trend_sma']
            downtrend = df['close'] < df['trend_sma']

            df.loc[oversold_cross & uptrend, 'signal'] = 1
            # Sell when overbought OR price breaks below trend
            df.loc[overbought_cross | (df['position'].shift(1) == 1) & downtrend, 'signal'] = -1
        else:
            df.loc[oversold_cross, 'signal'] = 1
            df.loc[overbought_cross, 'signal'] = -1

        # Calculate position (持仓状态)
        df['position'] = 0

        # Forward fill signals to maintain positions
        start_idx = self.rsi_period + 1
        if self.use_trend_filter:
            start_idx = max(start_idx, self.trend_period)

        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0

        # Clean up temporary columns
        df.drop(['prev_rsi'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (max of RSI period and trend period + buffer)
        """
        min_required = self.rsi_period + 10
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period + 10)
        return min_required

    def __repr__(self) -> str:
        """String representation of the strategy."""
        trend_str = f", trend_filter=SMA{self.trend_period}" if self.use_trend_filter else ""
        return (
            f"RSIOverboughtOversold(period={self.rsi_period}, "
            f"oversold={self.oversold_threshold}, overbought={self.overbought_threshold}"
            f"{trend_str})"
        )


class RSI30_70(RSIOverboughtOversold):
    """
    Classic RSI strategy using 30/70 thresholds.

    This is the most common RSI mean-reversion setup.
    - Oversold: RSI < 30
    - Overbought: RSI > 70
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with default 30/70 thresholds."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'RSI 30/70'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['rsi_period'] = config['parameters'].get('rsi_period', 14)
        config['parameters']['oversold_threshold'] = config['parameters'].get('oversold_threshold', 30)
        config['parameters']['overbought_threshold'] = config['parameters'].get('overbought_threshold', 70)

        super().__init__(config)


class RSI20_80(RSIOverboughtOversold):
    """
    Conservative RSI strategy using 20/80 thresholds.

    Generates fewer signals but with stronger oversold/overbought conditions.
    - Oversold: RSI < 20
    - Overbought: RSI > 80
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with conservative 20/80 thresholds."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'RSI 20/80 Conservative'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['rsi_period'] = config['parameters'].get('rsi_period', 14)
        config['parameters']['oversold_threshold'] = config['parameters'].get('oversold_threshold', 20)
        config['parameters']['overbought_threshold'] = config['parameters'].get('overbought_threshold', 80)

        super().__init__(config)
