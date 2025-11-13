import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { TrendingDown } from 'lucide-react';

interface DrawdownChartProps {
  equityCurve: Array<{ date: string; portfolio_value: number }>;
  initialCapital: number;
}

export const DrawdownChart: React.FC<DrawdownChartProps> = ({ equityCurve, initialCapital }) => {
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
        timeVisible: true,
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
    if (!chartRef.current || !equityCurve.length) return;

    try {
      // Calculate drawdown
      let peak = initialCapital;
      const drawdownData = equityCurve.map((point) => {
        const value = point.portfolio_value;
        if (value > peak) {
          peak = value;
        }
        const drawdown = ((value - peak) / peak) * 100; // As percentage
        return {
          time: new Date(point.date).getTime() / 1000,
          value: drawdown,
        };
      });

      // Add area series for drawdown
      const areaSeries = chartRef.current.addAreaSeries({
        lineColor: '#ef4444',
        topColor: '#ef444420',
        bottomColor: '#ef444405',
        lineWidth: 2,
      });

      areaSeries.setData(drawdownData);

      // Fit content
      chartRef.current.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating drawdown chart:', error);
    }
  }, [equityCurve, initialCapital]);

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <div className="flex items-center gap-2 mb-3">
          <TrendingDown className="w-4 h-4 text-danger" />
          <h3 className="text-lg font-semibold text-dark-text">Drawdown Chart</h3>
        </div>
        <div className="h-[300px] flex items-center justify-center text-dark-muted">
          No data to display
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center gap-2 mb-3">
        <TrendingDown className="w-4 h-4 text-danger" />
        <h3 className="text-lg font-semibold text-dark-text">Drawdown Over Time</h3>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
};
