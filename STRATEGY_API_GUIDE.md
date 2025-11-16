# Strategy Development API Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-14
**For:** Stock Picker Trading System

This is a **comprehensive, single-file guide** for external developers to create custom trading strategies for the Stock Picker system.

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Strategy Architecture](#strategy-architecture)
3. [Core Concepts](#core-concepts)
4. [Creating Your First Strategy](#creating-your-first-strategy)
5. [Strategy Types & Metadata](#strategy-types--metadata)
6. [Advanced Features](#advanced-features)
7. [Testing & Validation](#testing--validation)
8. [Best Practices](#best-practices)
9. [Complete Examples](#complete-examples)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Strategy Creation

```python
from app.services.strategy import Strategy, register_strategy, StrategyMetadata
from app.services.strategy import StrategyType, StrategyCategory, MarketRegime
import pandas as pd

# 1. Create metadata (optional but recommended)
MY_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.TREND_FOLLOWING,
    best_market_regime=[MarketRegime.TRENDING],
    complexity="simple",
    suitable_for_beginners=True,
    description="My first trading strategy",
    tags=["sma", "crossover"]
)

# 2. Define your strategy class
class MyFirstStrategy(Strategy):
    """A simple SMA crossover strategy."""

    def setup(self, data: pd.DataFrame) -> None:
        """Initialize strategy parameters."""
        # Validate we have enough data
        self.validate_data(data)

        # Get parameters from config
        self.fast_period = self.parameters.get('fast_period', 10)
        self.slow_period = self.parameters.get('slow_period', 20)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals."""
        df = data.copy()

        # Calculate indicators
        df['sma_fast'] = df['close'].rolling(self.fast_period).mean()
        df['sma_slow'] = df['close'].rolling(self.slow_period).mean()

        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1   # Buy
        df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1  # Sell

        # Track position
        df['position'] = 0
        for i in range(self.slow_period, len(df)):
            if df['signal'].iloc[i] == 1:
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:
                df.loc[df.index[i:], 'position'] = 0

        return df

# 3. Register with factory (optional)
register_strategy('my_strategy', MY_METADATA)(MyFirstStrategy)

# 4. Use your strategy
config = {
    'name': 'My SMA Strategy',
    'parameters': {'fast_period': 10, 'slow_period': 20}
}
strategy = MyFirstStrategy(config)
```

**That's it!** Your strategy is ready to backtest.

---

## Strategy Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Strategy System                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Strategy   │      │  Strategy    │                     │
│  │   Factory    │─────▶│   Registry   │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                      │                             │
│         │                      ▼                             │
│         │              ┌──────────────┐                     │
│         └─────────────▶│  Metadata    │                     │
│                        │  System      │                     │
│                        └──────────────┘                     │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │          Your Custom Strategy                    │        │
│  │  (inherits from Strategy base class)             │        │
│  └─────────────────────────────────────────────────┘        │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  Backtesting │      │  Technical   │                     │
│  │    Engine    │      │  Indicators  │                     │
│  └──────────────┘      └──────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Strategy Base Class** - Abstract base that all strategies inherit from
2. **Strategy Factory** - Creates strategy instances from configurations
3. **Strategy Registry** - Manages and discovers available strategies
4. **Metadata System** - Provides rich descriptions and categorization
5. **Backtesting Engine** - Simulates strategy performance on historical data
6. **Technical Indicators** - Pre-built indicator library

---

## Core Concepts

### 1. Strategy Lifecycle

```
Configuration → Setup → Signal Generation → Position Tracking → Risk Management
```

1. **Configuration**: Pass parameters to strategy
2. **Setup**: Validate data and initialize indicators
3. **Signal Generation**: Core logic producing buy/sell signals
4. **Position Tracking**: Maintain current position state
5. **Risk Management**: Apply stop-loss/take-profit rules

### 2. Signal Convention

Strategies generate **discrete signals** at each time step:

- `1` = **BUY signal** - Enter long position
- `0` = **HOLD signal** - No action, maintain current position
- `-1` = **SELL signal** - Exit position (or enter short if enabled)

### 3. Required DataFrame Columns

**Input (OHLCV data):**
```python
['open', 'high', 'low', 'close', 'volume']
```

**Output (your strategy must add):**
```python
['signal']    # Required: 1, 0, or -1
['position']  # Recommended: Current position (0 or 1 for long-only)
```

**Optional (for visualization):**
```python
['indicator_name']  # Any indicators you calculate
['entry_price']     # Entry prices for trades
['exit_price']      # Exit prices for trades
```

### 4. No Look-Ahead Bias

**CRITICAL:** Strategies must NEVER use future data.

```python
# ❌ WRONG - Uses future data
df['signal'] = (df['close'].shift(-1) > df['close']).astype(int)

# ✅ CORRECT - Only uses past data
df['signal'] = (df['close'] > df['close'].shift(1)).astype(int)
```

---

## Creating Your First Strategy

### Step-by-Step Tutorial

Let's build a **Bollinger Band Bounce** strategy from scratch.

#### Step 1: Import Required Modules

```python
from typing import Dict, Any
import pandas as pd
import numpy as np

from app.services.strategy import Strategy
from app.services.strategy.indicators import bollinger_bands, sma
from app.services.strategy import (
    StrategyType,
    StrategyCategory,
    MarketRegime,
    TimeFrame,
    StrategyMetadata,
    register_strategy
)
```

#### Step 2: Define Metadata

```python
BB_BOUNCE_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.MEAN_REVERSION,
    best_market_regime=[MarketRegime.RANGING, MarketRegime.LOW_VOLATILITY],
    typical_timeframe=TimeFrame.SWING,
    complexity="simple",
    requires_indicators=['Bollinger Bands'],
    min_data_points=30,
    suitable_for_beginners=True,
    description="Buy when price touches lower band, sell at upper band",
    pros=[
        "Clear entry/exit points",
        "Adapts to volatility",
        "Works in ranging markets"
    ],
    cons=[
        "Fails in strong trends",
        "False signals during breakouts"
    ],
    tags=["bollinger", "mean_reversion", "volatility"]
)
```

#### Step 3: Create Strategy Class

```python
class BollingerBounce(Strategy):
    """
    Bollinger Band Bounce Strategy.

    Buys when price touches lower band (oversold),
    Sells when price touches upper band (overbought).
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize strategy."""
        super().__init__(config)

        # Get parameters
        self.bb_period = self.parameters.get('bb_period', 20)
        self.bb_std = self.parameters.get('bb_std', 2.0)

        # Validate
        if self.bb_period < 2:
            raise ValueError(f"BB period must be >= 2, got {self.bb_period}")

        if self.bb_std <= 0:
            raise ValueError(f"BB std must be positive, got {self.bb_std}")

        # Track indicators
        self.indicators = [f'BB_{self.bb_period}_{self.bb_std}']

    def setup(self, data: pd.DataFrame) -> None:
        """Setup and validate data."""
        self.validate_data(data)

        if len(data) < self.bb_period + 10:
            raise ValueError(
                f"Need at least {self.bb_period + 10} bars, got {len(data)}"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals."""
        df = data.copy()

        # Calculate Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = bollinger_bands(
            df['close'],
            period=self.bb_period,
            std_dev=self.bb_std
        )

        # Initialize signals
        df['signal'] = 0
        df['position'] = 0

        # Buy when price touches lower band
        df.loc[df['close'] <= df['bb_lower'], 'signal'] = 1

        # Sell when price touches upper band
        df.loc[df['close'] >= df['bb_upper'], 'signal'] = -1

        # Track position
        start_idx = self.bb_period + 1
        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:  # Buy
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:  # Sell
                df.loc[df.index[i:], 'position'] = 0

        return df

    def get_required_history(self) -> int:
        """Minimum bars needed."""
        return self.bb_period + 20
```

#### Step 4: Register Strategy

```python
# Register with factory
register_strategy('bollinger_bounce', BB_BOUNCE_METADATA)(BollingerBounce)
```

#### Step 5: Test Your Strategy

```python
from app.services.backtesting.engine import BacktestEngine
from app.services.data import fetch_stock_data
from datetime import datetime, timedelta

# Fetch data
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

data = fetch_stock_data(
    symbol='AAPL',
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

# Create strategy
config = {
    'name': 'BB Bounce Test',
    'parameters': {
        'bb_period': 20,
        'bb_std': 2.0
    }
}
strategy = BollingerBounce(config)

# Run backtest
engine = BacktestEngine(
    initial_capital=100000,
    commission=0.001,
    slippage=0.0005
)

results = engine.run_backtest(strategy, data, 'AAPL')

# View results
print(f"Total Return: {results.metrics.total_return*100:.2f}%")
print(f"Win Rate: {results.metrics.win_rate*100:.1f}%")
print(f"Sharpe Ratio: {results.metrics.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.metrics.max_drawdown*100:.2f}%")
```

**Done!** You've created, registered, and tested your first strategy.

---

## Strategy Types & Metadata

### Available Strategy Types

```python
from app.services.strategy import StrategyType

StrategyType.SIGNAL                   # Type 1: Single-asset signals
StrategyType.PORTFOLIO                # Type 2: Multi-asset weights
StrategyType.PAIR_TRADING            # Type 3: Pair spreads
StrategyType.OPTIONS                  # Type 4: Options strategies
StrategyType.MARKET_MAKING           # Type 5: Market making
StrategyType.STATISTICAL_ARBITRAGE   # Type 6: Statistical arbitrage
StrategyType.ML_BASED                # Type 7: ML/AI strategies
```

### Strategy Categories

```python
from app.services.strategy import StrategyCategory

# For signal-based strategies
StrategyCategory.TREND_FOLLOWING     # MA crossovers, breakouts
StrategyCategory.MEAN_REVERSION      # RSI, Bollinger Bands
StrategyCategory.MOMENTUM            # MACD, ROC
StrategyCategory.VOLATILITY          # ATR, Keltner
StrategyCategory.VOLUME              # OBV, A/D line
StrategyCategory.MULTI_INDICATOR     # Combined signals
StrategyCategory.PATTERN             # Chart patterns
```

### Market Regimes

```python
from app.services.strategy import MarketRegime

MarketRegime.TRENDING        # Strong directional movement
MarketRegime.RANGING         # Sideways/choppy
MarketRegime.VOLATILE        # High volatility
MarketRegime.LOW_VOLATILITY  # Quiet markets
MarketRegime.BULL            # Rising markets
MarketRegime.BEAR            # Falling markets
MarketRegime.ALL             # Works everywhere
```

### Complete Metadata Example

```python
ADVANCED_METADATA = StrategyMetadata(
    # Classification
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.MULTI_INDICATOR,

    # Performance characteristics
    best_market_regime=[MarketRegime.TRENDING, MarketRegime.VOLATILE],
    typical_timeframe=TimeFrame.SWING,  # INTRADAY, SWING, POSITION, LONG_TERM

    # Complexity
    complexity="advanced",  # simple, medium, advanced, expert
    requires_indicators=['RSI', 'MACD', 'Volume'],
    requires_features=[],   # e.g., ['ml_model', 'options_data']
    min_data_points=100,

    # User guidance
    suitable_for_beginners=False,
    description="Multi-indicator confirmation strategy",
    pros=[
        "High-conviction signals",
        "Multiple confirmations",
        "Filters false signals"
    ],
    cons=[
        "Fewer trading opportunities",
        "More complex to tune",
        "Requires more data"
    ],

    # Searchability
    tags=["multi_indicator", "confirmation", "rsi", "macd"],
    author="Your Name",
    version="1.0.0"
)
```

---

## Advanced Features

### 1. Custom Position Sizing

Override `calculate_position_size()` for dynamic sizing:

```python
class VolatilityAdjustedStrategy(Strategy):
    """Adjust position size based on volatility."""

    def calculate_position_size(
        self,
        signal: int,
        portfolio_value: float,
        current_price: float,
        volatility: float = None
    ) -> float:
        """Reduce size in high volatility."""
        if signal == 0:
            return 0.0

        # Base position (10% of portfolio)
        base_position = portfolio_value * 0.10

        # Calculate ATR-based volatility
        if volatility is not None and volatility > 0:
            # Target 2% portfolio volatility
            target_vol = 0.02
            vol_adjustment = min(1.0, target_vol / volatility)
            base_position *= vol_adjustment

        # Convert to shares
        shares = base_position / current_price

        return shares if signal == 1 else -shares
```

### 2. Custom Risk Management

Override `risk_management()` for advanced exits:

```python
class TrailingStopStrategy(Strategy):
    """Use trailing stop instead of fixed stop."""

    def __init__(self, config):
        super().__init__(config)
        self.trailing_stop_pct = self.parameters.get('trailing_stop', 0.10)
        self.highest_price = {}  # Track highest price per position

    def risk_management(
        self,
        position: Dict[str, Any],
        current_price: float,
        data: pd.DataFrame = None
    ) -> str:
        """Trailing stop loss."""
        if not position or position.get('quantity', 0) == 0:
            return None

        position_id = id(position)

        # Update highest price
        if position_id not in self.highest_price:
            self.highest_price[position_id] = current_price
        else:
            self.highest_price[position_id] = max(
                self.highest_price[position_id],
                current_price
            )

        # Check trailing stop
        highest = self.highest_price[position_id]
        drawdown_from_peak = (highest - current_price) / highest

        if drawdown_from_peak >= self.trailing_stop_pct:
            # Clean up
            del self.highest_price[position_id]
            return 'close'

        return None
```

### 3. Multi-Timeframe Analysis

```python
class MultiTimeframeStrategy(Strategy):
    """Use multiple timeframes for confirmation."""

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Daily signals
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['daily_trend'] = (df['sma_20'] > df['sma_50']).astype(int)

        # Weekly signals (resample to weekly)
        weekly = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        weekly['sma_10'] = weekly['close'].rolling(10).mean()
        weekly['weekly_trend'] = (weekly['close'] > weekly['sma_10']).astype(int)

        # Merge weekly back to daily
        df = df.join(weekly[['weekly_trend']], how='left')
        df['weekly_trend'] = df['weekly_trend'].fillna(method='ffill')

        # Combine: only buy when both timeframes agree
        df['signal'] = 0
        df.loc[(df['daily_trend'] == 1) & (df['weekly_trend'] == 1), 'signal'] = 1
        df.loc[(df['daily_trend'] == 0) & (df['weekly_trend'] == 0), 'signal'] = -1

        # Position tracking...
        df['position'] = 0
        # (Implementation similar to previous examples)

        return df
```

### 4. Machine Learning Integration

```python
class MLStrategy(Strategy):
    """Strategy using ML model for predictions."""

    def __init__(self, config):
        super().__init__(config)
        self.model = None  # Load your trained model here

    def setup(self, data: pd.DataFrame) -> None:
        self.validate_data(data)
        # Load model
        # self.model = joblib.load('models/my_model.pkl')

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Engineer features
        df['returns'] = df['close'].pct_change()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        df['volume_sma'] = df['volume'].rolling(20).mean()

        # Prepare feature matrix
        features = ['returns', 'sma_20', 'rsi', 'volume_sma']
        X = df[features].dropna()

        # Predict
        # predictions = self.model.predict(X)
        # df.loc[X.index, 'prediction'] = predictions

        # Convert predictions to signals
        # df['signal'] = 0
        # df.loc[df['prediction'] > 0.6, 'signal'] = 1   # High confidence buy
        # df.loc[df['prediction'] < 0.4, 'signal'] = -1  # High confidence sell

        return df

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
```

---

## Testing & Validation

### Unit Testing Your Strategy

```python
# test_my_strategy.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from my_strategy import MyStrategy


class TestMyStrategy:
    """Unit tests for MyStrategy."""

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

        data = pd.DataFrame({
            'open': 100 + np.random.randn(100).cumsum(),
            'high': 102 + np.random.randn(100).cumsum(),
            'low': 98 + np.random.randn(100).cumsum(),
            'close': 100 + np.random.randn(100).cumsum(),
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)

        # Ensure OHLC relationships
        data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.randn(100))
        data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.randn(100))

        return data

    def test_strategy_initialization(self):
        """Test strategy can be initialized."""
        config = {'name': 'Test', 'parameters': {}}
        strategy = MyStrategy(config)
        assert strategy.name == 'Test'

    def test_generate_signals(self, sample_data):
        """Test signal generation."""
        config = {
            'name': 'Test Strategy',
            'parameters': {'fast_period': 10, 'slow_period': 20}
        }
        strategy = MyStrategy(config)
        strategy.setup(sample_data)

        result = strategy.generate_signals(sample_data)

        # Check required columns exist
        assert 'signal' in result.columns
        assert 'position' in result.columns

        # Check signal values are valid
        assert result['signal'].isin([-1, 0, 1]).all()

        # Check no NaN in signal column (after warmup)
        assert not result['signal'].iloc[20:].isna().any()

    def test_insufficient_data(self):
        """Test error handling for insufficient data."""
        config = {'name': 'Test', 'parameters': {}}
        strategy = MyStrategy(config)

        # Only 10 bars (insufficient)
        data = pd.DataFrame({
            'open': [100] * 10,
            'high': [101] * 10,
            'low': [99] * 10,
            'close': [100] * 10,
            'volume': [1000000] * 10
        })

        with pytest.raises(ValueError):
            strategy.setup(data)

    def test_no_lookahead_bias(self, sample_data):
        """Ensure strategy doesn't use future data."""
        config = {'name': 'Test', 'parameters': {}}
        strategy = MyStrategy(config)
        strategy.setup(sample_data)

        # Generate signals for full dataset
        full_signals = strategy.generate_signals(sample_data)

        # Generate signals for partial dataset
        partial_data = sample_data.iloc[:80]
        partial_signals = strategy.generate_signals(partial_data)

        # Signals at index 70 should be the same
        # (no future data was used)
        assert full_signals['signal'].iloc[70] == partial_signals['signal'].iloc[70]
```

### Integration Testing

```python
# test_strategy_integration.py
def test_strategy_with_backtest_engine():
    """Test strategy integrates with backtesting engine."""
    from app.services.backtesting.engine import BacktestEngine

    # Create strategy
    config = {
        'name': 'Integration Test',
        'parameters': {'fast_period': 10, 'slow_period': 20}
    }
    strategy = MyStrategy(config)

    # Create sample data
    data = create_sample_data(252)  # 1 year daily

    # Run backtest
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run_backtest(strategy, data, 'TEST')

    # Verify results structure
    assert results.metrics is not None
    assert results.trades is not None
    assert len(results.portfolio_history) > 0
```

### Performance Validation

```python
def validate_strategy_performance(strategy, test_data):
    """Validate strategy meets minimum performance criteria."""
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run_backtest(strategy, test_data, 'TEST')

    metrics = results.metrics

    # Minimum criteria
    assert metrics.total_trades > 0, "Strategy generated no trades"
    assert metrics.sharpe_ratio > 0, "Negative Sharpe ratio"
    assert metrics.max_drawdown < 0.50, "Max drawdown > 50%"
    assert metrics.win_rate > 0.30, "Win rate < 30%"

    # Check for overfitting
    assert metrics.total_trades > 10, "Too few trades (potential overfitting)"

    print("✅ Strategy passes validation")
    return True
```

---

## Best Practices

### 1. Parameter Validation

Always validate parameters in `__init__`:

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)

    # Get parameters
    self.period = self.parameters.get('period', 20)

    # Validate
    if self.period < 2:
        raise ValueError(f"Period must be >= 2, got {self.period}")

    if not isinstance(self.period, int):
        raise TypeError(f"Period must be integer, got {type(self.period)}")
```

### 2. Document Everything

Use docstrings extensively:

```python
class MyStrategy(Strategy):
    """
    One-line summary.

    Detailed description of what the strategy does, when it works best,
    and any important considerations.

    Parameters:
        param1 (type): Description (default: value)
        param2 (type): Description (default: value)

    Example:
        >>> config = {'name': 'My Strategy', 'parameters': {...}}
        >>> strategy = MyStrategy(config)

    References:
        - Paper/book that inspired this strategy
        - URL to methodology
    """
```

### 3. Handle Edge Cases

```python
def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Handle empty data
    if len(df) == 0:
        df['signal'] = 0
        df['position'] = 0
        return df

    # Calculate indicator
    df['indicator'] = df['close'].rolling(20).mean()

    # Handle NaN values
    df['indicator'] = df['indicator'].fillna(method='bfill')

    # Rest of logic...

    return df
```

### 4. Avoid Common Pitfalls

```python
# ❌ DON'T: Modify input data
def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
    data['signal'] = 0  # Modifies original!
    return data

# ✅ DO: Copy first
def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df['signal'] = 0
    return df

# ❌ DON'T: Use future data
df['tomorrow_high'] = df['high'].shift(-1)  # Look-ahead bias!

# ✅ DO: Use only past data
df['yesterday_high'] = df['high'].shift(1)

# ❌ DON'T: Hardcode values
self.threshold = 0.02  # What if we want to change this?

# ✅ DO: Use parameters
self.threshold = self.parameters.get('threshold', 0.02)
```

### 5. Performance Optimization

```python
# Use vectorized operations instead of loops
# ❌ SLOW
for i in range(len(df)):
    df.loc[i, 'sma'] = df['close'].iloc[i-20:i].mean()

# ✅ FAST
df['sma'] = df['close'].rolling(20).mean()

# Pre-allocate arrays
df['signal'] = 0  # Better than appending

# Use .iloc for position-based indexing
# .loc for label-based indexing
```

---

## Complete Examples

### Example 1: Triple Moving Average (Advanced)

```python
from app.services.strategy import Strategy, register_strategy
from app.services.strategy import StrategyMetadata, StrategyType, StrategyCategory
import pandas as pd

TRIPLE_MA_METADATA = StrategyMetadata(
    strategy_type=StrategyType.SIGNAL,
    category=StrategyCategory.TREND_FOLLOWING,
    complexity="medium",
    description="Buy when fast > medium > slow MA (all aligned)"
)

@register_strategy('triple_ma', TRIPLE_MA_METADATA)
class TripleMovingAverage(Strategy):
    """
    Triple MA alignment strategy.

    Only takes positions when all three MAs are aligned,
    reducing whipsaws compared to dual MA crossover.
    """

    def __init__(self, config):
        super().__init__(config)

        self.fast_period = self.parameters.get('fast_period', 10)
        self.medium_period = self.parameters.get('medium_period', 20)
        self.slow_period = self.parameters.get('slow_period', 50)

        # Validate ordering
        if not (self.fast_period < self.medium_period < self.slow_period):
            raise ValueError("Periods must be: fast < medium < slow")

        self.indicators = [
            f'SMA_{self.fast_period}',
            f'SMA_{self.medium_period}',
            f'SMA_{self.slow_period}'
        ]

    def setup(self, data: pd.DataFrame) -> None:
        self.validate_data(data)

        if len(data) < self.slow_period + 10:
            raise ValueError(
                f"Need at least {self.slow_period + 10} bars"
            )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Calculate all MAs
        df['sma_fast'] = df['close'].rolling(self.fast_period).mean()
        df['sma_medium'] = df['close'].rolling(self.medium_period).mean()
        df['sma_slow'] = df['close'].rolling(self.slow_period).mean()

        # Initialize
        df['signal'] = 0
        df['position'] = 0

        # Bullish alignment: fast > medium > slow
        bullish = (
            (df['sma_fast'] > df['sma_medium']) &
            (df['sma_medium'] > df['sma_slow'])
        )

        # Bearish alignment: fast < medium < slow
        bearish = (
            (df['sma_fast'] < df['sma_medium']) &
            (df['sma_medium'] < df['sma_slow'])
        )

        # Signals on transitions
        df['prev_bullish'] = bullish.shift(1)
        df['prev_bearish'] = bearish.shift(1)

        # Buy when entering bullish alignment
        df.loc[bullish & ~df['prev_bullish'], 'signal'] = 1

        # Sell when entering bearish alignment
        df.loc[bearish & ~df['prev_bearish'], 'signal'] = -1

        # Track position
        start_idx = self.slow_period + 1
        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:
                df.loc[df.index[i:], 'position'] = 0

        # Cleanup
        df.drop(['prev_bullish', 'prev_bearish'], axis=1, inplace=True)

        return df

    def get_required_history(self) -> int:
        return self.slow_period + 20
```

### Example 2: Hybrid Trend + Mean Reversion

```python
@register_strategy('trend_dip_buyer')
class TrendDipBuyer(Strategy):
    """
    Buy dips in uptrends.

    Only buys when:
    1. Long-term trend is up (200 SMA)
    2. Price pulls back to oversold (RSI < 30)

    Best of both: trend following + mean reversion
    """

    def __init__(self, config):
        super().__init__(config)

        self.trend_period = self.parameters.get('trend_period', 200)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.oversold = self.parameters.get('oversold', 30)
        self.overbought = self.parameters.get('overbought', 70)

    def setup(self, data: pd.DataFrame) -> None:
        self.validate_data(data)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Calculate trend
        df['trend_sma'] = df['close'].rolling(self.trend_period).mean()
        df['in_uptrend'] = df['close'] > df['trend_sma']

        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)

        # Initialize
        df['signal'] = 0
        df['position'] = 0

        # Buy: Uptrend + RSI oversold
        buy_condition = (
            df['in_uptrend'] &
            (df['rsi'] < self.oversold)
        )

        # Sell: RSI overbought OR trend breaks
        sell_condition = (
            (df['rsi'] > self.overbought) |
            ~df['in_uptrend']
        )

        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1

        # Position tracking
        start_idx = max(self.trend_period, self.rsi_period) + 1
        for i in range(start_idx, len(df)):
            if df['signal'].iloc[i] == 1:
                df.loc[df.index[i:], 'position'] = 1
            elif df['signal'].iloc[i] == -1:
                df.loc[df.index[i:], 'position'] = 0

        return df

    def _calculate_rsi(self, prices, period=14):
        """Helper to calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
```

---

## API Reference

### Strategy Base Class

```python
class Strategy(ABC):
    """Abstract base class for all strategies."""

    # Required Methods (must implement)
    @abstractmethod
    def setup(self, data: pd.DataFrame) -> None:
        """Initialize strategy before execution."""
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals."""
        pass

    # Optional Methods (can override)
    def calculate_position_size(
        self, signal, portfolio_value, current_price, volatility=None
    ) -> float:
        """Calculate position size (default: fixed 10%)."""
        pass

    def risk_management(
        self, position, current_price, data=None
    ) -> Optional[str]:
        """Check risk management rules (default: 5% stop, 15% target)."""
        pass

    def get_required_history(self) -> int:
        """Minimum bars needed (default: 50)."""
        return 50

    def validate_data(self, data: pd.DataFrame) -> None:
        """Validate OHLCV data."""
        pass

    # Properties
    self.name               # Strategy name
    self.parameters         # Dict of parameters
    self.description        # Description string
    self.version            # Version string
    self.indicators         # List of indicators used
    self.default_position_size   # Default position size (0.1 = 10%)
    self.default_stop_loss       # Default stop loss (0.05 = 5%)
    self.default_take_profit     # Default take profit (0.15 = 15%)
```

### Available Indicators

```python
from app.services.strategy.indicators import (
    sma,              # Simple Moving Average
    ema,              # Exponential Moving Average
    rsi,              # Relative Strength Index
    macd,             # MACD (returns macd, signal, histogram)
    bollinger_bands,  # Bollinger Bands (returns upper, middle, lower)
    atr,              # Average True Range
    stochastic,       # Stochastic Oscillator
    adx,              # Average Directional Index
)

# Usage examples
df['sma_20'] = sma(df['close'], period=20)
df['ema_12'] = ema(df['close'], period=12)
df['rsi_14'] = rsi(df['close'], period=14)

# MACD returns 3 values
df['macd'], df['signal'], df['hist'] = macd(
    df['close'],
    fast=12,
    slow=26,
    signal=9
)

# Bollinger Bands returns 3 values
df['bb_upper'], df['bb_middle'], df['bb_lower'] = bollinger_bands(
    df['close'],
    period=20,
    std_dev=2.0
)
```

### Factory Functions

```python
from app.services.strategy import (
    register_strategy,  # Decorator to register
    create_strategy,    # Create instance by name
    list_strategies,    # List all registered
    get_factory        # Get factory instance
)

# Register
@register_strategy('my_strategy', metadata)
class MyStrategy(Strategy):
    pass

# Create
strategy = create_strategy('my_strategy', config)

# List all
all_strategies = list_strategies()

# Search
factory = get_factory()
trend_strategies = factory.search(category='trend_following')
beginner_strategies = factory.search(beginner_friendly=True)
```

---

## Troubleshooting

### Common Errors

#### 1. "Insufficient data"

```
ValueError: Insufficient data: strategy requires 50 bars, got 30
```

**Solution:** Fetch more historical data or reduce lookback periods.

```python
# Increase data fetch period
start_date = end_date - timedelta(days=730)  # 2 years instead of 1

# OR reduce strategy periods
config['parameters']['period'] = 20  # Instead of 50
```

#### 2. "Look-ahead bias detected"

Your signals change when you add more data (using future information).

**Solution:** Only use `.shift(1)` or earlier data.

```python
# ❌ Wrong
df['signal'] = (df['close'].shift(-1) > df['close']).astype(int)

# ✅ Correct
df['signal'] = (df['close'] > df['close'].shift(1)).astype(int)
```

#### 3. "No trades generated"

Strategy runs but produces zero trades.

**Debug steps:**

```python
# 1. Check signal column
print(df['signal'].value_counts())

# 2. Check conditions are met
print(f"Indicator range: {df['indicator'].min()} to {df['indicator'].max()}")
print(f"Threshold: {self.threshold}")

# 3. Visualize
import matplotlib.pyplot as plt
df[['close', 'sma_fast', 'sma_slow']].plot()
plt.show()
```

#### 4. "Strategy overfits"

Great backtest results, poor live performance.

**Solutions:**
- Test on out-of-sample data
- Use walk-forward optimization
- Simplify the strategy
- Add realistic transaction costs

```python
# Use walk-forward testing
train_data = data[:'2023-01-01']
test_data = data['2023-01-01':]

# Train on first period, test on second
```

### Debugging Tips

```python
# Add debug prints
def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Debug: Print data info
    print(f"Data shape: {df.shape}")
    print(f"Data range: {df.index[0]} to {df.index[-1]}")

    # Calculate indicators
    df['sma'] = df['close'].rolling(20).mean()

    # Debug: Check for NaN
    print(f"NaN count: {df['sma'].isna().sum()}")

    # Generate signals
    df['signal'] = 0

    # Debug: Check signal distribution
    print(f"Signals: {df['signal'].value_counts().to_dict()}")

    return df
```

---

## Support & Resources

### Getting Help

1. **Check existing strategies** in `backend/app/services/strategy/examples/`
2. **Read the source code** of `base_strategy.py`
3. **Run tests** with `pytest tests/unit/test_strategies.py`
4. **Check documentation** in `docs/` folder

### Contributing Your Strategy

Want to share your strategy with the community?

1. Ensure it follows all guidelines in this document
2. Add comprehensive tests
3. Include metadata and documentation
4. Submit a pull request with example results

---

## Appendix: Quick Reference

### Strategy Checklist

Before deploying your strategy, ensure:

- [ ] Inherits from `Strategy` base class
- [ ] Implements `setup()` and `generate_signals()`
- [ ] Parameters are validated in `__init__()`
- [ ] No look-ahead bias (only uses past data)
- [ ] Returns DataFrame with 'signal' column
- [ ] Handles edge cases (empty data, NaN values)
- [ ] Has metadata defined
- [ ] Registered with factory (optional)
- [ ] Unit tests written
- [ ] Backtest results documented
- [ ] README/documentation updated

### Parameter Naming Conventions

```python
# Periods
'period', 'fast_period', 'slow_period', 'lookback'

# Thresholds
'threshold', 'oversold', 'overbought', 'entry_threshold'

# Risk management
'position_size', 'stop_loss', 'take_profit', 'max_loss'

# Filters
'use_trend_filter', 'use_volume_filter', 'require_confirmation'

# Indicator types
'ma_type', 'method', 'calculation_method'
```

### Common Patterns

```python
# Pattern 1: Crossover
buy = (df['fast'] > df['slow']) & (df['prev_fast'] <= df['prev_slow'])
sell = (df['fast'] < df['slow']) & (df['prev_fast'] >= df['prev_slow'])

# Pattern 2: Threshold
buy = df['indicator'] < threshold
sell = df['indicator'] > threshold

# Pattern 3: Trend Filter
buy = condition & (df['close'] > df['trend_sma'])

# Pattern 4: Position Tracking
for i in range(start_idx, len(df)):
    if df['signal'].iloc[i] == 1:
        df.loc[df.index[i:], 'position'] = 1
    elif df['signal'].iloc[i] == -1:
        df.loc[df.index[i:], 'position'] = 0
```

---

**End of Strategy Development API Guide v1.0.0**

For questions or support, please refer to the main project documentation or contact the development team.

Happy trading! 📈
