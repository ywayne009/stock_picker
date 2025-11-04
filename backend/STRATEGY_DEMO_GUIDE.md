# Strategy Demo Guide

This guide explains the enhanced `demo_strategy.py` script with comprehensive comments for understanding and adapting the Moving Average Crossover strategy.

## What's Included in the Demo

The demo script now includes extensive educational comments covering:

### 1. Strategy Mechanics
- **How the strategy works**: Detailed explanation of moving average crossovers
- **Signal generation**: When buy (golden cross) and sell (death cross) signals occur
- **Why it works**: The logic behind trend-following strategies
- **Limitations**: When the strategy struggles (ranging markets, whipsaws)

### 2. Tunable Parameters Guide

#### Moving Average Periods (fast_period, slow_period)
**Purpose**: Controls signal frequency and reliability

| Profile | Example | Pros | Cons | Best For |
|---------|---------|------|------|----------|
| Conservative | 50/200 | Very reliable | Fewer signals, late entries | Long-term, retirement |
| Moderate | 20/50 | Balanced | Moderate lag | Active portfolios |
| Aggressive | 10/30 | Quick signals | More false signals | Day/swing trading |

#### MA Type (sma vs ema)
- **SMA**: Equal weight, smoother, better for long-term
- **EMA**: Recent price weight, faster, better for short-term

#### Position Size (0.0 to 1.0)
| Risk Level | Size | Positions | Use Case |
|------------|------|-----------|----------|
| Conservative | 5-10% | 10-20 | Risk-averse, retirement |
| Moderate | 15-25% | 4-7 | Standard portfolios |
| Aggressive | 30-50% | 2-3 | High conviction |

#### Stop Loss (0.02 to 0.20)
Adjust based on asset volatility:
- **Tight (2-5%)**: Blue chips, large positions
- **Moderate (5-10%)**: Most stocks
- **Wide (10-20%)**: Volatile assets, crypto

#### Take Profit (0.10 to 0.50)
Set at 2-3x your stop loss for favorable risk/reward:
- If stop = 5%, set take profit = 10-15%
- If stop = 10%, set take profit = 20-30%

### 3. Portfolio Adaptation Examples

The demo includes complete configuration examples for:

```python
# RETIREMENT PORTFOLIO (Low Risk, Long-term)
{
    'fast_period': 50,
    'slow_period': 200,
    'ma_type': 'sma',
    'position_size': 0.05,
    'stop_loss': 0.05,
    'take_profit': 0.20
}

# BALANCED PORTFOLIO (Medium Risk, Multi-year)
{
    'fast_period': 20,
    'slow_period': 50,
    'ma_type': 'sma',
    'position_size': 0.10,
    'stop_loss': 0.07,
    'take_profit': 0.15
}

# ACTIVE TRADING PORTFOLIO (Higher Risk, Weeks-Months)
{
    'fast_period': 10,
    'slow_period': 30,
    'ma_type': 'ema',
    'position_size': 0.20,
    'stop_loss': 0.05,
    'take_profit': 0.10
}

# DAY TRADING PORTFOLIO (High Risk, Days)
{
    'fast_period': 5,
    'slow_period': 20,
    'ma_type': 'ema',
    'position_size': 0.30,
    'stop_loss': 0.03,
    'take_profit': 0.05
}

# VOLATILE ASSETS (Crypto, Small Caps)
{
    'fast_period': 10,
    'slow_period': 30,
    'ma_type': 'ema',
    'position_size': 0.10,  # Volatility will reduce this further
    'stop_loss': 0.15,      # Wider for volatility
    'take_profit': 0.30     # Larger moves expected
}
```

### 4. Position Sizing Demonstration

Shows how position sizing works with:
- Portfolio value example
- Share calculation
- Dollar value allocation
- Number of possible positions

**Key insight**: With 10% position sizing, you can hold up to 10 different positions for diversification.

### 5. Risk Management Demonstration

Illustrates:
- Stop loss triggering
- Take profit execution
- Risk/reward ratio calculation
- Different price scenarios

**Example output**:
```
Entry Price: $100.00
Stop Loss: 5.0% ($95.00)
Take Profit: 15.0% ($115.00)
Risk/Reward Ratio: 3.0:1

Current Price   % Change     Action     Reason
$95.00          -5.0%        CLOSE      Hit stop loss - cut losses
$105.00          5.0%        HOLD       Within acceptable range
$115.00         15.0%        CLOSE      Hit take profit - lock in gains
```

### 6. Parameter Tuning Workflow

**7-Step Process:**
1. Define your investment profile
2. Choose appropriate MA periods
3. Select MA type based on speed needs
4. Set position size based on risk tolerance
5. Configure stop loss for asset volatility
6. Set take profit at 2-3x your stop loss
7. Backtest and refine

### 7. Common Tuning Scenarios

The demo provides solutions for:

**Problem**: Too many false signals in ranging market
- **Solution**: Increase MA periods, switch to SMA, add filters

**Problem**: Missing quick reversals
- **Solution**: Decrease MA periods, switch to EMA

**Problem**: Getting stopped out too often
- **Solution**: Widen stop loss based on volatility

**Problem**: Missing profit targets
- **Solution**: Lower targets, use trailing stops

### 8. Advanced Adaptations

Covers:
- Multiple timeframe strategies
- Volatility-based position sizing (built-in)
- Market regime filters
- Portfolio-level risk management

## Running the Demo

```bash
cd backend
source venv/bin/activate
python demo_strategy.py
```

## What You'll See

1. **Sample data generation** with configurable trend and volatility
2. **Three strategy tests**:
   - Moderate (20/50 SMA) - Balanced approach
   - Conservative (50/200 SMA) - Golden Cross
   - Aggressive (10/30 EMA) - Fast crossover
3. **Strategy comparison** showing signal frequency differences
4. **Position sizing examples** with real dollar amounts
5. **Risk management scenarios** showing when stops trigger
6. **Complete parameter tuning guide** for adaptation

## Key Takeaways

### For Different Portfolio Types

**Conservative Investors:**
- Use longer periods (50/200)
- Prefer SMA for stability
- Small position sizes (5-10%)
- Tight stops relative to volatility

**Active Traders:**
- Use shorter periods (10/30 or 20/50)
- Consider EMA for responsiveness
- Larger positions (15-25%)
- Balance stops with trading frequency

**Day Traders:**
- Very short periods (5/20)
- Always use EMA
- Concentrated positions (20-30%)
- Very tight stops (3-5%)

### For Different Assets

**Blue Chip Stocks:**
- Longer periods, tighter stops
- Example: 50/200 SMA, 5% stop

**Growth Stocks:**
- Medium periods, moderate stops
- Example: 20/50 SMA, 7% stop

**Volatile Assets (Crypto, Small Caps):**
- Shorter periods, wider stops
- Example: 10/30 EMA, 15% stop

## Customizing for Your Portfolio

1. **Start with your risk tolerance**: This determines position size and stop loss
2. **Match timeframe to your availability**: Day trader vs. long-term investor
3. **Adjust for market volatility**: Wider stops for volatile assets
4. **Ensure good risk/reward**: Take profit should be 2-3x stop loss
5. **Backtest before live trading**: Use historical data to validate

## Next Steps

1. Modify the demo script with your preferred parameters
2. Test with historical data for your target assets
3. Paper trade to verify performance
4. Monitor and adjust based on results
5. Integrate with backtesting engine (coming soon)

## Important Reminders

- **No look-ahead bias**: Strategy only uses past data
- **Past performance ≠ future results**: Always test thoroughly
- **Transaction costs matter**: More signals = higher costs
- **Risk management is critical**: Never trade without stops
- **Diversification helps**: Don't put all eggs in one basket

---

For implementation details, see:
- `app/services/strategy/base_strategy.py` - Base class
- `app/services/strategy/examples/ma_crossover.py` - Strategy implementation
- `app/services/strategy/indicators.py` - Technical indicators
- `app/services/strategy/README.md` - Strategy framework docs
