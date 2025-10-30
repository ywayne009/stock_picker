# Stock Picking Tool - Development Plan

## Executive Summary

This document outlines the development plan for an AI-powered stock picking tool designed for professional traders. The system will integrate real-time and historical market data, maintain a repository of trading strategies, support backtesting, and leverage AI for strategy generation and optimization.

---

## 1. Project Overview

### 1.1 Objectives
- Fetch and process historical and live stock market data
- Maintain a flexible, extensible strategy framework
- Enable comprehensive backtesting with performance analytics
- Leverage AI for strategy generation, optimization, and discovery
- Generate detailed reports on workflows, performance, and insights

### 1.2 Key Stakeholders
- Primary User: Professional traders
- Development Team: Backend developers, data engineers, AI/ML engineers, frontend developers
- Data Providers: Market data API vendors

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  (Dashboard, Strategy Manager, Backtest UI, Reports)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   API Gateway / Backend                      │
│  (REST/WebSocket APIs, Authentication, Rate Limiting)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │               │
┌───────▼────────┐ ┌──▼─────────┐ ┌──▼──────────────┐
│  Data Layer    │ │  Strategy  │ │  AI/ML Engine   │
│                │ │  Engine    │ │                 │
│ - Market Data  │ │            │ │ - GPT-4 API     │
│ - Time Series  │ │ - Executor │ │ - Strategy Gen  │
│ - Level 2      │ │ - Backtest │ │ - Optimization  │
│ - Storage DB   │ │ - Signals  │ │ - Pattern Recog │
└────────────────┘ └────────────┘ └─────────────────┘
```

### 2.2 Technology Stack Recommendations

**Backend:**
- Language: Python 3.11+ (for data processing, ML integration)
- Framework: FastAPI (async support, WebSocket for live data)
- Database: PostgreSQL (primary data) + TimescaleDB (time-series)
- Cache: Redis (real-time data, session management)
- Message Queue: RabbitMQ or Kafka (for event-driven architecture)

**Data Processing:**
- Pandas, NumPy (data manipulation)
- TA-Lib, pandas-ta (technical indicators)
- Arctic or InfluxDB (high-performance time-series storage)

**AI/ML:**
- OpenAI API (GPT-4 for strategy generation)
- scikit-learn, XGBoost (optimization algorithms)
- TensorFlow/PyTorch (advanced pattern recognition)
- LangChain (AI agent orchestration)

**Frontend:**
- React or Next.js
- TradingView Charting Library
- Material-UI or Tailwind CSS
- Socket.io (real-time updates)

**DevOps:**
- Docker & Kubernetes
- GitHub Actions or GitLab CI/CD
- Prometheus & Grafana (monitoring)

---

## 3. Module Specifications

### 3.1 Data Acquisition Module

#### 3.1.1 Data Sources
**Primary APIs (choose based on budget and requirements):**
- **Tier 1 (Professional):** Bloomberg API, Reuters, Interactive Brokers API
- **Tier 2 (Mid-range):** Polygon.io, Alpaca, Alpha Vantage Premium
- **Tier 3 (Budget):** Yahoo Finance, Alpha Vantage Free, IEX Cloud

#### 3.1.2 Data Types
**Historical Data:**
- OHLCV (Open, High, Low, Close, Volume)
- Adjusted prices (splits, dividends)
- Intraday bars (1min, 5min, 15min, 1hour)
- Daily, weekly, monthly aggregates
- Historical Level 2 data (if available)

**Live Data:**
- Real-time quotes (bid/ask)
- Trade executions (price, volume, timestamp)
- Level 2 order book (market depth)
- Market status and trading halts
- News and sentiment feeds

**Fundamental Data (optional enhancement):**
- Financial statements
- Earnings reports
- Economic indicators

#### 3.1.3 Implementation Strategy

```python
# Pseudo-code structure
class DataProvider:
    """Base class for all data providers"""
    def fetch_historical(self, symbol, start_date, end_date, interval)
    def fetch_live_quote(self, symbol)
    def fetch_level2(self, symbol)
    def subscribe_realtime(self, symbols, callback)

class DataManager:
    """Manages multiple data providers and caching"""
    def __init__(self, providers: List[DataProvider])
    def get_data(self, symbol, timeframe, use_cache=True)
    def stream_data(self, symbols, handler)
    def store_data(self, data, symbol)
```

#### 3.1.4 Key Features
- **Multi-provider support:** Fallback mechanisms if primary source fails
- **Data normalization:** Standardize formats across providers
- **Caching strategy:** Redis for real-time, TimescaleDB for historical
- **Rate limiting:** Respect API quotas, implement exponential backoff
- **Data validation:** Check for gaps, outliers, and anomalies
- **WebSocket support:** For efficient real-time streaming

---

### 3.2 Strategy Management Module

#### 3.2.1 Strategy Framework

```python
# Base strategy structure
class Strategy:
    """Base class for all trading strategies"""
    
    def __init__(self, config: dict):
        self.name = config.get('name')
        self.parameters = config.get('parameters', {})
        self.indicators = []
        
    def setup(self, data):
        """Initialize indicators and prepare data"""
        pass
        
    def generate_signals(self, data) -> pd.DataFrame:
        """Generate buy/sell/hold signals"""
        pass
        
    def calculate_position_size(self, signal, portfolio):
        """Determine position sizing"""
        pass
        
    def risk_management(self, position, current_price):
        """Apply stop-loss, take-profit rules"""
        pass
```

#### 3.2.2 Strategy Categories

**Technical Strategies:**
- Moving Average Crossover (SMA, EMA)
- RSI Overbought/Oversold
- MACD Divergence
- Bollinger Bands Mean Reversion
- Breakout Strategies (Support/Resistance)
- Volume-based Strategies

**Quantitative Strategies:**
- Statistical Arbitrage
- Mean Reversion
- Momentum Strategies
- Factor-based Models

**Machine Learning Strategies:**
- Price Prediction Models
- Pattern Recognition
- Sentiment Analysis
- Ensemble Methods

**AI-Generated Strategies:**
- Natural language to strategy conversion
- Evolutionary strategy optimization
- Adaptive strategies

#### 3.2.3 Strategy Repository

**Database Schema:**
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    description TEXT,
    category VARCHAR(100),
    code TEXT,  -- Serialized strategy code
    parameters JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    creator VARCHAR(100),  -- 'user' or 'ai'
    performance_metrics JSONB,
    version INTEGER
);

CREATE TABLE strategy_versions (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    version INTEGER,
    code TEXT,
    parameters JSONB,
    change_notes TEXT,
    created_at TIMESTAMP
);
```

#### 3.2.4 Strategy Operations
- **CRUD operations:** Create, Read, Update, Delete strategies
- **Version control:** Track strategy modifications
- **Tagging system:** Categorize and search strategies
- **Dependency management:** Handle indicator libraries
- **Import/Export:** Share strategies (JSON/Python format)

---

### 3.3 Backtesting Engine

#### 3.3.1 Core Components

```python
class BacktestEngine:
    """Comprehensive backtesting framework"""
    
    def __init__(self, initial_capital, commission_model, slippage_model):
        self.portfolio = Portfolio(initial_capital)
        self.commission_model = commission_model
        self.slippage_model = slippage_model
        self.trades = []
        
    def run(self, strategy, data, start_date, end_date):
        """Execute backtest"""
        pass
        
    def calculate_metrics(self):
        """Compute performance statistics"""
        return {
            'total_return': ...,
            'sharpe_ratio': ...,
            'max_drawdown': ...,
            'win_rate': ...,
            'profit_factor': ...,
        }
```

#### 3.3.2 Performance Metrics

**Return Metrics:**
- Total Return (%)
- Annualized Return
- Compound Annual Growth Rate (CAGR)
- Daily/Monthly Returns Distribution

**Risk Metrics:**
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Beta (vs. benchmark)

**Trade Metrics:**
- Total Trades
- Win Rate
- Profit Factor
- Average Win/Loss
- Largest Win/Loss
- Average Holding Period

**Advanced Metrics:**
- Calmar Ratio
- Information Ratio
- Omega Ratio
- Tail Ratio

#### 3.3.3 Realistic Simulation Features
- **Commission modeling:** Fixed, percentage, or tiered
- **Slippage simulation:** Based on volume and volatility
- **Market impact:** Model large order effects
- **Liquidity constraints:** Ensure realistic order filling
- **Look-ahead bias prevention:** Strict data partitioning
- **Survivorship bias handling:** Include delisted stocks

#### 3.3.4 Walk-Forward Analysis
```python
class WalkForwardOptimizer:
    """Implement walk-forward optimization"""
    
    def __init__(self, in_sample_period, out_sample_period):
        self.in_sample = in_sample_period
        self.out_sample = out_sample_period
        
    def optimize(self, strategy, data, param_grid):
        """
        1. Split data into IS/OOS windows
        2. Optimize on IS data
        3. Test on OOS data
        4. Roll forward and repeat
        """
        pass
```

---

### 3.4 AI Strategy Generation & Optimization Module

#### 3.4.1 AI-Powered Features

**Strategy Generation:**
```python
class AIStrategyGenerator:
    """Generate strategies using LLM"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
    def generate_from_description(self, description: str) -> Strategy:
        """
        User input: "Create a strategy that buys when RSI < 30 
                     and sells when RSI > 70"
        Output: Executable strategy code
        """
        prompt = self._build_generation_prompt(description)
        code = self.llm.generate(prompt)
        strategy = self._parse_and_validate(code)
        return strategy
        
    def improve_strategy(self, strategy, performance_data):
        """Suggest improvements based on backtest results"""
        pass
```

**Prompt Engineering for Strategy Generation:**
```
You are an expert quantitative trader. Generate Python code for a trading 
strategy based on this description: {user_description}

Requirements:
- Use the Strategy base class
- Include proper indicator calculations
- Implement clear entry/exit logic
- Add risk management rules
- Follow best practices for backtesting

Return only valid, executable Python code.
```

#### 3.4.2 Optimization Algorithms

**Parameter Optimization:**
- **Grid Search:** Exhaustive search over parameter space
- **Random Search:** Sample random parameter combinations
- **Genetic Algorithms:** Evolutionary optimization
- **Bayesian Optimization:** Efficient hyperparameter tuning
- **Particle Swarm Optimization:** Swarm intelligence approach

```python
class GeneticOptimizer:
    """Optimize strategy parameters using genetic algorithm"""
    
    def __init__(self, population_size=50, generations=100):
        self.population_size = population_size
        self.generations = generations
        
    def optimize(self, strategy, data, param_ranges, objective='sharpe'):
        """
        1. Initialize random population
        2. Evaluate fitness (backtest)
        3. Selection (tournament/roulette)
        4. Crossover (combine parameters)
        5. Mutation (random changes)
        6. Repeat until convergence
        """
        pass
```

#### 3.4.3 AI-Driven Insights
- **Pattern Discovery:** Identify recurring profitable patterns
- **Market Regime Detection:** Classify market conditions
- **Correlation Analysis:** Find inter-asset relationships
- **Feature Importance:** Determine key indicators
- **Anomaly Detection:** Flag unusual market behavior

#### 3.4.4 Strategy Validation
```python
class StrategyValidator:
    """Validate AI-generated strategies"""
    
    def check_syntax(self, code: str) -> bool:
        """Verify code is syntactically correct"""
        
    def check_logic(self, strategy: Strategy) -> List[str]:
        """Detect logical issues (look-ahead bias, etc.)"""
        
    def stress_test(self, strategy: Strategy) -> dict:
        """Test under extreme market conditions"""
```

---

### 3.5 Reporting & Visualization Module

#### 3.5.1 Report Types

**Backtest Report:**
```
===============================================
BACKTEST REPORT: Moving Average Crossover
===============================================
Period: 2020-01-01 to 2024-12-31
Initial Capital: $100,000
Final Portfolio Value: $156,234

PERFORMANCE SUMMARY
-------------------
Total Return: 56.23%
Annualized Return: 11.24%
Sharpe Ratio: 1.45
Max Drawdown: -18.32%
Win Rate: 58.3%

TRADE STATISTICS
----------------
Total Trades: 127
Winning Trades: 74
Losing Trades: 53
Average Win: $842
Average Loss: -$523
Profit Factor: 1.61

[Equity Curve Chart]
[Drawdown Chart]
[Monthly Returns Heatmap]
```

**Strategy Comparison Report:**
- Side-by-side performance metrics
- Risk-adjusted returns comparison
- Correlation matrix between strategies
- Portfolio-level analysis (if combined)

**Workflow Report:**
```
WORKFLOW EXECUTION REPORT
=========================
Date: 2025-10-29
Triggered By: Scheduled Daily Scan

DATA COLLECTION
- Fetched data for 50 symbols
- Data range: Last 100 days
- Sources: Alpaca API, Yahoo Finance
- Status: ✓ Success

STRATEGY EXECUTION
- Active Strategies: 5
- Signals Generated: 12
  - BUY: 7 (AAPL, TSLA, NVDA, AMD, GOOGL, MSFT, META)
  - SELL: 3 (AMZN, NFLX, DIS)
  - HOLD: 2 (JPM, BAC)

AI OPTIMIZATION
- Strategies Optimized: 2
- Parameter Updates: 8
- Improvement in Sharpe: +0.12

ALERTS & NOTIFICATIONS
- High Priority: 2
- Medium Priority: 5
```

#### 3.5.2 Visualization Components

**Interactive Charts:**
- Equity curve with drawdown overlay
- Price charts with strategy signals
- Volume profile
- Indicator overlays (customizable)
- Order book depth (Level 2 visualization)

**Analytics Dashboards:**
- Real-time portfolio performance
- Strategy leaderboard
- Market overview (heat maps, sector performance)
- Risk dashboard (VaR, exposure, correlation)

**Export Formats:**
- PDF (professional reports)
- Excel (detailed trade logs, metrics)
- JSON/CSV (data interchange)
- HTML (interactive web reports)

---

## 4. Development Phases

### Phase 1: Foundation (Weeks 1-4)
**Objectives:**
- Set up development environment
- Design database schema
- Implement data acquisition module
- Basic API structure

**Deliverables:**
- Working data pipeline for 3+ data sources
- Database with historical data storage
- REST API for data queries
- Unit tests for data module

### Phase 2: Strategy Framework (Weeks 5-8)
**Objectives:**
- Implement strategy base classes
- Create 5-10 baseline strategies
- Build strategy repository
- Version control system

**Deliverables:**
- Strategy SDK documentation
- Working implementations of common strategies
- CRUD API for strategy management
- Strategy validation framework

### Phase 3: Backtesting Engine (Weeks 9-12)
**Objectives:**
- Build core backtesting engine
- Implement performance metrics
- Add realistic simulation features
- Create visualization components

**Deliverables:**
- Functional backtesting module
- Comprehensive metrics calculation
- Basic reporting system
- Integration tests

### Phase 4: AI Integration (Weeks 13-16)
**Objectives:**
- Integrate OpenAI API
- Implement strategy generation
- Build optimization algorithms
- Create AI-assisted analysis tools

**Deliverables:**
- Natural language strategy creation
- Parameter optimization framework
- AI insights dashboard
- Strategy improvement suggestions

### Phase 5: Live Trading Preparation (Weeks 17-20)
**Objectives:**
- Real-time data streaming
- Level 2 data integration
- Paper trading mode
- Alert system

**Deliverables:**
- WebSocket implementation for live data
- Order book visualization
- Paper trading environment
- Email/SMS/Push notification system

### Phase 6: Polish & Production (Weeks 21-24)
**Objectives:**
- Frontend development
- Performance optimization
- Security hardening
- Documentation

**Deliverables:**
- User-friendly web interface
- Admin dashboard
- API documentation (Swagger/OpenAPI)
- Deployment pipeline
- User manual

---

## 5. Key Features Specification

### 5.1 Data Management
- [ ] Historical data download (1min to daily bars)
- [ ] Real-time quote streaming (WebSocket)
- [ ] Level 2 order book data
- [ ] Data validation and cleaning
- [ ] Multi-provider support with fallback
- [ ] Efficient time-series storage
- [ ] Data export functionality

### 5.2 Strategy Development
- [ ] Pre-built strategy library (20+ strategies)
- [ ] Custom strategy creation (Python SDK)
- [ ] AI-powered strategy generation from text
- [ ] Strategy versioning and rollback
- [ ] Parameter configuration UI
- [ ] Strategy composition (combine multiple)
- [ ] Risk management rules builder

### 5.3 Backtesting
- [ ] Historical simulation engine
- [ ] Comprehensive performance metrics (50+ indicators)
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Slippage and commission modeling
- [ ] Multi-asset portfolio backtesting
- [ ] Benchmark comparison

### 5.4 Optimization
- [ ] Grid search
- [ ] Genetic algorithm optimization
- [ ] Bayesian optimization
- [ ] Walk-forward analysis
- [ ] Overfitting detection
- [ ] Cross-validation
- [ ] Parameter sensitivity analysis

### 5.5 AI Capabilities
- [ ] Natural language strategy creation
- [ ] Strategy improvement suggestions
- [ ] Pattern discovery
- [ ] Market regime classification
- [ ] Sentiment analysis integration
- [ ] Automated feature engineering
- [ ] Strategy explanation (interpretability)

### 5.6 Reporting
- [ ] Automated backtest reports (PDF/HTML)
- [ ] Trade journal
- [ ] Performance dashboards
- [ ] Strategy comparison reports
- [ ] Workflow execution logs
- [ ] Custom report builder
- [ ] Scheduled report delivery

### 5.7 Live Trading Support
- [ ] Real-time signal generation
- [ ] Paper trading mode
- [ ] Alert system (email, SMS, webhook)
- [ ] Position monitoring
- [ ] Risk alerts
- [ ] Order execution tracking (if broker API integrated)

---

## 6. Technical Requirements

### 6.1 Performance
- API response time: < 200ms (p95)
- Backtest execution: < 30 seconds for 1 year daily data
- Real-time data latency: < 100ms
- Support 100+ concurrent users
- Database query optimization for large time-series

### 6.2 Scalability
- Horizontal scaling for API servers
- Distributed backtesting (parallel processing)
- Message queue for async tasks
- CDN for static assets
- Database sharding if needed

### 6.3 Security
- OAuth 2.0 / JWT authentication
- API rate limiting
- Encrypted data at rest and in transit
- Secure API key storage
- Role-based access control (RBAC)
- Audit logging
- Regular security audits

### 6.4 Reliability
- 99.5% uptime SLA
- Automated backups (daily)
- Disaster recovery plan
- Health check endpoints
- Error logging and monitoring
- Graceful degradation

---

## 7. Data Flow Examples

### 7.1 Backtest Workflow
```
1. User selects strategy from repository
2. User configures parameters (date range, initial capital, etc.)
3. System fetches historical data from cache/API
4. Backtesting engine simulates trades
5. Performance metrics calculated
6. Report generated with charts
7. Results stored in database
8. User receives notification
```

### 7.2 AI Strategy Generation Workflow
```
1. User inputs strategy description (natural language)
2. System sends prompt to OpenAI API
3. LLM generates strategy code
4. Validator checks syntax and logic
5. System runs mini-backtest for sanity check
6. If valid, strategy added to repository
7. User can view/edit/backtest new strategy
```

### 7.3 Live Signal Generation Workflow
```
1. Real-time data streams via WebSocket
2. Active strategies process incoming data
3. Strategy generates buy/sell/hold signal
4. Signal passes through risk management filters
5. If valid, alert sent to user (email/SMS/UI)
6. User can execute trade manually or via API
7. Trade logged in database
```

---

## 8. API Endpoints Design

### 8.1 Data Endpoints
```
GET  /api/v1/data/historical/{symbol}?start=&end=&interval=
GET  /api/v1/data/quote/{symbol}
GET  /api/v1/data/level2/{symbol}
WS   /api/v1/data/stream?symbols=AAPL,TSLA
```

### 8.2 Strategy Endpoints
```
GET    /api/v1/strategies
POST   /api/v1/strategies
GET    /api/v1/strategies/{id}
PUT    /api/v1/strategies/{id}
DELETE /api/v1/strategies/{id}
POST   /api/v1/strategies/generate  (AI generation)
GET    /api/v1/strategies/{id}/versions
```

### 8.3 Backtest Endpoints
```
POST   /api/v1/backtest/run
GET    /api/v1/backtest/{id}/results
GET    /api/v1/backtest/{id}/report
POST   /api/v1/backtest/optimize
GET    /api/v1/backtest/compare?ids=1,2,3
```

### 8.4 AI Endpoints
```
POST   /api/v1/ai/generate-strategy
POST   /api/v1/ai/optimize-strategy
POST   /api/v1/ai/analyze-performance
GET    /api/v1/ai/insights/{symbol}
```

---

## 9. Risk Management & Compliance

### 9.1 Built-in Risk Controls
- Maximum position size limits
- Portfolio-level exposure limits
- Daily loss limits
- Drawdown thresholds
- Correlation-based risk checks
- Volatility-adjusted position sizing

### 9.2 Compliance Considerations
- **Disclaimer:** System is for research/education only
- **Regulatory:** Not a registered investment advisor
- **Data rights:** Ensure proper licensing for market data
- **Privacy:** GDPR compliance for user data
- **Terms of service:** Clear user agreement

### 9.3 Testing & Validation
- Unit tests (>80% coverage)
- Integration tests
- End-to-end tests
- Performance/load testing
- Security penetration testing
- User acceptance testing (UAT)

---

## 10. Future Enhancements (Post-MVP)

### 10.1 Advanced Features
- **Multi-asset support:** Crypto, forex, options, futures
- **Social features:** Share strategies, leaderboards
- **Broker integration:** Direct order execution
- **Mobile app:** iOS/Android applications
- **Advanced ML models:** Deep learning, reinforcement learning
- **Alternative data:** Satellite imagery, web scraping, sentiment
- **Portfolio optimization:** Modern portfolio theory, Black-Litterman

### 10.2 AI Enhancements
- **AutoML:** Automated model selection and training
- **Explainable AI:** Better strategy interpretability
- **Multi-agent systems:** Competing AI strategies
- **Continuous learning:** Strategies that adapt over time
- **Natural language interface:** Conversational AI for trading

---

## 11. Budget & Resource Estimation

### 11.1 Development Team (6 months)
- 1 Lead Developer / Architect
- 2 Backend Developers
- 1 Frontend Developer
- 1 ML/AI Engineer
- 1 QA Engineer
- 1 DevOps Engineer

### 11.2 Infrastructure Costs (Monthly)
- Cloud hosting (AWS/GCP): $500-2,000
- Database (managed): $200-500
- Market data APIs: $500-5,000 (varies widely)
- OpenAI API: $200-1,000
- CDN & Storage: $100-300
- Monitoring tools: $100-200

### 11.3 Third-Party Services
- Market data provider subscription
- OpenAI API credits
- Charting library license (TradingView)
- Email/SMS service (SendGrid, Twilio)
- Error tracking (Sentry)

---

## 12. Success Metrics

### 12.1 Technical KPIs
- System uptime: >99.5%
- API latency: <200ms (p95)
- Backtest completion time: <30s
- Data accuracy: >99.9%

### 12.2 User KPIs
- Strategy creation rate
- Backtest execution volume
- User retention rate
- AI feature adoption rate

### 12.3 Quality KPIs
- Bug escape rate: <5%
- Code coverage: >80%
- Security vulnerabilities: 0 critical

---

## 13. Conclusion

This comprehensive plan provides a roadmap for building a professional-grade stock picking tool with AI integration. The modular architecture ensures flexibility and scalability, while the phased approach allows for iterative development and testing.

**Critical Success Factors:**
1. Reliable, high-quality market data
2. Robust backtesting with realistic simulation
3. Effective AI integration for strategy generation
4. User-friendly interface with powerful features
5. Strong risk management and validation

**Next Steps:**
1. Finalize technology stack choices
2. Set up development environment
3. Secure market data provider contracts
4. Begin Phase 1 development
5. Establish CI/CD pipeline

This tool will empower professional traders with cutting-edge AI capabilities while maintaining the rigor and reliability required for serious trading applications.
