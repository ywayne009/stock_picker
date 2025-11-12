import React, { useEffect } from 'react';
import { useBacktestStore } from '../../stores/backtestStore';
import { Play, RefreshCw, Settings } from 'lucide-react';

export const BacktestConfigPanel: React.FC = () => {
  const {
    strategies,
    selectedStrategy,
    symbol,
    startDate,
    endDate,
    initialCapital,
    commission,
    customParameters,
    isLoading,
    isLoadingStrategies,
    error,
    loadStrategies,
    selectStrategy,
    setSymbol,
    setDateRange,
    setInitialCapital,
    setCommission,
    updateParameter,
    runBacktest,
    reset,
  } = useBacktestStore();

  // Load strategies on mount
  useEffect(() => {
    loadStrategies();
  }, [loadStrategies]);

  const handleRunBacktest = async () => {
    await runBacktest();
  };

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Backtest Configuration</h2>
        </div>
        <button
          onClick={reset}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-dark-muted hover:text-dark-text transition-colors"
          disabled={isLoading}
        >
          <RefreshCw className="w-4 h-4" />
          Reset
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-danger/10 border border-danger rounded-lg p-4">
          <p className="text-danger text-sm">{error}</p>
        </div>
      )}

      {/* Stock Symbol */}
      <div className="space-y-2">
        <label htmlFor="symbol" className="block text-sm font-medium text-dark-text">
          Stock Symbol
        </label>
        <input
          id="symbol"
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="e.g., AAPL"
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text placeholder-dark-muted focus:outline-none focus:ring-2 focus:ring-primary"
          disabled={isLoading}
        />
      </div>

      {/* Date Range */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="startDate" className="block text-sm font-medium text-dark-text">
            Start Date
          </label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setDateRange(e.target.value, endDate)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="endDate" className="block text-sm font-medium text-dark-text">
            End Date
          </label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setDateRange(startDate, e.target.value)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Strategy Selection */}
      <div className="space-y-2">
        <label htmlFor="strategy" className="block text-sm font-medium text-dark-text">
          Trading Strategy
        </label>
        {isLoadingStrategies ? (
          <div className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-muted">
            Loading strategies...
          </div>
        ) : (
          <select
            id="strategy"
            value={selectedStrategy?.id || ''}
            onChange={(e) => selectStrategy(e.target.value)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          >
            {strategies.map((strategy) => (
              <option key={strategy.id} value={strategy.id}>
                {strategy.name}
              </option>
            ))}
          </select>
        )}
        {selectedStrategy && (
          <p className="text-sm text-dark-muted mt-1">{selectedStrategy.description}</p>
        )}
      </div>

      {/* Strategy Parameters */}
      {selectedStrategy && selectedStrategy.parameters.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-dark-text">Strategy Parameters</h3>
          <div className="space-y-3">
            {selectedStrategy.parameters.map((param) => (
              <div key={param.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor={param.name} className="text-sm text-dark-text">
                    {param.name}
                  </label>
                  <span className="text-sm font-medium text-primary">
                    {customParameters[param.name]}
                  </span>
                </div>
                {param.description && (
                  <p className="text-xs text-dark-muted">{param.description}</p>
                )}
                {param.type === 'int' || param.type === 'float' ? (
                  <input
                    id={param.name}
                    type="range"
                    min={param.min_value}
                    max={param.max_value}
                    step={param.type === 'int' ? 1 : 0.01}
                    value={customParameters[param.name] || param.value}
                    onChange={(e) =>
                      updateParameter(
                        param.name,
                        param.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value)
                      )
                    }
                    className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer slider"
                    disabled={isLoading}
                  />
                ) : (
                  <input
                    id={param.name}
                    type="text"
                    value={customParameters[param.name] || param.value}
                    onChange={(e) => updateParameter(param.name, e.target.value)}
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={isLoading}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Capital & Commission */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="capital" className="block text-sm font-medium text-dark-text">
            Initial Capital ($)
          </label>
          <input
            id="capital"
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(Number(e.target.value))}
            min={1000}
            step={1000}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="commission" className="block text-sm font-medium text-dark-text">
            Commission (%)
          </label>
          <input
            id="commission"
            type="number"
            value={commission * 100}
            onChange={(e) => setCommission(Number(e.target.value) / 100)}
            min={0}
            max={1}
            step={0.01}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Run Button */}
      <button
        onClick={handleRunBacktest}
        disabled={isLoading || !selectedStrategy}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary hover:bg-primary-dark text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <RefreshCw className="w-5 h-5 animate-spin" />
            Running Backtest...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Run Backtest
          </>
        )}
      </button>
    </div>
  );
};
