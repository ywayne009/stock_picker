# Backend Structure Documentation

**Last Updated:** 2025-11-14
**Status:** Clean and Simplified ✅

## 📁 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   │
│   ├── api/                             # API Layer
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── backtest.py          # Backtest execution endpoints
│   │       │   └── data.py              # Market data endpoints
│   │       └── schemas.py               # Pydantic request/response models
│   │
│   ├── core/                            # Core configuration
│   │   └── config.py                    # App settings
│   │
│   ├── models/                          # Data models (empty - using dataclasses)
│   │   └── __init__.py
│   │
│   ├── schemas/                         # Pydantic schemas
│   │   ├── backtest.py                  # Backtest schemas
│   │   └── data.py                      # Data schemas
│   │
│   └── services/                        # Business Logic
│       ├── backtesting/                 # Backtesting engine
│       │   └── engine.py                # Core backtest simulation
│       │
│       ├── data/                        # Market data providers
│       │   ├── base_provider.py         # Provider interface
│       │   ├── data_manager.py          # Data management
│       │   ├── market_data.py           # yfinance implementation
│       │   └── validators.py            # Data validation
│       │
│       ├── strategy/                    # Strategy framework
│       │   ├── base_strategy.py         # Abstract base class
│       │   ├── indicators.py            # Technical indicators
│       │   ├── registry.py              # Legacy registry
│       │   ├── strategy_factory.py      # Factory pattern
│       │   ├── strategy_types.py        # Type system & metadata
│       │   └── examples/                # Example strategies
│       │       ├── rsi_strategy.py
│       │       ├── macd_strategy.py
│       │       ├── bollinger_strategy.py
│       │       ├── ma_crossover.py
│       │       └── register_all.py
│       │
│       └── visualization/               # Chart generation
│           ├── chart_themes.py
│           ├── performance_metrics.py
│           └── strategy_charts.py
│
├── tests/                               # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── test_strategy_factory.py            # Strategy factory tests
├── test_new_strategies.py              # Strategy integration tests
├── test_api_strategies.py              # API integration tests
│
└── venv/                                # Virtual environment
```

## 🗂️ What Was Removed

### Deleted Duplicate/Unused Code

**Services:**
- ❌ `app/services/backtest/` - Duplicate of backtesting
- ❌ `app/services/ai/` - Not implemented yet
- ❌ `app/services/reporting/` - Replaced by visualization
- ❌ `app/utils/` - Duplicate indicators

**Models/Schemas:**
- ❌ `app/models/user.py` - No authentication
- ❌ `app/models/backtest.py` - Using dataclasses
- ❌ `app/models/strategy.py` - Not needed
- ❌ `app/schemas/strategy.py` - Not used
- ❌ `app/core/security.py` - No auth
- ❌ `app/core/database.py` - In-memory only

**API Endpoints:**
- ❌ `app/api/v1/endpoints/ai.py` - Not implemented
- ❌ `app/api/v1/endpoints/strategies.py` - Mostly empty
- ❌ `app/api/v1/endpoints/health.py` - Empty file

**Root Files:**
- ❌ `demo_strategy.py` - Demo file
- ❌ `demo_multi_stock.py` - Demo file
- ❌ `run_backtest.py` - Duplicate
- ❌ `test_wsl_browser.py` - Not needed
- ❌ `backtesting_system/` - Old implementation
- ❌ `strategies_config.py` - Moved to examples

**Strategy Files:**
- ❌ `strategy_executor.py` - Empty
- ❌ `strategy_repository.py` - 1 line placeholder

## 📊 Current Module Count

**Before Cleanup:** ~90 Python files
**After Cleanup:** ~50 Python files
**Reduction:** 44% fewer files ✅

## 🎯 Core Modules

### 1. API Layer (`app/api/v1/`)

**Purpose:** REST API endpoints

**Files:**
- `endpoints/backtest.py` - Run backtests, get results
- `endpoints/data.py` - Fetch market data
- `schemas.py` - Request/response models

**Routes:**
```
GET  /                          # Root
GET  /health                    # Health check
GET  /api/v1/data/stock         # Get stock data
POST /api/v1/backtest/run       # Run single backtest
POST /api/v1/backtest/batch     # Run batch backtest
```

### 2. Backtesting Engine (`app/services/backtesting/`)

**Purpose:** Simulate trading strategies

**Key Class:**
```python
class BacktestEngine:
    def run_backtest(strategy, data, ticker) -> BacktestResult
```

**Features:**
- Realistic simulation (commissions, slippage)
- Force liquidation at period end
- 18 performance metrics
- Trade extraction

### 3. Strategy Framework (`app/services/strategy/`)

**Purpose:** Define and manage trading strategies

**Key Components:**
- `base_strategy.py` - Abstract Strategy base class
- `strategy_types.py` - Type system (7 types, metadata)
- `strategy_factory.py` - Factory pattern with search
- `indicators.py` - Technical indicators (SMA, EMA, RSI, MACD, BB, ATR)
- `registry.py` - Legacy strategy registry

**Current Strategies:** 6
- MA Crossover (20/50)
- Golden Cross (50/200)
- Fast MA (10/30)
- RSI 30/70 ⭐
- MACD 12/26/9 ⭐
- Bollinger Band 20,2 ⭐

### 4. Data Layer (`app/services/data/`)

**Purpose:** Fetch and validate market data

**Providers:**
- yfinance (primary)
- Alpaca (planned)
- Polygon (planned)
- Alpha Vantage (planned)

**Features:**
- OHLCV data fetching
- Data validation
- Caching (planned)

### 5. Visualization (`app/services/visualization/`)

**Purpose:** Generate charts and reports

**Features:**
- Price charts
- Equity curves
- Trade signals
- Performance metrics
- Custom themes

## 🔄 Data Flow

```
User Request
    ↓
API Endpoint (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
┌─────────────┬──────────────┬─────────────┐
│   Data      │  Strategy    │  Backtest   │
│  Service    │   Service    │   Engine    │
└─────────────┴──────────────┴─────────────┘
    ↓
Response (Pydantic Schema)
    ↓
User
```

## 🧪 Testing

**Test Files:**
- `test_strategy_factory.py` - Factory system tests
- `test_new_strategies.py` - Strategy integration tests
- `test_api_strategies.py` - API integration tests
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/e2e/` - End-to-end tests

**Run Tests:**
```bash
# Strategy factory
python test_strategy_factory.py

# Strategy integration
python test_new_strategies.py

# All unit tests
pytest tests/unit/

# All tests
pytest
```

## 📝 Code Quality

### Design Patterns Used

1. **Strategy Pattern** - Trading strategies inherit from base class
2. **Factory Pattern** - StrategyFactory creates strategies
3. **Repository Pattern** - Legacy registry for backward compatibility
4. **Dependency Injection** - Services injected via constructors

### Principles Followed

- ✅ **Single Responsibility** - Each module has one clear purpose
- ✅ **Open/Closed** - Easy to extend, hard to break
- ✅ **Dependency Inversion** - Depend on abstractions
- ✅ **DRY** - No code duplication
- ✅ **KISS** - Keep it simple

## 🚀 Adding New Features

### Add a New Strategy

1. Create file in `app/services/strategy/examples/`
2. Inherit from `Strategy` base class
3. Implement `setup()` and `generate_signals()`
4. Add metadata
5. Register with factory
6. Test

**See:** `STRATEGY_API_GUIDE.md`

### Add a New API Endpoint

1. Create function in `app/api/v1/endpoints/`
2. Add route decorator
3. Define request/response schemas
4. Implement business logic
5. Include router in `main.py`

### Add a New Data Provider

1. Create class in `app/services/data/`
2. Inherit from `BaseProvider`
3. Implement `fetch_data()` method
4. Register in data manager

## 📚 Documentation

- `STRATEGY_API_GUIDE.md` - Complete strategy development guide
- `PROJECT_STATUS.md` - Project status and progress
- `CLAUDE.md` - Development guidelines
- `README.md` - Project overview

## 🔧 Configuration

**Environment Variables:**
```bash
# Optional - defaults to yfinance
POLYGON_API_KEY=
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPHA_VANTAGE_KEY=
```

**App Settings:**
- File: `app/core/config.py`
- Load: `from app.core.config import settings`

## 🎯 Next Steps

**Immediate:**
- [x] Clean up unused code
- [ ] Add metadata to MACD and Bollinger strategies
- [ ] Add API documentation (Swagger/OpenAPI)

**Future:**
- [ ] Implement caching layer (Redis)
- [ ] Add database persistence (PostgreSQL + TimescaleDB)
- [ ] Implement authentication
- [ ] Add WebSocket support for real-time data
- [ ] Implement AI strategy generation

---

**Clean, simple, and maintainable!** 🎉
