export interface BacktestConfig {
  strategyId: number;
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
}

export interface BacktestResult {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  metrics: {
    totalReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
  };
  equityCurve: Array<{ date: string; value: number }>;
  trades: Array<Trade>;
}

export interface Trade {
  date: string;
  action: 'buy' | 'sell';
  price: number;
  quantity: number;
  pnl?: number;
}
