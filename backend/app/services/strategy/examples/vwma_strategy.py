"""
Volume-Weighted Moving Average (VWMA) Crossover Strategies

VWMA gives more weight to price periods with higher volume, making it more responsive
to institutional activity and significant price moves. This can provide earlier signals
than traditional moving averages during high-volume trend changes.
"""
from typing import Dict, Any
import pandas as pd
from app.services.strategy.base_strategy import Strategy
from app.services.strategy.indicators import vwma, sma


class VWMACrossover(Strategy):
    """
    VWMA Crossover Strategy.

    Entry Logic:
    - BUY: Fast VWMA crosses above Slow VWMA (bullish crossover with volume confirmation)
    - SELL: Fast VWMA crosses below Slow VWMA (bearish crossover with volume confirmation)

    Similar to MA Crossover but uses volume weighting to emphasize high-volume moves.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fast_period = self.parameters.get('fast_period', 10)
        self.slow_period = self.parameters.get('slow_period', 30)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on VWMA crossovers."""
        df = data.copy()

        # Calculate VWMAs
        df['vwma_fast'] = vwma(df['close'], df['volume'], self.fast_period)
        df['vwma_slow'] = vwma(df['close'], df['volume'], self.slow_period)

        # Previous values for crossover detection
        df['prev_fast'] = df['vwma_fast'].shift(1)
        df['prev_slow'] = df['vwma_slow'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: Fast VWMA crosses above Slow VWMA (golden cross with volume)
        bullish_cross = (df['prev_fast'] <= df['prev_slow']) & (df['vwma_fast'] > df['vwma_slow'])
        df.loc[bullish_cross, 'signal'] = 1

        # SELL: Fast VWMA crosses below Slow VWMA (death cross with volume)
        bearish_cross = (df['prev_fast'] >= df['prev_slow']) & (df['vwma_fast'] < df['vwma_slow'])
        df.loc[bearish_cross, 'signal'] = -1

        return df


class VWMAvsSMA(Strategy):
    """
    VWMA vs SMA Strategy.

    Entry Logic:
    - BUY: VWMA crosses above SMA (volume-weighted momentum turning bullish)
    - SELL: VWMA crosses below SMA (volume-weighted momentum turning bearish)

    Compares volume-weighted MA to simple MA to detect when volume is supporting price moves.
    If VWMA > SMA, recent high-volume periods are pushing price higher.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.period = self.parameters.get('period', 20)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals comparing VWMA to SMA."""
        df = data.copy()

        # Calculate VWMA and SMA of same period
        df['vwma'] = vwma(df['close'], df['volume'], self.period)
        df['sma'] = sma(df['close'], self.period)

        # Previous values for crossover detection
        df['prev_vwma'] = df['vwma'].shift(1)
        df['prev_sma'] = df['sma'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: VWMA crosses above SMA (volume supporting upside)
        bullish_cross = (df['prev_vwma'] <= df['prev_sma']) & (df['vwma'] > df['sma'])
        df.loc[bullish_cross, 'signal'] = 1

        # SELL: VWMA crosses below SMA (volume supporting downside)
        bearish_cross = (df['prev_vwma'] >= df['prev_sma']) & (df['vwma'] < df['sma'])
        df.loc[bearish_cross, 'signal'] = -1

        return df


class VWMAPricePosition(Strategy):
    """
    VWMA Price Position Strategy.

    Entry Logic:
    - BUY: Price crosses above VWMA (price strength vs volume-weighted average)
    - SELL: Price crosses below VWMA (price weakness vs volume-weighted average)

    Uses VWMA as a dynamic support/resistance level.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.vwma_period = self.parameters.get('vwma_period', 20)

    def setup(self, data: pd.DataFrame) -> None:
        """Setup strategy - no special initialization needed."""
        pass

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on price position vs VWMA."""
        df = data.copy()

        # Calculate VWMA
        df['vwma'] = vwma(df['close'], df['volume'], self.vwma_period)

        # Previous values for crossover detection
        df['prev_close'] = df['close'].shift(1)
        df['prev_vwma'] = df['vwma'].shift(1)

        # Initialize signal column
        df['signal'] = 0

        # BUY: Price crosses above VWMA (bullish)
        bullish_cross = (df['prev_close'] <= df['prev_vwma']) & (df['close'] > df['vwma'])
        df.loc[bullish_cross, 'signal'] = 1

        # SELL: Price crosses below VWMA (bearish)
        bearish_cross = (df['prev_close'] >= df['prev_vwma']) & (df['close'] < df['vwma'])
        df.loc[bearish_cross, 'signal'] = -1

        return df


# Strategy variants with different parameters
class VWMA10_30(VWMACrossover):
    """VWMA Crossover 10/30 (fast, more signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'fast_period': 10,
            'slow_period': 30
        }
        super().__init__(config)


class VWMA20_50(VWMACrossover):
    """VWMA Crossover 20/50 (standard, balanced signals)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'fast_period': 20,
            'slow_period': 50
        }
        super().__init__(config)


class VWMA50_200(VWMACrossover):
    """VWMA Crossover 50/200 (slow, golden/death cross equivalent)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'fast_period': 50,
            'slow_period': 200
        }
        super().__init__(config)


class VWMAvsSMA20(VWMAvsSMA):
    """VWMA vs SMA with 20-period (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'period': 20
        }
        super().__init__(config)


class VWMAvsSMA50(VWMAvsSMA):
    """VWMA vs SMA with 50-period (longer-term)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'period': 50
        }
        super().__init__(config)


class VWMAPrice20(VWMAPricePosition):
    """VWMA Price Position with 20-period (standard)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'vwma_period': 20
        }
        super().__init__(config)


class VWMAPrice50(VWMAPricePosition):
    """VWMA Price Position with 50-period (longer-term support/resistance)."""
    def __init__(self, config: Dict[str, Any]):
        config['parameters'] = {
            'vwma_period': 50
        }
        super().__init__(config)
