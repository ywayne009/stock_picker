# Phase 2: Frontend Visualization - Design Decisions

**Date**: 2025-11-03
**Status**: Planning → Implementation

---

## User Preferences

### Architecture
- **Approach**: Option 1 (Lightweight - FastAPI + React + TradingView Charts)
- **Extensibility**: Design to allow migration to Option 2 (Full Next.js) if needed
- **Key Requirement**: Keep architecture modular and API-driven

### Technology Stack
- **Frontend Framework**: React (chosen for ecosystem, TradingView support, easier Next.js migration)
- **Backend**: Extend existing FastAPI
- **Charts**: TradingView Lightweight Charts (industry standard for finance)
- **Styling**: Tailwind CSS (modern, flexible, production-ready)
- **State Management**: Zustand (lightweight, simpler than Redux)

### Deployment & Usage
- **Current**: Local testing
- **Future**: May be deployed to production
- **Implication**: Build with production-quality code from start (auth-ready, env configs, etc.)

### Priority & Focus
- **Primary Focus**: Backtesting workflow and results visualization
- **Quality**: Polished dashboard (not MVP/prototype)
- **Timeline**: Take time to build it right

---

## Key Design Principles

1. **API-First Design**
   - All data through REST APIs
   - Backend is source of truth
   - Frontend is pure presentation layer
   - Easy to swap frontend later

2. **Modularity**
   - Reusable React components
   - Separate API client service
   - Strategy logic stays in backend
   - Easy to extend with new features

3. **Production Quality**
   - Proper error handling
   - Loading states
   - Responsive design
   - TypeScript for type safety
   - Component documentation

4. **Extensibility Path to Option 2**
   - Use React (not Vue) for Next.js compatibility
   - Structure API endpoints RESTfully
   - Keep state management simple (Zustand → Redux easy)
   - Separate components from pages

---

## Phase 2 Implementation Plan

### Stage 1: Backend API Layer (Foundation)
**Goal**: Create robust API endpoints for frontend consumption

**Endpoints to Build**:
```
/api/v1/data/
  GET  /stocks/search?q={query}           # Search stock symbols
  GET  /stocks/{symbol}/info              # Company info
  GET  /stocks/{symbol}/ohlcv             # Historical OHLCV data

/api/v1/strategies/
  GET  /strategies                        # List available strategies
  GET  /strategies/{id}                   # Get strategy details
  POST /strategies                        # Create custom strategy

/api/v1/backtest/
  POST /backtest/run                      # Run backtest
  GET  /backtest/{id}/results             # Get results
  GET  /backtest/{id}/trades              # Get trade history
  GET  /backtest/{id}/metrics             # Get performance metrics
```

**Data Models** (Pydantic schemas):
- StockData
- StrategyConfig
- BacktestRequest
- BacktestResults
- Trade
- PerformanceMetrics

---

### Stage 2: Frontend Project Setup
**Goal**: Modern React setup with best practices

**Structure**:
```
frontend/
├── src/
│   ├── api/              # API client & endpoints
│   ├── components/       # Reusable UI components
│   │   ├── charts/       # Chart components
│   │   ├── forms/        # Input components
│   │   └── common/       # Buttons, cards, etc.
│   ├── pages/            # Page-level components
│   ├── stores/           # Zustand state stores
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Helper functions
│   ├── types/            # TypeScript types
│   └── App.tsx
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts        # Using Vite for fast dev
```

**Dependencies**:
- React 18
- TypeScript
- TradingView Lightweight Charts
- Tailwind CSS
- Zustand (state)
- React Router (navigation)
- Axios (HTTP client)
- date-fns (date formatting)
- React Hook Form (forms)

---

### Stage 3: Core Components (Polished)
**Priority Order** (backtesting focus):

1. **BacktestConfigPanel**
   - Stock symbol search/select
   - Date range picker (visual calendar)
   - Strategy selector (dropdown with descriptions)
   - Parameter sliders (smooth, real-time preview)
   - Run backtest button (with loading state)

2. **PriceChartWithSignals**
   - TradingView candlestick chart
   - Buy/sell signal markers
   - Moving average overlays
   - Volume bars
   - Zoom/pan controls
   - Tooltip with OHLCV data

3. **PerformanceMetricsGrid**
   - Card-based layout
   - Color-coded metrics (green/red)
   - Icons for each metric
   - Comparison to benchmark
   - Trend indicators (↑↓)

4. **EquityCurveChart**
   - Line chart of portfolio value
   - Drawdown shading (red zones)
   - Benchmark comparison line
   - Hover details

5. **TradesTable**
   - Sortable columns
   - Filterable by type (buy/sell)
   - Pagination
   - Export to CSV
   - Profit/loss highlighting

6. **StrategyComparisonView**
   - Side-by-side metrics
   - Overlaid equity curves
   - Win rate comparison chart
   - Sharpe ratio comparison

---

### Stage 4: Pages/Views

1. **Backtesting Dashboard** (Primary focus)
   ```
   Layout:
   ┌─────────────────────────────────────┐
   │  Header (Stock Search, Date Range)  │
   ├──────────┬──────────────────────────┤
   │          │                          │
   │ Strategy │    Price Chart           │
   │ Config   │    with Signals          │
   │ Panel    │                          │
   │          ├──────────────────────────┤
   │          │  Equity Curve            │
   ├──────────┴──────────────────────────┤
   │  Performance Metrics Grid           │
   ├─────────────────────────────────────┤
   │  Trades Table                       │
   └─────────────────────────────────────┘
   ```

2. **Strategy Comparison Page** (Secondary)
   - Run multiple strategies on same data
   - Side-by-side comparison

3. **Settings/Preferences** (Future)
   - Theme toggle
   - Default parameters
   - Export preferences

---

### Stage 5: Polish & UX Details

**Visual Design**:
- Dark theme (primary) with light theme option
- Professional color palette:
  - Primary: Blue (#3B82F6)
  - Success: Green (#10B981)
  - Danger: Red (#EF4444)
  - Background: Dark gray (#1F2937)
  - Cards: Slightly lighter gray (#374151)
- Smooth animations and transitions
- Loading skeletons (not spinners)
- Empty states with helpful messages

**Interactions**:
- Debounced inputs
- Optimistic updates where possible
- Error toasts (not alerts)
- Keyboard shortcuts
- Responsive (desktop-first, mobile-friendly)

**Performance**:
- Lazy load charts
- Virtualized tables for large datasets
- Memoized components
- Code splitting

---

## Implementation Timeline (Polished Dashboard)

**Week 1**: Backend API + Frontend Setup
- Days 1-2: Backend API endpoints
- Day 3: Frontend project setup
- Days 4-5: Core API integration

**Week 2**: Components & Charts
- Days 1-2: TradingView chart integration
- Days 3-4: Metrics & equity curve
- Day 5: Trades table

**Week 3**: Dashboard Assembly & Polish
- Days 1-2: Assemble backtesting dashboard
- Days 3-4: Styling, animations, UX polish
- Day 5: Testing & bug fixes

---

## Future Extension to Option 2 (Next.js)

When ready to migrate to full Next.js:

**Easy Migration Path**:
1. Keep all React components as-is (100% reusable)
2. Move from Vite → Next.js build system
3. Add server-side rendering for SEO
4. Convert API calls to Next.js API routes (optional)
5. Add authentication middleware
6. Deploy to Vercel/AWS

**What Changes**:
- `src/pages/` → Next.js `app/` or `pages/` directory
- Client-side routing → file-based routing
- Add `getServerSideProps` or `getStaticProps`
- Zustand stays the same (or upgrade to Redux)

**What Stays the Same**:
- All React components
- Tailwind config
- TypeScript types
- API client (just change base URL if needed)
- Chart components

---

## Notes for Future Sessions

- This file captures all Phase 2 decisions
- Refer to this when resuming work
- Update as decisions change
- Track progress in PROJECT_STATUS.md
