/**
 * ParameterTuningModal - Modal for tuning strategy parameters
 */
import React, { useState } from 'react';
import { X, Play } from 'lucide-react';
import type { MatrixCell } from '../../types/comparison';

interface ParameterTuningModalProps {
  cell: MatrixCell;
  onClose: () => void;
  onApplyAndRun: (updatedParams: Record<string, any>) => void;
}

export const ParameterTuningModal: React.FC<ParameterTuningModalProps> = ({
  cell,
  onClose,
  onApplyAndRun,
}) => {
  const [parameters, setParameters] = useState<Record<string, any>>(
    cell.strategy.parameters || {}
  );

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({ ...prev, [paramName]: value }));
  };

  const handleApply = () => {
    onApplyAndRun(parameters);
    onClose();
  };

  // Get parameter metadata if available (from strategy definition)
  const getParameterMeta = (paramName: string) => {
    // This would ideally come from the backend strategy definition
    // For now, we'll use some sensible defaults based on parameter name
    const defaults: Record<string, any> = {
      fast_period: { min: 2, max: 100, step: 1, type: 'number' },
      slow_period: { min: 5, max: 300, step: 1, type: 'number' },
      rsi_period: { min: 5, max: 50, step: 1, type: 'number' },
      oversold: { min: 10, max: 40, step: 1, type: 'number' },
      overbought: { min: 60, max: 90, step: 1, type: 'number' },
      bb_period: { min: 10, max: 50, step: 1, type: 'number' },
      bb_std: { min: 1, max: 3, step: 0.1, type: 'number' },
      signal_period: { min: 5, max: 20, step: 1, type: 'number' },
      position_size: { min: 0.01, max: 1.0, step: 0.01, type: 'number', label: 'Position Size (%)' },
      stop_loss: { min: 0.0, max: 0.5, step: 0.01, type: 'number', label: 'Stop Loss (%)' },
      take_profit: { min: 0.0, max: 2.0, step: 0.01, type: 'number', label: 'Take Profit (%)' },
      ma_type: { type: 'select', options: ['sma', 'ema'] },
    };
    return defaults[paramName] || { min: 0, max: 100, step: 1, type: 'number' };
  };

  const formatLabel = (paramName: string): string => {
    const meta = getParameterMeta(paramName);
    if (meta.label) return meta.label;

    // Convert snake_case to Title Case
    return paramName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-6 z-50"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
      onClick={onClose}
    >
      <div
        className="rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-2xl"
        style={{ backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: '1px' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="sticky top-0 px-6 py-4 flex items-center justify-between"
          style={{
            backgroundColor: '#1e293b',
            borderBottomColor: '#334155',
            borderBottomWidth: '1px'
          }}
        >
          <div>
            <h2 className="text-xl font-bold" style={{ color: '#f1f5f9' }}>
              Tune Parameters
            </h2>
            <p className="text-sm mt-1" style={{ color: '#94a3b8' }}>
              {cell.symbol} - {cell.strategy.name}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors hover:opacity-80"
            style={{ backgroundColor: '#0f172a' }}
          >
            <X className="w-5 h-5" style={{ color: '#94a3b8' }} />
          </button>
        </div>

        {/* Parameters Form */}
        <div className="p-6 space-y-4">
          {Object.entries(parameters).map(([paramName, paramValue]) => {
            const meta = getParameterMeta(paramName);

            return (
              <div key={paramName}>
                <label className="block text-sm font-medium mb-2" style={{ color: '#f1f5f9' }}>
                  {formatLabel(paramName)}
                </label>

                {meta.type === 'select' ? (
                  <select
                    value={String(paramValue)}
                    onChange={(e) => handleParameterChange(paramName, e.target.value)}
                    className="w-full px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2"
                    style={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderWidth: '1px',
                      color: '#f1f5f9'
                    }}
                  >
                    {meta.options.map((opt: string) => (
                      <option key={opt} value={opt}>
                        {opt.toUpperCase()}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="space-y-2">
                    <input
                      type="range"
                      min={meta.min}
                      max={meta.max}
                      step={meta.step}
                      value={Number(paramValue)}
                      onChange={(e) => handleParameterChange(paramName, Number(e.target.value))}
                      className="w-full"
                      style={{ accentColor: '#3b82f6' }}
                    />
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min={meta.min}
                        max={meta.max}
                        step={meta.step}
                        value={Number(paramValue)}
                        onChange={(e) => handleParameterChange(paramName, Number(e.target.value))}
                        className="w-24 px-3 py-1 rounded-lg text-sm focus:outline-none focus:ring-2"
                        style={{
                          backgroundColor: '#0f172a',
                          borderColor: '#334155',
                          borderWidth: '1px',
                          color: '#f1f5f9'
                        }}
                      />
                      <span className="text-xs" style={{ color: '#94a3b8' }}>
                        Range: {meta.min} - {meta.max}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div
          className="sticky bottom-0 px-6 py-4 flex items-center justify-end gap-3"
          style={{
            backgroundColor: '#1e293b',
            borderTopColor: '#334155',
            borderTopWidth: '1px'
          }}
        >
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg transition-colors hover:opacity-80"
            style={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderWidth: '1px',
              color: '#f1f5f9'
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors hover:opacity-90"
            style={{ backgroundColor: '#3b82f6', color: '#ffffff' }}
          >
            <Play className="w-4 h-4" />
            Apply & Run
          </button>
        </div>
      </div>
    </div>
  );
};
