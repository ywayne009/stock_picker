# Stock Picker Architecture Guide

## 📐 New Modular Architecture

The codebase has been refactored into a clean, modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│                                                               │
│  run_backtest.py        │  Easy CLI for running backtests   │
│  strategies_config.py    │  Strategy definitions & configs   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│                                                               │
│  • Fetches market data                                       │
│  • Creates strategy instances                                │
│  • Runs backtests                                             │
│  • Generates visualizations                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────┬──────────────────┬──────────────────────┐
│   BACKTEST ENGINE │  STRATEGY ENGINE │  VISUALIZATION       │
│                   │                  │                      │
│  • BacktestEngine │  • Base Strategy │  • Charts            │
│  • Portfolio sim  │  • MA Crossover  │  • Metrics           │
│  • Trade tracking │  • RSI          │  • Dashboards        │
│  • Metrics calc   │  • MACD          │  • Themes            │
│                   │  • Bollinger     │                      │
│                   │  • Registry      │                      │
└───────────────────┴──────────────────┴──────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│                                                               │
│  • Market Data Fetcher (multi-provider support)             │
│  • OHLCV data (stocks, crypto, options)                     │
│  • Caching & validation                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ File Structure

### **Core Modules**

```
backend/
├── run_backtest.py              ⭐ Main entry point (CLI)
├── strategies_config.py         ⭐ Strategy definitions (edit here!)
│
├── app/services/
│   ├── backtesting/
│   │   ├── __init__.py
│   │   └── engine.py           → BacktestEngine (strategy-agnostic)
│   │
│   ├── strategy/
│   │   ├── base_strategy.py    → Strategy base class
│   │   ├── registry.py         → Strategy registration system
│   │   ├── indicators.py       → Technical indicators
│   │   └── examples/
│   │       └── ma_crossover.py → Moving average strategies
│   │
│   ├── data/
│   │   └── market_data.py      → Data fetching (multi-provider)
│   │
│   └── visualization/
│       ├── strategy_charts.py  → Chart generation
│       ├── performance_metrics.py → Metrics calculation
│       └── chart_themes.py     → Dark/light themes
│
└── output/charts/              → Generated visualizations
```

### **Legacy Demo Files** (preserved for reference)

```
├── demo_strategy.py            → Original single-stock demo
└── demo_multi_stock.py         → Multi-stock comparison demo
```

---

## 🎯 How It Works

### **1. Define Your Strategy** (`strategies_config.py`)

This is the **ONLY file you need to edit** to test different strategies!

```python
# Example: Create a custom strategy configuration
MY_CUSTOM_STRATEGY = {
    'name': 'My Custom MA Strategy',
    'parameters': {
        'fast_period': 15,      # Try different values!
        'slow_period': 40,
        'ma_type': 'ema',       # 'sma' or 'ema'
        'position_size': 0.12,  # 12% per trade
        'stop_loss': 0.06,      # 6% stop loss
        'take_profit': 0.18     # 18% target
    }
}
```

**Or use pre-defined presets:**
- `moderate` - MA 20/50 SMA (balanced)
- `aggressive` - MA 10/30 EMA (active trading)
- `conservative` - MA 50/200 SMA (long-term)
- `rsi_oversold` - RSI mean reversion
- `bollinger_bounce` - Bollinger Bands
- `macd_crossover` - MACD signals

### **2. Run Backtest** (`run_backtest.py`)

Simple CLI with powerful options:

```bash
# Single stock, single strategy
python run_backtest.py --ticker AAPL --strategy moderate

# Multiple stocks, same strategy
python run_backtest.py --tickers AAPL MSFT NVDA --strategy aggressive

# Single stock, compare strategies
python run_backtest.py --ticker AAPL --strategies moderate aggressive conservative

# Custom parameters on the fly
python run_backtest.py --ticker TSLA --strategy moderate --custom fast_period=15 slow_period=40

# List all available strategies
python run_backtest.py --list
```

### **3. View Results**

Automatically generates interactive dark-themed dashboards:
- Equity curves
- Buy/sell signals on price charts
- Performance metrics (Return, Sharpe, Drawdown, etc.)
- Trade analysis
- Multi-asset/multi-strategy comparisons

All charts **auto-open in your browser!**

---

## 🔧 Key Components

### **BacktestEngine** (`app/services/backtesting/engine.py`)

Universal backtesting engine that works with **any strategy** and **any asset type**.

```python
from app.services.backtesting import BacktestEngine

engine = BacktestEngine(
    initial_capital=100000,
    commission=0.001,    # 0.1%
    slippage=0.0005      # 0.05%
)

result = engine.run_backtest(
    strategy=my_strategy,
    data=price_data,
    ticker='AAPL'
)
```

**Features:**
- ✅ Strategy-agnostic (works with any strategy class)
- ✅ Asset-agnostic (stocks, crypto, options, etc.)
- ✅ Realistic simulation (commissions, slippage)
- ✅ Comprehensive trade tracking
- ✅ Built-in performance metrics
- ✅ Multi-asset backtesting support

### **Strategy Base Class** (`app/services/strategy/base_strategy.py`)

All strategies inherit from this:

```python
from app.services.strategy.base_strategy import Strategy

class MyStrategy(Strategy):
    def setup(self, data):
        """Initialize indicators and parameters."""
        self.period = self.parameters.get('period', 20)

    def generate_signals(self, data):
        """Generate buy/sell signals."""
        df = data.copy()
        # Your logic here
        df['signal'] = 0  # 1=buy, -1=sell, 0=hold
        df['position'] = df['signal'].replace(0, method='ffill')
        return df
```

**Required Methods:**
- `setup(data)` - Initialize strategy
- `generate_signals(data)` - Generate buy/sell signals

**Built-in Features:**
- Position sizing
- Risk management (stop-loss, take-profit)
- Parameter validation

### **Strategy Registry** (`app/services/strategy/registry.py`)

Manage and access strategies easily:

```python
from app.services.strategy.registry import register_strategy

# Register a strategy with decorator
@register_strategy('my_strategy', 'Description', category='trend')
class MyStrategy(Strategy):
    pass

# Get strategy later
strategy_class = get_strategy('my_strategy')
```

---

## 📊 Performance Metrics

The system calculates 20+ metrics automatically:

**Returns:**
- Total Return %
- CAGR (Compound Annual Growth Rate)
- Expectancy (avg profit per trade)

**Risk:**
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown %
- Volatility

**Trade Stats:**
- Total Trades
- Win Rate %
- Profit Factor
- Average Win/Loss
- Largest Win/Loss

**Duration:**
- Average trade duration
- Max/min trade duration
- Drawdown duration

---

## 🎨 Visualization System

**Auto-generated charts:**

1. **Price Charts** - Candlesticks with buy/sell signals
2. **Equity Curves** - Portfolio value over time
3. **Drawdown Charts** - Visual drawdown analysis
4. **Metrics Dashboards** - Performance summary
5. **Comparison Charts** - Multi-stock or multi-strategy

**Themes:**
- Dark (default) - Professional, easy on eyes
- Light - Traditional appearance

**Export formats:**
- HTML (interactive, zoomable)
- PNG, PDF (static images)

---

## 🚀 Usage Examples

### Example 1: Test a Single Stock

```bash
python run_backtest.py --ticker NVDA --strategy aggressive
```

**Output:**
```
================================================================================
  Running Backtest: NVDA - Fast MA 10/30 EMA
================================================================================
  📊 Fetching NVDA data...
     → 689 days from 2022-01-03 to 2024-09-30

  📈 Results:
     → Total Return:     19.81%
     → CAGR:              6.83%
     → Sharpe Ratio:      0.80
     → Max Drawdown:      3.97%
     → Win Rate:          44.4%
     → Total Trades:         9

  ✅ Done! Dashboard opened in browser.
```

### Example 2: Compare Strategies

```bash
python run_backtest.py --ticker AAPL --strategies moderate aggressive rsi_oversold
```

Generates comparison chart showing all 3 strategies side-by-side.

### Example 3: Multi-Stock Comparison

```bash
python run_backtest.py --tickers AAPL MSFT TSLA NVDA META AMZN --strategy moderate
```

Generates unified dashboard comparing all stocks.

### Example 4: Custom Parameters

```bash
python run_backtest.py --ticker BTC-USD --strategy high_volatility \
    --custom fast_period=10 slow_period=30 stop_loss=0.15
```

---

## 🛠️ Adding a New Strategy

### Method 1: Use Presets (Easiest)

Edit `strategies_config.py` and add to `STRATEGY_PRESETS`:

```python
STRATEGY_PRESETS = {
    # ... existing presets ...

    'my_new_strategy': {
        'name': 'My New Strategy',
        'parameters': {
            'fast_period': 12,
            'slow_period': 26,
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.15
        }
    }
}
```

Then run:
```bash
python run_backtest.py --ticker AAPL --strategy my_new_strategy
```

### Method 2: Create Custom Strategy Class

Add to `strategies_config.py`:

```python
@register_strategy('momentum_strategy', 'Buy on strong momentum', category='trend')
class MomentumStrategy(Strategy):
    def setup(self, data):
        self.lookback = self.parameters.get('lookback', 20)

    def generate_signals(self, data):
        df = data.copy()

        # Calculate momentum
        momentum = df['close'].pct_change(self.lookback)

        # Generate signals
        df['signal'] = 0
        df.loc[momentum > 0.05, 'signal'] = 1   # Buy if +5% momentum
        df.loc[momentum < -0.05, 'signal'] = -1  # Sell if -5% momentum

        df['position'] = df['signal'].replace(0, method='ffill').fillna(0)
        return df
```

Then use it:
```bash
python run_backtest.py --ticker TSLA --strategy momentum_strategy
```

### Method 3: Import External Strategy

```python
# In strategies_config.py
from my_custom_strategies import AdvancedMLStrategy

STRATEGY_PRESETS = {
    'ml_strategy': {
        'name': 'Machine Learning Strategy',
        'parameters': {
            'model_type': 'random_forest',
            'features': ['rsi', 'macd', 'volume']
        }
    }
}
```

---

## 🔍 Asset Type Support

The architecture supports **multiple asset types**:

### Stocks
```bash
python run_backtest.py --ticker AAPL --strategy moderate
```

### Crypto
```bash
python run_backtest.py --ticker BTC-USD --strategy high_volatility
```

### ETFs
```bash
python run_backtest.py --ticker SPY --strategy conservative
```

### Forex (if data provider supports)
```bash
python run_backtest.py --ticker EURUSD=X --strategy day_trading
```

---

## 📈 Advanced Features

### Portfolio-Level Backtesting

```python
from app.services.backtesting import BacktestEngine

engine = BacktestEngine(initial_capital=100000)

# Backtest multiple assets
assets_data = {
    'AAPL': aapl_data,
    'MSFT': msft_data,
    'NVDA': nvda_data
}

results = engine.run_multi_asset_backtest(
    strategy=my_strategy,
    assets_data=assets_data
)
```

### Strategy Comparison

```python
from app.services.backtesting import MultiStrategyBacktest

comparator = MultiStrategyBacktest(
    strategies=[strategy1, strategy2, strategy3],
    data=price_data,
    ticker='AAPL'
)

results = comparator.run()
```

---

## 🎓 Best Practices

### 1. Strategy Development Workflow

1. **Start with a preset** - Use existing strategies as templates
2. **Modify parameters** - Tune for your needs
3. **Backtest** - Test on historical data
4. **Compare** - Test against other strategies
5. **Validate** - Test on different stocks/timeframes
6. **Refine** - Iterate based on results

### 2. Parameter Tuning

- **Conservative**: Longer MAs (50/200), wider stops (7-10%)
- **Aggressive**: Shorter MAs (10/30), tighter stops (3-5%)
- **Volatile assets**: Wider stops (10-20%), larger targets (20-40%)
- **Stable assets**: Tighter stops (3-5%), smaller targets (8-15%)

### 3. Avoid Overfitting

- ✅ Test on multiple stocks
- ✅ Test on different time periods
- ✅ Use walk-forward analysis
- ✅ Keep strategies simple
- ❌ Don't optimize for one stock only
- ❌ Don't over-tune parameters

### 4. Realistic Expectations

- Include commissions and slippage
- Account for market impact
- Consider position limits
- Factor in execution delays

---

## 🔄 Migration from Old Demos

**Old way** (`demo_strategy.py` or `demo_multi_stock.py`):
```python
# Lots of configuration and setup code
# Hard to modify
# Mixed concerns
```

**New way** (`run_backtest.py` + `strategies_config.py`):
```bash
# One-line command
python run_backtest.py --ticker AAPL --strategy moderate
```

**Benefits:**
- ✅ Cleaner separation of concerns
- ✅ Easy to switch strategies
- ✅ Reusable components
- ✅ Extensible architecture
- ✅ Better testing capabilities

---

## 📚 Additional Resources

- **Strategy Examples**: See `strategies_config.py`
- **API Reference**: See docstrings in each module
- **Indicators**: See `app/services/strategy/indicators.py`
- **Chart Customization**: See `app/services/visualization/`

---

## 🐛 Troubleshooting

**Q: Strategy not found**
```bash
python run_backtest.py --list  # See all available strategies
```

**Q: Data fetch failed**
- Check ticker symbol is valid
- Check internet connection
- Try different data provider

**Q: Backtest runs but no signals**
- Strategy parameters may be too conservative
- Not enough historical data (need 200+ days for 50/200 MA)
- Check strategy logic

**Q: Charts not opening**
- Check browser settings
- Look in `output/charts/` directory
- Open HTML files manually

---

## 🎯 Summary

**Key Features:**
- 🔧 Modular architecture
- 📝 Easy strategy definition
- 🚀 Simple CLI interface
- 📊 Comprehensive metrics
- 🎨 Beautiful visualizations
- 🔄 Multiple comparison modes
- 💎 Production-ready code

**Three simple steps:**
1. **Edit** `strategies_config.py`
2. **Run** `python run_backtest.py`
3. **Analyze** results in browser

That's it! 🎉
