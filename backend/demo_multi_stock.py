"""
Multi-Stock Strategy Comparison Demo

This demo runs the Moving Average Crossover strategy on multiple stocks
and creates compact, comparative visualizations to analyze performance
across different assets.

Stocks tested: AAPL, MSFT, TSLA, NVDA, META, AMZN
Strategy: MA 20/50 SMA (balanced swing trading approach)
"""
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

from app.services.strategy.examples.ma_crossover import MovingAverageCrossover
from app.services.data import fetch_demo_stock
from app.services.visualization import StrategyVisualizer, calculate_metrics
from app.services.visualization.performance_metrics import _simulate_portfolio


# Configuration
STOCKS = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN']
YEARS_BACK = 2.5  # 30 months of data

# Strategy configuration - balanced approach for all stocks
STRATEGY_CONFIG = {
    'name': 'MA Crossover 20/50',
    'parameters': {
        'fast_period': 20,      # Short-term trend (1 month)
        'slow_period': 50,      # Medium-term trend (2.5 months)
        'ma_type': 'sma',       # Simple MA for stability
        'position_size': 0.1,   # 10% position size
        'stop_loss': 0.05,      # 5% stop loss
        'take_profit': 0.15     # 15% take profit target
    }
}

INITIAL_CAPITAL = 100000  # $100k starting capital


def run_backtest_on_stock(ticker: str, years_back: float = 2.5) -> Dict[str, Any]:
    """
    Run backtest on a single stock.

    Args:
        ticker: Stock symbol
        years_back: Years of historical data to fetch

    Returns:
        Dictionary with stock info, data, signals, and metrics
    """
    print(f"\n{'='*80}")
    print(f"  Processing: {ticker}")
    print(f"{'='*80}")

    try:
        # Fetch data
        print(f"  📊 Fetching data...")
        data, stock_info = fetch_demo_stock(ticker, years_back=years_back)
        print(f"     → {len(data)} days from {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

        # Run strategy
        print(f"  🎯 Running strategy...")
        strategy = MovingAverageCrossover(STRATEGY_CONFIG)
        strategy.setup(data)
        signals = strategy.generate_signals(data)

        # Calculate metrics
        print(f"  📈 Calculating metrics...")
        metrics = calculate_metrics(signals, initial_capital=INITIAL_CAPITAL)

        # Count signals
        buy_signals = len(signals[signals['signal'] == 1])
        sell_signals = len(signals[signals['signal'] == -1])
        total_signals = buy_signals + sell_signals

        print(f"     → Buy signals: {buy_signals}")
        print(f"     → Sell signals: {sell_signals}")
        print(f"     → Total return: {metrics.total_return * 100:.2f}%")
        print(f"     → Sharpe ratio: {metrics.sharpe_ratio:.2f}")
        print(f"     ✓ Complete")

        return {
            'ticker': ticker,
            'stock_info': stock_info,
            'data': data,
            'signals': signals,
            'metrics': metrics,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': total_signals
        }

    except Exception as e:
        print(f"     ✗ Error: {e}")
        return None


def print_summary_table(results: List[Dict[str, Any]]) -> None:
    """Print a summary table comparing all stocks."""
    print(f"\n{'='*100}")
    print(f"  MULTI-STOCK PERFORMANCE SUMMARY")
    print(f"{'='*100}\n")

    # Header
    print(f"{'Stock':<8} {'Company':<20} {'Return %':<12} {'CAGR %':<10} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<10}")
    print("-" * 100)

    # Data rows
    for result in results:
        if result:
            m = result['metrics']
            ticker = result['ticker']
            company = result['stock_info']['name'][:18]  # Truncate long names

            print(f"{ticker:<8} {company:<20} "
                  f"{m.total_return * 100:>10.2f}% "
                  f"{m.cagr * 100:>9.2f}% "
                  f"{m.sharpe_ratio:>9.2f} "
                  f"{m.max_drawdown * 100:>10.2f}% "
                  f"{m.total_trades:>9}")

    print()

    # Calculate best performers
    valid_results = [r for r in results if r is not None]
    if valid_results:
        best_return = max(valid_results, key=lambda x: x['metrics'].total_return)
        best_sharpe = max(valid_results, key=lambda x: x['metrics'].sharpe_ratio)
        lowest_dd = min(valid_results, key=lambda x: x['metrics'].max_drawdown)

        print("🏆 Best Performers:")
        print(f"   Highest Return:  {best_return['ticker']} ({best_return['metrics'].total_return * 100:.2f}%)")
        print(f"   Best Sharpe:     {best_sharpe['ticker']} ({best_sharpe['metrics'].sharpe_ratio:.2f})")
        print(f"   Lowest Drawdown: {lowest_dd['ticker']} ({lowest_dd['metrics'].max_drawdown * 100:.2f}%)")
        print()


def create_multi_stock_comparison(results: List[Dict[str, Any]], output_dir: str = "output/charts") -> None:
    """
    Create comprehensive comparison charts for all stocks.

    Args:
        results: List of backtest results for each stock
        output_dir: Directory to save charts
    """
    print(f"\n{'='*80}")
    print(f"  GENERATING COMPARATIVE VISUALIZATIONS")
    print(f"{'='*80}\n")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Use dark theme and compact size
    viz = StrategyVisualizer(theme='dark', chart_size='large')

    valid_results = [r for r in results if r is not None]

    # Chart 1: Equity curves comparison (all stocks on one chart)
    print("  📊 Creating multi-stock equity comparison...")
    equity_fig = create_equity_comparison_chart(valid_results, viz)
    viz.export_chart(equity_fig, f"{output_dir}/multi_stock_equity_comparison.html")

    # Chart 2: Performance metrics comparison (bar charts)
    print("  📊 Creating performance metrics comparison...")
    metrics_fig = create_metrics_comparison_chart(valid_results, viz)
    viz.export_chart(metrics_fig, f"{output_dir}/multi_stock_metrics_comparison.html")

    # Chart 3: Individual stock dashboards (compact)
    print("  📊 Creating individual stock charts...")
    for result in valid_results:
        ticker = result['ticker']
        print(f"     → {ticker}")

        # Price chart with signals
        price_fig = viz.plot_price_and_signals(
            result['data'],
            result['signals'],
            strategy_name=f"{ticker} - MA 20/50 SMA",
            show_volume=True
        )
        viz.export_chart(price_fig, f"{output_dir}/{ticker.lower()}_signals.html")

    # Chart 4: Combined dashboard (all key info in one view)
    print("  📊 Creating unified dashboard...")
    dashboard_fig = create_unified_dashboard(valid_results, viz)
    viz.export_chart(dashboard_fig, f"{output_dir}/multi_stock_dashboard.html")

    print(f"\n✅ Visualizations complete!")
    print(f"\n📁 Generated files in {output_dir}/:")
    print(f"   • multi_stock_equity_comparison.html  - All equity curves overlaid")
    print(f"   • multi_stock_metrics_comparison.html - Performance metrics bars")
    print(f"   • multi_stock_dashboard.html          - Unified comparison dashboard")
    for result in valid_results:
        print(f"   • {result['ticker'].lower()}_signals.html                      - {result['ticker']} price chart with signals")

    # Auto-open the unified dashboard
    print(f"\n📈 Opening unified dashboard in browser...")
    from app.services.visualization.strategy_charts import open_in_browser
    open_in_browser(f"{output_dir}/multi_stock_dashboard.html")


def create_equity_comparison_chart(results: List[Dict[str, Any]], viz: StrategyVisualizer):
    """Create overlaid equity curves for all stocks."""
    import plotly.graph_objects as go

    fig = go.Figure()

    # Define colors for each stock
    colors = ['#00D9FF', '#FF6B9D', '#C0FF00', '#FFB800', '#9D00FF', '#FF3838']

    for i, result in enumerate(results):
        ticker = result['ticker']
        signals = result['signals']

        # Simulate portfolio to get equity curve
        portfolio_history = _simulate_portfolio(signals, INITIAL_CAPITAL, commission=0.001)
        equity = portfolio_history['portfolio_value']

        fig.add_trace(go.Scatter(
            x=signals.index,
            y=equity,
            mode='lines',
            name=ticker,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'<b>{ticker}</b><br>Date: %{{x|%Y-%m-%d}}<br>Equity: $%{{y:,.0f}}<extra></extra>'
        ))

    # Add benchmark (buy & hold starting capital)
    fig.add_trace(go.Scatter(
        x=[results[0]['signals'].index[0], results[0]['signals'].index[-1]],
        y=[INITIAL_CAPITAL, INITIAL_CAPITAL],
        mode='lines',
        name='Initial Capital',
        line=dict(color='#888888', width=1, dash='dash'),
        showlegend=True
    ))

    fig.update_layout(
        title={
            'text': 'Multi-Stock Equity Curve Comparison<br><sub>MA 20/50 SMA Strategy</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#FFFFFF'}
        },
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified',
        template='plotly_dark',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='#FFFFFF', size=12)
    )

    # Format y-axis as currency
    fig.update_yaxes(tickformat='$,.0f')

    return fig


def create_metrics_comparison_chart(results: List[Dict[str, Any]], viz: StrategyVisualizer):
    """Create bar charts comparing key metrics across stocks."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    tickers = [r['ticker'] for r in results]
    colors = ['#00D9FF', '#FF6B9D', '#C0FF00', '#FFB800', '#9D00FF', '#FF3838']

    # Extract metrics
    returns = [r['metrics'].total_return * 100 for r in results]
    sharpe = [r['metrics'].sharpe_ratio for r in results]
    max_dd = [r['metrics'].max_drawdown * 100 for r in results]
    win_rate = [r['metrics'].win_rate * 100 for r in results]

    # Create subplots: 2x2 grid
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Total Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)', 'Win Rate (%)'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Total Return
    fig.add_trace(go.Bar(
        x=tickers, y=returns,
        marker_color=colors[:len(tickers)],
        text=[f"{v:.1f}%" for v in returns],
        textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
    ), row=1, col=1)

    # Sharpe Ratio
    fig.add_trace(go.Bar(
        x=tickers, y=sharpe,
        marker_color=colors[:len(tickers)],
        text=[f"{v:.2f}" for v in sharpe],
        textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Sharpe: %{y:.2f}<extra></extra>'
    ), row=1, col=2)

    # Max Drawdown (negative values, so use abs for display)
    fig.add_trace(go.Bar(
        x=tickers, y=max_dd,
        marker_color=colors[:len(tickers)],
        text=[f"{v:.1f}%" for v in max_dd],
        textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Max DD: %{y:.2f}%<extra></extra>'
    ), row=2, col=1)

    # Win Rate
    fig.add_trace(go.Bar(
        x=tickers, y=win_rate,
        marker_color=colors[:len(tickers)],
        text=[f"{v:.1f}%" for v in win_rate],
        textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<extra></extra>'
    ), row=2, col=2)

    fig.update_layout(
        title={
            'text': 'Performance Metrics Comparison<br><sub>MA 20/50 SMA Strategy</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#FFFFFF'}
        },
        template='plotly_dark',
        height=700,
        showlegend=False,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='#FFFFFF', size=12)
    )

    return fig


def create_unified_dashboard(results: List[Dict[str, Any]], viz: StrategyVisualizer):
    """Create a unified dashboard with all key information in one compact view."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create 2x2 subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Equity Curves - All Stocks',
            'Total Returns Comparison',
            'Risk Metrics (Sharpe & Max Drawdown)',
            'Trade Statistics'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "table"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
        row_heights=[0.55, 0.45]
    )

    tickers = [r['ticker'] for r in results]
    colors = ['#00D9FF', '#FF6B9D', '#C0FF00', '#FFB800', '#9D00FF', '#FF3838']

    # 1. Equity curves (top left)
    for i, result in enumerate(results):
        ticker = result['ticker']
        signals = result['signals']

        # Simulate portfolio to get equity curve
        portfolio_history = _simulate_portfolio(signals, INITIAL_CAPITAL, commission=0.001)
        equity = portfolio_history['portfolio_value']

        fig.add_trace(go.Scatter(
            x=signals.index,
            y=equity,
            mode='lines',
            name=ticker,
            line=dict(color=colors[i], width=2),
            legendgroup='stocks',
            showlegend=True
        ), row=1, col=1)

    # 2. Total returns (top right)
    returns = [r['metrics'].total_return * 100 for r in results]
    fig.add_trace(go.Bar(
        x=tickers,
        y=returns,
        marker_color=colors[:len(tickers)],
        text=[f"{v:.1f}%" for v in returns],
        textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>%{y:.2f}%<extra></extra>'
    ), row=1, col=2)

    # 3. Risk metrics - grouped bar (bottom left)
    sharpe = [r['metrics'].sharpe_ratio for r in results]
    max_dd_abs = [abs(r['metrics'].max_drawdown * 100) for r in results]

    fig.add_trace(go.Bar(
        x=tickers,
        y=sharpe,
        name='Sharpe Ratio',
        marker_color='#00D9FF',
        showlegend=True,
        legendgroup='metrics'
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=tickers,
        y=max_dd_abs,
        name='Max DD (abs %)',
        marker_color='#FF6B9D',
        showlegend=True,
        legendgroup='metrics'
    ), row=2, col=1)

    # 4. Summary table (bottom right)
    table_data = []
    for result in results:
        m = result['metrics']
        table_data.append([
            result['ticker'],
            f"{m.total_return * 100:.1f}%",
            f"{m.sharpe_ratio:.2f}",
            f"{m.max_drawdown * 100:.1f}%",
            f"{m.win_rate * 100:.0f}%",
            str(m.total_trades)
        ])

    fig.add_trace(go.Table(
        header=dict(
            values=['<b>Stock</b>', '<b>Return</b>', '<b>Sharpe</b>', '<b>Max DD</b>', '<b>Win %</b>', '<b>Trades</b>'],
            fill_color='#1E1E1E',
            align='center',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=list(zip(*table_data)),
            fill_color='#0E1117',
            align='center',
            font=dict(color='white', size=11),
            height=25
        )
    ), row=2, col=2)

    # Update layout
    fig.update_layout(
        title={
            'text': 'Multi-Stock Strategy Dashboard<br><sub>MA 20/50 SMA - Comprehensive Performance Overview</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#FFFFFF'}
        },
        template='plotly_dark',
        height=900,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='#FFFFFF', size=11),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5
        ),
        barmode='group'
    )

    # Update axes
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Equity ($)", tickformat='$,.0f', row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=2)
    fig.update_yaxes(title_text="Value", row=2, col=1)

    return fig


def main():
    """Main execution function."""
    print("\n" + "="*100)
    print("  MULTI-STOCK MOVING AVERAGE CROSSOVER STRATEGY DEMO")
    print("="*100)

    print(f"\n📊 Configuration:")
    print(f"   Stocks: {', '.join(STOCKS)}")
    print(f"   Strategy: MA {STRATEGY_CONFIG['parameters']['fast_period']}/{STRATEGY_CONFIG['parameters']['slow_period']} {STRATEGY_CONFIG['parameters']['ma_type'].upper()}")
    print(f"   Period: {YEARS_BACK} years")
    print(f"   Initial Capital: ${INITIAL_CAPITAL:,}")

    # Run backtests on all stocks
    print(f"\n{'='*100}")
    print(f"  RUNNING BACKTESTS")
    print(f"{'='*100}")

    results = []
    for ticker in STOCKS:
        result = run_backtest_on_stock(ticker, years_back=YEARS_BACK)
        if result:
            results.append(result)

    if not results:
        print("\n❌ No successful backtests. Please check data availability.")
        return

    # Print summary
    print_summary_table(results)

    # Create visualizations
    create_multi_stock_comparison(results)

    print(f"\n{'='*100}")
    print(f"  DEMO COMPLETE!")
    print(f"{'='*100}\n")
    print(f"✅ Successfully backtested {len(results)}/{len(STOCKS)} stocks")
    print(f"✅ Generated comparative visualizations")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the unified dashboard in your browser")
    print(f"   2. Analyze which stocks perform best with this strategy")
    print(f"   3. Consider adjusting parameters for different asset classes")
    print(f"   4. Explore individual stock charts for detailed signal analysis\n")


if __name__ == '__main__':
    main()
