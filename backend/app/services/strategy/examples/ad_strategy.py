"""
Accumulation/Distribution (A/D) Line Strategies

The A/D Line is a volume-based indicator that measures cumulative buying and selling pressure.
It uses the Close Location Value (CLV) to weight volume based on where the close is
relative to the high-low range.

Rising A/D suggests accumulation (buying pressure), falling A/D suggests distribution (selling pressure).
"""
from typing import Dict, Any
import pandas as pd
from app.services.strategy.base_strategy import Strategy
from app.services.strategy.indicators import accumulation_distribution, sma, ema


class ADTrendConfirmation(Strategy):
    """
    A/D Line Trend Confirmation Strategy.

    Entry Logic:
    - BUY: Price rising AND A/D Line rising (buying pressure confirms uptrend)
    - SELL: Price falling AND A/D Line falling (selling pressure confirms downtrend)

    Uses moving averages of both price and A/D to smooth signals.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.price_ma_period = self.parameters.get('price_ma_period', 20)
        self.ad_ma_period = self.parameters.get('ad_ma_period', 20)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on A/D trend confirmation."""
        df = data.copy()

        # Calculate A/D Line
        df['ad_line'] = accumulation_distribution(df['high'], df['low'], df['close'], df['volume'])

        # Calculate moving averages
        df['price_ma'] = sma(df['close'], self.price_ma_period)
        df['ad_ma'] = sma(df['ad_line'], self.ad_ma_period)

        # Previous values for trend detection
        df['prev_price_ma'] = df['price_ma'].shift(1)
        df['prev_ad_ma'] = df['ad_ma'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: Both price MA and A/D MA rising (bullish confirmation)
        price_rising = df['price_ma'] > df['prev_price_ma']
        ad_rising = df['ad_ma'] > df['prev_ad_ma']
        df.loc[price_rising & ad_rising, 'signal'] = 1

        # SELL: Both price MA and A/D MA falling (bearish confirmation)
        price_falling = df['price_ma'] < df['prev_price_ma']
        ad_falling = df['ad_ma'] < df['prev_ad_ma']
        df.loc[price_falling & ad_falling, 'signal'] = -1

        return df


class ADDivergence(Strategy):
    """
    A/D Line Divergence Strategy.

    Entry Logic:
    - BUY: Bullish divergence (price making lower lows, A/D making higher lows)
    - SELL: Bearish divergence (price making higher highs, A/D making lower highs)

    Divergences between price and A/D can signal potential reversals.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.lookback_period = self.parameters.get('lookback_period', 20)
        self.divergence_threshold = self.parameters.get('divergence_threshold', 0.02)  # 2%

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on A/D divergences."""
        df = data.copy()

        # Calculate A/D Line
        df['ad_line'] = accumulation_distribution(df['high'], df['low'], df['close'], df['volume'])

        # Calculate rolling lows and highs
        df['price_low'] = df['close'].rolling(window=self.lookback_period).min()
        df['price_high'] = df['close'].rolling(window=self.lookback_period).max()
        df['ad_low'] = df['ad_line'].rolling(window=self.lookback_period).min()
        df['ad_high'] = df['ad_line'].rolling(window=self.lookback_period).max()

        # Shift values
        df['prev_price_low'] = df['price_low'].shift(self.lookback_period)
        df['prev_price_high'] = df['price_high'].shift(self.lookback_period)
        df['prev_ad_low'] = df['ad_low'].shift(self.lookback_period)
        df['prev_ad_high'] = df['ad_high'].shift(self.lookback_period)

        # Initialize signal column
        df['signal'] = 0

        # Bullish divergence: price lower low, A/D higher low
        price_lower_low = (df['price_low'] < df['prev_price_low']) & \
                         ((df['prev_price_low'] - df['price_low']) / df['prev_price_low'] > self.divergence_threshold)
        ad_higher_low = df['ad_low'] > df['prev_ad_low']
        df.loc[price_lower_low & ad_higher_low, 'signal'] = 1

        # Bearish divergence: price higher high, A/D lower high
        price_higher_high = (df['price_high'] > df['prev_price_high']) & \
                           ((df['price_high'] - df['prev_price_high']) / df['prev_price_high'] > self.divergence_threshold)
        ad_lower_high = df['ad_high'] < df['prev_ad_high']
        df.loc[price_higher_high & ad_lower_high, 'signal'] = -1

        return df


class ADCrossover(Strategy):
    """
    A/D Line Crossover Strategy.

    Entry Logic:
    - BUY: A/D Line crosses above its MA (accumulation phase starting)
    - SELL: A/D Line crosses below its MA (distribution phase starting)

    Simple momentum approach using A/D crossovers.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ad_ma_period = self.parameters.get('ad_ma_period', 20)
        self.ma_type = self.parameters.get('ma_type', 'sma')  # 'sma' or 'ema'

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on A/D crossovers."""
        df = data.copy()

        # Calculate A/D Line
        df['ad_line'] = accumulation_distribution(df['high'], df['low'], df['close'], df['volume'])

        # Calculate A/D MA
        if self.ma_type == 'ema':
            df['ad_ma'] = ema(df['ad_line'], self.ad_ma_period)
        else:
            df['ad_ma'] = sma(df['ad_line'], self.ad_ma_period)

        # Previous values for crossover detection
        df['prev_ad'] = df['ad_line'].shift(1)
        df['prev_ad_ma'] = df['ad_ma'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: A/D crosses above MA (bullish crossover)
        bullish_cross = (df['prev_ad'] <= df['prev_ad_ma']) & (df['ad_line'] > df['ad_ma'])
        df.loc[bullish_cross, 'signal'] = 1

        # SELL: A/D crosses below MA (bearish crossover)
        bearish_cross = (df['prev_ad'] >= df['prev_ad_ma']) & (df['ad_line'] < df['ad_ma'])
        df.loc[bearish_cross, 'signal'] = -1

        return df


# Strategy variants with different parameters
class ADTrend20(ADTrendConfirmation):
    """A/D Trend Confirmation with 20-period MAs (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'price_ma_period': 20,
            'ad_ma_period': 20
        }
        super().__init__(config)


class ADTrend50LongTerm(ADTrendConfirmation):
    """A/D Trend Confirmation with 50-period MAs (long-term, fewer signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'price_ma_period': 50,
            'ad_ma_period': 50
        }
        super().__init__(config)


class ADTrend10Fast(ADTrendConfirmation):
    """A/D Trend Confirmation with 10-period MAs (fast, more signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'price_ma_period': 10,
            'ad_ma_period': 10
        }
        super().__init__(config)


class ADDivergenceStandard(ADDivergence):
    """A/D Divergence with 20-period lookback (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'lookback_period': 20,
            'divergence_threshold': 0.02
        }
        super().__init__(config)


class ADCrossover20(ADCrossover):
    """A/D Crossover with 20-period SMA (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'ad_ma_period': 20,
            'ma_type': 'sma'
        }
        super().__init__(config)


class ADCrossover20EMA(ADCrossover):
    """A/D Crossover with 20-period EMA (more responsive)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'ad_ma_period': 20,
            'ma_type': 'ema'
        }
        super().__init__(config)
