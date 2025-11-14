import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import type { EquityPoint } from '../../types';
import { LineChart } from 'lucide-react';

interface EquityCurveProps {
  equityCurve: Array<{ date: string; portfolio_value: number }>;
  initialCapital: number;
}

const EquityCurveComponent: React.FC<EquityCurveProps> = ({ equityCurve, initialCapital }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const equitySeriesRef = useRef<any>(null);

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
        timeVisible: true,
      },
      crosshair: {
        mode: 1,
      },
    });

    chartRef.current = chart;

    // Add equity curve (area series)
    const equitySeries = chart.addAreaSeries({
      topColor: '#3b82f680',
      bottomColor: '#3b82f620',
      lineColor: '#3b82f6',
      lineWidth: 2,
    });

    equitySeriesRef.current = equitySeries;

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
    if (!equitySeriesRef.current || !equityCurve.length) return;

    try {
      // Convert equity data to chart format
      const equityData = equityCurve.map((d) => ({
        time: new Date(d.date).getTime() / 1000,
        value: d.portfolio_value,
      }));

      equitySeriesRef.current.setData(equityData);

      // Fit content
      chartRef.current?.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating equity curve:', error);
    }
  }, [equityCurve]);

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <div className="flex items-center gap-2 mb-3">
          <LineChart className="w-4 h-4 text-primary" />
          <h3 className="text-lg font-semibold text-dark-text">Equity Curve</h3>
        </div>
        <div className="h-[300px] flex items-center justify-center text-dark-muted">
          No data to display
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const finalValue = equityCurve[equityCurve.length - 1].portfolio_value;
  const totalReturn = finalValue - initialCapital;
  const totalReturnPct = ((finalValue - initialCapital) / initialCapital) * 100;

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <LineChart className="w-4 h-4 text-primary" />
          <h3 className="text-lg font-semibold text-dark-text">Portfolio Value</h3>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="text-right">
            <div className="text-dark-muted">Return</div>
            <div className={`font-semibold ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {totalReturnPct > 0 ? '+' : ''}
              {totalReturnPct.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
};

// Memoize to prevent unnecessary re-renders when data hasn't changed
export const EquityCurve = React.memo(EquityCurveComponent);
