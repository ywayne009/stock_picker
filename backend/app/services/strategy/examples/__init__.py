"""Example trading strategies."""
from .ma_crossover import (
    MovingAverageCrossover,
    GoldenCross50_200,
    FastMACrossover
)
from .rsi_strategy import (
    RSIOverboughtOversold,
    RSI30_70,
    RSI20_80
)
from .macd_strategy import (
    MACDCrossover,
    MACD_Standard,
    MACD_ZeroLine
)
from .bollinger_strategy import (
    BollingerBandMeanReversion,
    BB_Standard,
    BB_Tight,
    BB_Wide
)

__all__ = [
    # Moving Average strategies
    'MovingAverageCrossover',
    'GoldenCross50_200',
    'FastMACrossover',
    # RSI strategies
    'RSIOverboughtOversold',
    'RSI30_70',
    'RSI20_80',
    # MACD strategies
    'MACDCrossover',
    'MACD_Standard',
    'MACD_ZeroLine',
    # Bollinger Band strategies
    'BollingerBandMeanReversion',
    'BB_Standard',
    'BB_Tight',
    'BB_Wide'
]
