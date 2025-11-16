"""
On-Balance Volume (OBV) Strategies

OBV is a momentum indicator that uses volume flow to predict changes in stock price.
Rising OBV confirms uptrends, falling OBV confirms downtrends.
Divergences between price and OBV can signal potential reversals.
"""
from typing import Dict, Any
import pandas as pd
from app.services.strategy.base_strategy import Strategy
from app.services.strategy.indicators import obv, sma


class OBVTrendConfirmation(Strategy):
    """
    OBV Trend Confirmation Strategy.

    Entry Logic:
    - BUY: Price makes new high AND OBV makes new high (confirmation)
    - SELL: Price makes new low AND OBV makes new low (confirmation)

    This strategy looks for volume confirming price trends to avoid false breakouts.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.lookback_period = self.parameters.get('lookback_period', 20)
        self.obv_ma_period = self.parameters.get('obv_ma_period', 10)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed for OBV strategies."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on OBV trend confirmation."""
        df = data.copy()

        # Calculate OBV
        df['obv'] = obv(df['close'], df['volume'])

        # Calculate OBV moving average for smoothing
        df['obv_ma'] = sma(df['obv'], self.obv_ma_period)

        # Calculate rolling highs/lows for price and OBV
        df['price_high'] = df['close'].rolling(window=self.lookback_period).max()
        df['price_low'] = df['close'].rolling(window=self.lookback_period).min()
        df['obv_high'] = df['obv_ma'].rolling(window=self.lookback_period).max()
        df['obv_low'] = df['obv_ma'].rolling(window=self.lookback_period).min()

        # Shift to get previous values
        df['prev_price_high'] = df['price_high'].shift(1)
        df['prev_obv_high'] = df['obv_high'].shift(1)
        df['prev_price_low'] = df['price_low'].shift(1)
        df['prev_obv_low'] = df['obv_low'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: Price and OBV both making new highs (bullish confirmation)
        new_price_high = df['close'] >= df['prev_price_high']
        new_obv_high = df['obv_ma'] >= df['prev_obv_high']
        df.loc[new_price_high & new_obv_high, 'signal'] = 1

        # SELL: Price and OBV both making new lows (bearish confirmation)
        new_price_low = df['close'] <= df['prev_price_low']
        new_obv_low = df['obv_ma'] <= df['prev_obv_low']
        df.loc[new_price_low & new_obv_low, 'signal'] = -1

        return df


class OBVDivergence(Strategy):
    """
    OBV Divergence Strategy.

    Entry Logic:
    - BUY: Bullish divergence (price making lower lows, OBV making higher lows)
    - SELL: Bearish divergence (price making higher highs, OBV making lower highs)

    Divergences signal potential trend reversals.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.lookback_period = self.parameters.get('lookback_period', 14)
        self.obv_ma_period = self.parameters.get('obv_ma_period', 10)
        self.divergence_threshold = self.parameters.get('divergence_threshold', 0.02)  # 2% threshold

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on OBV divergences."""
        df = data.copy()

        # Calculate OBV and its MA
        df['obv'] = obv(df['close'], df['volume'])
        df['obv_ma'] = sma(df['obv'], self.obv_ma_period)

        # Calculate rolling lows and highs
        df['price_low'] = df['close'].rolling(window=self.lookback_period).min()
        df['price_high'] = df['close'].rolling(window=self.lookback_period).max()
        df['obv_low'] = df['obv_ma'].rolling(window=self.lookback_period).min()
        df['obv_high'] = df['obv_ma'].rolling(window=self.lookback_period).max()

        # Shift values
        df['prev_price_low'] = df['price_low'].shift(self.lookback_period)
        df['prev_price_high'] = df['price_high'].shift(self.lookback_period)
        df['prev_obv_low'] = df['obv_low'].shift(self.lookback_period)
        df['prev_obv_high'] = df['obv_high'].shift(self.lookback_period)

        # Initialize signal column
        df['signal'] = 0

        # Bullish divergence: price lower low, OBV higher low
        price_lower_low = (df['price_low'] < df['prev_price_low']) & \
                         ((df['prev_price_low'] - df['price_low']) / df['prev_price_low'] > self.divergence_threshold)
        obv_higher_low = df['obv_low'] > df['prev_obv_low']
        df.loc[price_lower_low & obv_higher_low, 'signal'] = 1

        # Bearish divergence: price higher high, OBV lower high
        price_higher_high = (df['price_high'] > df['prev_price_high']) & \
                           ((df['price_high'] - df['prev_price_high']) / df['prev_price_high'] > self.divergence_threshold)
        obv_lower_high = df['obv_high'] < df['prev_obv_high']
        df.loc[price_higher_high & obv_lower_high, 'signal'] = -1

        return df


class OBVBreakout(Strategy):
    """
    OBV Breakout Strategy.

    Entry Logic:
    - BUY: OBV crosses above its MA (volume momentum turning bullish)
    - SELL: OBV crosses below its MA (volume momentum turning bearish)

    Simple trend-following approach using OBV crossover.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.obv_ma_period = self.parameters.get('obv_ma_period', 20)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on OBV crossovers."""
        df = data.copy()

        # Calculate OBV and its MA
        df['obv'] = obv(df['close'], df['volume'])
        df['obv_ma'] = sma(df['obv'], self.obv_ma_period)

        # Previous values for crossover detection
        df['prev_obv'] = df['obv'].shift(1)
        df['prev_obv_ma'] = df['obv_ma'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: OBV crosses above MA (bullish crossover)
        bullish_cross = (df['prev_obv'] <= df['prev_obv_ma']) & (df['obv'] > df['obv_ma'])
        df.loc[bullish_cross, 'signal'] = 1

        # SELL: OBV crosses below MA (bearish crossover)
        bearish_cross = (df['prev_obv'] >= df['prev_obv_ma']) & (df['obv'] < df['obv_ma'])
        df.loc[bearish_cross, 'signal'] = -1

        return df


# Strategy variants with different parameters
class OBVTrend20(OBVTrendConfirmation):
    """OBV Trend Confirmation with 20-period lookback (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'lookback_period': 20,
            'obv_ma_period': 10
        }
        super().__init__(config)


class OBVTrend30Conservative(OBVTrendConfirmation):
    """OBV Trend Confirmation with 30-period lookback (conservative, fewer signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'lookback_period': 30,
            'obv_ma_period': 15
        }
        super().__init__(config)


class OBVTrend10Aggressive(OBVTrendConfirmation):
    """OBV Trend Confirmation with 10-period lookback (aggressive, more signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'lookback_period': 10,
            'obv_ma_period': 5
        }
        super().__init__(config)


class OBVDivergenceStandard(OBVDivergence):
    """OBV Divergence with 14-period lookback (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'lookback_period': 14,
            'obv_ma_period': 10,
            'divergence_threshold': 0.02
        }
        super().__init__(config)


class OBVBreakout20(OBVBreakout):
    """OBV Breakout with 20-period MA (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'obv_ma_period': 20
        }
        super().__init__(config)
