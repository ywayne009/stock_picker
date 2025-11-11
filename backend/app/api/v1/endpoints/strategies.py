"""
Strategy API Endpoints

Endpoints for listing, retrieving, and managing trading strategies.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add backtesting_system to path to access strategies_config
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backtesting_system"))

from app.api.v1.schemas import (
    StrategyInfo,
    StrategyListResponse,
    StrategyParameter,
    StrategyType,
    ErrorResponse
)
from app.services.strategy.examples.ma_crossover import MovingAverageCrossover
from app.services.strategy.registry import list_strategies, get_registry

# Import strategy configurations
try:
    from strategies_config import STRATEGY_PRESETS, get_strategy_config
except ImportError:
    STRATEGY_PRESETS = {}
    def get_strategy_config(name: str) -> dict:
        raise ImportError("strategies_config module not found")

router = APIRouter()


def _map_strategy_type(strategy_name: str) -> StrategyType:
    """Map strategy name to StrategyType enum."""
    name_lower = strategy_name.lower()

    if 'ma' in name_lower or 'moving average' in name_lower or 'crossover' in name_lower:
        return StrategyType.MA_CROSSOVER
    elif 'golden' in name_lower:
        return StrategyType.GOLDEN_CROSS
    elif 'rsi' in name_lower:
        return StrategyType.RSI
    elif 'macd' in name_lower:
        return StrategyType.MACD
    else:
        return StrategyType.CUSTOM


def _get_strategy_parameters(config: dict) -> List[StrategyParameter]:
    """Extract strategy parameters from configuration."""
    params = config.get('parameters', {})
    parameter_list = []

    # Parameter metadata (type, min, max, description)
    param_metadata = {
        'fast_period': {
            'type': 'int',
            'min_value': 2,
            'max_value': 200,
            'description': 'Fast moving average period'
        },
        'slow_period': {
            'type': 'int',
            'min_value': 5,
            'max_value': 300,
            'description': 'Slow moving average period'
        },
        'ma_type': {
            'type': 'str',
            'description': 'Moving average type (sma or ema)'
        },
        'position_size': {
            'type': 'float',
            'min_value': 0.01,
            'max_value': 1.0,
            'description': 'Position size as fraction of portfolio (0.10 = 10%)'
        },
        'stop_loss': {
            'type': 'float',
            'min_value': 0.0,
            'max_value': 0.5,
            'description': 'Stop loss as fraction (0.05 = 5%)'
        },
        'take_profit': {
            'type': 'float',
            'min_value': 0.0,
            'max_value': 2.0,
            'description': 'Take profit target as fraction (0.15 = 15%)'
        },
        'rsi_period': {
            'type': 'int',
            'min_value': 5,
            'max_value': 50,
            'description': 'RSI calculation period'
        },
        'oversold': {
            'type': 'float',
            'min_value': 10,
            'max_value': 40,
            'description': 'RSI oversold threshold'
        },
        'overbought': {
            'type': 'float',
            'min_value': 60,
            'max_value': 90,
            'description': 'RSI overbought threshold'
        },
        'bb_period': {
            'type': 'int',
            'min_value': 10,
            'max_value': 50,
            'description': 'Bollinger Bands period'
        },
        'bb_std': {
            'type': 'float',
            'min_value': 1.0,
            'max_value': 3.0,
            'description': 'Bollinger Bands standard deviations'
        },
        'signal_period': {
            'type': 'int',
            'min_value': 5,
            'max_value': 20,
            'description': 'MACD signal line period'
        }
    }

    for param_name, param_value in params.items():
        metadata = param_metadata.get(param_name, {})
        parameter_list.append(StrategyParameter(
            name=param_name,
            value=param_value,
            type=metadata.get('type', 'float'),
            min_value=metadata.get('min_value'),
            max_value=metadata.get('max_value'),
            description=metadata.get('description', param_name)
        ))

    return parameter_list


@router.get("/", response_model=StrategyListResponse)
async def list_all_strategies():
    """
    List all available trading strategies.

    Returns a comprehensive list of all strategies available for backtesting,
    including pre-configured presets and custom strategies.
    """
    try:
        strategies = []

        # Add all strategy presets from strategies_config.py
        for preset_id, config in STRATEGY_PRESETS.items():
            strategy_info = StrategyInfo(
                id=preset_id,
                name=config.get('name', preset_id),
                type=_map_strategy_type(preset_id),
                description=_get_strategy_description(preset_id),
                parameters=_get_strategy_parameters(config),
                default_params=config.get('parameters', {})
            )
            strategies.append(strategy_info)

        # Add registered strategies from registry
        registered = list_strategies()
        for reg_strategy in registered:
            # Skip if already in presets
            if reg_strategy['name'] in STRATEGY_PRESETS:
                continue

            # Create basic info for registered strategies
            strategy_info = StrategyInfo(
                id=reg_strategy['name'],
                name=reg_strategy['name'],
                type=StrategyType.CUSTOM,
                description=reg_strategy.get('description', ''),
                parameters=[],
                default_params={}
            )
            strategies.append(strategy_info)

        return StrategyListResponse(strategies=strategies)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing strategies: {str(e)}")


@router.get("/{strategy_id}", response_model=StrategyInfo)
async def get_strategy_details(strategy_id: str):
    """
    Get detailed information about a specific strategy.

    Returns the strategy's configuration, parameters, and metadata.
    """
    try:
        # Check if it's a preset strategy
        if strategy_id in STRATEGY_PRESETS:
            config = get_strategy_config(strategy_id)

            return StrategyInfo(
                id=strategy_id,
                name=config.get('name', strategy_id),
                type=_map_strategy_type(strategy_id),
                description=_get_strategy_description(strategy_id),
                parameters=_get_strategy_parameters(config),
                default_params=config.get('parameters', {})
            )

        # Check if it's a registered strategy
        registry = get_registry()
        registered = list_strategies()

        for reg_strategy in registered:
            if reg_strategy['name'] == strategy_id:
                return StrategyInfo(
                    id=strategy_id,
                    name=reg_strategy['name'],
                    type=StrategyType.CUSTOM,
                    description=reg_strategy.get('description', ''),
                    parameters=[],
                    default_params={}
                )

        # Strategy not found
        raise HTTPException(
            status_code=404,
            detail=f"Strategy '{strategy_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving strategy: {str(e)}")


@router.get("/categories/list", response_model=Dict[str, List[str]])
async def list_strategy_categories():
    """
    Get strategies organized by category.

    Returns a dictionary mapping category names to lists of strategy IDs.
    """
    try:
        categories = {
            'Moving Average Crossover': ['moderate', 'conservative', 'aggressive', 'day_trading', 'high_volatility'],
            'Mean Reversion': ['rsi_oversold', 'bollinger_bounce'],
            'Trend Following': ['macd_crossover']
        }

        return categories

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing categories: {str(e)}")


def _get_strategy_description(strategy_id: str) -> str:
    """Get human-readable description for a strategy."""
    descriptions = {
        'moderate': 'Balanced 20/50 SMA crossover strategy for swing trading and medium-term holds. Good for most market conditions.',
        'conservative': 'Golden Cross (50/200 SMA) strategy for long-term investing. Lower risk, fewer trades, ideal for retirement accounts.',
        'aggressive': 'Fast 10/30 EMA crossover for active trading in volatile markets. Higher risk/reward with more frequent signals.',
        'day_trading': 'Very fast 5/15 EMA crossover for intraday trading. Generates frequent signals for active traders.',
        'high_volatility': 'Optimized 15/45 EMA crossover for high volatility assets like crypto. Wider stops and targets.',
        'rsi_oversold': 'Mean reversion strategy that buys when RSI drops below 30 (oversold) and sells when RSI rises above 70 (overbought).',
        'bollinger_bounce': 'Trades price bounces off Bollinger Bands. Buys at lower band, sells at upper band. Works well in ranging markets.',
        'macd_crossover': 'Trend-following strategy using MACD indicator. Buys when MACD crosses above signal line, sells on opposite crossover.'
    }

    return descriptions.get(strategy_id, 'Custom trading strategy')
