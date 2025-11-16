"""
Test Suite for Phase 3: Volume-Based Strategies

Tests OBV, A/D Line, and VWMA strategies on real market data.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from app.services.backtesting.engine import BacktestEngine
from app.services.data import fetch_stock_data

# Import Phase 3 strategies
from app.services.strategy.examples.obv_strategy import (
    OBVTrend20,
    OBVTrend30Conservative,
    OBVTrend10Aggressive,
    OBVDivergenceStandard,
    OBVBreakout20
)
from app.services.strategy.examples.ad_strategy import (
    ADTrend20,
    ADTrend50LongTerm,
    ADTrend10Fast,
    ADDivergenceStandard,
    ADCrossover20,
    ADCrossover20EMA
)
from app.services.strategy.examples.vwma_strategy import (
    VWMA10_30,
    VWMA20_50,
    VWMA50_200,
    VWMAvsSMA20,
    VWMAvsSMA50,
    VWMAPrice20,
    VWMAPrice50
)


def test_strategy(strategy_class, strategy_name, symbol='AAPL', start_date='2024-01-01', end_date='2024-12-31'):
    """Test a single strategy on given data."""
    print(f"\n{'='*80}")
    print(f"Testing: {strategy_name}")
    print(f"Symbol: {symbol} | Period: {start_date} to {end_date}")
    print(f"{'='*80}")

    try:
        # Fetch data
        data = fetch_stock_data(symbol=symbol, start_date=start_date, end_date=end_date, interval='1d')
        print(f"✓ Fetched {len(data)} bars of data")

        # Create strategy instance
        config = {'name': strategy_name}
        strategy = strategy_class(config)

        # Run backtest
        engine = BacktestEngine(initial_capital=100000, commission=0.001, slippage=0.0005)
        result = engine.run_backtest(strategy=strategy, data=data, ticker=symbol)

        # Extract metrics
        m = result.metrics

        # Calculate percentage returns
        total_return_pct = m.total_return * 100
        buy_hold_return_pct = m.buy_hold_return * 100
        alpha = total_return_pct - buy_hold_return_pct
        max_drawdown_pct = m.max_drawdown * 100

        # Print results
        print(f"\n{'─'*80}")
        print(f"RESULTS:")
        print(f"{'─'*80}")
        print(f"Total Return:      {total_return_pct:>8.2f}%")
        print(f"Buy & Hold Return: {buy_hold_return_pct:>8.2f}%")
        print(f"Alpha:             {alpha:>8.2f}%")
        print(f"Total Trades:      {m.total_trades:>8}")
        print(f"Win Rate:          {m.win_rate*100:>8.2f}%")
        print(f"Sharpe Ratio:      {m.sharpe_ratio:>8.2f}")
        print(f"Max Drawdown:      {max_drawdown_pct:>8.2f}%")

        if m.total_trades > 0:
            print(f"\nTrade Details:")
            print(f"  Avg Win:         ${m.average_win:>8.2f}")
            print(f"  Avg Loss:        ${m.average_loss:>8.2f}")
            print(f"  Profit Factor:   {m.profit_factor:>8.2f}")

        # Return summary dict for aggregation
        return {
            'name': strategy_name,
            'return': total_return_pct,
            'sharpe': m.sharpe_ratio,
            'trades': m.total_trades,
            'win_rate': m.win_rate,
            'max_dd': max_drawdown_pct
        }

    except Exception as e:
        print(f"✗ Error testing {strategy_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all Phase 3 strategy tests."""
    print("\n" + "="*80)
    print(" PHASE 3 STRATEGY TEST SUITE - VOLUME-BASED STRATEGIES")
    print("="*80)

    # Test parameters
    symbol = 'AAPL'
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    # Define all Phase 3 strategies to test
    strategies = [
        # OBV Strategies
        (OBVTrend20, "OBV Trend 20 (Standard)"),
        (OBVTrend30Conservative, "OBV Trend 30 (Conservative)"),
        (OBVTrend10Aggressive, "OBV Trend 10 (Aggressive)"),
        (OBVDivergenceStandard, "OBV Divergence"),
        (OBVBreakout20, "OBV Breakout 20"),

        # A/D Line Strategies
        (ADTrend20, "A/D Trend 20 (Standard)"),
        (ADTrend50LongTerm, "A/D Trend 50 (Long-term)"),
        (ADTrend10Fast, "A/D Trend 10 (Fast)"),
        (ADDivergenceStandard, "A/D Divergence"),
        (ADCrossover20, "A/D Crossover 20 SMA"),
        (ADCrossover20EMA, "A/D Crossover 20 EMA"),

        # VWMA Strategies
        (VWMA10_30, "VWMA Crossover 10/30"),
        (VWMA20_50, "VWMA Crossover 20/50"),
        (VWMA50_200, "VWMA Crossover 50/200"),
        (VWMAvsSMA20, "VWMA vs SMA 20"),
        (VWMAvsSMA50, "VWMA vs SMA 50"),
        (VWMAPrice20, "VWMA Price Position 20"),
        (VWMAPrice50, "VWMA Price Position 50"),
    ]

    # Run tests and collect results
    results = []
    for strategy_class, strategy_name in strategies:
        result = test_strategy(strategy_class, strategy_name, symbol, start_date, end_date)
        if result:
            results.append(result)

    # Print summary
    print("\n" + "="*80)
    print(" TEST SUMMARY - ALL PHASE 3 STRATEGIES")
    print("="*80)
    print(f"Total Strategies Tested: {len(results)}")

    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)

    print(f"\n{'Strategy':<40} {'Return':>10} {'Sharpe':>8} {'Trades':>8} {'WinRate':>8} {'MaxDD':>8}")
    print("─"*95)
    for r in results:
        print(f"{r['name']:<40} {r['return']:>9.2f}% {r['sharpe']:>8.2f} {r['trades']:>8} {r['win_rate']*100:>7.1f}% {r['max_dd']:>7.2f}%")

    # Highlight best performers
    if results:
        print("\n" + "="*80)
        print(" TOP PERFORMERS")
        print("="*80)
        print(f"Best Return:       {results[0]['name']} ({results[0]['return']:.2f}%)")

        best_sharpe = max(results, key=lambda x: x['sharpe'])
        print(f"Best Sharpe:       {best_sharpe['name']} ({best_sharpe['sharpe']:.2f})")

        best_win_rate = max(results, key=lambda x: x['win_rate'])
        print(f"Best Win Rate:     {best_win_rate['name']} ({best_win_rate['win_rate']*100:.1f}%)")

        most_trades = max(results, key=lambda x: x['trades'])
        print(f"Most Trades:       {most_trades['name']} ({most_trades['trades']} trades)")

    print("\n" + "="*80)
    print(" PHASE 3 TESTING COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
