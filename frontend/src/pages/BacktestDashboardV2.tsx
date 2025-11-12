/**
 * BacktestDashboardV2 - High-density multi-stock multi-strategy comparison dashboard
 */
import React from 'react';
import { ComparisonMatrix } from '../components/comparison/ComparisonMatrix';
import { ParameterTuningModal } from '../components/comparison/ParameterTuningModal';
import { useComparisonStore } from '../stores/comparisonStore';
import { X } from 'lucide-react';

export const BacktestDashboardV2: React.FC = () => {
  const { selectedCell, clearSelection, tuningCell, closeTuning, updateCellParameters } = useComparisonStore();

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-[1800px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-dark-text">
              Stock Picker Dashboard V2
            </h1>
            <p className="text-dark-muted mt-1">
              Compare multiple stocks and strategies side-by-side
            </p>
          </div>
          <div className="px-3 py-1 bg-primary/20 border border-primary/30 rounded-lg">
            <span className="text-xs font-semibold text-primary">V2 Beta</span>
          </div>
        </div>

        {/* Comparison Matrix */}
        <ComparisonMatrix />

        {/* Detailed View Modal */}
        {selectedCell && (
          <div
            className="fixed inset-0 flex items-center justify-center p-6 z-50"
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
          >
            <div
              className="rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
              style={{ backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: '1px' }}
            >
              {/* Modal Header */}
              <div
                className="sticky top-0 px-6 py-4 flex items-center justify-between"
                style={{
                  backgroundColor: '#1e293b',
                  borderBottomColor: '#334155',
                  borderBottomWidth: '1px'
                }}
              >
                <div>
                  <h2 className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
                    {selectedCell.symbol} - {selectedCell.strategy.name}
                  </h2>
                  <p className="text-sm mt-1" style={{ color: '#94a3b8' }}>
                    {selectedCell.summary?.total_return_pct !== undefined
                      ? `${selectedCell.summary.total_return_pct > 0 ? '+' : ''}${selectedCell.summary.total_return_pct.toFixed(2)}% return`
                      : ''}
                  </p>
                </div>
                <button
                  onClick={clearSelection}
                  className="p-2 rounded-lg transition-colors hover:opacity-80"
                  style={{ backgroundColor: '#0f172a' }}
                >
                  <X className="w-5 h-5" style={{ color: '#94a3b8' }} />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6">
                <div
                  className="rounded-lg p-8 text-center"
                  style={{ backgroundColor: '#0f172a', borderColor: '#334155', borderWidth: '1px' }}
                >
                  <p className="mb-4" style={{ color: '#94a3b8' }}>
                    Detailed view coming soon...
                  </p>
                  <p className="text-sm" style={{ color: '#94a3b8' }}>
                    Will show: Price chart with signals, equity curve, metrics, and trades table
                  </p>
                  <div className="mt-6 grid grid-cols-3 gap-4 text-left">
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Total Return</div>
                      <div
                        className="text-xl font-bold"
                        style={{
                          color: selectedCell.summary?.total_return_pct !== undefined && selectedCell.summary.total_return_pct > 0
                            ? '#10b981'
                            : '#ef4444'
                        }}
                      >
                        {selectedCell.summary?.total_return_pct !== undefined
                          ? `${selectedCell.summary.total_return_pct > 0 ? '+' : ''}${selectedCell.summary.total_return_pct.toFixed(2)}%`
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Sharpe Ratio</div>
                      <div className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
                        {selectedCell.summary?.sharpe_ratio !== undefined
                          ? selectedCell.summary.sharpe_ratio.toFixed(2)
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Max Drawdown</div>
                      <div className="text-xl font-bold" style={{ color: '#ef4444' }}>
                        {selectedCell.summary?.max_drawdown_pct !== undefined
                          ? `${selectedCell.summary.max_drawdown_pct.toFixed(2)}%`
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Total Trades</div>
                      <div className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
                        {selectedCell.summary?.total_trades ?? 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Win Rate</div>
                      <div className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
                        {selectedCell.summary?.win_rate !== undefined
                          ? `${selectedCell.summary.win_rate.toFixed(1)}%`
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs mb-1" style={{ color: '#94a3b8' }}>Backtest ID</div>
                      <div className="text-xs font-mono truncate" style={{ color: '#94a3b8' }}>
                        {selectedCell.summary?.backtest_id ?? 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Parameter Tuning Modal */}
        {tuningCell && (
          <ParameterTuningModal
            cell={tuningCell}
            onClose={closeTuning}
            onApplyAndRun={(params) => updateCellParameters(tuningCell.symbol, tuningCell.strategy.name, params)}
          />
        )}

        {/* Instructions */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-dark-text mb-2">Quick Start</h3>
          <ul className="text-sm text-dark-muted space-y-1">
            <li>• Add stocks and strategies using the controls above</li>
            <li>• Click "Run All" to backtest all combinations in parallel</li>
            <li>• Hover over cells and click the gear icon to tune strategy parameters</li>
            <li>• Click completed cells to view detailed results (coming soon)</li>
            <li>• Green = profitable, Red = loss, higher Sharpe Ratio = better risk-adjusted returns</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
