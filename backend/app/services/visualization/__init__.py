"""
Visualization Module

Provides interactive charts and dashboards for strategy analysis and backtesting.

Main components:
- StrategyVisualizer: Create interactive charts for strategies
- calculate_metrics: Compute performance metrics
- Chart themes and styling options
"""
from .strategy_charts import StrategyVisualizer
from .performance_metrics import calculate_metrics, PerformanceMetrics

__all__ = [
    'StrategyVisualizer',
    'calculate_metrics',
    'PerformanceMetrics'
]
