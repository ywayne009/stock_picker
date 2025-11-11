import { create } from 'zustand';
import type {
  StrategyInfo,
  BacktestResults,
  BacktestRequest,
  OHLCVData,
} from '../types';
import { backtestAPI, strategyAPI } from '../api/client';

interface BacktestState {
  // Available strategies
  strategies: StrategyInfo[];
  selectedStrategy: StrategyInfo | null;

  // Stock data
  symbol: string;
  startDate: string;
  endDate: string;
  stockData: OHLCVData[] | null;

  // Backtest configuration
  initialCapital: number;
  commission: number;
  customParameters: Record<string, any>;

  // Backtest results
  backtestResults: BacktestResults | null;
  backtestId: string | null;

  // UI state
  isLoading: boolean;
  isLoadingStrategies: boolean;
  error: string | null;

  // Actions
  loadStrategies: () => Promise<void>;
  selectStrategy: (strategyId: string) => void;
  setSymbol: (symbol: string) => void;
  setDateRange: (startDate: string, endDate: string) => void;
  setInitialCapital: (capital: number) => void;
  setCommission: (commission: number) => void;
  updateParameter: (paramName: string, value: any) => void;
  runBacktest: () => Promise<void>;
  clearResults: () => void;
  reset: () => void;
}

// Default date range: last 1 year
const getDefaultDates = () => {
  const end = new Date();
  const start = new Date();
  start.setFullYear(start.getFullYear() - 1);

  return {
    startDate: start.toISOString().split('T')[0],
    endDate: end.toISOString().split('T')[0],
  };
};

const { startDate: defaultStart, endDate: defaultEnd } = getDefaultDates();

export const useBacktestStore = create<BacktestState>((set, get) => ({
  // Initial state
  strategies: [],
  selectedStrategy: null,
  symbol: 'AAPL',
  startDate: defaultStart,
  endDate: defaultEnd,
  stockData: null,
  initialCapital: 100000,
  commission: 0.001,
  customParameters: {},
  backtestResults: null,
  backtestId: null,
  isLoading: false,
  isLoadingStrategies: false,
  error: null,

  // Load available strategies from API
  loadStrategies: async () => {
    set({ isLoadingStrategies: true, error: null });
    try {
      const strategies = await strategyAPI.listStrategies();
      set({
        strategies,
        isLoadingStrategies: false,
        // Auto-select first strategy if none selected
        selectedStrategy: strategies.length > 0 ? strategies[0] : null,
        customParameters: strategies.length > 0 ? strategies[0].default_params : {},
      });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to load strategies',
        isLoadingStrategies: false,
      });
    }
  },

  // Select a strategy
  selectStrategy: (strategyId: string) => {
    const { strategies } = get();
    const strategy = strategies.find(s => s.id === strategyId);

    if (strategy) {
      set({
        selectedStrategy: strategy,
        customParameters: { ...strategy.default_params },
      });
    }
  },

  // Set stock symbol
  setSymbol: (symbol: string) => {
    set({ symbol: symbol.toUpperCase() });
  },

  // Set date range
  setDateRange: (startDate: string, endDate: string) => {
    set({ startDate, endDate });
  },

  // Set initial capital
  setInitialCapital: (capital: number) => {
    set({ initialCapital: capital });
  },

  // Set commission
  setCommission: (commission: number) => {
    set({ commission });
  },

  // Update a strategy parameter
  updateParameter: (paramName: string, value: any) => {
    const { customParameters } = get();
    set({
      customParameters: {
        ...customParameters,
        [paramName]: value,
      },
    });
  },

  // Run backtest
  runBacktest: async () => {
    const {
      symbol,
      startDate,
      endDate,
      selectedStrategy,
      initialCapital,
      commission,
      customParameters,
    } = get();

    // Validation
    if (!selectedStrategy) {
      set({ error: 'Please select a strategy' });
      return;
    }

    if (!symbol) {
      set({ error: 'Please enter a stock symbol' });
      return;
    }

    set({ isLoading: true, error: null, backtestResults: null });

    try {
      // Prepare backtest request
      const request: BacktestRequest = {
        symbol,
        start_date: startDate,
        end_date: endDate,
        strategy: {
          name: selectedStrategy.name,
          type: selectedStrategy.type,
          parameters: customParameters,
        },
        initial_capital: initialCapital,
        commission,
      };

      // Run backtest
      const statusResponse = await backtestAPI.runBacktest(request);

      if (statusResponse.status === 'failed') {
        throw new Error(statusResponse.message || 'Backtest failed');
      }

      // Get results
      const results = await backtestAPI.getResults(statusResponse.backtest_id);

      set({
        backtestResults: results,
        backtestId: statusResponse.backtest_id,
        isLoading: false,
        error: null,
      });

    } catch (error: any) {
      console.error('Backtest error:', error);
      set({
        error: error.response?.data?.detail || error.message || 'Failed to run backtest',
        isLoading: false,
      });
    }
  },

  // Clear results
  clearResults: () => {
    set({
      backtestResults: null,
      backtestId: null,
      error: null,
    });
  },

  // Reset to initial state
  reset: () => {
    const { startDate, endDate } = getDefaultDates();
    const { strategies } = get();

    set({
      selectedStrategy: strategies.length > 0 ? strategies[0] : null,
      symbol: 'AAPL',
      startDate,
      endDate,
      stockData: null,
      initialCapital: 100000,
      commission: 0.001,
      customParameters: strategies.length > 0 ? strategies[0].default_params : {},
      backtestResults: null,
      backtestId: null,
      isLoading: false,
      error: null,
    });
  },
}));
