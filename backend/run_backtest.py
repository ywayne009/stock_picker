"""
Universal Backtest Runner

This is your main entry point for running backtests.

USAGE:
------

1. SINGLE STOCK, SINGLE STRATEGY:
   python run_backtest.py --ticker AAPL --strategy moderate

2. MULTI-STOCK, SINGLE STRATEGY:
   python run_backtest.py --tickers AAPL MSFT NVDA --strategy aggressive

3. SINGLE STOCK, MULTI-STRATEGY COMPARISON:
   python run_backtest.py --ticker AAPL --strategies moderate aggressive conservative

4. MULTI-STOCK, MULTI-STRATEGY:
   python run_backtest.py --tickers AAPL MSFT --strategies moderate aggressive

5. CUSTOM PARAMETERS:
   python run_backtest.py --ticker AAPL --strategy moderate --custom fast_period=15 slow_period=40

All results are automatically saved to output/charts/ and browser opens with visualizations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import pandas as pd
from typing import List, Dict, Any

from app.services.backtesting import BacktestEngine
from app.services.strategy.examples.ma_crossover import MovingAverageCrossover
from app.services.data import fetch_demo_stock
from app.services.visualization import StrategyVisualizer
from strategies_config import (
    get_strategy_config,
    STRATEGY_PRESETS,
    print_available_strategies,
    RSIOversoldStrategy,
    BollingerBounceStrategy,
    MACDCrossoverStrategy
)


# ==============================================================================
# CONFIGURATION
# ==============================================================================

DEFAULT_TICKER = 'AAPL'
DEFAULT_STRATEGY = 'moderate'
DEFAULT_YEARS = 2.5
DEFAULT_CAPITAL = 100000
OUTPUT_DIR = 'output/charts'


# ==============================================================================
# MAIN BACKTEST FUNCTIONS
# ==============================================================================

def run_single_backtest(
    ticker: str,
    strategy_config: dict,
    years_back: float = 2.5,
    initial_capital: float = 100000
):
    """
    Run a single backtest on one stock with one strategy.

    Args:
        ticker: Stock ticker
        strategy_config: Strategy configuration dict
        years_back: Years of historical data
        initial_capital: Starting capital

    Returns:
        BacktestResult object
    """
    print(f"\n{'='*80}")
    print(f"  Running Backtest: {ticker} - {strategy_config['name']}")
    print(f"{'='*80}")

    # Fetch data
    print(f"  📊 Fetching {ticker} data...")
    data, stock_info = fetch_demo_stock(ticker, years_back=years_back)
    print(f"     → {len(data)} days from {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

    # Create strategy instance
    # Determine strategy class based on config name or type
    strategy_name_lower = strategy_config['name'].lower()

    if 'rsi' in strategy_name_lower:
        strategy = RSIOversoldStrategy(strategy_config)
    elif 'bollinger' in strategy_name_lower:
        strategy = BollingerBounceStrategy(strategy_config)
    elif 'macd' in strategy_name_lower:
        strategy = MACDCrossoverStrategy(strategy_config)
    else:
        # Default to MA Crossover
        strategy = MovingAverageCrossover(strategy_config)

    # Create backtest engine
    engine = BacktestEngine(initial_capital=initial_capital)

    # Run backtest
    print(f"  🎯 Running backtest...")
    result = engine.run_backtest(
        strategy=strategy,
        data=data,
        ticker=ticker
    )

    # Print results
    m = result.metrics
    print(f"\n  📈 Results:")
    print(f"     → Total Return:  {m.total_return * 100:>8.2f}%")
    print(f"     → CAGR:          {m.cagr * 100:>8.2f}%")
    print(f"     → Sharpe Ratio:  {m.sharpe_ratio:>8.2f}")
    print(f"     → Max Drawdown:  {m.max_drawdown * 100:>8.2f}%")
    print(f"     → Win Rate:      {m.win_rate * 100:>8.1f}%")
    print(f"     → Total Trades:  {m.total_trades:>8}")

    return result, stock_info


def run_multi_stock_backtest(
    tickers: List[str],
    strategy_config: dict,
    years_back: float = 2.5,
    initial_capital: float = 100000
):
    """
    Run backtest on multiple stocks with same strategy.

    Args:
        tickers: List of stock tickers
        strategy_config: Strategy configuration
        years_back: Years of historical data
        initial_capital: Starting capital

    Returns:
        Dict of ticker -> (BacktestResult, stock_info)
    """
    print(f"\n{'='*80}")
    print(f"  Multi-Stock Backtest: {strategy_config['name']}")
    print(f"  Stocks: {', '.join(tickers)}")
    print(f"{'='*80}\n")

    results = {}

    for ticker in tickers:
        try:
            result, stock_info = run_single_backtest(
                ticker=ticker,
                strategy_config=strategy_config,
                years_back=years_back,
                initial_capital=initial_capital
            )
            results[ticker] = (result, stock_info)
        except Exception as e:
            print(f"\n  ✗ Error with {ticker}: {e}")
            continue

    return results


def run_strategy_comparison(
    ticker: str,
    strategy_configs: List[dict],
    years_back: float = 2.5,
    initial_capital: float = 100000
):
    """
    Compare multiple strategies on the same stock.

    Args:
        ticker: Stock ticker
        strategy_configs: List of strategy configurations
        years_back: Years of historical data
        initial_capital: Starting capital

    Returns:
        Dict of strategy_name -> BacktestResult
    """
    print(f"\n{'='*80}")
    print(f"  Strategy Comparison: {ticker}")
    print(f"  Strategies: {len(strategy_configs)}")
    print(f"{'='*80}\n")

    # Fetch data once
    print(f"  📊 Fetching {ticker} data...")
    data, stock_info = fetch_demo_stock(ticker, years_back=years_back)
    print(f"     → {len(data)} days from {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}\n")

    results = {}

    for config in strategy_configs:
        try:
            # Create strategy
            strategy_name_lower = config['name'].lower()

            if 'rsi' in strategy_name_lower:
                strategy = RSIOversoldStrategy(config)
            elif 'bollinger' in strategy_name_lower:
                strategy = BollingerBounceStrategy(config)
            elif 'macd' in strategy_name_lower:
                strategy = MACDCrossoverStrategy(config)
            else:
                strategy = MovingAverageCrossover(config)

            # Run backtest
            engine = BacktestEngine(initial_capital=initial_capital)
            result = engine.run_backtest(strategy, data, ticker)

            results[config['name']] = result

            # Print quick summary
            m = result.metrics
            print(f"  ✓ {config['name']:<35} Return: {m.total_return*100:>7.2f}%  Sharpe: {m.sharpe_ratio:>6.2f}  Trades: {m.total_trades}")

        except Exception as e:
            print(f"  ✗ {config['name']:<35} Error: {e}")
            continue

    return results, stock_info


# ==============================================================================
# VISUALIZATION & REPORTING
# ==============================================================================

def create_single_stock_report(
    result,
    stock_info: dict,
    output_dir: str = OUTPUT_DIR
):
    """Create visualizations for a single backtest."""
    from app.services.visualization.strategy_charts import open_in_browser

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    viz = StrategyVisualizer(theme='dark', chart_size='large')

    ticker = result.ticker
    strategy_name = result.strategy_name

    print(f"\n  📊 Generating visualizations...")

    # Individual stock dashboard
    # Clean up strategy name for filename (remove special characters)
    safe_strategy_name = strategy_name.replace(' ', '_').replace('/', '_').lower()
    output_file = f"{output_dir}/{ticker.lower()}_{safe_strategy_name}_dashboard.html"

    dashboard_path = viz.create_dashboard(
        data=result.signals,
        signals=result.signals,
        metrics=result.metrics,
        strategy_name=f"{ticker} - {strategy_name}",
        output_path=output_file,
        auto_open=True
    )

    print(f"     → Dashboard: {output_file}")
    print(f"\n  ✅ Done! Dashboard opened in browser.\n")

    return dashboard_path


def create_multi_stock_report(
    results: Dict,
    strategy_name: str,
    output_dir: str = OUTPUT_DIR
):
    """Create comparative visualizations for multi-stock backtest."""
    from app.services.visualization.strategy_charts import open_in_browser
    from demo_multi_stock import (
        create_equity_comparison_chart,
        create_metrics_comparison_chart,
        create_unified_dashboard
    )

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    viz = StrategyVisualizer(theme='dark', chart_size='large')

    # Convert results format to match demo_multi_stock expectations
    formatted_results = []
    for ticker, (result, stock_info) in results.items():
        formatted_results.append({
            'ticker': ticker,
            'stock_info': stock_info,
            'data': result.signals,
            'signals': result.signals,
            'metrics': result.metrics
        })

    print(f"\n  📊 Generating comparative visualizations...")

    # Unified dashboard
    dashboard_fig = create_unified_dashboard(formatted_results, viz)
    dashboard_file = f"{output_dir}/multi_stock_dashboard.html"
    viz.export_chart(dashboard_fig, dashboard_file)

    print(f"     → Multi-stock dashboard: {dashboard_file}")
    print(f"\n  ✅ Done! Dashboard opened in browser.\n")

    open_in_browser(dashboard_file)

    return dashboard_file


def create_strategy_comparison_report(
    results: Dict,
    stock_info: dict,
    ticker: str,
    output_dir: str = OUTPUT_DIR
):
    """Create comparative visualizations for strategy comparison."""
    from app.services.visualization.strategy_charts import open_in_browser

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    viz = StrategyVisualizer(theme='dark', chart_size='large')

    # Convert to list format for comparison
    strategies_list = [
        {"name": name, "results": result.signals, "metrics": result.metrics}
        for name, result in results.items()
    ]

    print(f"\n  📊 Generating strategy comparison...")

    # Create comparison chart
    fig = viz.plot_strategy_comparison(strategies_list)
    output_file = f"{output_dir}/{ticker.lower()}_strategy_comparison.html"
    viz.export_chart(fig, output_file)

    print(f"     → Comparison chart: {output_file}")
    print(f"\n  ✅ Done! Comparison opened in browser.\n")

    open_in_browser(output_file)

    return output_file


# ==============================================================================
# COMMAND LINE INTERFACE
# ==============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Universal Stock Strategy Backtester',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--ticker', '-t',
        type=str,
        default=None,
        help=f'Stock ticker (default: {DEFAULT_TICKER})'
    )

    parser.add_argument(
        '--tickers', '-ts',
        nargs='+',
        default=None,
        help='Multiple stock tickers (e.g., AAPL MSFT NVDA)'
    )

    parser.add_argument(
        '--strategy', '-s',
        type=str,
        default=None,
        help=f'Strategy preset name (default: {DEFAULT_STRATEGY})'
    )

    parser.add_argument(
        '--strategies', '-ss',
        nargs='+',
        default=None,
        help='Multiple strategies to compare'
    )

    parser.add_argument(
        '--years', '-y',
        type=float,
        default=DEFAULT_YEARS,
        help=f'Years of historical data (default: {DEFAULT_YEARS})'
    )

    parser.add_argument(
        '--capital', '-c',
        type=float,
        default=DEFAULT_CAPITAL,
        help=f'Initial capital (default: ${DEFAULT_CAPITAL:,})'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available strategy presets'
    )

    parser.add_argument(
        '--custom',
        nargs='+',
        default=None,
        help='Custom parameters (e.g., fast_period=15 slow_period=40)'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # List strategies if requested
    if args.list:
        print_available_strategies()
        return

    # Determine mode of operation
    has_multi_tickers = args.tickers is not None
    has_multi_strategies = args.strategies is not None
    has_single_ticker = args.ticker is not None
    has_single_strategy = args.strategy is not None

    # Default to single ticker + single strategy if nothing specified
    if not any([has_multi_tickers, has_multi_strategies, has_single_ticker, has_single_strategy]):
        args.ticker = DEFAULT_TICKER
        args.strategy = DEFAULT_STRATEGY

    # MODE 1: Multi-stock, single strategy
    if has_multi_tickers and not has_multi_strategies:
        tickers = args.tickers
        strategy_name = args.strategy if has_single_strategy else DEFAULT_STRATEGY
        config = get_strategy_config(strategy_name)

        results = run_multi_stock_backtest(
            tickers=tickers,
            strategy_config=config,
            years_back=args.years,
            initial_capital=args.capital
        )

        create_multi_stock_report(results, config['name'])

    # MODE 2: Single stock, multi-strategy
    elif has_single_ticker and has_multi_strategies:
        ticker = args.ticker
        strategy_names = args.strategies
        configs = [get_strategy_config(name) for name in strategy_names]

        results, stock_info = run_strategy_comparison(
            ticker=ticker,
            strategy_configs=configs,
            years_back=args.years,
            initial_capital=args.capital
        )

        create_strategy_comparison_report(results, stock_info, ticker)

    # MODE 3: Single stock, single strategy
    else:
        ticker = args.ticker if has_single_ticker else DEFAULT_TICKER
        strategy_name = args.strategy if has_single_strategy else DEFAULT_STRATEGY
        config = get_strategy_config(strategy_name)

        # Apply custom parameters if provided
        if args.custom:
            for param in args.custom:
                key, value = param.split('=')
                try:
                    value = float(value)
                except ValueError:
                    pass
                config['parameters'][key] = value

        result, stock_info = run_single_backtest(
            ticker=ticker,
            strategy_config=config,
            years_back=args.years,
            initial_capital=args.capital
        )

        create_single_stock_report(result, stock_info)


if __name__ == '__main__':
    main()
