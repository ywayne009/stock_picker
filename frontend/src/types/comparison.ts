/**
 * Types for V2 Comparison Matrix Dashboard
 */

export interface BatchBacktestItem {
  symbol: string;
  strategy: StrategyConfig;
}

export interface BatchBacktestRequest {
  items: BatchBacktestItem[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission: number;
}

export interface BacktestSummary {
  backtest_id: string;
  symbol: string;
  strategy_name: string;
  status: 'completed' | 'running' | 'failed';

  // Key metrics
  total_return_pct?: number;
  sharpe_ratio?: number;
  max_drawdown_pct?: number;
  total_trades?: number;
  win_rate?: number;

  // Error info
  error_message?: string;
}

export interface BatchBacktestResponse {
  batch_id: string;
  total_items: number;
  summaries: BacktestSummary[];
  created_at: string;
}

export interface StrategyConfig {
  name: string;
  type: string;
  parameters: Record<string, any>;
  description?: string;
}

// Matrix cell data structure
export interface MatrixCell {
  symbol: string;
  strategy: StrategyConfig;
  summary?: BacktestSummary;
  isLoading: boolean;
  error?: string;
}

// Comparison matrix state
export interface ComparisonMatrix {
  symbols: string[];
  strategies: StrategyConfig[];
  cells: Map<string, MatrixCell>; // key: `${symbol}-${strategy.name}`
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
}

// For strategy parameter tuning
export interface StrategyParameter {
  name: string;
  value: any;
  type: 'int' | 'float' | 'str' | 'bool';
  min_value?: number;
  max_value?: number;
  description?: string;
}

export interface StrategyInfo {
  id: string;
  name: string;
  type: string;
  description: string;
  parameters: StrategyParameter[];
  default_params: Record<string, any>;
}
