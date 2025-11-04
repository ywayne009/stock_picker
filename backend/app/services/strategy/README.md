# Trading Strategy Framework

This module provides a complete framework for building, testing, and executing trading strategies.

## Overview

The strategy framework consists of:
- **Base Strategy Class** - Abstract base class that all strategies inherit from
- **Technical Indicators** - Pure pandas implementations of common indicators
- **Example Strategies** - Ready-to-use strategy implementations

## Quick Start

```python
from app.services.strategy.examples.ma_crossover import MovingAverageCrossover
import pandas as pd

# Create strategy configuration
config = {
    'name': 'My MA Strategy',
    'parameters': {
        'fast_period': 20,
        'slow_period': 50,
        'ma_type': 'sma',
        'position_size': 0.1,
        'stop_loss': 0.05,
        'take_profit': 0.15
    }
}

# Initialize strategy
strategy = MovingAverageCrossover(config)

# Load your OHLCV data (must have: open, high, low, close, volume)
data = pd.read_csv('your_data.csv')

# Setup and generate signals
strategy.setup(data)
results = strategy.generate_signals(data)

# View signals
buy_signals = results[results['signal'] == 1]
sell_signals = results[results['signal'] == -1]
```

## Base Strategy Class

All strategies must inherit from `Strategy` and implement:

### Required Methods

- `setup(data)` - Initialize strategy with data validation
- `generate_signals(data)` - Generate buy/sell signals (returns DataFrame with 'signal' column)

### Built-in Methods

- `calculate_position_size(signal, portfolio_value, current_price, volatility)` - Position sizing logic
- `risk_management(position, current_price, data)` - Stop-loss and take-profit
- `validate_data(data)` - Ensures required columns exist
- `get_required_history()` - Returns minimum bars needed

### Signal Convention

- `1` = Buy signal
- `0` = Hold / No signal
- `-1` = Sell signal

## Technical Indicators

The `indicators.py` module provides:

### Trend Indicators
- `sma(data, period)` - Simple Moving Average
- `ema(data, period)` - Exponential Moving Average
- `macd(data, fast, slow, signal)` - MACD with signal line and histogram

### Momentum Indicators
- `rsi(data, period)` - Relative Strength Index
- `stochastic(high, low, close, k_period, d_period)` - Stochastic Oscillator

### Volatility Indicators
- `bollinger_bands(data, period, std_dev)` - Bollinger Bands
- `atr(high, low, close, period)` - Average True Range
- `calculate_volatility(close, period)` - Rolling volatility

### Volume Indicators
- `obv(close, volume)` - On-Balance Volume
- `vwap(high, low, close, volume)` - Volume Weighted Average Price

### Trend Strength
- `adx(high, low, close, period)` - Average Directional Index

## Example Strategies

### 1. Moving Average Crossover

Classic trend-following strategy using two moving averages:

```python
from app.services.strategy.examples.ma_crossover import MovingAverageCrossover

strategy = MovingAverageCrossover({
    'name': 'My MA Strategy',
    'parameters': {
        'fast_period': 20,
        'slow_period': 50,
        'ma_type': 'sma'  # or 'ema'
    }
})
```

**Variants:**
- `GoldenCross50_200` - Classic 50/200 day golden cross
- `FastMACrossover` - Faster 10/30 day EMA crossover

## Creating Custom Strategies

```python
from app.services.strategy.base_strategy import Strategy
from app.services.strategy import indicators
import pandas as pd

class MyCustomStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.rsi_period = self.parameters.get('rsi_period', 14)
        self.rsi_oversold = self.parameters.get('rsi_oversold', 30)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 70)

    def setup(self, data):
        self.validate_data(data)

    def generate_signals(self, data):
        df = data.copy()

        # Calculate RSI
        df['rsi'] = indicators.rsi(df['close'], self.rsi_period)

        # Generate signals
        df['signal'] = 0
        df.loc[df['rsi'] < self.rsi_oversold, 'signal'] = 1  # Buy
        df.loc[df['rsi'] > self.rsi_overbought, 'signal'] = -1  # Sell

        return df

    def get_required_history(self):
        return self.rsi_period + 10
```

## Testing Strategies

Run the demo script to test strategies:

```bash
cd backend
source venv/bin/activate
python demo_strategy.py
```

The demo script shows:
- Signal generation
- Position sizing
- Risk management
- Strategy comparison

## Strategy Configuration

Strategies accept a configuration dictionary with:

```python
config = {
    'name': str,              # Required: Strategy name
    'description': str,       # Optional: Description
    'version': str,           # Optional: Version (default: '1.0.0')
    'parameters': {
        # Strategy-specific parameters
        'fast_period': int,
        'slow_period': int,

        # Common parameters (with defaults)
        'position_size': 0.1,      # 10% of portfolio per trade
        'stop_loss': 0.05,         # 5% stop loss
        'take_profit': 0.15        # 15% take profit
    }
}
```

## Risk Management

Default risk management includes:

- **Stop Loss**: Close position if loss exceeds threshold
- **Take Profit**: Close position if profit exceeds target
- **Position Sizing**: Fixed fractional sizing (10% default)
- **Volatility Adjustment**: Optional volatility-based position sizing

Override `risk_management()` and `calculate_position_size()` for custom logic.

## Data Requirements

All strategies expect OHLCV data in pandas DataFrame format:

```python
# Required columns
df = pd.DataFrame({
    'open': float,     # Opening price
    'high': float,     # High price
    'low': float,      # Low price
    'close': float,    # Closing price
    'volume': int      # Volume
}, index=pd.DatetimeIndex)
```

## Best Practices

1. **Avoid Look-Ahead Bias**: Only use data available at each timestamp
2. **Handle NaN Values**: Use `.fillna()` or `.dropna()` appropriately
3. **Test Thoroughly**: Use the demo script and backtest before live trading
4. **Document Parameters**: Clearly document strategy parameters
5. **Version Control**: Use semantic versioning for strategy changes

## Next Steps

1. Integrate with backtesting engine
2. Add database persistence (strategy repository)
3. Connect to live data feeds
4. Build API endpoints for strategy management
5. Add more example strategies (RSI, Bollinger Bands, etc.)

## Files

- `base_strategy.py` - Abstract base class
- `indicators.py` - Technical indicators library
- `examples/ma_crossover.py` - Moving average crossover strategies
- `strategy_repository.py` - Database persistence (placeholder)
- `strategy_executor.py` - Strategy execution engine (placeholder)
- `../../../demo_strategy.py` - Demo and testing script
