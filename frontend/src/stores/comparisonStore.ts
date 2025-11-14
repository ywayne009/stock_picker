/**
 * Zustand store for V2 Comparison Matrix Dashboard
 */
import { create } from 'zustand';
import type {
  ComparisonMatrix,
  MatrixCell,
  StrategyConfig,
  BacktestSummary,
  BatchBacktestRequest,
  StrategyInfo,
} from '../types/comparison';
import type { BacktestResults } from '../types';
import apiClient, { backtestAPI } from '../api/client';

interface ComparisonStore extends ComparisonMatrix {
  // Actions
  addSymbol: (symbol: string) => void;
  removeSymbol: (symbol: string) => void;
  addStrategy: (strategy: StrategyConfig) => void;
  removeStrategy: (strategyName: string) => void;
  setDateRange: (startDate: string, endDate: string) => void;
  setCapital: (capital: number) => void;
  setCommission: (commission: number) => void;
  runCell: (symbol: string, strategyName: string) => Promise<void>;
  runAllCells: () => Promise<void>;
  clearMatrix: () => void;
  getCell: (symbol: string, strategyName: string) => MatrixCell | undefined;

  // Strategy management
  availableStrategies: StrategyInfo[];
  loadAvailableStrategies: () => Promise<void>;

  // Selected cell for detailed view
  selectedCell: MatrixCell | null;
  selectedCellFullResults: BacktestResults | null;
  selectedCellLoading: boolean;
  selectCell: (symbol: string, strategyName: string) => Promise<void>;
  clearSelection: () => void;

  // Tuning cell for parameter adjustment
  tuningCell: MatrixCell | null;
  openTuning: (symbol: string, strategyName: string) => void;
  closeTuning: () => void;
  updateCellParameters: (symbol: string, strategyName: string, parameters: Record<string, any>) => Promise<void>;

  // Batch progress tracking
  batchProgress: {
    isRunning: boolean;
    completed: number;
    total: number;
  };

  // Cached backtest results (keyed by backtest_id)
  cachedResults: Map<string, BacktestResults>;

  // Export functions
  exportToCSV: () => void;

  // Save/Load configurations
  saveConfiguration: (name: string) => void;
  loadConfiguration: (name: string) => void;
  getSavedConfigurations: () => string[];
  deleteConfiguration: (name: string) => void;
}

const getCellKey = (symbol: string, strategyName: string) => `${symbol}-${strategyName}`;

// Default date range (last 2 years for better Golden Cross signals)
const getDefaultDateRange = () => {
  const end = new Date();
  const start = new Date();
  start.setFullYear(start.getFullYear() - 2);

  return {
    startDate: start.toISOString().split('T')[0],
    endDate: end.toISOString().split('T')[0],
  };
};

export const useComparisonStore = create<ComparisonStore>((set, get) => ({
  // Initial state
  symbols: ['AAPL', 'MSFT', 'GOOGL'],
  strategies: [],
  cells: new Map(),
  ...getDefaultDateRange(),
  initialCapital: 100000,
  commission: 0.001,
  availableStrategies: [],
  selectedCell: null,
  selectedCellFullResults: null,
  selectedCellLoading: false,
  tuningCell: null,
  batchProgress: {
    isRunning: false,
    completed: 0,
    total: 0,
  },
  cachedResults: new Map(),

  // Load available strategies from API
  loadAvailableStrategies: async () => {
    try {
      const response = await apiClient.get('/strategies/');
      set({ availableStrategies: response.data.strategies });

      // Auto-select first 3 strategies
      const firstThree = response.data.strategies.slice(0, 3).map((s: StrategyInfo) => ({
        name: s.name,
        type: s.type,
        parameters: s.default_params,
        description: s.description,
      }));

      set({ strategies: firstThree });
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  },

  // Symbol management
  addSymbol: (symbol: string) => {
    const upperSymbol = symbol.toUpperCase();
    const { symbols, strategies, cells } = get();

    if (symbols.includes(upperSymbol)) return;

    // Create cells for this symbol with all strategies
    const newCells = new Map(cells);
    strategies.forEach(strategy => {
      const key = getCellKey(upperSymbol, strategy.name);
      newCells.set(key, {
        symbol: upperSymbol,
        strategy,
        isLoading: false,
      });
    });

    set({ symbols: [...symbols, upperSymbol], cells: newCells });
  },

  removeSymbol: (symbol: string) => {
    const { symbols, strategies, cells } = get();

    // Remove cells for this symbol
    const newCells = new Map(cells);
    strategies.forEach(strategy => {
      const key = getCellKey(symbol, strategy.name);
      newCells.delete(key);
    });

    set({
      symbols: symbols.filter(s => s !== symbol),
      cells: newCells,
    });
  },

  // Strategy management
  addStrategy: (strategy: StrategyConfig) => {
    const { strategies, symbols, cells } = get();

    if (strategies.some(s => s.name === strategy.name)) return;

    // Create cells for this strategy with all symbols
    const newCells = new Map(cells);
    symbols.forEach(symbol => {
      const key = getCellKey(symbol, strategy.name);
      newCells.set(key, {
        symbol,
        strategy,
        isLoading: false,
      });
    });

    set({ strategies: [...strategies, strategy], cells: newCells });
  },

  removeStrategy: (strategyName: string) => {
    const { strategies, symbols, cells } = get();

    // Remove cells for this strategy
    const newCells = new Map(cells);
    symbols.forEach(symbol => {
      const key = getCellKey(symbol, strategyName);
      newCells.delete(key);
    });

    set({
      strategies: strategies.filter(s => s.name !== strategyName),
      cells: newCells,
    });
  },

  // Configuration
  setDateRange: (startDate: string, endDate: string) => {
    set({ startDate, endDate });
  },

  setCapital: (capital: number) => {
    set({ initialCapital: capital });
  },

  setCommission: (commission: number) => {
    set({ commission });
  },

  // Run single cell backtest
  runCell: async (symbol: string, strategyName: string) => {
    const { cells, startDate, endDate, initialCapital, commission } = get();
    const key = getCellKey(symbol, strategyName);
    const cell = cells.get(key);

    if (!cell) return;

    // Set loading state
    const newCells = new Map(cells);
    newCells.set(key, { ...cell, isLoading: true, error: undefined });
    set({ cells: newCells });

    try {
      const request: BatchBacktestRequest = {
        items: [{ symbol, strategy: cell.strategy }],
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        commission,
      };

      const response = await backtestAPI.runBatchBacktest(request);
      const summary = response.summaries[0];

      // Update cell with results
      const updatedCells = new Map(get().cells);
      updatedCells.set(key, {
        ...cell,
        summary,
        isLoading: false,
        error: summary.status === 'failed' ? summary.error_message : undefined,
      });
      set({ cells: updatedCells });

    } catch (error: any) {
      const updatedCells = new Map(get().cells);
      updatedCells.set(key, {
        ...cell,
        isLoading: false,
        error: error.message || 'Failed to run backtest',
      });
      set({ cells: updatedCells });
    }
  },

  // Run all cells in batch (with progress tracking)
  runAllCells: async () => {
    const { symbols, strategies, cells, startDate, endDate, initialCapital, commission } = get();

    // Calculate total number of backtests
    const totalBacktests = symbols.length * strategies.length;

    // Initialize progress tracking
    set({
      batchProgress: {
        isRunning: true,
        completed: 0,
        total: totalBacktests,
      }
    });

    // Set all cells to loading
    const loadingCells = new Map(cells);
    symbols.forEach(symbol => {
      strategies.forEach(strategy => {
        const key = getCellKey(symbol, strategy.name);
        const cell = loadingCells.get(key);
        if (cell) {
          loadingCells.set(key, { ...cell, isLoading: true, error: undefined });
        }
      });
    });
    set({ cells: loadingCells });

    try {
      // Run backtests one by one for real-time progress updates
      let completed = 0;

      for (const symbol of symbols) {
        for (const strategy of strategies) {
          const key = getCellKey(symbol, strategy.name);
          const cell = get().cells.get(key);

          if (!cell) continue;

          try {
            // Run single backtest
            const request: BatchBacktestRequest = {
              items: [{ symbol, strategy }],
              start_date: startDate,
              end_date: endDate,
              initial_capital: initialCapital,
              commission,
            };

            const response = await backtestAPI.runBatchBacktest(request);
            const summary = response.summaries[0];

            // Update this cell
            const updatedCells = new Map(get().cells);
            updatedCells.set(key, {
              ...cell,
              summary,
              isLoading: false,
              error: summary.status === 'failed' ? summary.error_message : undefined,
            });
            set({ cells: updatedCells });

          } catch (error: any) {
            // Update this cell with error
            const updatedCells = new Map(get().cells);
            updatedCells.set(key, {
              ...cell,
              isLoading: false,
              error: error.message || 'Failed to run backtest',
            });
            set({ cells: updatedCells });
          }

          // Update progress
          completed++;
          set({
            batchProgress: {
              isRunning: true,
              completed,
              total: totalBacktests,
            }
          });
        }
      }

      // Complete progress tracking
      set({
        batchProgress: {
          isRunning: false,
          completed: totalBacktests,
          total: totalBacktests,
        }
      });

    } catch (error: any) {
      // Set all cells to error state and stop progress
      const errorCells = new Map(get().cells);
      symbols.forEach(symbol => {
        strategies.forEach(strategy => {
          const key = getCellKey(symbol, strategy.name);
          const cell = errorCells.get(key);
          if (cell) {
            errorCells.set(key, {
              ...cell,
              isLoading: false,
              error: error.message || 'Failed to run backtest',
            });
          }
        });
      });
      set({
        cells: errorCells,
        batchProgress: {
          isRunning: false,
          completed: 0,
          total: totalBacktests,
        }
      });
    }
  },

  // Clear all results
  clearMatrix: () => {
    const { symbols, strategies } = get();
    const clearedCells = new Map<string, MatrixCell>();

    symbols.forEach(symbol => {
      strategies.forEach(strategy => {
        const key = getCellKey(symbol, strategy.name);
        clearedCells.set(key, {
          symbol,
          strategy,
          isLoading: false,
        });
      });
    });

    set({ cells: clearedCells, selectedCell: null });
  },

  // Get cell by coordinates
  getCell: (symbol: string, strategyName: string) => {
    const { cells } = get();
    return cells.get(getCellKey(symbol, strategyName));
  },

  // Selection for detailed view (with caching)
  selectCell: async (symbol: string, strategyName: string) => {
    const cell = get().getCell(symbol, strategyName);
    if (!cell || cell.summary?.status !== 'completed') return;

    const backtestId = cell.summary.backtest_id;
    const cachedResults = get().cachedResults;

    // Check cache first
    if (cachedResults.has(backtestId)) {
      const fullResults = cachedResults.get(backtestId)!;
      set({
        selectedCell: cell,
        selectedCellFullResults: fullResults,
        selectedCellLoading: false
      });
      return;
    }

    // Not in cache, fetch from API
    set({ selectedCell: cell, selectedCellLoading: true, selectedCellFullResults: null });

    try {
      const fullResults = await backtestAPI.getResults(backtestId);

      // Store in cache
      const updatedCache = new Map(cachedResults);
      updatedCache.set(backtestId, fullResults);

      set({
        selectedCellFullResults: fullResults,
        selectedCellLoading: false,
        cachedResults: updatedCache
      });
    } catch (error: any) {
      console.error('Failed to fetch full results:', error);
      set({ selectedCellLoading: false });
    }
  },

  clearSelection: () => {
    set({ selectedCell: null, selectedCellFullResults: null, selectedCellLoading: false });
  },

  // Tuning for parameter adjustment
  openTuning: (symbol: string, strategyName: string) => {
    const cell = get().getCell(symbol, strategyName);
    if (cell) {
      set({ tuningCell: cell });
    }
  },

  closeTuning: () => {
    set({ tuningCell: null });
  },

  updateCellParameters: async (symbol: string, strategyName: string, parameters: Record<string, any>) => {
    const { cells, startDate, endDate, initialCapital, commission } = get();
    const key = getCellKey(symbol, strategyName);
    const cell = cells.get(key);

    if (!cell) return;

    // Update cell strategy with new parameters
    const updatedStrategy = { ...cell.strategy, parameters };

    // Set loading state
    const newCells = new Map(cells);
    newCells.set(key, { ...cell, strategy: updatedStrategy, isLoading: true, error: undefined });
    set({ cells: newCells });

    try {
      const request: BatchBacktestRequest = {
        items: [{ symbol, strategy: updatedStrategy }],
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        commission,
      };

      const response = await backtestAPI.runBatchBacktest(request);
      const summary = response.summaries[0];

      // Update cell with results
      const updatedCells = new Map(get().cells);
      updatedCells.set(key, {
        ...cell,
        strategy: updatedStrategy,
        summary,
        isLoading: false,
        error: summary.status === 'failed' ? summary.error_message : undefined,
      });
      set({ cells: updatedCells });

    } catch (error: any) {
      const updatedCells = new Map(get().cells);
      updatedCells.set(key, {
        ...cell,
        strategy: updatedStrategy,
        isLoading: false,
        error: error.message || 'Failed to run backtest',
      });
      set({ cells: updatedCells });
    }
  },

  // Export matrix to CSV
  exportToCSV: () => {
    const { symbols, strategies, cells, startDate, endDate } = get();

    // Build CSV header
    const headers = [
      'Symbol',
      'Strategy',
      'Total Return %',
      'Sharpe Ratio',
      'Sortino Ratio',
      'Max Drawdown %',
      'Win Rate %',
      'Total Trades',
      'Profit Factor',
      'CAGR %',
      'Volatility %',
      'Expectancy',
      'Status'
    ];

    // Build CSV rows
    const rows: string[][] = [];
    symbols.forEach(symbol => {
      strategies.forEach(strategy => {
        const key = getCellKey(symbol, strategy.name);
        const cell = cells.get(key);

        if (cell && cell.summary) {
          const s = cell.summary;
          rows.push([
            symbol,
            strategy.name,
            s.total_return_pct !== undefined ? (s.total_return_pct * 100).toFixed(2) : 'N/A',
            s.sharpe_ratio !== undefined ? s.sharpe_ratio.toFixed(2) : 'N/A',
            s.sortino_ratio !== undefined ? s.sortino_ratio.toFixed(2) : 'N/A',
            s.max_drawdown_pct !== undefined ? (s.max_drawdown_pct * 100).toFixed(2) : 'N/A',
            s.win_rate !== undefined ? (s.win_rate * 100).toFixed(2) : 'N/A',
            s.total_trades !== undefined ? s.total_trades.toString() : 'N/A',
            s.profit_factor !== undefined ? s.profit_factor.toFixed(2) : 'N/A',
            s.cagr !== undefined ? (s.cagr * 100).toFixed(2) : 'N/A',
            s.volatility !== undefined ? (s.volatility * 100).toFixed(2) : 'N/A',
            s.expectancy !== undefined ? s.expectancy.toFixed(2) : 'N/A',
            s.status || 'N/A'
          ]);
        } else {
          // Empty cell
          rows.push([
            symbol,
            strategy.name,
            ...Array(11).fill('Not Run')
          ]);
        }
      });
    });

    // Convert to CSV string
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `backtest_comparison_${startDate}_to_${endDate}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  // Save current configuration to localStorage
  saveConfiguration: (name: string) => {
    const { symbols, strategies, startDate, endDate, initialCapital, commission } = get();

    const config = {
      symbols,
      strategies,
      startDate,
      endDate,
      initialCapital,
      commission,
      savedAt: new Date().toISOString(),
    };

    const savedConfigs = JSON.parse(localStorage.getItem('backtestConfigurations') || '{}');
    savedConfigs[name] = config;
    localStorage.setItem('backtestConfigurations', JSON.stringify(savedConfigs));
  },

  // Load configuration from localStorage
  loadConfiguration: (name: string) => {
    const savedConfigs = JSON.parse(localStorage.getItem('backtestConfigurations') || '{}');
    const config = savedConfigs[name];

    if (!config) {
      console.error(`Configuration "${name}" not found`);
      return;
    }

    // Clear existing cells and load new configuration
    set({
      symbols: config.symbols,
      strategies: config.strategies,
      startDate: config.startDate,
      endDate: config.endDate,
      initialCapital: config.initialCapital,
      commission: config.commission,
      cells: new Map(),
    });

    // Recreate cells for new configuration
    const newCells = new Map<string, MatrixCell>();
    config.symbols.forEach((symbol: string) => {
      config.strategies.forEach((strategy: StrategyConfig) => {
        const key = getCellKey(symbol, strategy.name);
        newCells.set(key, {
          symbol,
          strategy,
          summary: null,
          isLoading: false,
          error: undefined,
        });
      });
    });

    set({ cells: newCells });
  },

  // Get list of saved configuration names
  getSavedConfigurations: () => {
    const savedConfigs = JSON.parse(localStorage.getItem('backtestConfigurations') || '{}');
    return Object.keys(savedConfigs);
  },

  // Delete a saved configuration
  deleteConfiguration: (name: string) => {
    const savedConfigs = JSON.parse(localStorage.getItem('backtestConfigurations') || '{}');
    delete savedConfigs[name];
    localStorage.setItem('backtestConfigurations', JSON.stringify(savedConfigs));
  },
}));
