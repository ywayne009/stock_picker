# Professional Trading Strategy Taxonomy & Development Framework

**Last Updated:** 2025-11-14
**Status:** Architecture Design Phase
**Purpose:** Guide professional strategy development with proper abstraction layers

---

## Executive Summary

This document provides a comprehensive taxonomy of trading strategies, their technical requirements, and the code paradigms needed to support them. The goal is to create a plug-and-play framework where external developers can build strategies compatible with our backtesting infrastructure.

---

## 1. Strategy Classification

### 1.1 Type 1: Signal-Based Strategies (CURRENT IMPLEMENTATION)

**Description:** Generate discrete buy/sell signals based on technical indicators
**Complexity:** ⭐ Simple
**Current Status:** ✅ **IMPLEMENTED**

**Input Requirements:**
- OHLCV price data (Open, High, Low, Close, Volume)
- Optional: Additional technical indicators

**Output:**
- Signal: -1 (sell), 0 (hold), +1 (buy)
- Position size (optional)
- Stop loss / Take profit levels (optional)

**Examples:**
- Moving Average Crossover
- RSI Overbought/Oversold
- MACD Crossover
- Bollinger Band Breakouts
- Golden Cross / Death Cross

**Backtesting Requirements:**
- Simple order execution (market orders)
- Position tracking (long/short/flat)
- Commission modeling
- Slippage modeling

**Code Paradigm:**
```python
class SignalStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Returns -1, 0, or +1 for each timestamp"""
        pass

    def calculate_position_size(self, signal, portfolio_value, price):
        """Returns position size as % of portfolio"""
        pass
```

---

### 1.2 Type 2: Portfolio Weight Strategies

**Description:** Allocate capital across multiple assets with dynamic weights
**Complexity:** ⭐⭐ Moderate
**Current Status:** ❌ **NOT IMPLEMENTED**

**Input Requirements:**
- Multi-asset OHLCV data
- Returns matrix
- Covariance matrix
- Optional: Fundamental data (earnings, P/E, etc.)

**Output:**
- Portfolio weights for each asset (sum = 1.0)
- Rebalancing frequency
- Constraints (max position, sector limits, etc.)

**Examples:**
- **Modern Portfolio Theory (MPT)** - Markowitz mean-variance optimization
- **Risk Parity** - Equal risk contribution from each asset
- **Black-Litterman** - Bayesian approach combining market equilibrium + views
- **Minimum Variance** - Minimize portfolio volatility
- **Maximum Sharpe** - Maximize risk-adjusted returns
- **Equal Weight** - Naive diversification (1/N allocation)
- **Kelly Criterion** - Optimal bet sizing for maximum growth

**Backtesting Requirements:**
- Multi-asset portfolio tracking
- Rebalancing logic with transaction costs
- Constraint enforcement
- Cash management (fractional shares vs whole shares)
- Corporate actions (splits, dividends, mergers)

**Code Paradigm:**
```python
class PortfolioStrategy(BaseStrategy):
    def calculate_weights(
        self,
        returns: pd.DataFrame,
        covariance: pd.DataFrame,
        current_weights: dict,
        constraints: dict
    ) -> dict:
        """Returns target weights for each asset"""
        pass

    def should_rebalance(self, current_date, last_rebalance) -> bool:
        """Determines if rebalancing is needed"""
        pass
```

---

### 1.3 Type 3: Options Strategies

**Description:** Trade options for income, hedging, or speculation
**Complexity:** ⭐⭐⭐⭐ Complex
**Current Status:** ❌ **NOT IMPLEMENTED**

**Input Requirements:**
- Underlying OHLCV data
- Options chain data (strikes, expirations, Greeks)
- Implied volatility surface
- Interest rates
- Dividend schedule

**Output:**
- Multi-leg positions (combinations of calls, puts, stock)
- Entry/exit conditions for each leg
- Adjustment rules (roll, close, hedge)
- Greeks targets (delta-neutral, vega-positive, etc.)

**Examples:**

**Income Strategies:**
- Covered Call
- Cash-Secured Put
- Iron Condor
- Credit Spreads (Bull Put, Bear Call)

**Hedging Strategies:**
- Protective Put (married put)
- Collar (protective put + covered call)
- Delta Hedging (dynamic hedge ratio)
- Gamma Scalping

**Speculation Strategies:**
- Long Call/Put
- Debit Spreads (Bull Call, Bear Put)
- Straddle/Strangle (volatility plays)
- Butterfly, Condor (range-bound)
- Calendar Spreads (time decay)

**Backtesting Requirements:**
- Options pricing model (Black-Scholes, Binomial, Monte Carlo)
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Expiration handling (roll, exercise, expire worthless)
- Assignment risk modeling
- Early exercise (American options)
- Multi-leg order execution
- Margin requirements
- Pin risk at expiration

**Code Paradigm:**
```python
class OptionsStrategy(BaseStrategy):
    def construct_position(
        self,
        underlying_price: float,
        options_chain: pd.DataFrame,
        target_date: datetime
    ) -> list[OptionsLeg]:
        """Returns list of option legs to trade"""
        pass

    def calculate_greeks(self, position) -> dict:
        """Returns portfolio Greeks"""
        pass

    def should_adjust(self, position, market_data, greeks) -> bool:
        """Determines if position needs adjustment"""
        pass

    def adjustment_logic(self, position) -> list[OptionsLeg]:
        """Returns legs to add/remove for adjustment"""
        pass
```

---

### 1.4 Type 4: Statistical Arbitrage / Pairs Trading

**Description:** Exploit mean-reversion in relative price relationships
**Complexity:** ⭐⭐⭐ Moderate-Advanced
**Current Status:** ❌ **NOT IMPLEMENTED**

**Input Requirements:**
- Multi-asset price data (correlated pairs/baskets)
- Cointegration tests (ADF, Johansen)
- Spread calculation (price ratio, z-score, hedge ratio)
- Rolling correlation windows

**Output:**
- Spread signal (overbought/oversold)
- Hedge ratio (number of shares for each leg)
- Entry/exit thresholds (z-score levels)

**Examples:**
- **Pairs Trading** - Long undervalued, short overvalued in correlated pair
- **Triangular Arbitrage** - Exploit currency cross-rate discrepancies
- **Index Arbitrage** - ETF vs constituent stocks
- **Convertible Arbitrage** - Convertible bond vs underlying stock

**Backtesting Requirements:**
- Multi-leg position tracking
- Spread calculation and monitoring
- Cointegration testing (in-sample vs out-of-sample)
- Short selling costs (borrow fees, hard-to-borrow)
- Execution timing (simultaneous entry for both legs)
- Spread tracking through corporate actions

**Code Paradigm:**
```python
class PairsStrategy(BaseStrategy):
    def calculate_spread(
        self,
        asset1_prices: pd.Series,
        asset2_prices: pd.Series
    ) -> pd.Series:
        """Returns spread time series"""
        pass

    def calculate_hedge_ratio(self, lookback_window) -> float:
        """Returns optimal hedge ratio"""
        pass

    def generate_signals(self, spread_zscore) -> tuple:
        """Returns (signal_asset1, signal_asset2)"""
        pass
```

---

### 1.5 Type 5: Market Making / High-Frequency

**Description:** Provide liquidity and profit from bid-ask spread
**Complexity:** ⭐⭐⭐⭐⭐ Very Complex
**Current Status:** ❌ **NOT IMPLEMENTED** (Out of scope initially)

**Input Requirements:**
- Level 2 order book data (market depth)
- Tick-by-tick trade data
- Latency measurements
- Inventory positions
- Queue position estimation

**Output:**
- Bid/ask quote placement
- Order size at each level
- Cancellation logic
- Inventory risk management

**Examples:**
- Pure market making
- Arbitrage (cross-exchange, cross-asset)
- Statistical arbitrage (sub-second mean reversion)

**Note:** This type requires microsecond-level simulation and is typically not suitable for daily/minute-bar backtesting. **DEFERRED** for now.

---

### 1.6 Type 6: Fundamental / Value Strategies

**Description:** Trade based on company fundamentals and valuation metrics
**Complexity:** ⭐⭐⭐ Moderate-Advanced
**Current Status:** ❌ **NOT IMPLEMENTED**

**Input Requirements:**
- Financial statements (income, balance sheet, cash flow)
- Valuation ratios (P/E, P/B, EV/EBITDA, etc.)
- Growth metrics (revenue growth, earnings growth)
- Quality metrics (ROE, ROA, profit margin)
- Analyst estimates & revisions
- Earnings announcements & guidance

**Output:**
- Stock rankings/scores
- Portfolio weights based on valuations
- Holding period (typically longer: weeks to years)
- Rebalancing frequency (quarterly, annually)

**Examples:**
- **Value Investing** - Buy undervalued (low P/E, P/B)
- **Growth Investing** - Buy high-growth companies
- **Quality Investing** - Buy high-quality businesses (Buffett style)
- **Dividend Investing** - High dividend yield + growth
- **Magic Formula** (Greenblatt) - Combine value + quality
- **Piotroski F-Score** - Financial strength scoring

**Backtesting Requirements:**
- Fundamental data integration
- Look-ahead bias prevention (use point-in-time data!)
- Survivorship bias handling (delisted stocks)
- Sector/industry classification
- Rebalancing with transaction costs
- Dividends and splits handling

**Code Paradigm:**
```python
class FundamentalStrategy(BaseStrategy):
    def score_stocks(
        self,
        fundamentals: pd.DataFrame,
        current_date: datetime
    ) -> pd.Series:
        """Returns score for each stock"""
        pass

    def select_portfolio(
        self,
        scores: pd.Series,
        num_stocks: int
    ) -> list:
        """Returns list of stocks to hold"""
        pass
```

---

### 1.7 Type 7: Machine Learning / AI-Driven

**Description:** Use ML models to predict returns, classify regimes, or generate signals
**Complexity:** ⭐⭐⭐⭐ Complex
**Current Status:** ❌ **NOT IMPLEMENTED** (Planned for Phase 3)

**Input Requirements:**
- Feature engineering (technical, fundamental, sentiment, alternative data)
- Labels (future returns, regime classification, up/down)
- Training/validation/test splits (walk-forward)
- Model hyperparameters

**Output:**
- Predicted returns or probabilities
- Confidence scores
- Feature importance

**Examples:**
- **Supervised Learning:**
  - Regression (predict returns)
  - Classification (up/down/neutral)
  - Gradient Boosting (XGBoost, LightGBM)
  - Neural Networks (LSTM, Transformer for time series)

- **Unsupervised Learning:**
  - Clustering (regime detection)
  - PCA (dimensionality reduction)
  - Autoencoders (anomaly detection)

- **Reinforcement Learning:**
  - Q-Learning
  - Deep Q-Networks (DQN)
  - Policy Gradient methods

**Backtesting Requirements:**
- Walk-forward analysis (retrain periodically)
- Out-of-sample testing
- Overfitting detection
- Model decay monitoring
- Computational resource management

**Code Paradigm:**
```python
class MLStrategy(BaseStrategy):
    def train_model(
        self,
        features: pd.DataFrame,
        labels: pd.Series,
        train_end_date: datetime
    ):
        """Train model on data up to train_end_date"""
        pass

    def predict(
        self,
        features: pd.DataFrame
    ) -> pd.Series:
        """Generate predictions"""
        pass

    def generate_signals(self, predictions) -> pd.Series:
        """Convert predictions to trading signals"""
        pass
```

---

## 2. Development Roadmap (Ordered by Complexity)

### Phase 1: Signal-Based Strategies ✅ COMPLETE
- [x] Moving Average Crossover
- [x] Golden Cross
- [ ] RSI Strategy
- [ ] MACD Strategy
- [ ] Bollinger Band Strategy
- [ ] Momentum Strategy

### Phase 2: Portfolio Weight Strategies (NEXT)
- [ ] Equal Weight
- [ ] Minimum Variance
- [ ] Maximum Sharpe
- [ ] Risk Parity
- [ ] Black-Litterman

### Phase 3: Statistical Arbitrage
- [ ] Pairs Trading (cointegration-based)
- [ ] Mean Reversion Baskets
- [ ] Index Arbitrage

### Phase 4: Fundamental Strategies
- [ ] Value (low P/E, P/B)
- [ ] Quality (Piotroski F-Score)
- [ ] Magic Formula
- [ ] Dividend Growth

### Phase 5: Options Strategies
- [ ] Covered Call
- [ ] Cash-Secured Put
- [ ] Iron Condor
- [ ] Delta Hedging

### Phase 6: AI/ML Strategies
- [ ] LSTM Price Prediction
- [ ] Regime Classification
- [ ] Reinforcement Learning

---

## 3. Backtest Engine Requirements by Strategy Type

| Strategy Type | Engine Features Needed | Data Requirements | Execution Complexity |
|---------------|------------------------|-------------------|---------------------|
| **Signal-Based** | Single asset, market orders, commissions | OHLCV | Low ⭐ |
| **Portfolio Weight** | Multi-asset, rebalancing, constraints | Multi-asset OHLCV, correlations | Medium ⭐⭐ |
| **Options** | Multi-leg, Greeks, expiration, assignment | Options chain, IV surface | Very High ⭐⭐⭐⭐⭐ |
| **Pairs Trading** | Multi-leg, spread tracking, short selling | Multi-asset OHLCV, cointegration | Medium ⭐⭐⭐ |
| **Fundamental** | Point-in-time data, survivorship bias handling | Financial statements, ratios | Medium ⭐⭐⭐ |
| **ML/AI** | Walk-forward, model retraining | Feature data, labels | High ⭐⭐⭐⭐ |

---

## 4. Architecture Design Principles

### 4.1 Separation of Concerns

```
┌─────────────────────────────────────────────────────┐
│              Strategy Layer (User Code)             │
│  - Implements strategy logic                        │
│  - Returns signals/weights/positions                │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│            Backtesting Engine Layer                 │
│  - Executes orders                                  │
│  - Tracks portfolio state                           │
│  - Calculates P&L and metrics                       │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Data Layer                             │
│  - Fetches market data                              │
│  - Handles data validation                          │
│  - Provides indicators                              │
└─────────────────────────────────────────────────────┘
```

### 4.2 Base Strategy Interface (Polymorphism)

```python
class BaseStrategy(ABC):
    """Abstract base class for all strategies"""

    @property
    @abstractmethod
    def strategy_type(self) -> StrategyType:
        """Returns the type of strategy (signal, portfolio, options, etc.)"""
        pass

    @abstractmethod
    def setup(self, data: pd.DataFrame):
        """Initialize strategy with data (calculate indicators, etc.)"""
        pass

    # Each strategy type implements its own methods:
    # - SignalStrategy: generate_signals()
    # - PortfolioStrategy: calculate_weights()
    # - OptionsStrategy: construct_position()
```

### 4.3 Engine Registry Pattern

```python
class BacktestEngineFactory:
    _engines = {
        StrategyType.SIGNAL: SignalBacktestEngine,
        StrategyType.PORTFOLIO: PortfolioBacktestEngine,
        StrategyType.OPTIONS: OptionsBacktestEngine,
        # ...
    }

    @classmethod
    def get_engine(cls, strategy: BaseStrategy):
        """Returns appropriate engine for strategy type"""
        engine_class = cls._engines[strategy.strategy_type]
        return engine_class()
```

---

## 5. Data Requirements Matrix

| Data Type | Signal | Portfolio | Options | Pairs | Fundamental | ML |
|-----------|--------|-----------|---------|-------|-------------|-----|
| OHLCV | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Volume | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Options Chain | ❌ | ❌ | ✅ | ❌ | ❌ | Optional |
| Greeks | ❌ | ❌ | ✅ | ❌ | ❌ | Optional |
| Fundamentals | ❌ | Optional | ❌ | ❌ | ✅ | ✅ |
| Sentiment | ❌ | Optional | ❌ | ❌ | Optional | ✅ |
| Alternative Data | ❌ | Optional | ❌ | ❌ | Optional | ✅ |
| Level 2 / Order Book | ❌ | ❌ | ❌ | ❌ | ❌ | Optional |

---

## 6. External Developer Guidelines (To Be Created)

For each strategy type, we will create:

1. **`STRATEGY_TYPE_<X>_GUIDE.md`** - Detailed implementation guide
   - Required methods to implement
   - Input/output specifications
   - Example strategies
   - Common pitfalls
   - Testing checklist

2. **`strategy_template_<type>.py`** - Copy-paste template with:
   - Skeleton code with docstrings
   - Type hints
   - Validation logic
   - Example parameter definitions

3. **Strategy Validator** - Automated checking:
   - Ensures strategy implements required interface
   - Validates input/output types
   - Checks for common errors (look-ahead bias, etc.)

---

## 7. Next Steps

### Immediate (This Session):
1. ✅ Create this taxonomy document
2. ⏳ Design enhanced base strategy architecture
3. ⏳ Implement Signal-Based strategy examples (RSI, MACD, Bollinger)

### Short Term (Next 1-2 Sessions):
4. Portfolio Weight engine development
5. Example portfolio strategies (Equal Weight, Min Variance, Max Sharpe)
6. Create developer guides for Types 1-2

### Medium Term:
7. Pairs trading engine
8. Fundamental data integration
9. Options pricing & Greeks calculation

### Long Term:
10. ML/AI framework integration
11. Advanced options strategies
12. Performance optimization for large-scale backtesting

---

## 8. Success Criteria

A successful implementation means:

✅ **Modularity** - New strategies can be added without modifying engine code
✅ **Type Safety** - Clear contracts prevent runtime errors
✅ **Extensibility** - Easy to add new strategy types
✅ **Testability** - Each component can be tested independently
✅ **Documentation** - External developers can build strategies without our help
✅ **Realism** - Backtests reflect actual trading constraints
✅ **Performance** - Can backtest years of data in seconds

---

## Appendix A: Industry References

- **QuantConnect** - Multi-asset backtesting platform (good API design reference)
- **Backtrader** - Python backtesting library (flexible event-driven architecture)
- **Zipline** - Quantopian's open-source backtesting (Pythonic, pandas-based)
- **VectorBT** - Vectorized backtesting (performance-optimized)

---

**End of Document**
