/**
 * BacktestDashboardV2 - High-density multi-stock multi-strategy comparison dashboard
 */
import React, { useState, useEffect } from 'react';
import { ComparisonMatrix } from '../components/comparison/ComparisonMatrix';
import { ParameterTuningModal } from '../components/comparison/ParameterTuningModal';
import { DetailedCellView } from '../components/comparison/DetailedCellView';
import { useComparisonStore } from '../stores/comparisonStore';
import { dataAPI } from '../api/client';

export const BacktestDashboardV2: React.FC = () => {
  const {
    selectedCell,
    selectedCellFullResults,
    selectedCellLoading,
    clearSelection,
    tuningCell,
    closeTuning,
    updateCellParameters,
    startDate,
    endDate,
  } = useComparisonStore();

  const [stockData, setStockData] = useState<any>(null);

  // Fetch stock data when a cell is selected
  useEffect(() => {
    if (selectedCell && selectedCellFullResults) {
      const fetchStockData = async () => {
        try {
          const data = await dataAPI.getOHLCV(
            selectedCell.symbol,
            startDate,
            endDate,
            '1d'
          );
          setStockData(data);
        } catch (error) {
          console.error('Failed to fetch stock data:', error);
          setStockData(null);
        }
      };
      fetchStockData();
    } else {
      setStockData(null);
    }
  }, [selectedCell, selectedCellFullResults, startDate, endDate]);

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
          <DetailedCellView
            cell={selectedCell}
            fullResults={selectedCellFullResults}
            isLoading={selectedCellLoading}
            stockData={stockData}
            onClose={clearSelection}
          />
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
            <li>• Click completed cells to view detailed results with charts and trade history</li>
            <li>• Green = profitable, Red = loss, higher Sharpe Ratio = better risk-adjusted returns</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
