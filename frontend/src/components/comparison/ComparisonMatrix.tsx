/**
 * ComparisonMatrix - Multi-stock multi-strategy comparison grid
 */
import React, { useEffect } from 'react';
import { useComparisonStore } from '../../stores/comparisonStore';
import { ComparisonCell } from './ComparisonCell';
import { Plus, Play, Trash2 } from 'lucide-react';

export const ComparisonMatrix: React.FC = () => {
  const {
    symbols,
    strategies,
    startDate,
    endDate,
    initialCapital,
    commission,
    addSymbol,
    removeSymbol,
    addStrategy,
    removeStrategy,
    setDateRange,
    setCapital,
    setCommission,
    runAllCells,
    clearMatrix,
    getCell,
    availableStrategies,
    loadAvailableStrategies,
  } = useComparisonStore();

  const [newSymbol, setNewSymbol] = React.useState('');
  const [selectedStrategyId, setSelectedStrategyId] = React.useState('');

  useEffect(() => {
    loadAvailableStrategies();
  }, []);

  const handleAddSymbol = () => {
    if (newSymbol.trim()) {
      addSymbol(newSymbol.trim());
      setNewSymbol('');
    }
  };

  const handleAddStrategy = () => {
    const strategy = availableStrategies.find(s => s.id === selectedStrategyId);
    if (strategy) {
      addStrategy({
        name: strategy.name,
        type: strategy.type,
        parameters: strategy.default_params,
        description: strategy.description,
      });
      setSelectedStrategyId('');
    }
  };

  const handleRunAll = async () => {
    await runAllCells();
  };

  return (
    <div className="space-y-4">
      {/* Header Controls */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-dark-text">Comparison Matrix</h2>
          <div className="flex gap-2">
            <button
              onClick={handleRunAll}
              disabled={symbols.length === 0 || strategies.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              <Play className="w-4 h-4" />
              Run All
            </button>
            <button
              onClick={clearMatrix}
              className="flex items-center gap-2 px-4 py-2 bg-dark-bg hover:bg-dark-bg/80 text-dark-text rounded-lg border border-dark-border transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Clear
            </button>
          </div>
        </div>

        {/* Configuration */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm text-dark-muted mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setDateRange(e.target.value, endDate)}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm text-dark-muted mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setDateRange(startDate, e.target.value)}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm text-dark-muted mb-1">Initial Capital</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm text-dark-muted mb-1">Commission (%)</label>
            <input
              type="number"
              step="0.001"
              value={(commission * 100).toFixed(3)}
              onChange={(e) => setCommission(Number(e.target.value) / 100)}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Add Symbols */}
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className="text-sm text-dark-muted font-medium">Stocks:</span>
          {symbols.map(symbol => (
            <div
              key={symbol}
              className="flex items-center gap-1 px-3 py-1 bg-dark-bg rounded-lg border border-dark-border"
            >
              <span className="text-sm text-dark-text font-medium">{symbol}</span>
              <button
                onClick={() => removeSymbol(symbol)}
                className="text-dark-muted hover:text-danger transition-colors"
              >
                ×
              </button>
            </div>
          ))}
          <div className="flex gap-1">
            <input
              type="text"
              placeholder="Add symbol..."
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
              className="px-3 py-1 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm w-24 focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              onClick={handleAddSymbol}
              disabled={!newSymbol.trim()}
              className="px-2 py-1 bg-primary/20 hover:bg-primary/30 disabled:bg-gray-700 disabled:cursor-not-allowed text-primary rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Add Strategies */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-dark-muted font-medium">Strategies:</span>
          {strategies.map(strategy => (
            <div
              key={strategy.name}
              className="flex items-center gap-1 px-3 py-1 bg-dark-bg rounded-lg border border-dark-border"
            >
              <span className="text-sm text-dark-text">{strategy.name}</span>
              <button
                onClick={() => removeStrategy(strategy.name)}
                className="text-dark-muted hover:text-danger transition-colors"
              >
                ×
              </button>
            </div>
          ))}
          <div className="flex gap-1">
            <select
              value={selectedStrategyId}
              onChange={(e) => setSelectedStrategyId(e.target.value)}
              className="px-3 py-1 bg-dark-bg border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Add strategy...</option>
              {availableStrategies
                .filter(s => !strategies.some(existing => existing.name === s.name))
                .map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
            </select>
            <button
              onClick={handleAddStrategy}
              disabled={!selectedStrategyId}
              className="px-2 py-1 bg-primary/20 hover:bg-primary/30 disabled:bg-gray-700 disabled:cursor-not-allowed text-primary rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Matrix Grid */}
      {symbols.length > 0 && strategies.length > 0 ? (
        <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-dark-bg border-b border-dark-border">
                  <th className="sticky left-0 bg-dark-bg px-4 py-3 text-left text-sm font-semibold text-dark-muted">
                    Stock \ Strategy
                  </th>
                  {strategies.map(strategy => (
                    <th
                      key={strategy.name}
                      className="px-4 py-3 text-left text-sm font-semibold text-dark-muted min-w-[200px]"
                    >
                      {strategy.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {symbols.map((symbol, rowIndex) => (
                  <tr
                    key={symbol}
                    className={rowIndex % 2 === 0 ? 'bg-dark-card' : 'bg-dark-bg/50'}
                  >
                    <td className="sticky left-0 bg-inherit px-4 py-3 text-sm font-semibold text-dark-text border-r border-dark-border">
                      {symbol}
                    </td>
                    {strategies.map(strategy => {
                      const cell = getCell(symbol, strategy.name);
                      return (
                        <td key={`${symbol}-${strategy.name}`} className="px-2 py-2">
                          {cell && <ComparisonCell cell={cell} />}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
          <p className="text-dark-muted mb-2">No stocks or strategies selected</p>
          <p className="text-sm text-dark-muted">
            Add stocks and strategies above to start comparing
          </p>
        </div>
      )}
    </div>
  );
};
