# Stock Picker - Quick Reference

**Last Updated:** 2024-11-08
**Version:** Phase 1 Complete

---

## 📐 Project Structure

```
backend/
├── backtesting_system/         ⭐ NEW: Modular backtesting framework
│   ├── run_backtest.py         → Main CLI entry point
│   ├── strategies_config.py    → Strategy definitions (EDIT HERE!)
│   ├── README.md               → System documentation
│   ├── docs/
│   │   ├── QUICK_START.md      → Quick start guide
│   │   └── ARCHITECTURE_GUIDE.md → Detailed architecture
│   └── output/charts/          → Generated visualizations
│
├── app/services/
│   ├── backtesting/            → Universal backtest engine
│   │   └── engine.py
│   ├── strategy/
│   │   ├── base_strategy.py    → Strategy base class
│   │   ├── registry.py         → Strategy registry
│   │   ├── indicators.py       → Technical indicators
│   │   └── examples/
│   │       └── ma_crossover.py
│   ├── data/
│   │   └── market_data.py      → Multi-provider data fetching
│   └── visualization/
│       ├── strategy_charts.py  → Chart generation
│       ├── performance_metrics.py
│       └── chart_themes.py
│
├── demo_strategy.py            → Legacy: Single-stock demo
├── demo_multi_stock.py         → Legacy: Multi-stock demo
│
├── ARCHITECTURE_GUIDE.md       → Old architecture guide
├── QUICK_START.md              → Old quick start
├── MULTI_STOCK_DEMO_README.md
└── QUICK_REFERENCE.md          ← YOU ARE HERE
```

---

## 🚀 Most Common Commands

### Using the New Backtesting System

```bash
cd backtesting_system

# List all strategies
python run_backtest.py --list

# Single stock backtest
python run_backtest.py --ticker AAPL --strategy moderate

# Compare strategies
python run_backtest.py --ticker NVDA --strategies moderate aggressive rsi_oversold

# Multi-stock comparison
python run_backtest.py --tickers AAPL MSFT NVDA META --strategy aggressive

# Custom parameters
python run_backtest.py --ticker TSLA --strategy moderate \
    --custom fast_period=15 slow_period=35 stop_loss=0.08

# Different time period and capital
python run_backtest.py --ticker AAPL --strategy aggressive --years 5 --capital 250000
```

### Using Legacy Demos

```bash
# Original single-stock demo
python demo_strategy.py

# Multi-stock comparison demo
python demo_multi_stock.py
```

---

## 📊 Available Strategies

**Moving Average Crossover:**
- `moderate` - MA 20/50 SMA (balanced, swing trading)
- `aggressive` - MA 10/30 EMA (active trading)
- `conservative` - MA 50/200 SMA (long-term, Golden Cross)
- `day_trading` - MA 5/15 EMA (very active)
- `high_volatility` - MA 15/45 EMA (crypto, volatile assets)

**Mean Reversion:**
- `rsi_oversold` - RSI strategy (buy low at RSI<30, sell high at RSI>70)
- `bollinger_bounce` - Bollinger Bands (buy at lower band, sell at upper)

**Trend Following:**
- `macd_crossover` - MACD signal line crossovers

---

## ✏️ How to Create/Edit Strategies

### Quick Edit (Change Parameters)

Edit `backtesting_system/strategies_config.py`:

```python
STRATEGY_PRESETS = {
    'moderate': {
        'name': 'MA Crossover 20/50 SMA',
        'parameters': {
            'fast_period': 20,      # ← Change these
            'slow_period': 50,      # ← Change these
            'ma_type': 'sma',       # 'sma' or 'ema'
            'position_size': 0.10,  # 10% per trade
            'stop_loss': 0.05,      # 5% stop loss
            'take_profit': 0.15     # 15% target
        }
    }
}
```

### Add New Strategy Preset

Add to `STRATEGY_PRESETS` dictionary:

```python
'my_strategy': {
    'name': 'My Custom Strategy',
    'parameters': {
        'fast_period': 15,
        'slow_period': 40,
        # ... other params
    }
}
```

### Create Custom Strategy Class

Add to `backtesting_system/strategies_config.py`:

```python
@register_strategy('momentum', 'Momentum strategy', category='trend')
class MomentumStrategy(Strategy):
    def setup(self, data):
        self.lookback = self.parameters.get('lookback', 20)

    def generate_signals(self, data):
        df = data.copy()
        momentum = df['close'].pct_change(self.lookback)

        df['signal'] = 0
        df.loc[momentum > 0.05, 'signal'] = 1   # Buy
        df.loc[momentum < -0.05, 'signal'] = -1  # Sell

        df['position'] = df['signal'].replace(0, method='ffill').fillna(0)
        return df
```

---

## 📈 Performance Metrics Explained

**Total Return** - Overall profit/loss percentage
- Good: >15% per year
- Moderate: 8-15% per year
- Poor: <8% per year

**Sharpe Ratio** - Risk-adjusted return (higher is better)
- Excellent: >2.0
- Good: 1.0-2.0
- Moderate: 0.5-1.0
- Poor: <0.5

**Max Drawdown** - Largest peak-to-trough decline
- Low risk: <10%
- Medium risk: 10-20%
- High risk: >20%

**Win Rate** - Percentage of profitable trades
- Trend strategies: 30-50% (few big wins)
- Mean reversion: 50-70% (many small wins)

---

## 🎯 Common Workflows

### 1. Find Best Strategy for a Stock
```bash
cd backtesting_system
python run_backtest.py --ticker NVDA \
    --strategies moderate aggressive conservative rsi_oversold
```

### 2. Find Best Stock for a Strategy
```bash
python run_backtest.py \
    --tickers AAPL MSFT TSLA NVDA META AMZN \
    --strategy aggressive
```

### 3. Optimize Strategy Parameters
```bash
# Test different fast_period values
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=15
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=20
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=25
```

### 4. Backtest Your Portfolio
```bash
python run_backtest.py \
    --tickers AAPL GOOGL MSFT AMZN \
    --strategy moderate
```

### 5. Test Crypto Strategy
```bash
python run_backtest.py \
    --tickers BTC-USD ETH-USD \
    --strategy high_volatility \
    --years 3
```

---

## 🏗️ Architecture Overview

### New Modular Design

```
┌──────────────────────────────────────┐
│   run_backtest.py (CLI Interface)    │
│   strategies_config.py (Definitions) │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│    BacktestEngine (Universal)        │
│    • Strategy-agnostic               │
│    • Asset-agnostic                  │
│    • Realistic simulation            │
└──────────────────────────────────────┘
                ↓
┌───────────┬──────────────┬───────────┐
│ Strategies│  Data Layer  │  Viz      │
│ • MA      │  • yfinance  │  • Charts │
│ • RSI     │  • Alpaca    │  • Metrics│
│ • MACD    │  • Polygon   │  • Themes │
│ • Custom  │  • Cache     │           │
└───────────┴──────────────┴───────────┘
```

### Key Benefits

✅ **Separation of Concerns**
- Backtesting logic separate from strategies
- Strategies separate from data
- Visualization separate from everything

✅ **Easy to Extend**
- Add new strategies without changing core code
- Support new asset types without modifications
- Swap data providers easily

✅ **Reusable Components**
- BacktestEngine works with ANY strategy
- Strategy base class for consistent interface
- Visualization system handles all chart types

---

## 🎨 Visualization Features

**Interactive Charts:**
- Zoom: Click and drag
- Pan: Hold shift and drag
- Hover: See exact values
- Legend: Click to hide/show series

**Chart Types:**
- Price charts with buy/sell signals
- Equity curves
- Drawdown analysis
- Performance metrics dashboards
- Multi-asset comparisons
- Multi-strategy comparisons

**Themes:**
- Dark (default) - Professional, easy on eyes
- Light - Traditional appearance

**Locations:**
- `backtesting_system/output/charts/` (new system)
- `output/charts/` (legacy demos)

---

## 🛠️ Development Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install/update dependencies
pip install -r requirements.txt

# Run backtests
cd backtesting_system
python run_backtest.py --ticker AAPL --strategy moderate

# List strategies
python run_backtest.py --list

# View strategy code
cat strategies_config.py

# List available strategies programmatically
python strategies_config.py
```

---

## 📚 Documentation Files

**Backtesting System:**
- `backtesting_system/README.md` - System overview
- `backtesting_system/docs/QUICK_START.md` - Get started in 3 minutes
- `backtesting_system/docs/ARCHITECTURE_GUIDE.md` - Detailed architecture

**Legacy Demos:**
- `MULTI_STOCK_DEMO_README.md` - Multi-stock demo docs
- `STRATEGY_DEMO_GUIDE.md` - Strategy demo guide

**Core Documentation:**
- `README.md` - Main project README
- `QUICKSTART.md` - 5-minute project setup
- `CLAUDE.md` - Developer guide for Claude
- `PROJECT_STATUS.md` - Session handoff & status

---

## 🔧 Troubleshooting

**Import errors in backtesting_system:**
```bash
# Make sure you're in the backtesting_system directory
cd backtesting_system
python run_backtest.py --ticker AAPL --strategy moderate
```

**Strategy not found:**
```bash
python run_backtest.py --list
```

**No data for ticker:**
- Use Yahoo Finance format (e.g., `BTC-USD` not `BTCUSD`)
- Check internet connection
- Try different ticker symbol

**Browser doesn't open:**
- Charts are saved to `output/charts/`
- Open `.html` files manually
- Check default browser settings

---

## 💡 Tips & Best Practices

### Strategy Development
1. Start with a preset
2. Modify parameters
3. Backtest on real data
4. Compare with other strategies
5. Validate on different stocks
6. Iterate based on results

### Parameter Tuning
- **Conservative**: Longer MAs (50/200), wider stops (7-10%)
- **Aggressive**: Shorter MAs (10/30), tighter stops (3-5%)
- **Volatile assets**: Wider stops (10-20%), larger targets (20-40%)
- **Stable assets**: Tighter stops (3-5%), smaller targets (8-15%)

### Avoiding Overfitting
- ✅ Test on multiple stocks
- ✅ Test on different time periods
- ✅ Keep strategies simple
- ❌ Don't optimize for one stock only
- ❌ Don't over-tune parameters

---

## 🎯 Phase Status

### ✅ Phase 1: Backend Framework - COMPLETE
- ✅ Strategy system with base classes
- ✅ Technical indicators (SMA, EMA, RSI, MACD, Bollinger)
- ✅ Market data fetching (multi-provider)
- ✅ Backtesting engine (universal, strategy-agnostic)
- ✅ Visualization system (Plotly, dark theme)
- ✅ Performance metrics (20+ metrics)
- ✅ Demo scripts (single & multi-stock)
- ✅ **NEW: Modular backtesting system**
- ✅ **NEW: 8 pre-built strategies**
- ✅ **NEW: Strategy registry**
- ✅ **NEW: Clean CLI interface**

### ⏳ Phase 2: Frontend & API - PLANNED
- Backend REST API endpoints
- React + Vite frontend
- TradingView Lightweight Charts
- Real-time data streaming
- Interactive parameter tuning
- Portfolio management UI

### ⏳ Phase 3: AI Integration - PLANNED
- AI strategy generation
- Parameter optimization
- Pattern recognition
- Market regime detection
- NLP for strategy description

---

## 📞 Quick Help

```bash
# Command help
cd backtesting_system
python run_backtest.py --help

# List strategies
python run_backtest.py --list

# View strategy config
cat strategies_config.py

# Check Python environment
python --version
which python

# Activate venv
source venv/bin/activate
```

---

## 🔗 Useful Links

- **Project Root:** `/Users/wayne/main/labs/stock_picker/`
- **Backend:** `/Users/wayne/main/labs/stock_picker/backend/`
- **Backtesting System:** `/Users/wayne/main/labs/stock_picker/backend/backtesting_system/`
- **Charts Output:** `backtesting_system/output/charts/`

---

## 📝 Session Notes

**Latest Session (2024-11-08):**
- ✅ Created modular backtesting system
- ✅ Separated strategy definition from backtest execution
- ✅ Built universal BacktestEngine
- ✅ Created 8 pre-built strategies
- ✅ Implemented strategy registry
- ✅ Built CLI interface with multiple modes
- ✅ Organized new code into `backtesting_system/` folder
- ✅ Preserved legacy demos in original location
- ✅ Created comprehensive documentation

**Token Usage:** ~102k / 200k (51% used, 49% remaining)

---

**This is your go-to reference for the stock picker project!** 🚀

For detailed guides, see the documentation files listed above.
For quick commands, use the examples in this file.

**Happy backtesting!** 📈
