"""
Comprehensive test suite for Phase 2 Signal Strategies.

Tests:
1. ADX Trend Strength Filter (3 variants)
2. Stochastic Oscillator (3 variants)
3. Donchian Channel Breakout (3 variants)

Each test performs a real backtest on AAPL with 1-year data.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.strategy.examples.adx_strategy import (
    ADX25,
    ADX30Conservative,
    ADX20Aggressive
)
from app.services.strategy.examples.stochastic_strategy import (
    Stochastic14_3,
    StochasticSlow,
    StochasticFast
)
from app.services.strategy.examples.donchian_strategy import (
    Donchian20_10,
    Donchian50_25,
    Donchian10_5Fast
)
from app.services.backtesting.engine import BacktestEngine
from app.services.data.market_data import fetch_stock_data


def run_backtest(strategy, symbol='AAPL', days=365):
    """
    Run a backtest for a given strategy.

    Args:
        strategy: Strategy instance
        symbol: Stock symbol (default: AAPL)
        days: Number of days of historical data (default: 365)

    Returns:
        dict: Backtest results
    """
    print(f"\n{'='*80}")
    print(f"Testing: {strategy.name}")
    print(f"{'='*80}")

    # Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"Fetching {symbol} data from {start_date.date()} to {end_date.date()}...")
    data = fetch_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    if data is None or len(data) == 0:
        print(f"❌ Failed to fetch data for {symbol}")
        return None

    print(f"✓ Fetched {len(data)} bars")

    # Run backtest
    print(f"\nRunning backtest...")
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,  # 0.1%
        slippage=0.0005    # 0.05%
    )

    try:
        results = engine.run_backtest(strategy, data, symbol)

        # Extract metrics
        metrics = results.metrics

        # Print results
        print(f"\n{'─'*80}")
        print(f"BACKTEST RESULTS")
        print(f"{'─'*80}")
        print(f"\n📊 RETURNS:")
        print(f"  Initial Capital:     ${metrics.initial_portfolio_value:,.2f}")
        print(f"  Final Capital:       ${metrics.final_portfolio_value:,.2f}")
        print(f"  Total Return:        {metrics.total_return*100:.2f}%")
        print(f"  CAGR:                {metrics.cagr*100:.2f}%")

        print(f"\n📉 RISK METRICS:")
        print(f"  Max Drawdown:        {metrics.max_drawdown*100:.2f}%")
        print(f"  Sharpe Ratio:        {metrics.sharpe_ratio:.2f}")
        print(f"  Sortino Ratio:       {metrics.sortino_ratio:.2f}")

        print(f"\n📈 TRADE STATISTICS:")
        print(f"  Total Trades:        {metrics.total_trades}")
        print(f"  Winning Trades:      {metrics.winning_trades}")
        print(f"  Losing Trades:       {metrics.losing_trades}")
        print(f"  Win Rate:            {metrics.win_rate*100:.1f}%")
        print(f"  Profit Factor:       {metrics.profit_factor:.2f}")
        print(f"  Avg Win:             ${metrics.average_win:,.2f}")
        print(f"  Avg Loss:            ${metrics.average_loss:,.2f}")

        return {
            'name': strategy.name,
            'total_return': metrics.total_return * 100,
            'win_rate': metrics.win_rate * 100,
            'total_trades': metrics.total_trades,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown * 100
        }

    except Exception as e:
        print(f"❌ Backtest failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_adx_strategies():
    """Test all ADX strategy variants."""
    print("\n" + "="*80)
    print("PHASE 2 - ADX TREND STRENGTH STRATEGIES")
    print("="*80)

    strategies = [
        ADX25(),
        ADX30Conservative(),
        ADX20Aggressive()
    ]

    results = []
    for strategy in strategies:
        result = run_backtest(strategy)
        if result:
            results.append(result)

    return results


def test_stochastic_strategies():
    """Test all Stochastic strategy variants."""
    print("\n" + "="*80)
    print("PHASE 2 - STOCHASTIC OSCILLATOR STRATEGIES")
    print("="*80)

    strategies = [
        Stochastic14_3(),
        StochasticSlow(),
        StochasticFast()
    ]

    results = []
    for strategy in strategies:
        result = run_backtest(strategy)
        if result:
            results.append(result)

    return results


def test_donchian_strategies():
    """Test all Donchian strategy variants."""
    print("\n" + "="*80)
    print("PHASE 2 - DONCHIAN CHANNEL BREAKOUT STRATEGIES")
    print("="*80)

    strategies = [
        Donchian20_10(),
        Donchian50_25(),
        Donchian10_5Fast()
    ]

    results = []
    for strategy in strategies:
        result = run_backtest(strategy)
        if result:
            results.append(result)

    return results


def print_summary(all_results):
    """Print summary comparison of all strategies."""
    print("\n" + "="*80)
    print("PHASE 2 STRATEGIES - SUMMARY COMPARISON")
    print("="*80)

    if not all_results:
        print("No results to display")
        return

    # Sort by total return
    sorted_results = sorted(all_results, key=lambda x: x['total_return'], reverse=True)

    print(f"\n{'Strategy':<35} {'Return':<10} {'Trades':<8} {'Win%':<8} {'Sharpe':<8} {'MaxDD':<8}")
    print("-" * 80)

    for r in sorted_results:
        print(
            f"{r['name']:<35} "
            f"{r['total_return']:>8.2f}% "
            f"{r['total_trades']:>7} "
            f"{r['win_rate']:>7.1f}% "
            f"{r['sharpe_ratio']:>7.2f} "
            f"{r['max_drawdown']:>7.2f}%"
        )

    # Best performers
    print(f"\n{'='*80}")
    print("BEST PERFORMERS")
    print(f"{'='*80}")

    best_return = max(all_results, key=lambda x: x['total_return'])
    best_winrate = max(all_results, key=lambda x: x['win_rate'])
    best_sharpe = max(all_results, key=lambda x: x['sharpe_ratio'])

    print(f"🏆 Highest Return:   {best_return['name']:<35} ({best_return['total_return']:.2f}%)")
    print(f"🎯 Highest Win Rate: {best_winrate['name']:<35} ({best_winrate['win_rate']:.1f}%)")
    print(f"📊 Best Sharpe:      {best_sharpe['name']:<35} ({best_sharpe['sharpe_ratio']:.2f})")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 2 SIGNAL STRATEGIES - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbol: AAPL")
    print(f"Period: 1 year")
    print(f"Initial Capital: $100,000")
    print(f"Commission: 0.1%")
    print(f"Slippage: 0.05%")

    all_results = []

    # Test ADX strategies
    adx_results = test_adx_strategies()
    if adx_results:
        all_results.extend(adx_results)

    # Test Stochastic strategies
    stoch_results = test_stochastic_strategies()
    if stoch_results:
        all_results.extend(stoch_results)

    # Test Donchian strategies
    donchian_results = test_donchian_strategies()
    if donchian_results:
        all_results.extend(donchian_results)

    # Print summary
    print_summary(all_results)

    print("\n" + "="*80)
    print("✅ PHASE 2 TESTING COMPLETE")
    print("="*80)
