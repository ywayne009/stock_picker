# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🚀 Starting a New Session (READ THIS FIRST!)

**When you start working on this project, follow these steps:**

1. **Read PROJECT_STATUS.md** - This tells you exactly where the project is and what to work on next
2. **Check the git log** - `git log --oneline -5` to see recent changes
3. **Review last session notes** - Bottom of PROJECT_STATUS.md has session log
4. **Ask the user** - "What would you like to work on today?"
5. **Update PROJECT_STATUS.md** - When you finish your session

**Quick Context Check:**
```bash
# Where am I?
pwd  # Should be: /Users/wayne/main/labs/stock_picker

# What's the latest?
git status
git log --oneline -3

# What needs to be done?
cat PROJECT_STATUS.md | grep "Next Steps" -A 10
```

---

## Project Overview

This is an AI-powered stock picking tool designed for professional traders. The system integrates real-time and historical market data, maintains a repository of trading strategies, supports backtesting, and leverages AI for strategy generation and optimization.

## Technology Stack

**Backend:**
- Python 3.11+ (primary language)
- FastAPI (async support, WebSocket for live data)
- PostgreSQL + TimescaleDB (time-series data)
- Redis (caching real-time data)
- RabbitMQ or Kafka (event-driven architecture)

**Data Processing:**
- Pandas, NumPy (data manipulation)
- TA-Lib, pandas-ta (technical indicators)
- Arctic or InfluxDB (time-series storage)

**AI/ML:**
- OpenAI API (GPT-4 for strategy generation)
- scikit-learn, XGBoost (optimization algorithms)
- TensorFlow/PyTorch (pattern recognition)
- LangChain (AI agent orchestration)

**Frontend:**
- React or Next.js
- TradingView Charting Library
- Material-UI or Tailwind CSS
- Socket.io (real-time updates)

## Architecture Overview

The system follows a modular architecture with four primary layers:

1. **Data Layer** - Market data acquisition, time-series storage, Level 2 order book data
2. **Strategy Engine** - Strategy execution, backtesting, signal generation
3. **AI/ML Engine** - GPT-4 API integration, strategy generation, optimization, pattern recognition
4. **API Gateway / Backend** - REST/WebSocket APIs, authentication, rate limiting

## Core Modules

### Data Acquisition Module
- Multi-provider support (Polygon.io, Alpaca, Alpha Vantage, Yahoo Finance, IEX Cloud)
- Handles OHLCV data, real-time quotes, Level 2 order book, news/sentiment feeds
- Implements caching strategy (Redis for real-time, TimescaleDB for historical)
- WebSocket support for efficient real-time streaming

### Strategy Management Module
- Base `Strategy` class that all strategies inherit from
- Strategies must implement: `setup()`, `generate_signals()`, `calculate_position_size()`, `risk_management()`
- Strategy categories: Technical, Quantitative, Machine Learning, AI-Generated
- Version control for strategies stored in PostgreSQL with JSONB parameters

### Backtesting Engine
- Core `BacktestEngine` class with portfolio management
- Performance metrics: Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, Profit Factor, CAGR
- Realistic simulation: commission modeling, slippage, market impact, liquidity constraints
- Walk-forward optimization support

### AI Strategy Generation & Optimization
- `AIStrategyGenerator` class for creating strategies from natural language descriptions
- Optimization algorithms: Grid Search, Genetic Algorithms, Bayesian Optimization, Particle Swarm
- AI-driven insights: pattern discovery, market regime detection, correlation analysis
- `StrategyValidator` for syntax checking, logic validation, and stress testing

### Reporting & Visualization
- Report types: Backtest reports, Strategy comparison, Workflow execution
- Interactive charts: equity curves, drawdown overlays, volume profiles, order book depth
- Export formats: PDF, Excel, JSON/CSV, HTML

## Development Commands

This project is in initial development phase. Once implemented:

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

**Development:**
```bash
# Run backend server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run linter
pylint app/

# Format code
black app/ tests/
```

**Database:**
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Key Design Patterns

### Strategy Pattern
All trading strategies inherit from a base `Strategy` class and implement standardized methods. This allows strategies to be plugged in/out without modifying the backtesting engine.

### Repository Pattern
Strategies are stored in a PostgreSQL database with version control. Each strategy modification creates a new version entry while maintaining the current version reference.

### Observer Pattern
Real-time data streaming uses WebSocket connections with callbacks. Strategies subscribe to data streams and react to market events.

### Factory Pattern
The `AIStrategyGenerator` creates strategy instances from natural language descriptions by generating code and validating it before instantiation.

## Data Schema Conventions

**Strategies Table:**
- `code` field stores serialized Python strategy code
- `parameters` field uses JSONB for flexible parameter storage
- `performance_metrics` field uses JSONB for storing backtest results
- `creator` field distinguishes between 'user' and 'ai' generated strategies

**Strategy Versions Table:**
- Maintains full history of strategy modifications
- Links to parent strategy via `strategy_id`
- Stores `change_notes` for documentation

## API Endpoint Structure

```
/api/v1/data/*          - Historical data, quotes, Level 2, WebSocket streams
/api/v1/strategies/*    - CRUD operations, AI generation, versioning
/api/v1/backtest/*      - Run backtests, get results, optimize, compare
/api/v1/ai/*            - Strategy generation, optimization, insights
```

## Critical Development Considerations

1. **Look-ahead Bias Prevention**: Ensure backtesting engine strictly partitions data and strategies only access historical data available at each timestamp

2. **Realistic Simulation**: Always model commissions, slippage, and market impact. Avoid unrealistic assumptions that inflate backtest performance

3. **API Rate Limiting**: Respect market data provider quotas. Implement exponential backoff and caching strategies

4. **Data Validation**: Always validate incoming market data for gaps, outliers, and anomalies before storage or strategy execution

5. **AI Code Validation**: Never execute AI-generated strategy code without syntax checking, logic validation, and sandboxed testing

6. **Risk Management**: Implement position size limits, portfolio exposure limits, and drawdown thresholds at multiple levels

## Testing Strategy

- **Unit Tests**: Test individual components (data fetchers, indicators, strategy logic)
- **Integration Tests**: Test module interactions (data → strategy → backtest)
- **End-to-End Tests**: Test complete workflows (strategy creation → optimization → backtesting → reporting)
- **Performance Tests**: Ensure backtests complete within SLA (<30s for 1 year daily data)
- **Security Tests**: Validate API authentication, rate limiting, input sanitization

## Performance Requirements

- API response time: < 200ms (p95)
- Backtest execution: < 30 seconds for 1 year daily data
- Real-time data latency: < 100ms
- Support 100+ concurrent users
- Database queries optimized for large time-series datasets

## Security Considerations

- OAuth 2.0 / JWT for authentication
- API keys stored securely (never in code or git)
- All data encrypted at rest and in transit
- Rate limiting on all endpoints
- Input validation and sanitization for AI-generated code
- Audit logging for all strategy modifications and trades
