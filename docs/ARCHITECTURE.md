# System Architecture

## Overview

The Stock Picking Tool follows a modular, microservices-inspired architecture with clear separation between data layer, business logic, and presentation.

## Core Layers

### 1. Data Layer
- Market data acquisition from multiple providers
- Time-series storage (TimescaleDB)
- Real-time data streaming (WebSocket)
- Caching strategy (Redis)

### 2. Strategy Engine
- Base strategy framework
- Strategy repository with versioning
- Strategy executor
- Signal generation

### 3. Backtesting Engine
- Historical simulation
- Performance metrics calculation
- Walk-forward optimization
- Portfolio management

### 4. AI/ML Engine
- Strategy generation from natural language
- Parameter optimization
- Pattern recognition
- Market regime detection

### 5. API Layer
- RESTful endpoints
- WebSocket for real-time data
- Authentication & authorization
- Rate limiting

### 6. Frontend
- Next.js application
- Interactive dashboards
- Real-time updates
- TradingView chart integration

## Data Flow

1. **Data Acquisition** → Market data fetched and stored
2. **Strategy Execution** → Strategies process data and generate signals
3. **Backtesting** → Historical simulation of strategy performance
4. **AI Enhancement** → LLM improves strategies based on results
5. **Visualization** → Results displayed in dashboards

## Database Schema

See individual model files in `backend/app/models/` for detailed schemas.

Key tables:
- strategies
- strategy_versions
- backtests
- trades
- market_data (TimescaleDB)
