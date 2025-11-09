# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### 1. See Available Strategies
```bash
python run_backtest.py --list
```

Output shows all pre-configured strategies:
- `moderate` - MA 20/50 SMA (balanced)
- `aggressive` - MA 10/30 EMA (active)
- `conservative` - MA 50/200 SMA (long-term)
- `rsi_oversold` - RSI mean reversion
- `bollinger_bounce` - Bollinger Bands
- `macd_crossover` - MACD signals
- And more...

### 2. Run Your First Backtest
```bash
python run_backtest.py --ticker AAPL --strategy moderate
```

**What happens:**
1. Fetches 2.5 years of AAPL data
2. Runs MA 20/50 SMA strategy
3. Calculates all metrics
4. Generates interactive dashboard
5. **Opens in your browser automatically!**

### 3. View Results

The dashboard shows:
- 📈 Price chart with buy/sell signals
- 💰 Equity curve
- 📊 Performance metrics
- 📉 Drawdown analysis

---

## 📖 Common Commands

### Single Stock Backtests
```bash
# Test different strategies
python run_backtest.py --ticker AAPL --strategy aggressive
python run_backtest.py --ticker TSLA --strategy high_volatility
python run_backtest.py --ticker BTC-USD --strategy conservative

# Different time periods
python run_backtest.py --ticker MSFT --strategy moderate --years 5

# Different starting capital
python run_backtest.py --ticker NVDA --strategy aggressive --capital 250000
```

### Compare Multiple Strategies
```bash
# Which strategy works best for AAPL?
python run_backtest.py --ticker AAPL --strategies moderate aggressive conservative
```

### Compare Multiple Stocks
```bash
# Test FAANG stocks with aggressive strategy
python run_backtest.py --tickers META AAPL AMZN NFLX GOOGL --strategy aggressive

# Test portfolio of tech stocks
python run_backtest.py --tickers AAPL MSFT NVDA --strategy moderate
```

### Custom Parameters
```bash
# Override default parameters
python run_backtest.py --ticker TSLA --strategy moderate \
    --custom fast_period=15 slow_period=35 stop_loss=0.08
```

---

## 🎯 Example Workflows

### Workflow 1: Find Best Strategy for a Stock
```bash
# Compare all trend-following strategies on NVDA
python run_backtest.py --ticker NVDA \
    --strategies moderate aggressive conservative
```

**Analyze results:**
- Which has highest return?
- Which has best Sharpe ratio?
- Which has lowest drawdown?

### Workflow 2: Find Best Stock for a Strategy
```bash
# Test aggressive strategy on multiple tech stocks
python run_backtest.py --tickers AAPL MSFT TSLA NVDA META AMZN \
    --strategy aggressive
```

**Analyze results:**
- Which stock performs best?
- Which has most consistent returns?
- Which has fewest trades?

### Workflow 3: Optimize Parameters
```bash
# Test different MA periods
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=15
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=20
python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=25
```

**Compare:**
- Total return
- Number of trades
- Win rate

---

## ✏️ Creating Your Own Strategy

### Step 1: Edit `strategies_config.py`

Add to `STRATEGY_PRESETS` dictionary:

```python
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
```

### Step 2: Run It
```bash
python run_backtest.py --ticker AAPL --strategy my_strategy
```

### Step 3: Tune Parameters

Edit the numbers in `strategies_config.py` and re-run!

---

## 📊 Understanding Results

### Key Metrics Explained

**Total Return** - Overall profit/loss %
- Good: > 15% per year
- Moderate: 8-15% per year
- Poor: < 8% per year

**Sharpe Ratio** - Risk-adjusted return
- Excellent: > 2.0
- Good: 1.0 - 2.0
- Moderate: 0.5 - 1.0
- Poor: < 0.5

**Max Drawdown** - Largest peak-to-trough decline
- Low risk: < 10%
- Medium risk: 10-20%
- High risk: > 20%

**Win Rate** - % of profitable trades
- Trend strategies: 30-50% (few big wins)
- Mean reversion: 50-70% (many small wins)

---

## 🎨 Customizing Visualizations

All charts are in `output/charts/` directory:

```
output/charts/
├── aapl_ma_crossover_20_50_sma_dashboard.html  ← Open this in browser
├── nvda_strategy_comparison.html
└── multi_stock_dashboard.html
```

**Interactive Features:**
- Zoom: Click and drag
- Pan: Hold shift and drag
- Hover: See exact values
- Legend: Click to hide/show series

---

## 💡 Tips & Tricks

### Tip 1: Save Command History
```bash
# Create a script with your favorite commands
cat > my_backtests.sh <<'EOF'
#!/bin/bash
python run_backtest.py --ticker AAPL --strategy moderate
python run_backtest.py --ticker MSFT --strategy aggressive
python run_backtest.py --tickers NVDA TSLA --strategy moderate
EOF

chmod +x my_backtests.sh
./my_backtests.sh
```

### Tip 2: Quick Strategy Selection
```bash
# Create aliases
alias bt='python run_backtest.py'
alias btlist='python run_backtest.py --list'

# Now you can use:
bt --ticker AAPL --strategy moderate
btlist
```

### Tip 3: Batch Testing
```bash
# Test multiple tickers with a loop
for ticker in AAPL MSFT NVDA; do
    python run_backtest.py --ticker $ticker --strategy moderate
done
```

### Tip 4: Different Asset Classes
```bash
# Stocks
python run_backtest.py --ticker AAPL --strategy moderate

# Crypto
python run_backtest.py --ticker BTC-USD --strategy high_volatility

# ETFs
python run_backtest.py --ticker SPY --strategy conservative

# Commodities (if supported)
python run_backtest.py --ticker GLD --strategy moderate
```

---

## 🔧 Troubleshooting

### Problem: "Strategy 'xyz' not found"
**Solution:**
```bash
python run_backtest.py --list  # Check available strategies
```

### Problem: "No data for ticker XYZ"
**Solution:**
- Check ticker spelling (use Yahoo Finance format)
- Try different ticker (e.g., `BTC-USD` not `BTCUSD`)
- Check internet connection

### Problem: "Not enough data"
**Solution:**
- Reduce years: `--years 1` instead of `--years 5`
- Some stocks don't have long history
- New cryptocurrencies may have limited data

### Problem: "No signals generated"
**Solution:**
- Strategy may be too conservative (50/200 MA needs 200+ days)
- Try more aggressive strategy: `--strategy aggressive`
- Increase time period: `--years 5`

### Problem: "Browser doesn't open"
**Solution:**
- Manually open files in `output/charts/`
- Check browser is set as default
- WSL users: Charts still generate, open from Windows Explorer

---

## 📚 Next Steps

1. **Read** `ARCHITECTURE_GUIDE.md` for deep dive
2. **Explore** `strategies_config.py` to see all options
3. **Experiment** with different parameters
4. **Create** your own custom strategies
5. **Share** your best strategies!

---

## 🎯 Common Use Cases

### Use Case 1: Portfolio Analysis
```bash
# Test your portfolio holdings
python run_backtest.py --tickers AAPL MSFT GOOGL AMZN --strategy moderate
```

### Use Case 2: Strategy Validation
```bash
# Validate strategy on different sectors
python run_backtest.py --ticker XLF --strategy moderate  # Financials
python run_backtest.py --ticker XLK --strategy moderate  # Technology
python run_backtest.py --ticker XLE --strategy moderate  # Energy
```

### Use Case 3: Crypto Trading
```bash
# Test on major cryptocurrencies
python run_backtest.py --tickers BTC-USD ETH-USD --strategy high_volatility
```

### Use Case 4: Risk Assessment
```bash
# Compare risk profiles
python run_backtest.py --ticker TSLA --strategies conservative moderate aggressive
```

---

## ⚡ Performance Tips

**Faster backtests:**
- Use fewer years: `--years 1`
- Test fewer stocks at once
- Close unused applications

**Better results:**
- Test on multiple timeframes
- Test on different market conditions
- Validate on different stocks
- Consider transaction costs

---

## 🎉 You're Ready!

Start with this simple command:

```bash
python run_backtest.py --ticker AAPL --strategy moderate
```

Then experiment and have fun! 🚀

---

**Questions?** Check `ARCHITECTURE_GUIDE.md` for detailed docs.

**Want more examples?** Look at `strategies_config.py`.

**Need help?** Run `python run_backtest.py --help`.
