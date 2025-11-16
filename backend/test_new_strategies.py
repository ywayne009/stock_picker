#!/usr/bin/env python3
"""
Test script for the new Phase 1 strategies:
- RSI Overbought/Oversold
- MACD Crossover
- Bollinger Band Mean Reversion

This script runs backtests on each strategy and reports key metrics.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.strategy.examples.rsi_strategy import RSI30_70
from app.services.strategy.examples.macd_strategy import MACD_Standard
from app.services.strategy.examples.bollinger_strategy import BB_Standard
from app.services.backtesting.engine import BacktestEngine
from app.services.data import fetch_stock_data
from datetime import datetime, timedelta


def test_strategy(strategy, strategy_name, symbol='AAPL', period='1y'):
    """Test a single strategy and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {strategy_name}")
    print(f"Symbol: {symbol} | Period: {period}")
    print(f"{'='*60}")

    try:
        # Fetch data
        print("Fetching market data...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 1 year

        data = fetch_stock_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if data is None or len(data) == 0:
            print(f"❌ Failed to fetch data for {symbol}")
            return False

        print(f"✓ Fetched {len(data)} bars")

        # Run backtest
        print("Running backtest...")
        engine = BacktestEngine(
            initial_capital=100000,
            commission=0.001,  # 0.1%
            slippage=0.0005    # 0.05%
        )

        # BacktestEngine.run_backtest takes (strategy, data, ticker)
        results = engine.run_backtest(strategy, data, symbol)

        # Count signals from results
        signals_df = results.signals
        buy_signals = (signals_df['signal'] == 1).sum()
        sell_signals = (signals_df['signal'] == -1).sum()
        print(f"✓ Buy signals: {buy_signals}, Sell signals: {sell_signals}")

        metrics = results.metrics

        # Print results
        print(f"\n{'-'*60}")
        print("BACKTEST RESULTS")
        print(f"{'-'*60}")
        print(f"Initial Capital:     ${metrics.initial_portfolio_value:,.2f}")
        print(f"Final Value:         ${metrics.final_portfolio_value:,.2f}")
        print(f"Total Return:        {metrics.total_return*100:.2f}%")
        print(f"CAGR:                {metrics.cagr*100:.2f}%")
        print(f"Sharpe Ratio:        {metrics.sharpe_ratio:.2f}")
        print(f"Max Drawdown:        {metrics.max_drawdown*100:.2f}%")
        print(f"\nTotal Trades:        {metrics.total_trades}")
        print(f"Winning Trades:      {metrics.winning_trades}")
        print(f"Losing Trades:       {metrics.losing_trades}")
        print(f"Win Rate:            {metrics.win_rate*100:.1f}%")
        print(f"Profit Factor:       {metrics.profit_factor:.2f}")
        print(f"Avg Win:             ${metrics.average_win:,.2f}")
        print(f"Avg Loss:            ${metrics.average_loss:,.2f}")

        # Determine if strategy is profitable
        if metrics.total_return > 0:
            print(f"\n✅ Strategy is PROFITABLE")
        else:
            print(f"\n⚠️  Strategy is UNPROFITABLE (but may work on other stocks/timeframes)")

        return True

    except Exception as e:
        print(f"\n❌ Error testing {strategy_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests for all new strategies."""
    print("\n" + "="*60)
    print(" TESTING PHASE 1 SIGNAL STRATEGIES")
    print("="*60)

    test_symbols = ['AAPL']  # Can expand to ['AAPL', 'MSFT', 'TSLA'] for more thorough testing

    strategies = [
        (RSI30_70(), "RSI 30/70 Overbought/Oversold"),
        (MACD_Standard(), "MACD 12/26/9 Standard"),
        (BB_Standard(), "Bollinger Band 20,2 Mean Reversion"),
    ]

    results = {}

    for symbol in test_symbols:
        print(f"\n\n{'#'*60}")
        print(f"# Testing Symbol: {symbol}")
        print(f"{'#'*60}")

        symbol_results = {}
        for strategy, name in strategies:
            success = test_strategy(strategy, name, symbol)
            symbol_results[name] = success

        results[symbol] = symbol_results

    # Print summary
    print("\n\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)

    for symbol, strategy_results in results.items():
        print(f"\n{symbol}:")
        for strategy_name, success in strategy_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {strategy_name}")

    # Overall result
    all_passed = all(
        all(strategy_results.values())
        for strategy_results in results.values()
    )

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
