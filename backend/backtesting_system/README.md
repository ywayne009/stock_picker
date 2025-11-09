# Backtesting System

**Version:** 1.0.0
**Status:** Production Ready ✅

A modular, strategy-agnostic backtesting framework for stocks, cryptocurrency, and other financial assets.

---

## 🎯 Quick Start

```bash
cd backtesting_system

# List all available strategies
python run_backtest.py --list

# Run a simple backtest
python run_backtest.py --ticker AAPL --strategy moderate

# Compare strategies
python run_backtest.py --ticker NVDA --strategies moderate aggressive rsi_oversold

# Test multiple stocks
python run_backtest.py --tickers AAPL MSFT NVDA --strategy aggressive
```

**Results auto-open in your browser!** 🎉

---

## 📁 Folder Structure

```
backtesting_system/
├── run_backtest.py         ⭐ Main CLI entry point
├── strategies_config.py    ⭐ Strategy definitions (EDIT THIS!)
├── __init__.py
│
├── docs/
│   ├── QUICK_START.md      → Quick reference guide
│   └── ARCHITECTURE_GUIDE.md → Detailed architecture docs
│
└── output/
    └── charts/             → Generated visualizations (auto-created)
```

---

## 🚀 Features

### ✅ Multiple Backtest Modes

1. **Single Stock, Single Strategy**
   - Test one strategy on one stock
   - Perfect for parameter tuning

2. **Multi-Stock, Single Strategy**
   - Test one strategy across multiple stocks
   - Find which stocks work best

3. **Single Stock, Multi-Strategy**
   - Compare different strategies on same stock
   - Find which strategy performs best

4. **Custom Parameters**
   - Override any parameter on the fly
   - No code changes needed

### ✅ Pre-Built Strategies

**Moving Average Crossover:**
- `moderate` - MA 20/50 SMA
- `aggressive` - MA 10/30 EMA
- `conservative` - MA 50/200 SMA
- `day_trading` - MA 5/15 EMA
- `high_volatility` - MA 15/45 EMA (for crypto)

**Mean Reversion:**
- `rsi_oversold` - RSI buy low, sell high
- `bollinger_bounce` - Bollinger Bands bounce

**Trend Following:**
- `macd_crossover` - MACD signal crosses

### ✅ Professional Visualizations

- Interactive price charts with buy/sell signals
- Equity curves with drawdown analysis
- Comprehensive performance metrics
- Multi-asset/strategy comparison dashboards
- Dark theme (default) + light theme option

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 3 minutes
- **[Architecture Guide](docs/ARCHITECTURE_GUIDE.md)** - Deep dive into system design

---

## 🛠️ Customizing Strategies

### Method 1: Edit Existing Preset (Easiest)

Open `strategies_config.py` and modify parameters:

```python
STRATEGY_PRESETS = {
    'moderate': {
        'name': 'MA Crossover 20/50 SMA',
        'parameters': {
            'fast_period': 20,      # ← Change this
            'slow_period': 50,      # ← Change this
            'ma_type': 'sma',
            'position_size': 0.10,
            'stop_loss': 0.05,
            'take_profit': 0.15
        }
    }
}
```

### Method 2: Create New Preset

Add to `STRATEGY_PRESETS` in `strategies_config.py`:

```python
STRATEGY_PRESETS = {
    # ... existing presets ...

    'my_strategy': {
        'name': 'My Custom Strategy',
        'parameters': {
            'fast_period': 15,
            'slow_period': 40,
            'ma_type': 'ema',
            'position_size': 0.12,
            'stop_loss': 0.06,
            'take_profit': 0.18
        }
    }
}
```

Then run:
```bash
python run_backtest.py --ticker AAPL --strategy my_strategy
```

### Method 3: Create Custom Strategy Class

Add custom logic in `strategies_config.py`:

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

## 📊 Performance Metrics

The system automatically calculates 20+ metrics:

**Returns:**
- Total Return %
- CAGR (Compound Annual Growth Rate)
- Expectancy (avg profit per trade)

**Risk:**
- Sharpe Ratio (risk-adjusted return)
- Sortino Ratio (downside risk)
- Maximum Drawdown %
- Volatility

**Trading:**
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

## 🎓 Example Workflows

### Find Best Strategy for a Stock

```bash
python run_backtest.py --ticker NVDA \
    --strategies moderate aggressive conservative rsi_oversold
```

Compare results to see which strategy works best.

### Find Best Stock for a Strategy

```bash
python run_backtest.py \
    --tickers AAPL MSFT TSLA NVDA META AMZN \
    --strategy aggressive
```

See which stocks perform best with your strategy.

### Optimize Parameters

```bash
# Test different MA periods
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=15
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=20
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=25
```

Compare to find optimal parameters.

---

## 🔧 Command Line Reference

```bash
# Basic usage
python run_backtest.py --ticker TICKER --strategy STRATEGY

# Options
--ticker AAPL              # Single stock ticker
--tickers AAPL MSFT NVDA   # Multiple stocks
--strategy moderate        # Strategy preset name
--strategies mod agg cons  # Multiple strategies to compare
--years 2.5                # Years of historical data (default: 2.5)
--capital 100000           # Initial capital (default: $100k)
--list                     # List all available strategies
--custom key=value         # Override parameters

# Examples
python run_backtest.py --list
python run_backtest.py --ticker AAPL --strategy moderate
python run_backtest.py --tickers AAPL MSFT --strategy aggressive --years 5
python run_backtest.py --ticker TSLA --strategy moderate --custom stop_loss=0.08
```

---

## 🌟 Best Practices

### Strategy Development

1. Start with a preset
2. Modify parameters in `strategies_config.py`
3. Backtest on historical data
4. Compare with other strategies
5. Validate on different stocks/timeframes
6. Iterate based on results

### Avoiding Overfitting

✅ DO:
- Test on multiple stocks
- Test on different time periods
- Use walk-forward analysis
- Keep strategies simple

❌ DON'T:
- Optimize for one stock only
- Over-tune parameters
- Ignore transaction costs
- Use unrealistic assumptions

### Realistic Backtesting

- Include commissions (0.1% default)
- Account for slippage (0.05% default)
- Consider position limits
- Factor in execution delays
- Test different market conditions

---

## 🎨 Output Files

All visualizations are saved to `output/charts/`:

```
output/charts/
├── aapl_ma_crossover_20_50_sma_dashboard.html  # Single stock dashboard
├── nvda_strategy_comparison.html               # Strategy comparison
└── multi_stock_dashboard.html                  # Multi-stock comparison
```

Open any `.html` file in your browser to view interactive charts.

---

## 🔗 Integration with Main Project

This backtesting system is part of the larger stock picker project:

```
backend/
├── backtesting_system/     ← YOU ARE HERE
│   ├── run_backtest.py
│   └── strategies_config.py
│
├── app/services/
│   ├── backtesting/        → Backtest engine
│   ├── strategy/           → Strategy classes
│   ├── data/               → Market data
│   └── visualization/      → Charts & metrics
│
├── demo_strategy.py        → Legacy single-stock demo
└── demo_multi_stock.py     → Legacy multi-stock demo
```

The backtesting system uses the core `app/` modules but provides a cleaner, more user-friendly interface.

---

## 🐛 Troubleshooting

**Q: Module not found error**
```bash
# Make sure you're in the backtesting_system directory
cd backtesting_system
python run_backtest.py --ticker AAPL --strategy moderate
```

**Q: Strategy not found**
```bash
# List all available strategies
python run_backtest.py --list
```

**Q: No data for ticker**
- Check ticker symbol (use Yahoo Finance format)
- Try different ticker (e.g., `BTC-USD` not `BTCUSD`)
- Check internet connection

**Q: Charts don't open**
- Charts are still saved to `output/charts/`
- Open `.html` files manually in browser
- Check default browser settings

---

## 📝 Version History

**v1.0.0** (2024-11-08)
- Initial release
- Modular architecture with clean separation of concerns
- 8 pre-built strategy presets
- Multi-mode backtesting support
- Interactive dark-themed visualizations
- Comprehensive documentation

---

## 🤝 Contributing

To add new strategies:
1. Edit `strategies_config.py`
2. Add to `STRATEGY_PRESETS` or create new strategy class
3. Test with `run_backtest.py`
4. Share your best strategies!

---

## 📄 License

Part of the stock_picker project.

---

## 📞 Support

- **Quick Questions**: See `docs/QUICK_START.md`
- **Detailed Docs**: See `docs/ARCHITECTURE_GUIDE.md`
- **Command Help**: `python run_backtest.py --help`

---

**Happy Backtesting! 🚀📈**
