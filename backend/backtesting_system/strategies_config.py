"""
Strategy Configurations

THIS FILE IS WHERE YOU DEFINE AND CONFIGURE YOUR STRATEGIES.

You can:
1. Create new strategy instances with different parameters
2. Import existing strategy classes and configure them
3. Define custom strategies by inheriting from Strategy base class
4. Register strategies for easy access

This file is separate from the backtesting engine, making it easy to
experiment with different strategies without changing core code.
"""

import sys
from pathlib import Path

# Add parent directory (backend/) to path to access app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.strategy.examples.ma_crossover import (
    MovingAverageCrossover,
    GoldenCross50_200,
    FastMACrossover
)
from app.services.strategy.registry import register_strategy
from app.services.strategy.base_strategy import Strategy
import pandas as pd
import numpy as np


# ==============================================================================
# PRE-DEFINED STRATEGY CONFIGURATIONS
# ==============================================================================
# These are ready-to-use strategy configurations.
# Simply modify the parameters and run your backtest!

# Strategy 1: Moderate/Balanced (20/50 SMA)
# Best for: Swing trading, medium-term holds
STRATEGY_MODERATE = {
    'name': 'MA Crossover 20/50 SMA',
    'parameters': {
        'fast_period': 20,
        'slow_period': 50,
        'ma_type': 'sma',
        'position_size': 0.10,  # 10%
        'stop_loss': 0.05,      # 5%
        'take_profit': 0.15     # 15%
    }
}

# Strategy 2: Conservative (50/200 SMA - Golden Cross)
# Best for: Long-term investing, retirement accounts
STRATEGY_CONSERVATIVE = {
    'name': 'Golden Cross 50/200 SMA',
    'parameters': {
        'fast_period': 50,
        'slow_period': 200,
        'ma_type': 'sma',
        'position_size': 0.05,  # 5%
        'stop_loss': 0.07,      # 7%
        'take_profit': 0.20     # 20%
    }
}

# Strategy 3: Aggressive (10/30 EMA)
# Best for: Active trading, volatile markets
STRATEGY_AGGRESSIVE = {
    'name': 'Fast MA 10/30 EMA',
    'parameters': {
        'fast_period': 10,
        'slow_period': 30,
        'ma_type': 'ema',
        'position_size': 0.20,  # 20%
        'stop_loss': 0.04,      # 4%
        'take_profit': 0.10     # 10%
    }
}

# Strategy 4: Day Trading (5/15 EMA)
# Best for: Very active trading, intraday signals
STRATEGY_DAY_TRADING = {
    'name': 'Day Trading 5/15 EMA',
    'parameters': {
        'fast_period': 5,
        'slow_period': 15,
        'ma_type': 'ema',
        'position_size': 0.25,  # 25%
        'stop_loss': 0.02,      # 2%
        'take_profit': 0.05     # 5%
    }
}

# Strategy 5: Crypto/High Volatility (15/45 EMA)
# Best for: Crypto, volatile small caps
STRATEGY_HIGH_VOLATILITY = {
    'name': 'Crypto 15/45 EMA',
    'parameters': {
        'fast_period': 15,
        'slow_period': 45,
        'ma_type': 'ema',
        'position_size': 0.15,  # 15%
        'stop_loss': 0.12,      # 12%
        'take_profit': 0.30     # 30%
    }
}


# ==============================================================================
# CUSTOM STRATEGY EXAMPLES
# ==============================================================================
# You can define your own strategies here by inheriting from Strategy.

@register_strategy(
    'rsi_oversold',
    'Buy when RSI < 30, sell when RSI > 70',
    category='mean_reversion'
)
class RSIOversoldStrategy(Strategy):
    """
    Simple RSI-based mean reversion strategy.

    Buys when RSI drops below oversold threshold (default 30)
    Sells when RSI rises above overbought threshold (default 70)
    """

    def setup(self, data: pd.DataFrame) -> None:
        """Setup RSI parameters."""
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.oversold = self.parameters.get('oversold', 30)
        self.overbought = self.parameters.get('overbought', 70)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate RSI-based signals."""
        df = data.copy()

        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Generate signals
        df['rsi'] = rsi
        df['signal'] = 0
        df.loc[rsi < self.oversold, 'signal'] = 1   # Buy when oversold
        df.loc[rsi > self.overbought, 'signal'] = -1  # Sell when overbought

        # Track position
        df['position'] = df['signal'].replace(0, method='ffill').fillna(0)

        return df


@register_strategy(
    'bollinger_bounce',
    'Buy at lower band, sell at upper band',
    category='mean_reversion'
)
class BollingerBounceStrategy(Strategy):
    """
    Bollinger Bands mean reversion strategy.

    Buys when price touches lower band
    Sells when price touches upper band
    """

    def setup(self, data: pd.DataFrame) -> None:
        """Setup Bollinger Bands parameters."""
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std = self.parameters.get('bb_std', 2)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate Bollinger Bands signals."""
        df = data.copy()

        # Calculate Bollinger Bands
        sma = df['close'].rolling(window=self.bb_period).mean()
        std = df['close'].rolling(window=self.bb_period).std()
        upper_band = sma + (self.bb_std * std)
        lower_band = sma - (self.bb_std * std)

        df['bb_upper'] = upper_band
        df['bb_middle'] = sma
        df['bb_lower'] = lower_band

        # Generate signals
        df['signal'] = 0
        df.loc[df['close'] <= lower_band, 'signal'] = 1   # Buy at lower band
        df.loc[df['close'] >= upper_band, 'signal'] = -1  # Sell at upper band

        # Track position
        df['position'] = df['signal'].replace(0, method='ffill').fillna(0)

        return df


@register_strategy(
    'macd_crossover',
    'MACD line crosses signal line',
    category='trend'
)
class MACDCrossoverStrategy(Strategy):
    """
    MACD crossover strategy.

    Buys when MACD line crosses above signal line
    Sells when MACD line crosses below signal line
    """

    def setup(self, data: pd.DataFrame) -> None:
        """Setup MACD parameters."""
        self.fast_period = self.parameters.get('fast_period', 12)
        self.slow_period = self.parameters.get('slow_period', 26)
        self.signal_period = self.parameters.get('signal_period', 9)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate MACD signals."""
        df = data.copy()

        # Calculate MACD
        ema_fast = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = macd_line - signal_line

        # Generate signals on crossovers
        df['signal'] = 0
        df['prev_macd'] = macd_line.shift(1)
        df['prev_signal'] = signal_line.shift(1)

        # Buy: MACD crosses above signal
        df.loc[
            (macd_line > signal_line) & (df['prev_macd'] <= df['prev_signal']),
            'signal'
        ] = 1

        # Sell: MACD crosses below signal
        df.loc[
            (macd_line < signal_line) & (df['prev_macd'] >= df['prev_signal']),
            'signal'
        ] = -1

        # Track position
        df['position'] = df['signal'].replace(0, method='ffill').fillna(0)

        return df


# ==============================================================================
# STRATEGY PRESETS
# ==============================================================================
# Easy-to-use presets that you can reference by name

STRATEGY_PRESETS = {
    # Moving Average Crossover variations
    'moderate': STRATEGY_MODERATE,
    'conservative': STRATEGY_CONSERVATIVE,
    'aggressive': STRATEGY_AGGRESSIVE,
    'day_trading': STRATEGY_DAY_TRADING,
    'high_volatility': STRATEGY_HIGH_VOLATILITY,

    # Mean reversion
    'rsi_oversold': {
        'name': 'RSI Oversold Strategy',
        'parameters': {
            'rsi_period': 14,
            'oversold': 30,
            'overbought': 70,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.10
        }
    },

    'bollinger_bounce': {
        'name': 'Bollinger Bounce Strategy',
        'parameters': {
            'bb_period': 20,
            'bb_std': 2,
            'position_size': 0.10,
            'stop_loss': 0.04,
            'take_profit': 0.08
        }
    },

    # Trend following
    'macd_crossover': {
        'name': 'MACD Crossover Strategy',
        'parameters': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'position_size': 0.15,
            'stop_loss': 0.05,
            'take_profit': 0.12
        }
    }
}


def get_strategy_config(preset_name: str) -> dict:
    """
    Get a strategy configuration by preset name.

    Args:
        preset_name: Name of the preset (e.g., 'moderate', 'aggressive')

    Returns:
        Strategy configuration dictionary

    Example:
        config = get_strategy_config('moderate')
        strategy = MovingAverageCrossover(config)
    """
    if preset_name not in STRATEGY_PRESETS:
        available = ', '.join(STRATEGY_PRESETS.keys())
        raise ValueError(
            f"Preset '{preset_name}' not found. "
            f"Available presets: {available}"
        )

    return STRATEGY_PRESETS[preset_name]


def create_custom_strategy(
    strategy_type: str,
    **params
) -> dict:
    """
    Create a custom strategy configuration.

    Args:
        strategy_type: Type of strategy (e.g., 'ma_crossover', 'rsi')
        **params: Strategy parameters

    Returns:
        Strategy configuration dictionary

    Example:
        config = create_custom_strategy(
            'ma_crossover',
            fast_period=15,
            slow_period=40,
            ma_type='ema',
            position_size=0.12
        )
    """
    return {
        'name': f"Custom {strategy_type}",
        'parameters': params
    }


# ==============================================================================
# HELPER: PRINT ALL AVAILABLE STRATEGIES
# ==============================================================================

def print_available_strategies():
    """Print all available strategy presets."""
    print("\n" + "="*80)
    print("  AVAILABLE STRATEGY PRESETS")
    print("="*80 + "\n")

    categories = {
        'Moving Average Crossover': ['moderate', 'conservative', 'aggressive', 'day_trading', 'high_volatility'],
        'Mean Reversion': ['rsi_oversold', 'bollinger_bounce'],
        'Trend Following': ['macd_crossover']
    }

    for category, strategies in categories.items():
        print(f"\n{category}:")
        print("-" * 80)
        for name in strategies:
            if name in STRATEGY_PRESETS:
                config = STRATEGY_PRESETS[name]
                params = config.get('parameters', {})
                print(f"  • {name:<20} - {config.get('name', 'N/A')}")
                if 'fast_period' in params:
                    print(f"      → MA: {params['fast_period']}/{params['slow_period']} {params.get('ma_type', 'sma').upper()}")
                print(f"      → Position: {params.get('position_size', 0)*100:.0f}%, "
                      f"Stop: {params.get('stop_loss', 0)*100:.0f}%, "
                      f"Target: {params.get('take_profit', 0)*100:.0f}%")

    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    # When run directly, print available strategies
    print_available_strategies()
