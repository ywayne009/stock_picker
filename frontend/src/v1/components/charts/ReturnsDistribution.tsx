import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { BarChart3 } from 'lucide-react';
import type { Trade } from '../../types';

interface ReturnsDistributionProps {
  trades: Trade[];
}

export const ReturnsDistribution: React.FC<ReturnsDistributionProps> = ({ trades }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1e293b' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#334155' },
        horzLines: { color: '#334155' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      rightPriceScale: {
        borderColor: '#334155',
      },
      timeScale: {
        borderColor: '#334155',
        visible: false,
      },
    });

    chartRef.current = chart;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current || !trades.length) return;

    try {
      // Get all return percentages
      const returns = trades.map(t => t.profit_loss_pct);

      // Create histogram bins
      const numBins = 20;
      const minReturn = Math.min(...returns);
      const maxReturn = Math.max(...returns);
      const binWidth = (maxReturn - minReturn) / numBins;

      // Initialize bins
      const bins: { [key: number]: number } = {};
      for (let i = 0; i < numBins; i++) {
        bins[i] = 0;
      }

      // Count returns in each bin
      returns.forEach(ret => {
        const binIndex = Math.min(Math.floor((ret - minReturn) / binWidth), numBins - 1);
        bins[binIndex]++;
      });

      // Convert to chart data
      const histogramData = Object.keys(bins).map((binIndex) => {
        const idx = parseInt(binIndex);
        const binStart = minReturn + idx * binWidth;
        const count = bins[idx];
        const color = binStart >= 0 ? '#10b981' : '#ef4444';

        return {
          time: idx,
          value: count,
          color,
        };
      });

      // Add histogram series
      const histogramSeries = chartRef.current.addHistogramSeries({
        priceFormat: {
          type: 'volume',
        },
      });

      histogramSeries.setData(histogramData);

      // Fit content
      chartRef.current.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating returns distribution chart:', error);
    }
  }, [trades]);

  if (!trades || trades.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-4 h-4 text-primary" />
          <h3 className="text-lg font-semibold text-dark-text">Returns Distribution</h3>
        </div>
        <div className="h-[300px] flex items-center justify-center text-dark-muted">
          No trades to display
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-primary" />
          <h3 className="text-lg font-semibold text-dark-text">Returns Distribution</h3>
        </div>
        <div className="text-xs text-dark-muted">
          {trades.length} trades
        </div>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
};
