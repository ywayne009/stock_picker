"""
Pydantic Schemas for API Request/Response Models

These schemas define the data structures for API communication
between the frontend and backend.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class IntervalEnum(str, Enum):
    """Data interval options"""
    ONE_DAY = "1d"
    ONE_HOUR = "1h"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"


class SignalType(str, Enum):
    """Trade signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StrategyType(str, Enum):
    """Available strategy types"""
    # Classic MA strategies
    MA_CROSSOVER = "ma_crossover"
    GOLDEN_CROSS = "golden_cross"

    # Phase 1: Signal strategies
    RSI_30_70 = "rsi_30_70"
    RSI_20_80 = "rsi_20_80"
    MACD_STANDARD = "macd_standard"
    BB_STANDARD = "bb_standard"

    # Phase 2: ADX strategies
    ADX_25 = "adx_25"
    ADX_30 = "adx_30"
    ADX_20 = "adx_20"

    # Phase 2: Stochastic strategies
    STOCHASTIC_14_3 = "stochastic_14_3"
    STOCHASTIC_SLOW = "stochastic_slow"
    STOCHASTIC_FAST = "stochastic_fast"

    # Phase 2: Donchian strategies
    DONCHIAN_20_10 = "donchian_20_10"
    DONCHIAN_50_25 = "donchian_50_25"
    DONCHIAN_10_5 = "donchian_10_5"

    # Legacy
    RSI = "rsi"
    MACD = "macd"
    CUSTOM = "custom"


# ============================================================================
# Data/Market Endpoints
# ============================================================================

class StockInfo(BaseModel):
    """Stock company information"""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None


class StockSearchResult(BaseModel):
    """Stock search result item"""
    symbol: str
    name: str
    exchange: Optional[str] = None


class OHLCVData(BaseModel):
    """OHLCV price data for a single time period"""
    date: str  # ISO format date string
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockDataResponse(BaseModel):
    """Response for stock OHLCV data"""
    symbol: str
    data: List[OHLCVData]
    start_date: str
    end_date: str
    interval: str


class StockDataRequest(BaseModel):
    """Request to fetch stock data"""
    symbol: str = Field(..., description="Stock ticker symbol")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    interval: IntervalEnum = Field(default=IntervalEnum.ONE_DAY, description="Data interval")

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper()


# ============================================================================
# Strategy Endpoints
# ============================================================================

class StrategyParameter(BaseModel):
    """A single strategy parameter"""
    name: str
    value: Any
    type: str  # "int", "float", "str", "bool"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: Optional[str] = None


class StrategyConfig(BaseModel):
    """Strategy configuration"""
    name: str
    type: StrategyType
    parameters: Dict[str, Any]
    description: Optional[str] = None


class StrategyInfo(BaseModel):
    """Strategy information for listing"""
    id: str
    name: str
    type: StrategyType
    description: str
    parameters: List[StrategyParameter]
    default_params: Dict[str, Any]


class StrategyListResponse(BaseModel):
    """Response for listing strategies"""
    strategies: List[StrategyInfo]


# ============================================================================
# Backtest Endpoints
# ============================================================================

class BacktestRequest(BaseModel):
    """Request to run a backtest"""
    symbol: str = Field(..., description="Stock ticker symbol")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    strategy: StrategyConfig = Field(..., description="Strategy configuration")
    initial_capital: float = Field(default=100000.0, description="Starting capital")
    commission: float = Field(default=0.001, description="Commission rate (0.001 = 0.1%)")

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper()

    @validator('initial_capital')
    def capital_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Initial capital must be positive')
        return v


class TradeSignal(BaseModel):
    """A single trade signal"""
    date: str
    signal_type: SignalType
    price: float
    shares: Optional[float] = None
    position_value: Optional[float] = None
    reason: Optional[str] = None


class Trade(BaseModel):
    """A completed trade"""
    entry_date: str
    exit_date: Optional[str] = None
    entry_price: float
    exit_price: Optional[float] = None
    shares: float
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    duration_days: Optional[int] = None


class PerformanceMetrics(BaseModel):
    """Performance metrics for a backtest"""
    # Returns
    total_return: float
    total_return_pct: float
    cagr: float

    # Risk metrics
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    volatility: float

    # Trading metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    avg_trade: float
    largest_win: float
    largest_loss: float

    # Time metrics
    avg_holding_period: Optional[float] = None

    # Other
    expectancy: float

    # Buy and hold comparison
    buy_hold_return: Optional[float] = None
    risk_free_rate: float = 0.02


class EquityPoint(BaseModel):
    """A single point in the equity curve"""
    date: str
    portfolio_value: float
    cash: float
    position_value: float
    drawdown: float
    drawdown_pct: float


class BacktestResults(BaseModel):
    """Complete backtest results"""
    backtest_id: str
    symbol: str
    strategy: StrategyConfig
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float

    # Core results
    metrics: PerformanceMetrics
    signals: List[TradeSignal]
    trades: List[Trade]
    equity_curve: List[EquityPoint]

    # Metadata
    created_at: str
    status: str  # "completed", "running", "failed"
    error_message: Optional[str] = None


class BacktestStatusResponse(BaseModel):
    """Response for backtest status check"""
    backtest_id: str
    status: str
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None


# ============================================================================
# Strategy Comparison
# ============================================================================

class CompareStrategiesRequest(BaseModel):
    """Request to compare multiple strategies"""
    symbol: str
    start_date: str
    end_date: str
    strategies: List[StrategyConfig]
    initial_capital: float = 100000.0
    commission: float = 0.001


class StrategyComparisonResult(BaseModel):
    """Results for one strategy in comparison"""
    strategy: StrategyConfig
    metrics: PerformanceMetrics
    final_value: float


class CompareStrategiesResponse(BaseModel):
    """Response for strategy comparison"""
    symbol: str
    start_date: str
    end_date: str
    results: List[StrategyComparisonResult]
    best_strategy: str  # Strategy name with highest Sharpe ratio


# ============================================================================
# Batch Backtesting (Multi-Stock Multi-Strategy)
# ============================================================================

class BatchBacktestItem(BaseModel):
    """Single backtest configuration in a batch"""
    symbol: str
    strategy: StrategyConfig

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper()


class BatchBacktestRequest(BaseModel):
    """Request to run multiple backtests in parallel"""
    items: List[BatchBacktestItem] = Field(..., description="List of stock-strategy pairs to backtest")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(default=100000.0, description="Starting capital for each backtest")
    commission: float = Field(default=0.001, description="Commission rate (0.001 = 0.1%)")

    @validator('initial_capital')
    def capital_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Initial capital must be positive')
        return v


class BacktestSummary(BaseModel):
    """Compact backtest summary for matrix display"""
    backtest_id: str
    symbol: str
    strategy_name: str
    status: str  # "completed", "running", "failed"

    # Key metrics only (for matrix display)
    total_return_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    total_trades: Optional[int] = None
    win_rate: Optional[float] = None

    # Error info
    error_message: Optional[str] = None


class BatchBacktestResponse(BaseModel):
    """Response for batch backtest request"""
    batch_id: str
    total_items: int
    summaries: List[BacktestSummary]
    created_at: str


# ============================================================================
# Chart Data
# ============================================================================

class ChartDataPoint(BaseModel):
    """A single candlestick/OHLCV data point for charts"""
    time: int  # Unix timestamp (required by TradingView Lightweight Charts)
    open: float
    high: float
    low: float
    close: float
    volume: int


class SignalMarker(BaseModel):
    """A signal marker for the chart"""
    time: int  # Unix timestamp
    position: str  # "aboveBar" or "belowBar"
    color: str  # Hex color
    shape: str  # "arrowUp" or "arrowDown"
    text: str  # "BUY" or "SELL"


class ChartDataResponse(BaseModel):
    """Chart-ready data for TradingView"""
    symbol: str
    candlesticks: List[ChartDataPoint]
    signals: List[SignalMarker]
    moving_averages: Optional[Dict[str, List[Dict[str, Any]]]] = None  # e.g., {"MA20": [{time, value}]}


# ============================================================================
# Error Responses
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
