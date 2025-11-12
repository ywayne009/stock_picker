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
import apiClient from '../api/client';

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
  selectCell: (symbol: string, strategyName: string) => void;
  clearSelection: () => void;

  // Tuning cell for parameter adjustment
  tuningCell: MatrixCell | null;
  openTuning: (symbol: string, strategyName: string) => void;
  closeTuning: () => void;
  updateCellParameters: (symbol: string, strategyName: string, parameters: Record<string, any>) => Promise<void>;
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
  tuningCell: null,

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

      const response = await apiClient.post('/backtest/batch', request);
      const summary = response.data.summaries[0];

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

  // Run all cells in batch
  runAllCells: async () => {
    const { symbols, strategies, cells, startDate, endDate, initialCapital, commission } = get();

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
      // Build batch request
      const items = symbols.flatMap(symbol =>
        strategies.map(strategy => ({ symbol, strategy }))
      );

      const request: BatchBacktestRequest = {
        items,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        commission,
      };

      const response = await apiClient.post('/backtest/batch', request);
      const summaries: BacktestSummary[] = response.data.summaries;

      // Update all cells with results
      const updatedCells = new Map(get().cells);
      summaries.forEach(summary => {
        const key = getCellKey(summary.symbol, summary.strategy_name);
        const cell = updatedCells.get(key);
        if (cell) {
          updatedCells.set(key, {
            ...cell,
            summary,
            isLoading: false,
            error: summary.status === 'failed' ? summary.error_message : undefined,
          });
        }
      });
      set({ cells: updatedCells });

    } catch (error: any) {
      // Set all cells to error state
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
      set({ cells: errorCells });
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

  // Selection for detailed view
  selectCell: (symbol: string, strategyName: string) => {
    const cell = get().getCell(symbol, strategyName);
    if (cell && cell.summary?.status === 'completed') {
      set({ selectedCell: cell });
    }
  },

  clearSelection: () => {
    set({ selectedCell: null });
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

      const response = await apiClient.post('/backtest/batch', request);
      const summary = response.data.summaries[0];

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
}));
