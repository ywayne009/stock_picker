/**
 * DetailedCellView - Full backtest results view for a single cell
 * Reuses V1 components for charts and tables
 */
import React, { useState } from 'react';
import { X, Loader2, Printer } from 'lucide-react';
import type { MatrixCell, StrategyConfig } from '../../types/comparison';
import type { BacktestResults } from '../../types';

// Import V1 components
import { PriceChart } from '../../v1/components/charts/PriceChart';
import { EquityCurve } from '../../v1/components/charts/EquityCurve';
import { DrawdownChart } from '../../v1/components/charts/DrawdownChart';
import { ReturnsDistribution } from '../../v1/components/charts/ReturnsDistribution';
import { MetricsGrid } from '../../v1/components/metrics/MetricsGrid';
import { TradesTable } from '../../v1/components/metrics/TradesTable';

interface DetailedCellViewProps {
  cell: MatrixCell;
  fullResults: BacktestResults | null;
  isLoading: boolean;
  stockData: any; // OHLCV data for price chart
  onClose: () => void;
}

// Helper to extract MA parameters from strategy configuration
function getMovingAveragesFromStrategy(strategy: StrategyConfig) {
  const mas = [];
  const params = strategy.parameters;

  // Check if strategy has fast/slow period parameters (MA crossover strategies)
  if (params.fast_period && params.slow_period) {
    const maType = (params.ma_type?.toUpperCase() || 'SMA') as 'SMA' | 'EMA';

    mas.push({
      period: params.fast_period,
      type: maType,
      color: '#3b82f6', // Blue for fast MA
    });

    mas.push({
      period: params.slow_period,
      type: maType,
      color: '#f59e0b', // Orange for slow MA
    });
  }

  return mas;
}

export const DetailedCellView: React.FC<DetailedCellViewProps> = ({
  cell,
  fullResults,
  isLoading,
  stockData,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'charts' | 'trades'>('overview');

  const handlePrint = () => {
    window.print();
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-6 z-50 animate-fadeIn"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
      onClick={onClose}
    >
      <div
        className="rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden shadow-2xl flex flex-col animate-slideDown"
        style={{ backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: '1px' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{
            backgroundColor: '#1e293b',
            borderBottomColor: '#334155',
            borderBottomWidth: '1px',
          }}
        >
          <div>
            <h2 className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
              {cell.symbol} - {cell.strategy.name}
            </h2>
            {cell.summary && (
              <p className="text-sm mt-1" style={{ color: '#94a3b8' }}>
                {cell.summary.total_return_pct !== undefined
                  ? `${cell.summary.total_return_pct > 0 ? '+' : ''}${cell.summary.total_return_pct.toFixed(2)}% return`
                  : ''}
                {cell.summary.sharpe_ratio !== undefined && ` • Sharpe: ${cell.summary.sharpe_ratio.toFixed(2)}`}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:opacity-90 print:hidden"
              style={{ backgroundColor: '#3b82f6', color: '#ffffff' }}
            >
              <Printer className="w-4 h-4" />
              <span className="text-sm">Print / PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg transition-colors hover:opacity-80 print:hidden"
              style={{ backgroundColor: '#0f172a' }}
            >
              <X className="w-5 h-5" style={{ color: '#94a3b8' }} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div
          className="flex px-6 pt-3"
          style={{ borderBottomColor: '#334155', borderBottomWidth: '1px' }}
        >
          {['overview', 'charts', 'trades'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className="px-4 py-2 text-sm font-medium transition-colors capitalize"
              style={{
                color: activeTab === tab ? '#3b82f6' : '#94a3b8',
                borderBottomColor: activeTab === tab ? '#3b82f6' : 'transparent',
                borderBottomWidth: '2px',
              }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin" style={{ color: '#3b82f6' }} />
              <span className="ml-3" style={{ color: '#94a3b8' }}>
                Loading full results...
              </span>
            </div>
          ) : !fullResults ? (
            <div className="flex items-center justify-center h-64">
              <p style={{ color: '#94a3b8' }}>Failed to load full results</p>
            </div>
          ) : (
            <>
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <MetricsGrid metrics={fullResults.metrics} />
                </div>
              )}

              {/* Charts Tab */}
              {activeTab === 'charts' && (
                <div className="space-y-4">
                  {/* Price Chart with Signals */}
                  {stockData && stockData.data && stockData.data.length > 0 ? (
                    <PriceChart
                      data={stockData.data}
                      signals={fullResults.signals}
                      symbol={fullResults.symbol}
                      movingAverages={getMovingAveragesFromStrategy(cell.strategy)}
                    />
                  ) : (
                    <div
                      className="rounded-lg p-4 text-center"
                      style={{ backgroundColor: '#0f172a', borderColor: '#334155', borderWidth: '1px' }}
                    >
                      <p style={{ color: '#94a3b8' }}>
                        Stock data not available. Price chart cannot be displayed.
                      </p>
                    </div>
                  )}

                  {/* Equity Curve and Drawdown side by side */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <EquityCurve
                      equityCurve={fullResults.equity_curve}
                      initialCapital={fullResults.initial_capital}
                    />
                    <DrawdownChart
                      equityCurve={fullResults.equity_curve}
                      initialCapital={fullResults.initial_capital}
                    />
                  </div>

                  {/* Returns Distribution */}
                  <ReturnsDistribution trades={fullResults.trades} />
                </div>
              )}

              {/* Trades Tab */}
              {activeTab === 'trades' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3" style={{ color: '#f1f5f9' }}>
                      Trade History
                    </h3>
                    <TradesTable trades={fullResults.trades} />
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
