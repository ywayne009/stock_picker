# Signal-Based Trading Strategies - Implementation Roadmap

**Last Updated:** 2025-11-14
**Strategy Type:** Type 1 - Signal-Based
**Purpose:** Comprehensive catalog of discrete buy/sell signal strategies

---

## Overview

Signal-based strategies generate discrete trading signals (-1, 0, +1) based on technical indicators and price patterns. These are the foundation of systematic trading and suitable for stocks, ETFs, forex, and crypto.

---

## Strategy Categories

### 1. Trend-Following Strategies ✅ (3 implemented, 5 more to add)

**Philosophy:** "The trend is your friend" - Capture sustained directional moves

**Current Implementation:**
- ✅ **MA Crossover 20/50 SMA** - Short/medium term trend
- ✅ **Golden Cross 50/200 SMA** - Long-term bull/bear signals
- ✅ **Fast MA 10/30 EMA** - Quick trend detection

**To Implement:**

#### 1.1 Triple Moving Average Crossover
- **Indicators:** 3 MAs (e.g., 10/20/50)
- **Buy:** Fast > Medium > Slow (all aligned)
- **Sell:** Fast < Medium < Slow
- **Advantage:** Filters out whipsaws better than dual MA
- **Disadvantage:** Later entries, fewer trades

#### 1.2 ADX Trend Strength Filter
- **Indicators:** ADX (Average Directional Index) + DI+/DI-
- **Buy:** ADX > 25 (strong trend) AND DI+ > DI-
- **Sell:** ADX > 25 AND DI- > DI+
- **Advantage:** Only trades when trend is strong
- **Disadvantage:** Misses range-bound profits

#### 1.3 Donchian Channel Breakout (Turtle Trader)
- **Indicators:** 20-day high/low channel
- **Buy:** Price breaks above 20-day high
- **Sell:** Price breaks below 20-day low
- **Advantage:** Classic trend-following, simple, robust
- **Disadvantage:** Lots of false breakouts in choppy markets

#### 1.4 Parabolic SAR (Stop and Reverse)
- **Indicators:** Parabolic SAR dots
- **Buy:** SAR flips below price
- **Sell:** SAR flips above price
- **Advantage:** Always in the market (long or short)
- **Disadvantage:** Whipsaws in sideways markets

#### 1.5 Supertrend Indicator
- **Indicators:** ATR-based trailing stop
- **Buy:** Price > Supertrend line
- **Sell:** Price < Supertrend line
- **Advantage:** Adaptive to volatility, visual clarity
- **Disadvantage:** Lagging in fast reversals

---

### 2. Mean-Reversion Strategies (6 to implement)

**Philosophy:** "What goes up must come down" - Profit from price extremes returning to average

#### 2.1 RSI Overbought/Oversold ⭐ Priority
- **Indicators:** 14-period RSI
- **Buy:** RSI < 30 (oversold)
- **Sell:** RSI > 70 (overbought)
- **Enhancement:** Add trend filter (only buy oversold in uptrend)
- **Advantage:** Simple, well-known, works in ranging markets
- **Disadvantage:** Can stay oversold/overbought in strong trends

#### 2.2 Bollinger Band Mean Reversion ⭐ Priority
- **Indicators:** 20-period BB with 2 std dev
- **Buy:** Price touches lower band
- **Sell:** Price touches upper band
- **Exit:** Price returns to middle band (20 SMA)
- **Advantage:** Adaptive to volatility
- **Disadvantage:** Trend breakouts trigger losing trades

#### 2.3 Stochastic Oscillator
- **Indicators:** %K and %D lines (14, 3, 3)
- **Buy:** %K crosses above %D below 20 (oversold zone)
- **Sell:** %K crosses below %D above 80 (overbought zone)
- **Advantage:** Good for range-bound markets
- **Disadvantage:** Many false signals in trends

#### 2.4 CCI (Commodity Channel Index)
- **Indicators:** 20-period CCI
- **Buy:** CCI < -100 (oversold)
- **Sell:** CCI > +100 (overbought)
- **Advantage:** Works well for commodities and cyclical stocks
- **Disadvantage:** Requires parameter tuning per asset

#### 2.5 Williams %R
- **Indicators:** 14-period Williams %R
- **Buy:** %R < -80 (oversold)
- **Sell:** %R > -20 (overbought)
- **Advantage:** Similar to Stochastic but simpler
- **Disadvantage:** Less popular, similar weaknesses

#### 2.6 Z-Score Mean Reversion
- **Indicators:** Price z-score vs rolling mean
- **Buy:** Z-score < -2 (2 std dev below mean)
- **Sell:** Z-score > +2 (2 std dev above mean)
- **Advantage:** Statistical rigor, customizable lookback
- **Disadvantage:** Assumes normal distribution (often violated)

---

### 3. Momentum Strategies (4 to implement)

**Philosophy:** "Momentum tends to persist" - Ride the wave of strong price movements

#### 3.1 MACD Crossover ⭐ Priority
- **Indicators:** MACD line (12, 26) and Signal line (9)
- **Buy:** MACD crosses above signal line
- **Sell:** MACD crosses below signal line
- **Enhancement:** Add histogram divergence detection
- **Advantage:** Combines trend and momentum, widely used
- **Disadvantage:** Lags in fast markets

#### 3.2 Rate of Change (ROC)
- **Indicators:** 12-period ROC
- **Buy:** ROC crosses above 0
- **Sell:** ROC crosses below 0
- **Advantage:** Simple momentum measure
- **Disadvantage:** Whipsaws around zero line

#### 3.3 Relative Strength (Not RSI)
- **Indicators:** Price vs benchmark (e.g., SPY) ratio
- **Buy:** Stock outperforming benchmark + rising
- **Sell:** Stock underperforming benchmark + falling
- **Advantage:** Market-relative performance
- **Disadvantage:** Needs benchmark data

#### 3.4 Price Action Momentum
- **Indicators:** 20-day highest high, 20-day lowest low
- **Buy:** Price makes new 20-day high
- **Sell:** Price makes new 20-day low
- **Advantage:** Pure price action, no indicators
- **Disadvantage:** Late entries, many false signals

---

### 4. Volatility-Based Strategies (3 to implement)

**Philosophy:** Volatility expansion/contraction predicts moves

#### 4.1 Bollinger Band Squeeze Breakout
- **Indicators:** BB width, Keltner Channels
- **Setup:** BB width < historical average (squeeze)
- **Buy:** Price breaks above upper BB after squeeze
- **Sell:** Price breaks below lower BB after squeeze
- **Advantage:** Catches explosive moves after consolidation
- **Disadvantage:** Many false breakouts

#### 4.2 ATR Breakout
- **Indicators:** ATR (Average True Range)
- **Buy:** Price moves > 2x ATR from yesterday's close (up)
- **Sell:** Price moves > 2x ATR from yesterday's close (down)
- **Advantage:** Adapts to current volatility
- **Disadvantage:** Noise in low volatility periods

#### 4.3 Keltner Channel Breakout
- **Indicators:** 20 EMA ± 2x ATR
- **Buy:** Price closes above upper Keltner
- **Sell:** Price closes below lower Keltner
- **Advantage:** Less sensitive than Bollinger Bands
- **Disadvantage:** Similar to other breakout strategies

---

### 5. Volume-Based Strategies (3 to implement)

**Philosophy:** Volume confirms price movements

#### 5.1 On-Balance Volume (OBV)
- **Indicators:** OBV + 20-day SMA of OBV
- **Buy:** OBV crosses above its SMA (accumulation)
- **Sell:** OBV crosses below its SMA (distribution)
- **Advantage:** Leading indicator, tracks smart money
- **Disadvantage:** Can be noisy

#### 5.2 Volume-Weighted MA Crossover
- **Indicators:** VWMA (Volume-Weighted MA)
- **Buy:** Fast VWMA crosses above slow VWMA
- **Sell:** Fast VWMA crosses below slow VWMA
- **Advantage:** Weighs prices by volume importance
- **Disadvantage:** More complex, similar to regular MA

#### 5.3 Accumulation/Distribution Line
- **Indicators:** A/D line + 20-day MA
- **Buy:** A/D crosses above its MA (buying pressure)
- **Sell:** A/D crosses below its MA (selling pressure)
- **Advantage:** Combines price and volume
- **Disadvantage:** Lag, similar to OBV

---

### 6. Multi-Indicator Combination Strategies (5 to implement)

**Philosophy:** Combine signals to reduce false positives

#### 6.1 Trend + Momentum Combo
- **Conditions:** 50 SMA > 200 SMA (trend) + RSI crosses above 50 (momentum)
- **Buy:** Both conditions met
- **Sell:** 50 SMA < 200 SMA OR RSI < 40
- **Advantage:** Filters out weak trends
- **Disadvantage:** Fewer trading opportunities

#### 6.2 Triple Confirmation
- **Indicators:** MACD, RSI, Volume
- **Buy:** MACD > 0 + RSI > 50 + Volume > avg
- **Sell:** Any 2 of 3 flip bearish
- **Advantage:** High-conviction signals
- **Disadvantage:** Very few trades

#### 6.3 Trend + Mean Reversion Hybrid
- **Indicators:** 200 SMA (trend), BB (mean reversion)
- **Buy:** Price > 200 SMA AND price touches lower BB (buy dip in uptrend)
- **Sell:** Price < 200 SMA OR price > upper BB
- **Advantage:** Best of both worlds
- **Disadvantage:** Complex logic

#### 6.4 Ichimoku Cloud
- **Indicators:** Tenkan, Kijun, Senkou A/B, Chikou
- **Buy:** Price > cloud + Tenkan > Kijun + Chikou > price
- **Sell:** Price < cloud + Tenkan < Kijun + Chikou < price
- **Advantage:** Comprehensive system, visual
- **Disadvantage:** Complex, needs tuning

#### 6.5 Elder's Triple Screen
- **Screens:** Weekly trend + Daily oscillator + Intraday entry
- **Buy:** Weekly MACD up + Daily RSI oversold + Entry trigger
- **Sell:** Weekly MACD down OR Daily RSI overbought
- **Advantage:** Multi-timeframe confirmation
- **Disadvantage:** Requires multi-timeframe data

---

### 7. Pattern Recognition Strategies (Advanced - Later)

**Philosophy:** Chart patterns predict future moves

#### 7.1 Support/Resistance Breakout
- Detect S/R levels from historical pivots
- Buy on breakout above resistance
- Sell on breakdown below support

#### 7.2 Candlestick Patterns
- Bullish: Hammer, Engulfing, Morning Star
- Bearish: Shooting Star, Evening Star, Dark Cloud
- Combine with trend filter

#### 7.3 Head & Shoulders Detection
- Classic reversal pattern
- Neckline break triggers trade
- Requires pattern recognition algorithm

---

## Implementation Priority (Recommended Order)

### **Phase 1: Core Signal Strategies** (Next session)
1. ⭐ **RSI Overbought/Oversold** - Most popular mean-reversion
2. ⭐ **MACD Crossover** - Most popular momentum
3. ⭐ **Bollinger Band Mean Reversion** - Popular volatility strategy

**Rationale:** These 3 + existing MAs give us trend + mean-reversion + momentum coverage

### **Phase 2: Advanced Single-Indicator**
4. ADX Trend Strength
5. Stochastic Oscillator
6. Donchian Channel Breakout

### **Phase 3: Volume-Based**
7. On-Balance Volume
8. Accumulation/Distribution

### **Phase 4: Multi-Indicator Combos**
9. Trend + Momentum Combo
10. Triple Confirmation
11. Ichimoku Cloud

### **Phase 5: Advanced Patterns** (Long-term)
12. Support/Resistance Breakout
13. Candlestick Patterns

---

## Strategy Parameters to Expose

For each strategy, make these configurable:

### Common Parameters:
- **position_size**: % of capital per trade (default: 0.1 = 10%)
- **stop_loss**: % stop loss (default: 0.05 = 5%)
- **take_profit**: % take profit (default: 0.15 = 15%)
- **max_holding_period**: Days to force exit (default: None)
- **trend_filter**: Apply trend filter? (default: False)

### Strategy-Specific:
- **MA strategies**: periods (fast, slow), type (SMA/EMA)
- **RSI**: period (default: 14), oversold (default: 30), overbought (default: 70)
- **MACD**: fast (12), slow (26), signal (9)
- **Bollinger**: period (20), std dev (2)

---

## Backtesting Considerations

### What to Test:
1. **Transaction costs:** Commission + slippage
2. **Position sizing:** Fixed % vs volatility-adjusted
3. **Risk management:** Stop loss + take profit
4. **Market regimes:** Trending vs ranging performance
5. **Robustness:** Parameter sensitivity

### Red Flags:
❌ Over-optimization (curve fitting)
❌ Look-ahead bias (using future data)
❌ Data snooping (testing too many variations)
❌ Survivorship bias (only backtesting winners)
❌ Ignoring transaction costs

---

## Strategy Evaluation Metrics

For each strategy, track:

### Return Metrics:
- Total Return %
- CAGR
- Max Drawdown
- Sharpe Ratio
- Sortino Ratio

### Trade Metrics:
- Win Rate
- Profit Factor
- Average Win/Loss
- Expectancy

### Efficiency Metrics:
- % Time in Market
- Trades per Year
- Average Holding Period

### Robustness:
- Parameter sensitivity
- Performance across different market regimes
- Correlation with other strategies

---

## Next Steps

1. ✅ Taxonomy reviewed and approved
2. ⏳ Implement **RSI, MACD, Bollinger Band** strategies (Phase 1)
3. ⏳ Create strategy comparison dashboard
4. ⏳ Run walk-forward analysis on all strategies
5. ⏳ Document best practices for external developers

---

**End of Document**
