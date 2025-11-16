"""
MACD Crossover Strategy

A momentum strategy that generates signals based on MACD (Moving Average Convergence Divergence) crossovers.

Strategy Logic:
- BUY when MACD line crosses above signal line (bullish momentum)
- SELL when MACD line crosses below signal line (bearish momentum)

The strategy can be enhanced with:
- Histogram divergence detection (price makes new high/low but MACD doesn't - reversal signal)
- Zero-line filter (only take longs above zero, shorts below zero)

Performance Notes:
- Works best in trending markets
- Combines trend-following (MACD direction) with momentum (crossover speed)
- Lagging indicator - signals come after trend has started
- Can generate whipsaws in choppy, sideways markets
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import macd as calculate_macd, sma


class MACDCrossover(Strategy):
    """
    MACD Crossover Strategy.

    Generates buy signals when MACD line crosses above signal line and sell signals
    when MACD line crosses below signal line.

    Parameters:
        fast_period (int): Fast EMA period for MACD (default: 12)
        slow_period (int): Slow EMA period for MACD (default: 26)
        signal_period (int): Signal line EMA period (default: 9)
        use_histogram_divergence (bool): Detect histogram divergence (default: False)
        use_zero_line_filter (bool): Only trade in direction of MACD vs zero (default: False)
        use_trend_filter (bool): Only trade with overall trend (default: False)
        trend_period (int): Period for trend SMA if using trend filter (default: 200)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'MACD 12/26/9',
        ...     'parameters': {
        ...         'fast_period': 12,
        ...         'slow_period': 26,
        ...         'signal_period': 9,
        ...         'use_zero_line_filter': True
        ...     }
        ... }
        >>> strategy = MACDCrossover(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the MACD Crossover strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.fast_period = self.parameters.get('fast_period', 12)
        self.slow_period = self.parameters.get('slow_period', 26)
        self.signal_period = self.parameters.get('signal_period', 9)
        self.use_histogram_divergence = self.parameters.get('use_histogram_divergence', False)
        self.use_zero_line_filter = self.parameters.get('use_zero_line_filter', False)
        self.use_trend_filter = self.parameters.get('use_trend_filter', False)
        self.trend_period = self.parameters.get('trend_period', 200)

        # Validate parameters
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"Fast period ({self.fast_period}) must be less than "
                f"slow period ({self.slow_period})"
            )

        if self.signal_period < 2:
            raise ValueError(f"Signal period must be at least 2, got {self.signal_period}")

        # Set indicators list for tracking
        self.indicators = [f'MACD_{self.fast_period}_{self.slow_period}_{self.signal_period}']
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

        # Calculate minimum required data points (slow period + signal period)
        min_required = self.slow_period + self.signal_period + 10
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period)

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on MACD crossovers.

        Args:
            data: OHLCV DataFrame with at least 'close' column

        Returns:
            DataFrame with added columns:
                - macd: MACD line
                - macd_signal: Signal line
                - macd_histogram: MACD histogram
                - trend_sma: Trend filter SMA (if enabled)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            Basic:
            - BUY when MACD crosses above signal line
            - SELL when MACD crosses below signal line

            With zero-line filter:
            - BUY only when MACD > 0 (bullish momentum)
            - SELL when MACD crosses below signal OR MACD < 0

            With trend filter:
            - BUY when MACD cross AND price > trend SMA
            - SELL when MACD cross OR price < trend SMA
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate MACD
        df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(
            df['close'],
            self.fast_period,
            self.slow_period,
            self.signal_period
        )

        # Calculate trend filter if enabled
        if self.use_trend_filter:
            df['trend_sma'] = sma(df['close'], self.trend_period)

        # Initialize signal and position columns
        df['signal'] = 0
        df['position'] = 0

        # Detect MACD crossovers
        df['prev_macd'] = df['macd'].shift(1)
        df['prev_signal'] = df['macd_signal'].shift(1)

        # Bullish crossover: MACD crosses above signal line (was below, now above)
        bullish_cross = (df['prev_macd'] <= df['prev_signal']) & (df['macd'] > df['macd_signal'])

        # Bearish crossover: MACD crosses below signal line (was above, now below)
        bearish_cross = (df['prev_macd'] >= df['prev_signal']) & (df['macd'] < df['macd_signal'])

        # Apply filters
        if self.use_zero_line_filter:
            # Only buy when MACD is above zero (bullish territory)
            bullish_cross = bullish_cross & (df['macd'] > 0)
            # Sell when bearish cross OR MACD drops below zero
            bearish_cross = bearish_cross | ((df['prev_macd'] >= 0) & (df['macd'] < 0))

        if self.use_trend_filter:
            # Only buy in uptrend
            uptrend = df['close'] > df['trend_sma']
            bullish_cross = bullish_cross & uptrend

        # Set signals
        df.loc[bullish_cross, 'signal'] = 1
        df.loc[bearish_cross, 'signal'] = -1

        # Histogram divergence detection (optional advanced feature)
        if self.use_histogram_divergence:
            df = self._detect_divergence(df)

        # Forward fill signals to maintain positions
        start_idx = self.slow_period + self.signal_period + 1
        if self.use_trend_filter:
            start_idx = max(start_idx, self.trend_period)

        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0
            elif self.use_trend_filter and df['position'].iloc[i-1] == 1:
                # Check if we should exit due to trend break (only if we have a position)
                if df['close'].iloc[i] < df['trend_sma'].iloc[i]:
                    df.loc[df.index[i:], 'position'] = 0

        # Clean up temporary columns
        df.drop(['prev_macd', 'prev_signal'], axis=1, inplace=True)

        return df

    def _detect_divergence(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect bullish/bearish divergence in MACD histogram.

        Divergence occurs when price makes new high/low but MACD histogram doesn't confirm.
        This can signal a potential reversal.

        Args:
            df: DataFrame with price and MACD data

        Returns:
            DataFrame with divergence signals added
        """
        # Look for divergence over a rolling window
        window = 20

        # Bullish divergence: price makes lower low, but MACD histogram makes higher low
        # This suggests weakening bearish momentum - potential reversal up
        for i in range(window, len(df)):
            window_data = df.iloc[i-window:i+1]

            # Check if current price is local low
            if df['close'].iloc[i] == window_data['close'].min():
                # Check if MACD histogram is NOT at its lowest (higher low)
                if df['macd_histogram'].iloc[i] > window_data['macd_histogram'].min():
                    # Bullish divergence detected - potential buy signal
                    if df['signal'].iloc[i] == 1:  # Strengthen buy signal
                        df.loc[df.index[i], 'signal'] = 1

            # Bearish divergence: price makes higher high, but MACD histogram makes lower high
            # This suggests weakening bullish momentum - potential reversal down
            if df['close'].iloc[i] == window_data['close'].max():
                # Check if MACD histogram is NOT at its highest (lower high)
                if df['macd_histogram'].iloc[i] < window_data['macd_histogram'].max():
                    # Bearish divergence detected - potential sell signal
                    if df['signal'].iloc[i] == -1:  # Strengthen sell signal
                        df.loc[df.index[i], 'signal'] = -1

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (slow period + signal period + buffer)
        """
        min_required = self.slow_period + self.signal_period + 20
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period + 10)
        return min_required

    def __repr__(self) -> str:
        """String representation of the strategy."""
        filters = []
        if self.use_zero_line_filter:
            filters.append("zero_line")
        if self.use_histogram_divergence:
            filters.append("divergence")
        if self.use_trend_filter:
            filters.append(f"trend_SMA{self.trend_period}")

        filter_str = f", filters=[{', '.join(filters)}]" if filters else ""

        return (
            f"MACDCrossover({self.fast_period}/{self.slow_period}/{self.signal_period}"
            f"{filter_str})"
        )


class MACD_Standard(MACDCrossover):
    """
    Standard MACD strategy using 12/26/9 parameters.

    This is the classic MACD setup popularized by Gerald Appel.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with standard MACD parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'MACD 12/26/9'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['fast_period'] = config['parameters'].get('fast_period', 12)
        config['parameters']['slow_period'] = config['parameters'].get('slow_period', 26)
        config['parameters']['signal_period'] = config['parameters'].get('signal_period', 9)

        super().__init__(config)


class MACD_ZeroLine(MACDCrossover):
    """
    MACD strategy with zero-line filter.

    Only takes long positions when MACD is above zero (strong uptrend).
    Reduces false signals in weak trends.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with zero-line filter enabled."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'MACD Zero-Line Filter'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['fast_period'] = config['parameters'].get('fast_period', 12)
        config['parameters']['slow_period'] = config['parameters'].get('slow_period', 26)
        config['parameters']['signal_period'] = config['parameters'].get('signal_period', 9)
        config['parameters']['use_zero_line_filter'] = True

        super().__init__(config)
