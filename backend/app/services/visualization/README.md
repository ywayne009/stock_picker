# Strategy Visualization Module

Interactive charting and performance analysis for trading strategies.

## Overview

This module provides professional, interactive visualizations for analyzing trading strategy performance. Built with Plotly, it generates HTML charts with full interactivity (zoom, pan, hover tooltips) that can be viewed in any browser.

## Features

- **Interactive Price Charts**: Candlestick charts with moving averages and trade signals
- **Equity Curves**: Portfolio value over time with drawdown visualization
- **Performance Metrics**: Comprehensive dashboard of strategy statistics
- **Strategy Comparison**: Side-by-side comparison of multiple strategies
- **Complete Dashboards**: All-in-one view combining multiple chart types
- **Export Options**: Save as HTML (interactive), PNG, or PDF

## Quick Start

```python
from app.services.visualization import StrategyVisualizer, calculate_metrics

# Calculate performance metrics
metrics = calculate_metrics(
    signals_df,  # DataFrame with 'signal', 'close' columns
    initial_capital=100000
)

# Create visualizer
viz = StrategyVisualizer(theme='dark', chart_size='large')

# Generate price chart with signals
fig = viz.plot_price_and_signals(
    data,      # Original OHLCV data
    signals,   # Signals DataFrame with MA columns
    strategy_name="My Strategy"
)

# Save chart
viz.export_chart(fig, "output/charts/my_strategy.html")
```

## Installation

Dependencies are already in `requirements.txt`:
```bash
pip install plotly==5.18.0 kaleido==0.2.1
```

## Available Charts

### 1. Price Chart with Signals

Shows candlestick price action with moving averages and buy/sell signals.

```python
fig = viz.plot_price_and_signals(
    data=ohlcv_df,           # OHLCV DataFrame
    signals=signals_df,      # Signals with MA columns
    strategy_name="MA 20/50",
    show_volume=True         # Include volume subplot
)
```

**Features:**
- Candlestick OHLC chart
- Fast & Slow MA overlay lines
- Buy signals (green triangles)
- Sell signals (red triangles)
- Volume subplot
- Interactive hover tooltips
- Range selector (1M, 3M, 6M, YTD, 1Y, All)
- Zoom and pan

**Required DataFrame columns:**
- `data`: 'open', 'high', 'low', 'close', 'volume'
- `signals`: 'close', 'signal', 'fast_ma' (optional), 'slow_ma' (optional)

### 2. Equity Curve

Shows portfolio value evolution over time with drawdown periods.

```python
fig = viz.plot_equity_curve(
    signals=signals_df,
    initial_capital=100000,
    benchmark=spy_data,      # Optional benchmark for comparison
    strategy_name="My Strategy"
)
```

**Features:**
- Portfolio value line chart
- Drawdown shading (red areas)
- Optional benchmark comparison (buy & hold)
- Hover tooltips with exact values
- Shows cumulative returns

### 3. Performance Metrics Dashboard

Grid of key performance indicators.

```python
fig = viz.plot_performance_metrics(
    metrics=metrics,         # PerformanceMetrics object or dict
    strategy_name="My Strategy"
)
```

**Displays:**
- Total Return %
- Win Rate %
- Profit Factor
- Sharpe Ratio
- Max Drawdown %
- Total Trades
- Average Trade $
- Volatility %
- CAGR %

**Color coding:**
- Green: Positive/good values
- Red: Negative/poor values

### 4. Strategy Comparison

Compare multiple strategies side-by-side.

```python
fig = viz.plot_strategy_comparison(
    strategies=[
        {
            "name": "Strategy A",
            "results": results_a,
            "metrics": metrics_a
        },
        {
            "name": "Strategy B",
            "results": results_b,
            "metrics": metrics_b
        }
    ],
    initial_capital=100000
)
```

**Features:**
- Overlaid equity curves
- Side-by-side metrics comparison
- Color-coded strategies
- Bar chart comparison of key metrics

### 5. Complete Dashboard

All-in-one dashboard with tabs.

```python
dashboard_path = viz.create_dashboard(
    data=ohlcv_df,
    signals=signals_df,
    metrics=metrics,
    strategy_name="My Strategy",
    output_path="output/charts/dashboard.html",
    auto_open=True          # Open in browser automatically
)
```

**Features:**
- Tabbed interface
- Summary metrics at top
- Price chart, equity curve, and metrics in tabs
- Professional styling
- Auto-opens in default browser

## Performance Metrics Calculation

Calculate comprehensive strategy statistics:

```python
from app.services.visualization import calculate_metrics

metrics = calculate_metrics(
    signals_df,              # DataFrame with signals
    initial_capital=100000,  # Starting capital
    commission=0.001,        # Commission rate (0.1%)
    risk_free_rate=0.02      # Risk-free rate for Sharpe (2%)
)

# Access metrics
print(f"Total Return: {metrics.total_return * 100:.2f}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Win Rate: {metrics.win_rate * 100:.1f}%")

# Convert to dictionary
metrics_dict = metrics.to_dict()
```

**Calculated Metrics:**

**Returns:**
- Total Return
- CAGR (Compound Annual Growth Rate)
- Total Trades
- Winning/Losing Trades

**Win Rate:**
- Win Rate %
- Profit Factor
- Average Win/Loss
- Largest Win/Loss
- Expectancy

**Risk-Adjusted:**
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown
- Average Drawdown
- Volatility (annualized)

**Trade Statistics:**
- Average Trade Duration
- Max/Min Trade Duration

## Export Options

### HTML (Interactive)
```python
viz.export_chart(fig, "chart.html", format='html')
```
- Fully interactive
- Zoom, pan, hover tooltips
- Can be shared via email
- Opens in any browser
- ~1-2 MB file size

### PNG (Static Image)
```python
viz.export_chart(fig, "chart.png", format='png')
```
- High resolution (2x scale)
- Good for presentations
- ~500 KB file size
- 1600x800 px (large size)

### PDF (Report Ready)
```python
viz.export_chart(fig, "chart.pdf", format='pdf')
```
- Vector graphics
- Print quality
- Good for reports
- Scalable

## Customization

### Themes

Choose between dark and light themes:

```python
# Dark theme (default) - professional, easy on eyes
viz = StrategyVisualizer(theme='dark')

# Light theme - good for printing
viz = StrategyVisualizer(theme='light')
```

### Chart Sizes

Adjust chart dimensions:

```python
viz = StrategyVisualizer(chart_size='small')   # 800x400
viz = StrategyVisualizer(chart_size='medium')  # 1200x600 (default)
viz = StrategyVisualizer(chart_size='large')   # 1600x800
viz = StrategyVisualizer(chart_size='dashboard') # 1400x900
```

### Colors

Default color scheme (configurable in `chart_themes.py`):
- **Bullish candles**: Teal (#26A69A)
- **Bearish candles**: Red (#EF5350)
- **Buy signals**: Bright green (#00E676)
- **Sell signals**: Bright red (#FF1744)
- **Fast MA**: Blue (#2196F3)
- **Slow MA**: Orange (#FF9800)

## Examples

### Example 1: Basic Visualization

```python
from app.services.visualization import StrategyVisualizer, calculate_metrics
import pandas as pd

# Assuming you have data and signals DataFrames
viz = StrategyVisualizer()
metrics = calculate_metrics(signals, initial_capital=100000)

# Create and save price chart
fig = viz.plot_price_and_signals(data, signals, "My Strategy")
viz.export_chart(fig, "output/charts/price_chart.html")
```

### Example 2: Complete Analysis

```python
# Calculate metrics
metrics = calculate_metrics(signals, initial_capital=100000)

# Create visualizer
viz = StrategyVisualizer(theme='dark', chart_size='large')

# Generate all chart types
price_fig = viz.plot_price_and_signals(data, signals, "Strategy")
equity_fig = viz.plot_equity_curve(signals, strategy_name="Strategy")
metrics_fig = viz.plot_performance_metrics(metrics, "Strategy")

# Save all charts
viz.export_chart(price_fig, "output/charts/price.html")
viz.export_chart(equity_fig, "output/charts/equity.html")
viz.export_chart(metrics_fig, "output/charts/metrics.html")

# Or create a complete dashboard
viz.create_dashboard(
    data, signals, metrics,
    strategy_name="My Strategy",
    output_path="output/charts/dashboard.html",
    auto_open=True
)
```

### Example 3: Compare Multiple Strategies

```python
# Run multiple strategies
results1 = strategy1.generate_signals(data)
results2 = strategy2.generate_signals(data)
results3 = strategy3.generate_signals(data)

# Calculate metrics
metrics1 = calculate_metrics(results1, initial_capital=100000)
metrics2 = calculate_metrics(results2, initial_capital=100000)
metrics3 = calculate_metrics(results3, initial_capital=100000)

# Create comparison chart
viz = StrategyVisualizer()
fig = viz.plot_strategy_comparison([
    {"name": "Conservative", "results": results1, "metrics": metrics1},
    {"name": "Moderate", "results": results2, "metrics": metrics2},
    {"name": "Aggressive", "results": results3, "metrics": metrics3}
])

viz.export_chart(fig, "output/charts/comparison.html")
```

## Integration with Demo Script

The `demo_strategy.py` automatically generates all visualizations:

```bash
cd backend
source venv/bin/activate
python demo_strategy.py
```

This will:
1. Run three different strategies
2. Calculate performance metrics
3. Generate 5 interactive charts
4. Auto-open dashboard in browser
5. Print key metrics to console

Generated files:
- `output/charts/ma_20_50_signals.html` - Price with signals
- `output/charts/ma_20_50_equity.html` - Equity curve
- `output/charts/ma_20_50_metrics.html` - Metrics dashboard
- `output/charts/strategy_comparison.html` - All strategies compared
- `output/charts/ma_20_50_dashboard.html` - Complete dashboard

## API Reference

### StrategyVisualizer Class

```python
class StrategyVisualizer(theme='dark', chart_size='medium')
```

**Methods:**

- `plot_price_and_signals(data, signals, strategy_name, show_volume)` → Figure
- `plot_equity_curve(signals, initial_capital, benchmark, strategy_name)` → Figure
- `plot_performance_metrics(metrics, strategy_name)` → Figure
- `plot_strategy_comparison(strategies, initial_capital)` → Figure
- `create_dashboard(data, signals, metrics, strategy_name, output_path, auto_open)` → str
- `export_chart(figure, filename, format)` → None

### calculate_metrics Function

```python
calculate_metrics(
    signals_df: pd.DataFrame,
    initial_capital: float = 100000.0,
    commission: float = 0.001,
    risk_free_rate: float = 0.02
) → PerformanceMetrics
```

### PerformanceMetrics Class

Dataclass with all calculated metrics. Access as attributes:

```python
metrics.total_return       # 0.15 = 15% return
metrics.sharpe_ratio       # 1.5
metrics.win_rate           # 0.6 = 60% win rate
metrics.max_drawdown       # 0.1 = 10% drawdown
# ... and many more
```

## File Structure

```
app/services/visualization/
├── __init__.py              # Module exports
├── strategy_charts.py       # StrategyVisualizer class
├── performance_metrics.py   # Metrics calculation
├── chart_themes.py          # Color schemes and styling
└── README.md                # This file
```

## Output Directory

Charts are saved to:
```
backend/output/charts/
```

These files are gitignored and not committed to the repository.

## Future Enhancements

Planned features:
- Real-time chart updates via WebSocket
- Custom indicator overlays
- Heatmaps for parameter optimization
- Correlation analysis charts
- Risk/return scatter plots
- Trade analysis (duration, size distribution)
- Integration with backtesting engine
- API endpoints to serve chart data to frontend

## Troubleshooting

**Charts not generating:**
- Ensure plotly and kaleido are installed: `pip install plotly kaleido`
- Check that output/charts/ directory exists
- Verify signals DataFrame has required columns

**Charts look wrong:**
- Check DataFrame index is DatetimeIndex
- Ensure 'signal' column has values 1, 0, -1
- Verify OHLCV data is complete (no NaN values)

**Browser doesn't open:**
- Set `auto_open=False` and manually open the HTML file
- Check browser settings allow local file access

**Export fails:**
- For PNG/PDF: Ensure kaleido is installed correctly
- Try exporting to HTML first to verify chart is valid

## Support

For issues or questions:
1. Check the examples in this README
2. Run `demo_strategy.py` to see working implementation
3. Review the code in `strategy_charts.py` for advanced usage
