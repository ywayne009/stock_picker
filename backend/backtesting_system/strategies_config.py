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
from app.services.strategy.examples.rsi_strategy import (
    RSIOverboughtOversold,
    RSI30_70,
    RSI20_80
)
from app.services.strategy.examples.macd_strategy import (
    MACDCrossover,
    MACD_Standard,
    MACD_ZeroLine
)
from app.services.strategy.examples.bollinger_strategy import (
    BollingerBandMeanReversion,
    BB_Standard,
    BB_Tight,
    BB_Wide
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
# STRATEGY REGISTRATION
# ==============================================================================
# Register our professional strategy implementations

# Note: The old inline strategy classes have been replaced with professional
# implementations in app/services/strategy/examples/
# These new implementations include:
# - Comprehensive parameter validation
# - Optional trend filters
# - Better signal detection (crossover-based vs level-based)
# - More configuration options
# - Better documentation


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

    # RSI Mean Reversion Strategies
    'rsi_30_70': {
        'name': 'RSI 30/70',
        'parameters': {
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70,
            'use_trend_filter': False,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.10
        }
    },

    'rsi_20_80': {
        'name': 'RSI 20/80 Conservative',
        'parameters': {
            'rsi_period': 14,
            'oversold_threshold': 20,
            'overbought_threshold': 80,
            'use_trend_filter': False,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.15
        }
    },

    'rsi_trend_filter': {
        'name': 'RSI 30/70 with Trend Filter',
        'parameters': {
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70,
            'use_trend_filter': True,
            'trend_period': 200,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.12
        }
    },

    # MACD Trend Following Strategies
    'macd_standard': {
        'name': 'MACD 12/26/9',
        'parameters': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'use_zero_line_filter': False,
            'use_trend_filter': False,
            'position_size': 0.15,
            'stop_loss': 0.05,
            'take_profit': 0.12
        }
    },

    'macd_zero_line': {
        'name': 'MACD Zero-Line Filter',
        'parameters': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'use_zero_line_filter': True,
            'use_trend_filter': False,
            'position_size': 0.15,
            'stop_loss': 0.05,
            'take_profit': 0.15
        }
    },

    'macd_divergence': {
        'name': 'MACD with Divergence Detection',
        'parameters': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'use_histogram_divergence': True,
            'use_zero_line_filter': False,
            'position_size': 0.15,
            'stop_loss': 0.05,
            'take_profit': 0.12
        }
    },

    # Bollinger Band Mean Reversion Strategies
    'bb_standard': {
        'name': 'BB Mean Reversion 20,2',
        'parameters': {
            'bb_period': 20,
            'bb_std_dev': 2.0,
            'exit_at_middle': True,
            'use_trend_filter': False,
            'position_size': 0.10,
            'stop_loss': 0.04,
            'take_profit': 0.08
        }
    },

    'bb_tight': {
        'name': 'BB Tight 20,1.5',
        'parameters': {
            'bb_period': 20,
            'bb_std_dev': 1.5,
            'exit_at_middle': True,
            'use_trend_filter': False,
            'position_size': 0.10,
            'stop_loss': 0.03,
            'take_profit': 0.06
        }
    },

    'bb_wide': {
        'name': 'BB Wide 20,2.5',
        'parameters': {
            'bb_period': 20,
            'bb_std_dev': 2.5,
            'exit_at_middle': True,
            'use_trend_filter': False,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.10
        }
    },

    'bb_trend_filter': {
        'name': 'BB with Trend Filter',
        'parameters': {
            'bb_period': 20,
            'bb_std_dev': 2.0,
            'exit_at_middle': True,
            'use_trend_filter': True,
            'trend_period': 200,
            'position_size': 0.10,
            'stop_loss': 0.04,
            'take_profit': 0.10
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
