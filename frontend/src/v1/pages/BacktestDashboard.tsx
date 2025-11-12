import React, { useEffect, useState } from 'react';
import { useBacktestStore } from '../stores/backtestStore';
import { BacktestConfigPanel } from '../components/forms/BacktestConfigPanel';
import { PriceChart } from '../components/charts/PriceChart';
import { EquityCurve } from '../components/charts/EquityCurve';
import { MetricsGrid } from '../components/metrics/MetricsGrid';
import { TradesTable } from '../components/metrics/TradesTable';
import { dataAPI } from '../api/client';
import type { OHLCVData } from '../types';

export const BacktestDashboard: React.FC = () => {
  const { backtestResults, symbol, startDate, endDate } = useBacktestStore();
  const [stockData, setStockData] = useState<OHLCVData[]>([]);
  const [loadingStockData, setLoadingStockData] = useState(false);

  // Fetch stock data when symbol or date range changes
  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol || !startDate || !endDate) return;

      setLoadingStockData(true);
      try {
        const response = await dataAPI.getOHLCV(symbol, startDate, endDate);
        setStockData(response.data);
      } catch (error) {
        console.error('Failed to fetch stock data:', error);
        setStockData([]);
      } finally {
        setLoadingStockData(false);
      }
    };

    // Only fetch if we have results (after a backtest has run)
    if (backtestResults) {
      fetchStockData();
    }
  }, [symbol, startDate, endDate, backtestResults]);

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-dark-text mb-2">Backtesting Dashboard</h1>
          <p className="text-dark-muted">
            Configure your backtest parameters, run simulations, and analyze results
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Config Panel */}
          <div className="lg:col-span-1">
            <BacktestConfigPanel />
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {!backtestResults ? (
              <div className="bg-dark-card rounded-lg border border-dark-border p-12 text-center">
                <div className="text-dark-muted mb-4">
                  <svg
                    className="w-20 h-20 mx-auto mb-4 opacity-50"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  <h3 className="text-xl font-semibold text-dark-text mb-2">No Results Yet</h3>
                  <p className="text-sm">
                    Configure your backtest parameters and click "Run Backtest" to see results
                  </p>
                </div>
              </div>
            ) : (
              <>
                {/* Price Chart */}
                {loadingStockData ? (
                  <div className="bg-dark-card rounded-lg border border-dark-border p-12 text-center">
                    <div className="text-dark-muted">Loading chart data...</div>
                  </div>
                ) : (
                  <PriceChart
                    data={stockData}
                    signals={backtestResults.signals}
                    symbol={backtestResults.symbol}
                  />
                )}

                {/* Equity Curve */}
                <EquityCurve
                  data={backtestResults.equity_curve}
                  initialCapital={backtestResults.initial_capital}
                />

                {/* Performance Metrics */}
                <MetricsGrid metrics={backtestResults.metrics} />

                {/* Trades Table */}
                <TradesTable trades={backtestResults.trades} />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
