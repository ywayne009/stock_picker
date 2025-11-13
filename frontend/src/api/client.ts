import axios from 'axios';
import type {
  StockInfo,
  StockSearchResult,
  OHLCVData,
  StrategyInfo,
  BacktestRequest,
  BacktestResults,
  BacktestStatus,
  PerformanceMetrics,
  Trade,
} from '../types';
import type {
  BatchBacktestRequest,
  BatchBacktestResponse,
  BacktestSummary,
} from '../types/comparison';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for backtests
});

// Data endpoints
export const dataAPI = {
  searchStocks: async (query: string): Promise<StockSearchResult[]> => {
    const response = await apiClient.get(`/data/stocks/search`, {
      params: { q: query },
    });
    return response.data;
  },

  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    const response = await apiClient.get(`/data/stocks/${symbol}/info`);
    return response.data;
  },

  getOHLCV: async (
    symbol: string,
    startDate: string,
    endDate: string,
    interval: string = '1d'
  ): Promise<{ symbol: string; data: OHLCVData[] }> => {
    const response = await apiClient.get(`/data/stocks/${symbol}/ohlcv`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        interval,
      },
    });
    return response.data;
  },

  getPopularStocks: async (): Promise<Record<string, string[]>> => {
    const response = await apiClient.get('/data/popular');
    return response.data;
  },
};

// Strategy endpoints
export const strategyAPI = {
  listStrategies: async (): Promise<StrategyInfo[]> => {
    const response = await apiClient.get('/strategies/');
    return response.data.strategies;
  },

  getStrategy: async (strategyId: string): Promise<StrategyInfo> => {
    const response = await apiClient.get(`/strategies/${strategyId}`);
    return response.data;
  },

  getStrategyCategories: async (): Promise<Record<string, string[]>> => {
    const response = await apiClient.get('/strategies/categories/list');
    return response.data;
  },
};

// Backtest endpoints
export const backtestAPI = {
  runBacktest: async (request: BacktestRequest): Promise<BacktestStatus> => {
    const response = await apiClient.post('/backtest/run', request);
    return response.data;
  },

  getStatus: async (backtestId: string): Promise<BacktestStatus> => {
    const response = await apiClient.get(`/backtest/${backtestId}/status`);
    return response.data;
  },

  getResults: async (backtestId: string): Promise<BacktestResults> => {
    const response = await apiClient.get(`/backtest/${backtestId}/results`);
    return response.data;
  },

  getMetrics: async (backtestId: string): Promise<PerformanceMetrics> => {
    const response = await apiClient.get(`/backtest/${backtestId}/metrics`);
    return response.data;
  },

  getTrades: async (backtestId: string): Promise<Trade[]> => {
    const response = await apiClient.get(`/backtest/${backtestId}/trades`);
    return response.data;
  },

  deleteBacktest: async (backtestId: string): Promise<void> => {
    await apiClient.delete(`/backtest/${backtestId}`);
  },

  listBacktests: async (): Promise<any> => {
    const response = await apiClient.get('/backtest/list/all');
    return response.data;
  },

  // Batch backtest for V2 dashboard
  runBatchBacktest: async (request: BatchBacktestRequest): Promise<BatchBacktestResponse> => {
    const response = await apiClient.post('/backtest/batch', request);
    return response.data;
  },

  getSummary: async (backtestId: string): Promise<BacktestSummary> => {
    const response = await apiClient.get(`/backtest/${backtestId}/summary`);
    return response.data;
  },
};

export default apiClient;
