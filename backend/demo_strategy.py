"""
Demo script to test the Moving Average Crossover strategy.

================================================================================
HOW THE STRATEGY WORKS
================================================================================

Moving Average Crossover is a classic trend-following strategy that uses two
moving averages of different periods to identify trend changes:

1. FAST MA (Short Period): Reacts quickly to recent price changes
2. SLOW MA (Long Period): Represents the longer-term trend

SIGNAL GENERATION:
- BUY (Golden Cross): When Fast MA crosses ABOVE Slow MA
  → Indicates upward momentum is building
  → Suggests the start of an uptrend

- SELL (Death Cross): When Fast MA crosses BELOW Slow MA
  → Indicates downward momentum is building
  → Suggests the start of a downtrend

WHY IT WORKS:
- Crossovers indicate a shift in market sentiment
- Helps filter out short-term noise
- Works well in trending markets
- Reduces emotional decision-making

LIMITATIONS:
- Generates false signals in ranging/choppy markets
- Lagging indicator (signals come after trend has started)
- May miss quick reversals
- Can experience whipsaws in volatile conditions

================================================================================
TUNABLE PARAMETERS FOR PORTFOLIO ADAPTATION
================================================================================

1. MOVING AVERAGE PERIODS (fast_period, slow_period)
   ------------------------------------------------------
   Controls signal frequency and reliability:

   CONSERVATIVE (Long-term investing):
   - Example: 50/200 (Golden Cross)
   - Pros: Very reliable signals, filters noise well
   - Cons: Fewer signals, enters/exits later
   - Best for: Long-term portfolios, retirement accounts
   - Market fit: Stocks, ETFs, indices

   MODERATE (Swing trading):
   - Example: 20/50
   - Pros: Balance of reliability and responsiveness
   - Cons: Moderate lag, some false signals
   - Best for: Active portfolios, medium-term holds
   - Market fit: Most equities, commodities

   AGGRESSIVE (Day/Short-term trading):
   - Example: 10/30 or 5/20
   - Pros: Quick signals, catches short-term trends
   - Cons: More false signals, higher trading costs
   - Best for: Active traders, high-frequency portfolios
   - Market fit: Volatile stocks, crypto, forex

2. MOVING AVERAGE TYPE (ma_type: 'sma' vs 'ema')
   ------------------------------------------------------
   SMA (Simple Moving Average):
   - Equal weight to all prices in period
   - Smoother, more stable
   - Better for: Long-term trends, reducing whipsaws
   - Use when: You want confirmed, reliable signals

   EMA (Exponential Moving Average):
   - More weight to recent prices
   - More responsive to price changes
   - Better for: Short-term trading, quick reversals
   - Use when: You want faster signals and can tolerate more trades

3. POSITION SIZE (position_size: 0.0 to 1.0)
   ------------------------------------------------------
   Determines what % of portfolio to risk per trade:

   CONSERVATIVE (0.05 - 0.10 = 5-10%):
   - Lower risk, more diversification
   - Better for: Risk-averse portfolios, retirement accounts
   - Allows: 10-20 different positions
   - Drawdown impact: Limited

   MODERATE (0.15 - 0.25 = 15-25%):
   - Balanced risk/reward
   - Better for: Standard portfolios, managed accounts
   - Allows: 4-7 different positions
   - Drawdown impact: Moderate

   AGGRESSIVE (0.30 - 0.50 = 30-50%):
   - Higher risk, concentrated positions
   - Better for: High conviction trades, small portfolios
   - Allows: 2-3 different positions
   - Drawdown impact: Significant

   Note: Can also use volatility-adjusted sizing (built-in):
   - Lower size for volatile assets
   - Higher size for stable assets

4. STOP LOSS (stop_loss: 0.02 to 0.20)
   ------------------------------------------------------
   Maximum loss before auto-exit:

   TIGHT (0.02 - 0.05 = 2-5%):
   - Pros: Limits losses quickly, preserves capital
   - Cons: May get stopped out on normal volatility
   - Best for: Low volatility stocks, large positions, risk-averse
   - Example: Blue chip stocks, bonds

   MODERATE (0.05 - 0.10 = 5-10%):
   - Pros: Balances protection vs whipsaws
   - Cons: Larger potential losses
   - Best for: Most stocks, balanced portfolios
   - Example: S&P 500 stocks, established companies

   WIDE (0.10 - 0.20 = 10-20%):
   - Pros: Allows for volatility, fewer stop-outs
   - Cons: Larger drawdowns if wrong
   - Best for: Volatile assets, long-term holds
   - Example: Small caps, crypto, high-growth tech

5. TAKE PROFIT (take_profit: 0.10 to 0.50)
   ------------------------------------------------------
   Target gain before auto-exit:

   CONSERVATIVE (0.10 - 0.15 = 10-15%):
   - Lock in gains quickly
   - Higher win rate
   - Best for: Choppy markets, conservative portfolios
   - May miss large trends

   MODERATE (0.15 - 0.30 = 15-30%):
   - Balance between quick wins and big gains
   - Best for: Most strategies
   - Good risk/reward ratio (2:1 to 3:1)

   AGGRESSIVE (0.30 - 0.50 = 30-50%):
   - Swing for home runs
   - Lower win rate but bigger wins
   - Best for: Strong trending markets, growth stocks
   - May give back gains waiting for target

================================================================================
PORTFOLIO ADAPTATION EXAMPLES
================================================================================

RETIREMENT PORTFOLIO (Low Risk, Long-term):
  fast_period: 50
  slow_period: 200
  ma_type: 'sma'
  position_size: 0.05 (5%)
  stop_loss: 0.05 (5%)
  take_profit: 0.20 (20%)
  → Few high-quality signals, minimal risk

BALANCED PORTFOLIO (Medium Risk, Multi-year):
  fast_period: 20
  slow_period: 50
  ma_type: 'sma'
  position_size: 0.10 (10%)
  stop_loss: 0.07 (7%)
  take_profit: 0.15 (15%)
  → Moderate activity, reasonable risk/reward

ACTIVE TRADING PORTFOLIO (Higher Risk, Weeks-Months):
  fast_period: 10
  slow_period: 30
  ma_type: 'ema'
  position_size: 0.20 (20%)
  stop_loss: 0.05 (5%)
  take_profit: 0.10 (10%)
  → More signals, quicker entries/exits

DAY TRADING PORTFOLIO (High Risk, Days):
  fast_period: 5
  slow_period: 20
  ma_type: 'ema'
  position_size: 0.30 (30%)
  stop_loss: 0.03 (3%)
  take_profit: 0.05 (5%)
  → Very active, tight risk controls

VOLATILE ASSETS (Crypto, Small Caps):
  fast_period: 10
  slow_period: 30
  ma_type: 'ema'
  position_size: 0.10 (10% - volatility will reduce this)
  stop_loss: 0.15 (15% - wider for volatility)
  take_profit: 0.30 (30% - larger moves expected)
  → Adjusted for higher volatility

================================================================================
This demo script shows:
1. How to create synthetic market data for testing
2. How to configure strategies with different parameters
3. How signals are generated in different market conditions
4. How position sizing and risk management work
================================================================================
"""
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.services.strategy.examples.ma_crossover import (
    MovingAverageCrossover,
    GoldenCross50_200,
    FastMACrossover
)


def generate_sample_data(
    start_date: str = '2023-01-01',
    end_date: str = '2024-01-01',
    initial_price: float = 100.0,
    trend: float = 0.0001,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing.

    Args:
        start_date: Start date for data
        end_date: End date for data
        initial_price: Starting price
        trend: Daily trend component (0.0001 = 0.01% daily drift)
        volatility: Daily volatility (0.02 = 2% daily std dev)

    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)

    # Generate random returns with trend
    np.random.seed(42)
    returns = np.random.normal(trend, volatility, n_days)
    prices = initial_price * (1 + returns).cumprod()

    # Generate OHLC data
    data = pd.DataFrame(index=dates)
    data['close'] = prices

    # Generate realistic OHLC values
    daily_range = np.abs(np.random.normal(0, volatility * 0.5, n_days))
    data['high'] = data['close'] * (1 + daily_range)
    data['low'] = data['close'] * (1 - daily_range)
    data['open'] = data['close'].shift(1).fillna(initial_price)

    # Generate volume
    data['volume'] = np.random.randint(1000000, 5000000, n_days)

    return data


def print_signals(df: pd.DataFrame, strategy_name: str) -> None:
    """
    Print trading signals from the strategy results.

    Args:
        df: DataFrame with strategy signals
        strategy_name: Name of the strategy for display
    """
    print(f"\n{'='*80}")
    print(f"  {strategy_name}")
    print(f"{'='*80}\n")

    # Get buy signals
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]

    print(f"Total Trading Days: {len(df)}")
    print(f"Buy Signals: {len(buy_signals)}")
    print(f"Sell Signals: {len(sell_signals)}")

    if len(buy_signals) > 0:
        print(f"\n📈 BUY SIGNALS:")
        print(f"{'Date':<12} {'Price':<10} {'Fast MA':<10} {'Slow MA':<10}")
        print("-" * 50)
        for idx, row in buy_signals.head(10).iterrows():
            print(f"{idx.strftime('%Y-%m-%d'):<12} "
                  f"${row['close']:>8.2f} "
                  f"${row['fast_ma']:>8.2f} "
                  f"${row['slow_ma']:>8.2f}")
        if len(buy_signals) > 10:
            print(f"... and {len(buy_signals) - 10} more")

    if len(sell_signals) > 0:
        print(f"\n📉 SELL SIGNALS:")
        print(f"{'Date':<12} {'Price':<10} {'Fast MA':<10} {'Slow MA':<10}")
        print("-" * 50)
        for idx, row in sell_signals.head(10).iterrows():
            print(f"{idx.strftime('%Y-%m-%d'):<12} "
                  f"${row['close']:>8.2f} "
                  f"${row['fast_ma']:>8.2f} "
                  f"${row['slow_ma']:>8.2f}")
        if len(sell_signals) > 10:
            print(f"... and {len(sell_signals) - 10} more")

    # Calculate basic performance metrics
    if len(buy_signals) > 0 or len(sell_signals) > 0:
        print(f"\n📊 BASIC METRICS:")
        print(f"  First Signal: {df[df['signal'] != 0].index[0].strftime('%Y-%m-%d')}")
        print(f"  Last Signal: {df[df['signal'] != 0].index[-1].strftime('%Y-%m-%d')}")
        print(f"  Average Days Between Signals: {len(df) / (len(buy_signals) + len(sell_signals)):.1f}")

        # Show current position
        current_position = df['position'].iloc[-1]
        position_status = "LONG" if current_position == 1 else "FLAT"
        print(f"  Current Position: {position_status}")


def test_strategy(strategy, data: pd.DataFrame) -> pd.DataFrame:
    """
    Test a strategy with the provided data.

    Args:
        strategy: Strategy instance
        data: OHLCV DataFrame

    Returns:
        DataFrame with signals
    """
    print(f"\n{'='*80}")
    print(f"Testing: {strategy}")
    print(f"{'='*80}")

    # Setup strategy
    strategy.setup(data)

    # Generate signals
    results = strategy.generate_signals(data)

    # Print signals
    print_signals(results, str(strategy))

    return results


def main():
    """Main demo function."""
    print("\n" + "="*80)
    print("  MOVING AVERAGE CROSSOVER STRATEGY DEMO")
    print("="*80)

    # ============================================================================
    # DATA SOURCE SELECTION
    # ============================================================================
    # Choose between real market data or synthetic data for testing
    #
    # REAL DATA: Fetch actual stock data from Yahoo Finance
    # - More realistic results
    # - Shows how strategy performs in real markets
    # - Requires internet connection
    # - Examples: 'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY'
    #
    # SYNTHETIC DATA: Generate random price data
    # - Fast and works offline
    # - Good for testing strategy logic
    # - Results may not reflect real market behavior

    USE_REAL_DATA = True  # Set to False to use synthetic data
    STOCK_SYMBOL = 'MSFT'  # Change to any stock ticker
    YEARS_BACK = 2.5  # Years of historical data to fetch (2.5 years = ~30 months)

    # Alternative stock options:
    # STOCK_SYMBOL = 'MSFT'   # Microsoft
    # STOCK_SYMBOL = 'GOOGL'  # Google
    # STOCK_SYMBOL = 'TSLA'   # Tesla
    # STOCK_SYMBOL = 'SPY'    # S&P 500 ETF
    # STOCK_SYMBOL = '^GSPC'  # S&P 500 Index

    # ============================================================================
    # STEP 1: Load market data
    # ============================================================================
    if USE_REAL_DATA:
        print(f"\n1. Fetching real market data for {STOCK_SYMBOL}...")
        try:
            from app.services.data import fetch_demo_stock

            data, stock_info = fetch_demo_stock(STOCK_SYMBOL, years_back=YEARS_BACK)

            print(f"\n   📈 Stock Information:")
            print(f"   Company: {stock_info['name']}")
            print(f"   Sector: {stock_info['sector']}")
            print(f"   Industry: {stock_info['industry']}")
            print(f"   Data Points: {len(data)}")
            print(f"   Date Range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

        except Exception as e:
            print(f"\n   ⚠️  Error fetching real data: {e}")
            print(f"   ⚠️  Falling back to synthetic data...")
            USE_REAL_DATA = False

    if not USE_REAL_DATA:
        print("\n1. Generating synthetic market data...")
        data = generate_sample_data(
            start_date='2023-01-01',
            end_date='2024-01-01',
            initial_price=100.0,
            trend=0.0002,  # 0.02% daily drift = ~7.6% annual return
            volatility=0.015  # 1.5% daily std dev = ~24% annualized volatility
        )
        print(f"   ✓ Generated {len(data)} days of data")
        print(f"   ✓ Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        stock_info = {'name': 'Synthetic Stock', 'sector': 'Test', 'industry': 'Demo'}

    # ============================================================================
    # STRATEGY TEST 1: Moderate/Balanced Portfolio Strategy (20/50 SMA)
    # ============================================================================
    # This configuration is suitable for:
    # - Swing traders holding positions for weeks to months
    # - Balanced portfolios with moderate risk tolerance
    # - Most equity markets (stocks, ETFs)
    #
    # Parameter choices:
    # - fast_period=20: ~1 month of trading days, captures short-term trend
    # - slow_period=50: ~2.5 months, represents medium-term trend
    # - ma_type='sma': Smoother signals, less prone to whipsaws
    # - position_size=0.1: 10% per position allows for 10 different holdings
    # - stop_loss=0.05: 5% loss limit protects capital on wrong signals
    # - take_profit=0.15: 15% target gives 3:1 reward:risk ratio
    #
    # Expected behavior:
    # - Moderate signal frequency (5-15 signals per year typical)
    # - Good balance between catching trends and avoiding false signals
    # - Suitable for both individual stocks and indices
    print("\n2. Testing Custom MA Crossover (20/50 SMA)...")
    config1 = {
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
    strategy1 = MovingAverageCrossover(config1)
    results1 = test_strategy(strategy1, data)

    # ============================================================================
    # STRATEGY TEST 2: Conservative/Long-term Portfolio Strategy (50/200 SMA)
    # ============================================================================
    # This is the famous "Golden Cross" strategy, suitable for:
    # - Long-term investors (buy and hold for months/years)
    # - Retirement accounts and conservative portfolios
    # - Index funds, blue-chip stocks, sector ETFs
    #
    # Parameter choices:
    # - fast_period=50: ~2.5 months, filters out short-term noise
    # - slow_period=200: ~10 months (1 trading year), major trend indicator
    # - ma_type='sma': Institutional standard for long-term signals
    #
    # Expected behavior:
    # - Very few signals (0-3 per year typical)
    # - Only triggers on major trend changes
    # - High reliability but significant lag
    # - May need 1+ years of data to generate first signal
    # - Ideal for "set and forget" strategies
    #
    # Note: With only 1 year of data, this may generate NO signals
    # (requires at least 200 days before any signal can occur)
    print("\n3. Testing Golden Cross (50/200 SMA)...")
    strategy2 = GoldenCross50_200()
    results2 = test_strategy(strategy2, data)

    # ============================================================================
    # STRATEGY TEST 3: Aggressive/Active Trading Strategy (10/30 EMA)
    # ============================================================================
    # This configuration is suitable for:
    # - Active traders and day/swing traders
    # - Volatile stocks, growth stocks, crypto
    # - Those who can monitor positions frequently
    #
    # Parameter choices:
    # - fast_period=10: ~2 weeks, very responsive to price changes
    # - slow_period=30: ~1.5 months, short-term trend
    # - ma_type='ema': More weight on recent prices = faster signals
    #
    # Expected behavior:
    # - High signal frequency (15-30+ signals per year)
    # - Catches short-term trends quickly
    # - More false signals / whipsaws
    # - Higher trading costs (more commissions, slippage)
    # - Requires active monitoring and quick execution
    #
    # Trade-offs:
    # - PRO: Gets in early on moves, more opportunities
    # - CON: More noise, lower win rate, higher transaction costs
    # - Best in: Trending markets with clear momentum
    # - Worst in: Choppy, range-bound markets
    print("\n4. Testing Fast MA Crossover (10/30 EMA)...")
    strategy3 = FastMACrossover()
    results3 = test_strategy(strategy3, data)

    # Compare strategies
    print(f"\n{'='*80}")
    print("  STRATEGY COMPARISON")
    print(f"{'='*80}\n")

    strategies_info = [
        ('MA 20/50 SMA', results1),
        ('Golden Cross 50/200', results2),
        ('Fast 10/30 EMA', results3)
    ]

    print(f"{'Strategy':<20} {'Buy Signals':<15} {'Sell Signals':<15} {'Total Signals':<15}")
    print("-" * 70)

    for name, results in strategies_info:
        buy_count = len(results[results['signal'] == 1])
        sell_count = len(results[results['signal'] == -1])
        total = buy_count + sell_count
        print(f"{name:<20} {buy_count:<15} {sell_count:<15} {total:<15}")

    # ============================================================================
    # POSITION SIZING DEMONSTRATION
    # ============================================================================
    # Position sizing determines how much capital to allocate to each trade.
    # This is critical for risk management and portfolio diversification.
    #
    # The calculate_position_size() method takes:
    # - signal: 1 (buy) or -1 (sell)
    # - portfolio_value: Total portfolio size
    # - current_price: Price per share
    # - volatility (optional): For dynamic sizing based on risk
    #
    # Default method uses FIXED FRACTIONAL SIZING:
    # - Allocates a fixed % of portfolio to each position
    # - Example: 10% position size with $100k portfolio = $10k per trade
    #
    # Key considerations for different portfolios:
    # - Small portfolio (<$25k): Use 10-20% to build concentrated positions
    # - Medium portfolio ($25k-$250k): Use 5-15% for diversification
    # - Large portfolio (>$250k): Use 2-10% for broad diversification
    # - High volatility assets: Reduce size to manage risk
    # - Low volatility assets: Can increase size slightly
    print(f"\n{'='*80}")
    print("  POSITION SIZING EXAMPLE")
    print(f"{'='*80}\n")

    portfolio_value = 100000  # Example: $100k portfolio
    current_price = data['close'].iloc[-1]

    print(f"SCENARIO: You have a ${portfolio_value:,} portfolio")
    print(f"Strategy uses {strategy1.default_position_size*100}% position sizing\n")

    for signal_type, signal_value in [('BUY', 1), ('SELL', -1)]:
        shares = strategy1.calculate_position_size(signal_value, portfolio_value, current_price)
        position_value = abs(shares * current_price)
        print(f"{signal_type} Signal:")
        print(f"  Portfolio Value: ${portfolio_value:,.2f}")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Shares to Trade: {abs(shares):.2f}")
        print(f"  Position Value: ${position_value:,.2f}")
        print(f"  % of Portfolio: {(position_value/portfolio_value)*100:.1f}%")
        print(f"  → This allows you to hold up to {int(1/strategy1.default_position_size)} positions")
        print()

    # ============================================================================
    # RISK MANAGEMENT DEMONSTRATION
    # ============================================================================
    # Risk management protects your capital by automatically exiting positions
    # when they hit stop-loss or take-profit levels.
    #
    # The risk_management() method monitors each position and returns:
    # - 'close': Exit the position immediately
    # - None: Hold the position
    #
    # Two key levels:
    # 1. STOP LOSS: Maximum acceptable loss before exit
    #    - Prevents small losses from becoming large losses
    #    - Essential for preserving capital
    #    - Should be based on volatility and support/resistance levels
    #
    # 2. TAKE PROFIT: Target profit level for exit
    #    - Locks in gains before reversal
    #    - Prevents "riding winners back down"
    #    - Should give favorable risk/reward ratio (aim for 2:1 or better)
    #
    # Best practices:
    # - Always use stops (never trade without them!)
    # - Risk/reward ratio should be at least 2:1 (take_profit >= 2 * stop_loss)
    # - Adjust stops based on market volatility
    # - Consider trailing stops for trending markets
    # - Never move stop loss further away (only tighter or leave it)
    print(f"{'='*80}")
    print("  RISK MANAGEMENT EXAMPLE")
    print(f"{'='*80}\n")

    # Example position: Bought 100 shares at $100
    position = {
        'quantity': 100,
        'entry_price': 100.0,
        'entry_date': datetime.now()
    }

    print(f"SCENARIO: You bought {position['quantity']} shares at ${position['entry_price']:.2f}")
    print(f"Position value: ${position['quantity'] * position['entry_price']:,.2f}\n")

    # Test different price scenarios
    test_prices = [95.0, 92.0, 105.0, 115.0, 120.0]
    print(f"Entry Price: ${position['entry_price']:.2f}")
    print(f"Stop Loss: {strategy1.default_stop_loss*100}% (${position['entry_price'] * (1-strategy1.default_stop_loss):.2f})")
    print(f"Take Profit: {strategy1.default_take_profit*100}% (${position['entry_price'] * (1+strategy1.default_take_profit):.2f})")
    print(f"\nRisk/Reward Ratio: {strategy1.default_take_profit/strategy1.default_stop_loss:.1f}:1")
    print()
    print(f"{'Current Price':<15} {'% Change':<12} {'Action':<10} {'Reason'}")
    print("-" * 65)

    for price in test_prices:
        action = strategy1.risk_management(position, price)
        pct_change = (price - position['entry_price']) / position['entry_price'] * 100
        action_str = action.upper() if action else 'HOLD'

        # Determine reason for action
        if action == 'close':
            if price < position['entry_price']:
                reason = "Hit stop loss - cut losses"
            else:
                reason = "Hit take profit - lock in gains"
        else:
            reason = "Within acceptable range"

        print(f"${price:<14.2f} {pct_change:>6.1f}%      {action_str:<10} {reason}")

    # ============================================================================
    # INTERACTIVE VISUALIZATIONS
    # ============================================================================
    # Generate interactive charts for visual analysis
    # Charts will auto-open in your browser and save to output/charts/
    print(f"\n{'='*80}")
    print("  GENERATING INTERACTIVE VISUALIZATIONS")
    print(f"{'='*80}\n")

    try:
        from app.services.visualization import StrategyVisualizer, calculate_metrics

        print("📊 Creating visualizations...")

        # Calculate metrics for each strategy
        print("  → Calculating performance metrics...")
        metrics1 = calculate_metrics(results1, initial_capital=100000)
        metrics2 = calculate_metrics(results2, initial_capital=100000)
        metrics3 = calculate_metrics(results3, initial_capital=100000)

        # Create visualizer
        viz = StrategyVisualizer(theme='dark', chart_size='large')

        # Prepare strategy names with stock symbol
        stock_label = f"{STOCK_SYMBOL} - " if USE_REAL_DATA else ""

        # Chart 1: Price with signals for MA 20/50
        print("  → Generating price chart with signals (MA 20/50)...")
        fig1 = viz.plot_price_and_signals(
            data,
            results1,
            strategy_name=f"{stock_label}Moving Average 20/50 SMA"
        )
        viz.export_chart(fig1, "output/charts/ma_20_50_signals.html")

        # Chart 2: Equity curve for MA 20/50
        print("  → Generating equity curve (MA 20/50)...")
        fig2 = viz.plot_equity_curve(
            results1,
            initial_capital=100000,
            benchmark=data if USE_REAL_DATA else None,  # Add buy & hold benchmark for real data
            strategy_name=f"{stock_label}MA 20/50 SMA"
        )
        viz.export_chart(fig2, "output/charts/ma_20_50_equity.html")

        # Chart 3: Performance metrics for MA 20/50
        print("  → Generating performance metrics dashboard (MA 20/50)...")
        fig3 = viz.plot_performance_metrics(
            metrics1,
            strategy_name=f"{stock_label}MA 20/50 SMA"
        )
        viz.export_chart(fig3, "output/charts/ma_20_50_metrics.html")

        # Chart 4: Strategy comparison
        print("  → Generating multi-strategy comparison...")
        fig4 = viz.plot_strategy_comparison([
            {"name": f"{stock_label}MA 20/50 SMA", "results": results1, "metrics": metrics1},
            {"name": f"{stock_label}Golden Cross 50/200", "results": results2, "metrics": metrics2},
            {"name": f"{stock_label}Fast MA 10/30 EMA", "results": results3, "metrics": metrics3}
        ])
        viz.export_chart(fig4, "output/charts/strategy_comparison.html")

        # Chart 5: Complete dashboard for MA 20/50
        print("  → Creating complete interactive dashboard...")
        dashboard_path = viz.create_dashboard(
            data=data,
            signals=results1,
            metrics=metrics1,
            strategy_name=f"{stock_label}MA 20/50 SMA",
            output_path="output/charts/ma_20_50_dashboard.html",
            auto_open=True
        )

        print(f"\n✅ Visualizations generated successfully!")
        print(f"\nGenerated files:")
        print(f"  • output/charts/ma_20_50_signals.html      - Price chart with buy/sell signals")
        print(f"  • output/charts/ma_20_50_equity.html       - Portfolio equity curve")
        print(f"  • output/charts/ma_20_50_metrics.html      - Performance metrics dashboard")
        print(f"  • output/charts/strategy_comparison.html   - Compare all 3 strategies")
        print(f"  • output/charts/ma_20_50_dashboard.html    - Complete interactive dashboard")

        print(f"\n📈 Dashboard opened in your browser!")
        print(f"   All charts are interactive: hover, zoom, pan to explore\n")

        # Print key metrics
        print(f"{'='*80}")
        print("  KEY PERFORMANCE METRICS (MA 20/50)")
        print(f"{'='*80}\n")

        metrics_dict = metrics1.to_dict()
        print(f"  Total Return:        {metrics_dict['total_return_pct']:>8.2f}%")
        print(f"  CAGR:                {metrics_dict['cagr_pct']:>8.2f}%")
        print(f"  Sharpe Ratio:        {metrics_dict['sharpe_ratio']:>8.2f}")
        print(f"  Sortino Ratio:       {metrics_dict['sortino_ratio']:>8.2f}")
        print(f"  Max Drawdown:        {metrics_dict['max_drawdown_pct']:>8.2f}%")
        print(f"  Win Rate:            {metrics_dict['win_rate_pct']:>8.1f}%")
        print(f"  Profit Factor:       {metrics_dict['profit_factor']:>8.2f}")
        print(f"  Total Trades:        {metrics_dict['total_trades']:>8}")
        print(f"  Average Win:         ${metrics_dict['average_win']:>8,.2f}")
        print(f"  Average Loss:        ${metrics_dict['average_loss']:>8,.2f}")
        print(f"  Expectancy:          ${metrics_dict['expectancy']:>8,.2f}")
        print()

    except ImportError as e:
        print(f"⚠️  Visualization module not available: {e}")
        print(f"   Charts were not generated, but the demo completed successfully.\n")
    except Exception as e:
        print(f"⚠️  Error generating visualizations: {e}")
        print(f"   Continuing with demo...\n")

    # ============================================================================
    # PARAMETER TUNING WORKFLOW
    # ============================================================================
    print(f"\n{'='*80}")
    print("  PARAMETER TUNING TIPS")
    print(f"{'='*80}\n")

    print("HOW TO ADAPT THIS STRATEGY TO YOUR PORTFOLIO:\n")

    print("STEP 1: Define Your Investment Profile")
    print("-" * 50)
    print("  Ask yourself:")
    print("  - What's my time horizon? (days, weeks, months, years)")
    print("  - How much risk can I tolerate?")
    print("  - How often can I monitor positions?")
    print("  - What's my portfolio size?")
    print("  - What assets am I trading? (stocks, crypto, forex, etc.)\n")

    print("STEP 2: Choose Appropriate MA Periods")
    print("-" * 50)
    print("  Day Trading:       5/15, 10/20, 10/30")
    print("  Swing Trading:     10/30, 15/45, 20/50")
    print("  Position Trading:  20/50, 30/100, 50/150")
    print("  Long-term:         50/200, 100/300\n")

    print("STEP 3: Select MA Type Based on Speed Needs")
    print("-" * 50)
    print("  SMA: More stable, fewer false signals, better for long-term")
    print("  EMA: More responsive, faster signals, better for short-term\n")

    print("STEP 4: Set Position Size Based on Risk Tolerance")
    print("-" * 50)
    print("  Conservative:  5-10%  (allows 10-20 positions)")
    print("  Moderate:     10-20%  (allows 5-10 positions)")
    print("  Aggressive:   20-30%  (allows 3-5 positions)\n")

    print("STEP 5: Configure Stop Loss for Asset Volatility")
    print("-" * 50)
    print("  Low volatility (blue chips):     3-5%")
    print("  Medium volatility (most stocks): 5-10%")
    print("  High volatility (small caps):   10-15%")
    print("  Very high volatility (crypto):  15-25%\n")

    print("STEP 6: Set Take Profit at 2-3x Your Stop Loss")
    print("-" * 50)
    print("  If stop_loss = 5%, set take_profit = 10-15%")
    print("  If stop_loss = 10%, set take_profit = 20-30%")
    print("  This ensures favorable risk/reward ratio\n")

    print("STEP 7: Backtest and Refine")
    print("-" * 50)
    print("  - Test on historical data")
    print("  - Measure: Win rate, average profit/loss, max drawdown")
    print("  - Adjust if: Too many signals, too few signals, poor win rate")
    print("  - Remember: Past performance doesn't guarantee future results\n")

    print("EXAMPLE TUNING SCENARIOS:")
    print("-" * 50)
    print("\n  Scenario: Too many false signals in ranging market")
    print("  Solution: ↑ Increase MA periods (e.g., 20/50 → 30/100)")
    print("           ↑ Switch from EMA to SMA for smoothing")
    print("           ↑ Add filters (volume, RSI, trend confirmation)\n")

    print("  Scenario: Missing quick reversals")
    print("  Solution: ↓ Decrease MA periods (e.g., 50/200 → 20/50)")
    print("           ↓ Switch from SMA to EMA for responsiveness")
    print("           ↓ Consider dual timeframe strategy\n")

    print("  Scenario: Getting stopped out too often")
    print("  Solution: ↑ Widen stop loss based on ATR or volatility")
    print("           → Calculate average swing range for your asset")
    print("           → Set stop just beyond normal price fluctuation\n")

    print("  Scenario: Missing profit targets (price reverses before target)")
    print("  Solution: ↓ Lower take profit target")
    print("           → Use trailing stop instead of fixed target")
    print("           → Consider pyramiding (scale out at multiple levels)\n")

    print("ADVANCED ADAPTATIONS:")
    print("-" * 50)
    print("  1. Multiple Timeframes:")
    print("     - Use longer timeframe (daily) for trend direction")
    print("     - Use shorter timeframe (hourly) for entry timing\n")

    print("  2. Volatility-Based Position Sizing (already built-in):")
    print("     - Pass volatility parameter to calculate_position_size()")
    print("     - Automatically reduces size for volatile assets\n")

    print("  3. Market Regime Filters:")
    print("     - Only trade when market is trending (ADX > 25)")
    print("     - Avoid trading in ranging markets")
    print("     - Add volume confirmation for signals\n")

    print("  4. Portfolio-Level Risk Management:")
    print("     - Limit total exposure (e.g., max 50% invested at once)")
    print("     - Correlate positions to avoid concentrated risk")
    print("     - Use position sizing to balance across sectors\n")

    print(f"\n{'='*80}")
    print("  DEMO COMPLETE!")
    print(f"{'='*80}")
    print("\nNext steps:")
    print("  1. Modify the config parameters above to match your profile")
    print("  2. Test with real historical data for your target assets")
    print("  3. Integrate with the backtesting engine (coming soon)")
    print("  4. Paper trade before going live")
    print("  5. Monitor and refine based on actual performance\n")


if __name__ == '__main__':
    main()
