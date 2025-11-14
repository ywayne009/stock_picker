import React from 'react';
import type { PerformanceMetrics } from '../../types';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Percent,
  Activity,
  Target,
  BarChart3,
  Award,
  HelpCircle
} from 'lucide-react';

interface MetricsGridProps {
  metrics: PerformanceMetrics;
}

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: 'positive' | 'negative' | 'neutral';
  suffix?: string;
  tooltip?: string;
}

const MetricCardComponent: React.FC<MetricCardProps> = ({ label, value, icon, trend = 'neutral', suffix = '', tooltip }) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'positive':
        return 'text-success';
      case 'negative':
        return 'text-danger';
      default:
        return 'text-primary';
    }
  };

  return (
    <div className="bg-dark-bg rounded-lg border border-dark-border p-2.5 relative group">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-1">
          <span className="text-xs text-dark-muted">{label}</span>
          {tooltip && (
            <div className="relative">
              <HelpCircle className="w-3 h-3 text-dark-muted opacity-50 group-hover:opacity-100 transition-opacity cursor-help" />
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block z-50 w-64 p-2 bg-dark-card border border-dark-border rounded shadow-lg text-xs text-dark-text">
                {tooltip}
                <div className="absolute left-2 top-full w-2 h-2 bg-dark-card border-r border-b border-dark-border transform rotate-45 -mt-1"></div>
              </div>
            </div>
          )}
        </div>
        <div className={`${getTrendColor()}`}>{React.cloneElement(icon as React.ReactElement, { className: 'w-3.5 h-3.5' })}</div>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`text-lg font-bold ${getTrendColor()}`}>
          {value}
        </span>
        {suffix && <span className="text-xs text-dark-muted">{suffix}</span>}
      </div>
    </div>
  );
};

// Memoize to prevent unnecessary re-renders
const MetricCard = React.memo(MetricCardComponent);

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const formatPercent = (value: number): string => {
    return (value * 100).toFixed(2);
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number, decimals: number = 2): string => {
    return value.toFixed(decimals);
  };

  const getTrend = (value: number): 'positive' | 'negative' | 'neutral' => {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
  };

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="w-4 h-4 text-primary" />
        <h2 className="text-lg font-semibold text-dark-text">Performance Metrics</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {/* Returns */}
        <MetricCard
          label="Total Return"
          value={formatCurrency(metrics.total_return)}
          icon={<DollarSign className="w-5 h-5" />}
          trend={getTrend(metrics.total_return)}
          tooltip="Total profit or loss in dollars from all trades during the backtest period."
        />

        <MetricCard
          label="Total Return %"
          value={formatPercent(metrics.total_return_pct)}
          icon={<Percent className="w-5 h-5" />}
          trend={getTrend(metrics.total_return_pct)}
          suffix="%"
          tooltip="Total return as a percentage of initial capital. Shows the overall strategy performance."
        />

        <MetricCard
          label="CAGR"
          value={formatPercent(metrics.cagr)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend={getTrend(metrics.cagr)}
          suffix="%"
          tooltip="Compound Annual Growth Rate - The annualized rate of return over the period. Higher is better."
        />

        <MetricCard
          label="Max Drawdown"
          value={formatPercent(metrics.max_drawdown_pct)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
          suffix="%"
          tooltip="Largest peak-to-trough decline in portfolio value. Measures the worst-case loss. Lower is better."
        />

        {/* Risk Metrics */}
        <MetricCard
          label="Sharpe Ratio"
          value={formatNumber(metrics.sharpe_ratio)}
          icon={<Activity className="w-5 h-5" />}
          trend={metrics.sharpe_ratio > 1 ? 'positive' : 'neutral'}
          tooltip="Risk-adjusted return metric. Measures excess return per unit of risk. >1 is good, >2 is excellent."
        />

        <MetricCard
          label="Sortino Ratio"
          value={formatNumber(metrics.sortino_ratio)}
          icon={<Activity className="w-5 h-5" />}
          trend={metrics.sortino_ratio > 1 ? 'positive' : 'neutral'}
          tooltip="Similar to Sharpe but only penalizes downside volatility. Better measure for asymmetric returns."
        />

        <MetricCard
          label="Volatility"
          value={formatPercent(metrics.volatility)}
          icon={<Activity className="w-5 h-5" />}
          trend="neutral"
          suffix="%"
          tooltip="Standard deviation of returns. Measures how much returns fluctuate. Higher means more risk."
        />

        <MetricCard
          label="Profit Factor"
          value={formatNumber(metrics.profit_factor)}
          icon={<Award className="w-5 h-5" />}
          trend={metrics.profit_factor > 1 ? 'positive' : 'negative'}
          tooltip="Ratio of gross profits to gross losses. >1 means profitable, >2 is strong. Accounts for win size vs loss size."
        />

        {/* Trade Statistics */}
        <MetricCard
          label="Total Trades"
          value={metrics.total_trades}
          icon={<Target className="w-5 h-5" />}
          trend="neutral"
          tooltip="Total number of completed trades. More trades generally means more statistical significance."
        />

        <MetricCard
          label="Win Rate"
          value={formatPercent(metrics.win_rate)}
          icon={<Percent className="w-5 h-5" />}
          trend={metrics.win_rate > 0.5 ? 'positive' : 'negative'}
          suffix="%"
          tooltip="Percentage of trades that were profitable. 50% means half your trades win. >60% is strong."
        />

        <MetricCard
          label="Avg Win"
          value={formatCurrency(metrics.avg_win)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend="positive"
          tooltip="Average profit per winning trade. Higher is better. Compare with Avg Loss for risk/reward ratio."
        />

        <MetricCard
          label="Avg Loss"
          value={formatCurrency(metrics.avg_loss)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
          tooltip="Average loss per losing trade. Smaller (closer to $0) is better. Compare with Avg Win."
        />

        <MetricCard
          label="Largest Win"
          value={formatCurrency(metrics.largest_win)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend="positive"
          tooltip="The single most profitable trade in the backtest period. Shows best-case potential."
        />

        <MetricCard
          label="Largest Loss"
          value={formatCurrency(metrics.largest_loss)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
          tooltip="The single worst losing trade in the backtest period. Shows worst-case risk."
        />

        <MetricCard
          label="Expectancy"
          value={formatCurrency(metrics.expectancy)}
          icon={<DollarSign className="w-5 h-5" />}
          trend={getTrend(metrics.expectancy)}
          tooltip="Average expected profit per trade. Positive means profitable over time. Combines win rate and avg win/loss."
        />

        <MetricCard
          label="Winning Trades"
          value={`${metrics.winning_trades} / ${metrics.total_trades}`}
          icon={<Target className="w-5 h-5" />}
          trend="neutral"
          tooltip="Number of profitable trades out of total trades. Same info as Win Rate but in absolute numbers."
        />

        {/* Buy and Hold Comparison */}
        {metrics.buy_hold_return !== undefined && (
          <MetricCard
            label="Buy & Hold Return"
            value={formatPercent(metrics.buy_hold_return)}
            icon={<TrendingUp className="w-5 h-5" />}
            trend={getTrend(metrics.buy_hold_return)}
            suffix="%"
            tooltip="Return from simply buying at start and holding until end (10% position, 90% cash). Baseline for comparison."
          />
        )}

        {metrics.buy_hold_return !== undefined && (
          <MetricCard
            label="Outperformance"
            value={formatPercent(metrics.total_return_pct - metrics.buy_hold_return)}
            icon={<Award className="w-5 h-5" />}
            trend={getTrend(metrics.total_return_pct - metrics.buy_hold_return)}
            suffix="%"
            tooltip="How much the strategy beat (or lost to) buy-and-hold. Positive means strategy added value."
          />
        )}
      </div>
    </div>
  );
};
