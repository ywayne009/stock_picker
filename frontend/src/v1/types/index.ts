// API Types matching backend schemas

export interface StockInfo {
  symbol: string;
  name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  description?: string;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange?: string;
}

export interface OHLCVData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StrategyParameter {
  name: string;
  value: any;
  type: string;
  min_value?: number;
  max_value?: number;
  description?: string;
}

export interface StrategyConfig {
  name: string;
  type: string;
  parameters: Record<string, any>;
}

export interface StrategyInfo {
  id: string;
  name: string;
  type: string;
  description: string;
  parameters: StrategyParameter[];
  default_params: Record<string, any>;
}

export interface PerformanceMetrics {
  total_return: number;
  total_return_pct: number;
  cagr: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  volatility: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
  avg_trade: number;
  largest_win: number;
  largest_loss: number;
  avg_holding_period?: number;
  expectancy: number;
  risk_free_rate: number;
}

export interface Trade {
  entry_date: string;
  exit_date?: string;
  entry_price: number;
  exit_price?: number;
  shares: number;
  profit_loss?: number;
  profit_loss_pct?: number;
  duration_days?: number;
}

export interface TradeSignal {
  date: string;
  signal_type: 'BUY' | 'SELL' | 'HOLD';
  price: number;
  shares?: number;
  position_value?: number;
  reason?: string;
}

export interface EquityPoint {
  date: string;
  portfolio_value: number;
  cash: number;
  position_value: number;
  drawdown: number;
  drawdown_pct: number;
}

export interface BacktestRequest {
  symbol: string;
  start_date: string;
  end_date: string;
  strategy: StrategyConfig;
  initial_capital: number;
  commission: number;
}

export interface BacktestResults {
  backtest_id: string;
  symbol: string;
  strategy: StrategyConfig;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_value: number;
  metrics: PerformanceMetrics;
  signals: TradeSignal[];
  trades: Trade[];
  equity_curve: EquityPoint[];
  created_at: string;
  status: string;
  error_message?: string;
}

export interface BacktestStatus {
  backtest_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
}

// Chart data types for TradingView
export interface CandlestickData {
  time: number;  // Unix timestamp
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface VolumeData {
  time: number;
  value: number;
  color?: string;
}

export interface LineData {
  time: number;
  value: number;
}
