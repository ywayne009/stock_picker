import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import type { OHLCVData, TradeSignal } from '../../types';
import { TrendingUp } from 'lucide-react';

interface PriceChartProps {
  data: OHLCVData[];
  signals?: TradeSignal[];
  symbol: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ data, signals = [], symbol }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);

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

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    volumeSeriesRef.current = volumeSeries;

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
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || !data.length) return;

    try {
      // Convert OHLCV data to chart format
      const candleData = data.map((d) => ({
        time: new Date(d.date).getTime() / 1000,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }));

      const volumeData = data.map((d) => ({
        time: new Date(d.date).getTime() / 1000,
        value: d.volume,
        color: d.close >= d.open ? '#10b98180' : '#ef444480',
      }));

      candlestickSeriesRef.current.setData(candleData);
      volumeSeriesRef.current.setData(volumeData);

      // Add markers for buy/sell signals
      if (signals.length > 0 && candlestickSeriesRef.current) {
        const markers = signals
          .filter((s) => s.signal_type === 'BUY' || s.signal_type === 'SELL')
          .map((signal) => ({
            time: new Date(signal.date).getTime() / 1000,
            position: signal.signal_type === 'BUY' ? 'belowBar' : 'aboveBar',
            color: signal.signal_type === 'BUY' ? '#10b981' : '#ef4444',
            shape: signal.signal_type === 'BUY' ? 'arrowUp' : 'arrowDown',
            text: signal.signal_type,
          }));

        candlestickSeriesRef.current.setMarkers(markers);
      }

      // Fit content
      chartRef.current?.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating price chart:', error);
    }
  }, [data, signals]);

  if (!data || data.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Price Chart</h2>
        </div>
        <div className="h-[400px] flex items-center justify-center text-dark-muted">
          No data to display. Run a backtest to see the chart.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold text-dark-text">Price Chart - {symbol}</h2>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-success rounded"></div>
            <span className="text-dark-muted">Buy Signal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-danger rounded"></div>
            <span className="text-dark-muted">Sell Signal</span>
          </div>
        </div>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
};
