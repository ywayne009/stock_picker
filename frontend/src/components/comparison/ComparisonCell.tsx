/**
 * ComparisonCell - Individual cell in the comparison matrix
 * Shows compact metrics and allows clicking for detailed view
 */
import React from 'react';
import type { MatrixCell } from '../../types/comparison';
import { useComparisonStore } from '../../stores/comparisonStore';
import { TrendingUp, TrendingDown, Loader2, AlertCircle, Settings } from 'lucide-react';

interface ComparisonCellProps {
  cell: MatrixCell;
}

export const ComparisonCell: React.FC<ComparisonCellProps> = ({ cell }) => {
  const { selectCell, runCell, openTuning } = useComparisonStore();
  const { symbol, strategy, summary, isLoading, error } = cell;

  const handleClick = () => {
    if (summary?.status === 'completed') {
      selectCell(symbol, strategy.name);
    }
  };

  const handleRun = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await runCell(symbol, strategy.name);
  };

  const handleTune = (e: React.MouseEvent) => {
    e.stopPropagation();
    openTuning(symbol, strategy.name);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-24 bg-dark-bg border border-dark-border rounded-lg">
        <Loader2 className="w-5 h-5 text-primary animate-spin" />
      </div>
    );
  }

  // Error state
  if (error || summary?.status === 'failed') {
    return (
      <div className="h-24 bg-danger/10 border border-danger/30 rounded-lg p-2">
        <div className="flex items-start gap-1 mb-1">
          <AlertCircle className="w-4 h-4 text-danger flex-shrink-0 mt-0.5" />
          <span className="text-xs text-danger line-clamp-2">
            {error || summary?.error_message || 'Failed'}
          </span>
        </div>
        <button
          onClick={handleRun}
          className="text-xs text-danger hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  // Empty state (not run yet)
  if (!summary) {
    return (
      <div className="h-24 bg-dark-bg border border-dark-border rounded-lg p-2 hover:border-primary/50 transition-colors group">
        <div className="flex flex-col items-center justify-center h-full gap-2">
          <button
            onClick={handleRun}
            className="text-sm text-dark-muted group-hover:text-primary transition-colors"
          >
            Run
          </button>
          <button
            onClick={handleTune}
            className="flex items-center gap-1 text-xs text-dark-muted hover:text-primary transition-colors"
          >
            <Settings className="w-3 h-3" />
            Tune
          </button>
        </div>
      </div>
    );
  }

  // Completed state - show metrics
  const { total_return_pct, sharpe_ratio, max_drawdown_pct, total_trades, win_rate } = summary;
  const isPositive = total_return_pct !== undefined && total_return_pct > 0;
  const returnColor = isPositive ? 'text-success' : 'text-danger';

  return (
    <div
      onClick={handleClick}
      className="h-24 bg-dark-bg border border-dark-border rounded-lg p-2 hover:border-primary/70 hover:shadow-lg transition-all cursor-pointer group relative"
    >
      {/* Tune button */}
      <button
        onClick={handleTune}
        className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-dark-card rounded"
      >
        <Settings className="w-3 h-3 text-dark-muted hover:text-primary" />
      </button>

      <div className="space-y-1">
        {/* Return */}
        <div className="flex items-center gap-1">
          {isPositive ? (
            <TrendingUp className="w-3 h-3 text-success" />
          ) : (
            <TrendingDown className="w-3 h-3 text-danger" />
          )}
          <span className={`text-lg font-bold ${returnColor}`}>
            {total_return_pct !== undefined
              ? `${total_return_pct > 0 ? '+' : ''}${total_return_pct.toFixed(2)}%`
              : 'N/A'}
          </span>
        </div>

        {/* Sharpe Ratio */}
        <div className="text-xs text-dark-muted">
          <span className="font-medium">SR:</span>{' '}
          <span className={sharpe_ratio && sharpe_ratio > 1 ? 'text-success' : ''}>
            {sharpe_ratio !== undefined ? sharpe_ratio.toFixed(2) : 'N/A'}
          </span>
        </div>

        {/* Additional metrics */}
        <div className="flex items-center justify-between text-xs text-dark-muted">
          <span title="Max Drawdown">
            DD: {max_drawdown_pct !== undefined ? `${max_drawdown_pct.toFixed(1)}%` : 'N/A'}
          </span>
          <span title="Win Rate">
            WR: {win_rate !== undefined ? `${win_rate.toFixed(0)}%` : 'N/A'}
          </span>
        </div>

        {/* Trade count */}
        <div className="text-xs text-dark-muted">
          {total_trades !== undefined ? `${total_trades} trades` : ''}
        </div>
      </div>
    </div>
  );
};
