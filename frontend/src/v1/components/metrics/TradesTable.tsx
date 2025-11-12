import React, { useState } from 'react';
import type { Trade } from '../../types';
import { List, TrendingUp, TrendingDown } from 'lucide-react';
import { format } from 'date-fns';

interface TradesTableProps {
  trades: Trade[];
}

export const TradesTable: React.FC<TradesTableProps> = ({ trades }) => {
  const [sortColumn, setSortColumn] = useState<keyof Trade>('entry_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterType, setFilterType] = useState<'all' | 'winning' | 'losing'>('all');

  // Filter trades
  const filteredTrades = trades.filter((trade) => {
    if (filterType === 'all') return true;
    if (filterType === 'winning') return (trade.profit_loss ?? 0) > 0;
    if (filterType === 'losing') return (trade.profit_loss ?? 0) < 0;
    return true;
  });

  // Sort trades
  const sortedTrades = [...filteredTrades].sort((a, b) => {
    const aValue = a[sortColumn];
    const bValue = b[sortColumn];

    if (aValue === undefined || aValue === null) return 1;
    if (bValue === undefined || bValue === null) return -1;

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const handleSort = (column: keyof Trade) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Open';
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number | undefined) => {
    if (value === undefined) return '-';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${(value * 100).toFixed(2)}%`;
  };

  if (!trades || trades.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <List className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Trades</h2>
        </div>
        <div className="text-center text-dark-muted py-12">
          No trades to display. Run a backtest to see trade history.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <List className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Trades</h2>
          <span className="text-sm text-dark-muted">({filteredTrades.length} trades)</span>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterType === 'all'
                ? 'bg-primary text-white'
                : 'bg-dark-bg text-dark-muted hover:text-dark-text'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilterType('winning')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterType === 'winning'
                ? 'bg-success text-white'
                : 'bg-dark-bg text-dark-muted hover:text-dark-text'
            }`}
          >
            Winning
          </button>
          <button
            onClick={() => setFilterType('losing')}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterType === 'losing'
                ? 'bg-danger text-white'
                : 'bg-dark-bg text-dark-muted hover:text-dark-text'
            }`}
          >
            Losing
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-dark-border">
              <th
                className="text-left py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('entry_date')}
              >
                Entry Date {sortColumn === 'entry_date' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-left py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('exit_date')}
              >
                Exit Date {sortColumn === 'exit_date' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('entry_price')}
              >
                Entry Price {sortColumn === 'entry_price' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('exit_price')}
              >
                Exit Price {sortColumn === 'exit_price' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('shares')}
              >
                Shares {sortColumn === 'shares' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('profit_loss')}
              >
                P&L {sortColumn === 'profit_loss' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('profit_loss_pct')}
              >
                Return % {sortColumn === 'profit_loss_pct' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="text-right py-3 px-4 text-dark-muted font-medium cursor-pointer hover:text-dark-text"
                onClick={() => handleSort('duration_days')}
              >
                Duration {sortColumn === 'duration_days' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedTrades.map((trade, index) => {
              const isWinning = (trade.profit_loss ?? 0) > 0;
              const isOpen = !trade.exit_date;

              return (
                <tr
                  key={index}
                  className="border-b border-dark-border hover:bg-dark-bg transition-colors"
                >
                  <td className="py-3 px-4 text-dark-text">{formatDate(trade.entry_date)}</td>
                  <td className="py-3 px-4 text-dark-text">
                    {isOpen ? (
                      <span className="text-warning">Open</span>
                    ) : (
                      formatDate(trade.exit_date)
                    )}
                  </td>
                  <td className="py-3 px-4 text-right text-dark-text">
                    {formatCurrency(trade.entry_price)}
                  </td>
                  <td className="py-3 px-4 text-right text-dark-text">
                    {trade.exit_price ? formatCurrency(trade.exit_price) : '-'}
                  </td>
                  <td className="py-3 px-4 text-right text-dark-text">{trade.shares}</td>
                  <td
                    className={`py-3 px-4 text-right font-medium ${
                      isOpen ? 'text-dark-muted' : isWinning ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {trade.profit_loss !== undefined ? (
                      <div className="flex items-center justify-end gap-1">
                        {!isOpen &&
                          (isWinning ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          ))}
                        {formatCurrency(trade.profit_loss)}
                      </div>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td
                    className={`py-3 px-4 text-right font-medium ${
                      isOpen ? 'text-dark-muted' : isWinning ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {formatPercent(trade.profit_loss_pct)}
                  </td>
                  <td className="py-3 px-4 text-right text-dark-text">
                    {trade.duration_days !== undefined ? `${trade.duration_days}d` : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
