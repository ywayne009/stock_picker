"""
Bollinger Band Mean Reversion Strategy

A mean-reversion strategy that generates signals when price touches Bollinger Band extremes.

Strategy Logic:
- BUY when price touches or crosses below lower band (price is stretched to downside)
- SELL when price touches or crosses above upper band (price is stretched to upside)
- EXIT when price returns to middle band (20 SMA)

Bollinger Bands adapt to volatility - they widen during volatile periods and narrow
during quiet periods, making them effective across different market conditions.

Performance Notes:
- Works best in ranging/sideways markets
- Can generate significant losses during breakouts (price stays outside bands)
- Adding trend filter helps avoid false signals during strong trends
- Band squeeze (narrow bands) often precedes large moves
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from ..base_strategy import Strategy
from ..indicators import bollinger_bands, sma, atr


class BollingerBandMeanReversion(Strategy):
    """
    Bollinger Band Mean Reversion Strategy.

    Generates buy signals when price touches lower band and sell signals when price
    touches upper band. Exits positions when price returns to middle band.

    Parameters:
        bb_period (int): Period for Bollinger Bands (default: 20)
        bb_std_dev (float): Number of standard deviations for bands (default: 2.0)
        exit_at_middle (bool): Exit when price returns to middle band (default: True)
        use_trend_filter (bool): Only trade with overall trend (default: False)
        trend_period (int): Period for trend SMA if using trend filter (default: 200)
        position_size (float): Fraction of portfolio to risk per trade (default: 0.1)
        stop_loss (float): Stop loss percentage (default: 0.05 = 5%)
        take_profit (float): Take profit percentage (default: 0.15 = 15%)

    Example:
        >>> config = {
        ...     'name': 'BB Mean Reversion 20,2',
        ...     'parameters': {
        ...         'bb_period': 20,
        ...         'bb_std_dev': 2.0,
        ...         'exit_at_middle': True,
        ...         'use_trend_filter': True
        ...     }
        ... }
        >>> strategy = BollingerBandMeanReversion(config)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Bollinger Band Mean Reversion strategy."""
        super().__init__(config)

        # Strategy-specific parameters
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std_dev = self.parameters.get('bb_std_dev', 2.0)
        self.exit_at_middle = self.parameters.get('exit_at_middle', True)
        self.use_trend_filter = self.parameters.get('use_trend_filter', False)
        self.trend_period = self.parameters.get('trend_period', 200)

        # Validate parameters
        if self.bb_period < 2:
            raise ValueError(f"BB period must be at least 2, got {self.bb_period}")

        if self.bb_std_dev <= 0:
            raise ValueError(f"BB std dev must be positive, got {self.bb_std_dev}")

        # Set indicators list for tracking
        self.indicators = [f'BB_{self.bb_period}_{self.bb_std_dev}']
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
        min_required = self.bb_period + 10
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period)

        if len(data) < min_required:
            raise ValueError(
                f"Insufficient data: strategy requires at least {min_required} bars, "
                f"got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Bollinger Band touches.

        Args:
            data: OHLCV DataFrame with at least 'close' column

        Returns:
            DataFrame with added columns:
                - bb_upper: Upper Bollinger Band
                - bb_middle: Middle Bollinger Band (SMA)
                - bb_lower: Lower Bollinger Band
                - bb_width: Band width (volatility measure)
                - trend_sma: Trend filter SMA (if enabled)
                - signal: Trading signal (1=buy, 0=hold, -1=sell)
                - position: Current position (1=long, 0=flat)

        Signal Logic:
            Basic:
            - BUY when price touches/crosses below lower band
            - SELL when price touches/crosses above upper band
            - EXIT (if enabled) when price returns to middle band

            With trend filter:
            - BUY when price touches lower band AND price > trend SMA (uptrend)
            - SELL when price touches upper band OR price < trend SMA (downtrend)
        """
        # Make a copy to avoid modifying original data
        df = data.copy()

        # Calculate Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = bollinger_bands(
            df['close'],
            self.bb_period,
            self.bb_std_dev
        )

        # Calculate band width (useful for detecting squeezes)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        # Calculate trend filter if enabled
        if self.use_trend_filter:
            df['trend_sma'] = sma(df['close'], self.trend_period)

        # Initialize signal and position columns
        df['signal'] = 0
        df['position'] = 0

        # Detect band touches
        # Buy signal: price touches or goes below lower band
        lower_band_touch = df['close'] <= df['bb_lower']

        # Sell signal: price touches or goes above upper band
        upper_band_touch = df['close'] >= df['bb_upper']

        # Exit signal: price returns to middle band (optional)
        middle_band_return = None
        if self.exit_at_middle:
            # Price crosses middle band from below (close position after buying dip)
            df['prev_close'] = df['close'].shift(1)
            middle_band_return = (df['prev_close'] < df['bb_middle']) & (df['close'] >= df['bb_middle'])

        # Apply trend filter if enabled
        if self.use_trend_filter:
            uptrend = df['close'] > df['trend_sma']

            # Only buy dips in uptrend
            df.loc[lower_band_touch & uptrend, 'signal'] = 1
            df.loc[upper_band_touch, 'signal'] = -1
        else:
            # No trend filter - pure mean reversion
            df.loc[lower_band_touch, 'signal'] = 1

            if self.exit_at_middle:
                # Exit on middle band return OR upper band touch
                df.loc[upper_band_touch | middle_band_return, 'signal'] = -1
            else:
                df.loc[upper_band_touch, 'signal'] = -1

        # Forward fill signals to maintain positions
        start_idx = self.bb_period + 1
        if self.use_trend_filter:
            start_idx = max(start_idx, self.trend_period)

        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:  # Buy signal
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:  # Sell signal
                df.loc[df.index[i:], 'position'] = 0
            elif self.use_trend_filter and self.exit_at_middle and df['position'].iloc[i-1] == 1:
                # Check for exit conditions when trend filter is enabled
                if df['close'].iloc[i] < df['trend_sma'].iloc[i]:
                    # Trend broke down
                    df.loc[df.index[i:], 'position'] = 0
                elif middle_band_return is not None and middle_band_return.iloc[i]:
                    # Price returned to middle band
                    df.loc[df.index[i:], 'position'] = 0

        # Clean up temporary columns
        if 'prev_close' in df.columns:
            df.drop(['prev_close'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        """
        Return the minimum number of bars required for this strategy.

        Returns:
            Number of bars (BB period + buffer)
        """
        min_required = self.bb_period + 20
        if self.use_trend_filter:
            min_required = max(min_required, self.trend_period + 10)
        return min_required

    def __repr__(self) -> str:
        """String representation of the strategy."""
        exit_str = ", exit_at_middle=True" if self.exit_at_middle else ""
        trend_str = f", trend_filter=SMA{self.trend_period}" if self.use_trend_filter else ""

        return (
            f"BollingerBandMeanReversion(period={self.bb_period}, "
            f"std_dev={self.bb_std_dev}{exit_str}{trend_str})"
        )


class BB_Standard(BollingerBandMeanReversion):
    """
    Standard Bollinger Band strategy using 20-period, 2 std dev.

    This is the classic Bollinger Band setup developed by John Bollinger.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with standard BB parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'BB Mean Reversion 20,2'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['bb_period'] = config['parameters'].get('bb_period', 20)
        config['parameters']['bb_std_dev'] = config['parameters'].get('bb_std_dev', 2.0)
        config['parameters']['exit_at_middle'] = config['parameters'].get('exit_at_middle', True)

        super().__init__(config)


class BB_Tight(BollingerBandMeanReversion):
    """
    Tight Bollinger Band strategy using 20-period, 1.5 std dev.

    Generates more signals with tighter bands. More sensitive to price movements.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with tighter BB parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'BB Tight 20,1.5'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['bb_period'] = config['parameters'].get('bb_period', 20)
        config['parameters']['bb_std_dev'] = config['parameters'].get('bb_std_dev', 1.5)
        config['parameters']['exit_at_middle'] = config['parameters'].get('exit_at_middle', True)

        super().__init__(config)


class BB_Wide(BollingerBandMeanReversion):
    """
    Wide Bollinger Band strategy using 20-period, 2.5 std dev.

    Generates fewer signals with wider bands. More conservative, catches extreme moves.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with wider BB parameters."""
        if config is None:
            config = {}

        if 'name' not in config:
            config['name'] = 'BB Wide 20,2.5'

        if 'parameters' not in config:
            config['parameters'] = {}

        config['parameters']['bb_period'] = config['parameters'].get('bb_period', 20)
        config['parameters']['bb_std_dev'] = config['parameters'].get('bb_std_dev', 2.5)
        config['parameters']['exit_at_middle'] = config['parameters'].get('exit_at_middle', True)

        super().__init__(config)
