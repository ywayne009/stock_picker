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
  Award
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
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon, trend = 'neutral', suffix = '' }) => {
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
    <div className="bg-dark-bg rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-dark-muted">{label}</span>
        <div className={`${getTrendColor()}`}>{icon}</div>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${getTrendColor()}`}>
          {value}
        </span>
        {suffix && <span className="text-sm text-dark-muted">{suffix}</span>}
      </div>
    </div>
  );
};

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
    <div className="bg-dark-card rounded-lg border border-dark-border p-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-5 h-5 text-primary" />
        <h2 className="text-xl font-semibold text-dark-text">Performance Metrics</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Returns */}
        <MetricCard
          label="Total Return"
          value={formatCurrency(metrics.total_return)}
          icon={<DollarSign className="w-5 h-5" />}
          trend={getTrend(metrics.total_return)}
        />

        <MetricCard
          label="Total Return %"
          value={formatPercent(metrics.total_return_pct)}
          icon={<Percent className="w-5 h-5" />}
          trend={getTrend(metrics.total_return_pct)}
          suffix="%"
        />

        <MetricCard
          label="CAGR"
          value={formatPercent(metrics.cagr)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend={getTrend(metrics.cagr)}
          suffix="%"
        />

        <MetricCard
          label="Max Drawdown"
          value={formatPercent(metrics.max_drawdown_pct)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
          suffix="%"
        />

        {/* Risk Metrics */}
        <MetricCard
          label="Sharpe Ratio"
          value={formatNumber(metrics.sharpe_ratio)}
          icon={<Activity className="w-5 h-5" />}
          trend={metrics.sharpe_ratio > 1 ? 'positive' : 'neutral'}
        />

        <MetricCard
          label="Sortino Ratio"
          value={formatNumber(metrics.sortino_ratio)}
          icon={<Activity className="w-5 h-5" />}
          trend={metrics.sortino_ratio > 1 ? 'positive' : 'neutral'}
        />

        <MetricCard
          label="Volatility"
          value={formatPercent(metrics.volatility)}
          icon={<Activity className="w-5 h-5" />}
          trend="neutral"
          suffix="%"
        />

        <MetricCard
          label="Profit Factor"
          value={formatNumber(metrics.profit_factor)}
          icon={<Award className="w-5 h-5" />}
          trend={metrics.profit_factor > 1 ? 'positive' : 'negative'}
        />

        {/* Trade Statistics */}
        <MetricCard
          label="Total Trades"
          value={metrics.total_trades}
          icon={<Target className="w-5 h-5" />}
          trend="neutral"
        />

        <MetricCard
          label="Win Rate"
          value={formatPercent(metrics.win_rate)}
          icon={<Percent className="w-5 h-5" />}
          trend={metrics.win_rate > 0.5 ? 'positive' : 'negative'}
          suffix="%"
        />

        <MetricCard
          label="Avg Win"
          value={formatCurrency(metrics.avg_win)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend="positive"
        />

        <MetricCard
          label="Avg Loss"
          value={formatCurrency(metrics.avg_loss)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
        />

        <MetricCard
          label="Largest Win"
          value={formatCurrency(metrics.largest_win)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend="positive"
        />

        <MetricCard
          label="Largest Loss"
          value={formatCurrency(metrics.largest_loss)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="negative"
        />

        <MetricCard
          label="Expectancy"
          value={formatCurrency(metrics.expectancy)}
          icon={<DollarSign className="w-5 h-5" />}
          trend={getTrend(metrics.expectancy)}
        />

        <MetricCard
          label="Winning Trades"
          value={`${metrics.winning_trades} / ${metrics.total_trades}`}
          icon={<Target className="w-5 h-5" />}
          trend="neutral"
        />
      </div>
    </div>
  );
};
