import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import type { EquityPoint } from '../../types';
import { LineChart } from 'lucide-react';

interface EquityCurveProps {
  data: EquityPoint[];
  initialCapital: number;
}

export const EquityCurve: React.FC<EquityCurveProps> = ({ data, initialCapital }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const equitySeriesRef = useRef<any>(null);
  const drawdownSeriesRef = useRef<any>(null);

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
      height: 400,
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

    // Add drawdown line (on separate scale)
    const drawdownSeries = chart.addLineSeries({
      color: '#ef4444',
      lineWidth: 2,
      priceScaleId: 'right',
    });

    drawdownSeriesRef.current = drawdownSeries;

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
    if (!equitySeriesRef.current || !drawdownSeriesRef.current || !data.length) return;

    try {
      // Convert equity data to chart format
      const equityData = data.map((d) => ({
        time: new Date(d.date).getTime() / 1000,
        value: d.portfolio_value,
      }));

      const drawdownData = data.map((d) => ({
        time: new Date(d.date).getTime() / 1000,
        value: d.drawdown_pct,
      }));

      equitySeriesRef.current.setData(equityData);
      drawdownSeriesRef.current.setData(drawdownData);

      // Fit content
      chartRef.current?.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating equity curve:', error);
    }
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <LineChart className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Equity Curve</h2>
        </div>
        <div className="h-[400px] flex items-center justify-center text-dark-muted">
          No data to display. Run a backtest to see the equity curve.
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const finalValue = data[data.length - 1].portfolio_value;
  const totalReturn = finalValue - initialCapital;
  const totalReturnPct = ((finalValue - initialCapital) / initialCapital) * 100;
  const maxDrawdown = Math.min(...data.map((d) => d.drawdown_pct));

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Equity Curve</h2>
        </div>
        <div className="flex items-center gap-6 text-sm">
          <div className="text-right">
            <div className="text-dark-muted">Initial Capital</div>
            <div className="text-dark-text font-semibold">
              ${initialCapital.toLocaleString()}
            </div>
          </div>
          <div className="text-right">
            <div className="text-dark-muted">Final Value</div>
            <div className={`font-semibold ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              ${finalValue.toLocaleString()}
            </div>
          </div>
          <div className="text-right">
            <div className="text-dark-muted">Return</div>
            <div className={`font-semibold ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {totalReturnPct > 0 ? '+' : ''}
              {totalReturnPct.toFixed(2)}%
            </div>
          </div>
          <div className="text-right">
            <div className="text-dark-muted">Max Drawdown</div>
            <div className="text-danger font-semibold">{maxDrawdown.toFixed(2)}%</div>
          </div>
        </div>
      </div>
      <div ref={chartContainerRef} />
      <div className="flex items-center gap-4 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded"></div>
          <span className="text-dark-muted">Portfolio Value</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-danger rounded"></div>
          <span className="text-dark-muted">Drawdown %</span>
        </div>
      </div>
    </div>
  );
};
