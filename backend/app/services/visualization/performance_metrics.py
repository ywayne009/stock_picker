"""
Performance Metrics Calculator

Calculates trading strategy performance metrics including:
- Returns and profitability
- Risk-adjusted metrics (Sharpe, Sortino)
- Drawdown analysis
- Trade statistics
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for strategy performance metrics."""

    # Return metrics
    total_return: float
    cagr: float
    total_trades: int
    winning_trades: int
    losing_trades: int

    # Win rate metrics
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    average_trade: float
    largest_win: float
    largest_loss: float

    # Risk metrics
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    average_drawdown: float
    volatility: float

    # Trade duration
    average_trade_duration: float
    max_trade_duration: int
    min_trade_duration: int

    # Expectancy
    expectancy: float

    # Portfolio metrics
    final_portfolio_value: float
    initial_portfolio_value: float

    # Buy and hold comparison
    buy_hold_return: float  # Buy and hold return percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_return_pct': self.total_return * 100,
            'cagr_pct': self.cagr * 100,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_pct': self.win_rate * 100,
            'profit_factor': self.profit_factor,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'average_trade': self.average_trade,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown_pct': self.max_drawdown * 100,
            'max_drawdown_duration_days': self.max_drawdown_duration,
            'average_drawdown_pct': self.average_drawdown * 100,
            'volatility_pct': self.volatility * 100,
            'average_trade_duration_days': self.average_trade_duration,
            'max_trade_duration_days': self.max_trade_duration,
            'min_trade_duration_days': self.min_trade_duration,
            'expectancy': self.expectancy,
            'final_portfolio_value': self.final_portfolio_value,
            'initial_portfolio_value': self.initial_portfolio_value,
            'buy_hold_return_pct': self.buy_hold_return * 100
        }


def calculate_metrics(
    signals_df: pd.DataFrame,
    initial_capital: float = 100000.0,
    commission: float = 0.001,
    risk_free_rate: float = 0.02
) -> PerformanceMetrics:
    """
    Calculate comprehensive performance metrics for a trading strategy.

    Args:
        signals_df: DataFrame with 'signal', 'position', 'close' columns
        initial_capital: Starting capital (default: $100,000)
        commission: Commission rate as decimal (default: 0.001 = 0.1%)
        risk_free_rate: Annual risk-free rate for Sharpe calculation (default: 0.02 = 2%)

    Returns:
        PerformanceMetrics object with all calculated metrics
    """
    if 'signal' not in signals_df.columns or 'close' not in signals_df.columns:
        raise ValueError("signals_df must contain 'signal' and 'close' columns")

    # Calculate portfolio value over time
    portfolio_history = _simulate_portfolio(signals_df, initial_capital, commission)

    # Calculate returns
    returns = portfolio_history['portfolio_value'].pct_change().dropna()

    # Total return
    final_value = portfolio_history['portfolio_value'].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital

    # CAGR (Compound Annual Growth Rate)
    num_years = len(signals_df) / 252  # Assuming 252 trading days per year
    cagr = (final_value / initial_capital) ** (1 / num_years) - 1 if num_years > 0 else 0

    # Trade statistics
    trades = _extract_trades(portfolio_history)

    total_trades = len(trades)
    winning_trades = len([t for t in trades if t['profit'] > 0])
    losing_trades = len([t for t in trades if t['profit'] < 0])

    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    # Profit/Loss statistics
    wins = [t['profit'] for t in trades if t['profit'] > 0]
    losses = [t['profit'] for t in trades if t['profit'] < 0]

    average_win = np.mean(wins) if wins else 0
    average_loss = np.mean(losses) if losses else 0
    largest_win = max(wins) if wins else 0
    largest_loss = min(losses) if losses else 0

    # Profit factor
    total_wins = sum(wins) if wins else 0
    total_losses = abs(sum(losses)) if losses else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

    # Average trade
    average_trade = np.mean([t['profit'] for t in trades]) if trades else 0

    # Risk-adjusted metrics
    sharpe_ratio = _calculate_sharpe_ratio(returns, risk_free_rate)
    sortino_ratio = _calculate_sortino_ratio(returns, risk_free_rate)

    # Drawdown metrics
    drawdown_metrics = _calculate_drawdown_metrics(portfolio_history['portfolio_value'])

    # Volatility
    volatility = returns.std() * np.sqrt(252)  # Annualized

    # Trade duration
    durations = [t['duration'] for t in trades]
    average_duration = np.mean(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0

    # Expectancy (average profit/loss per trade)
    expectancy = (win_rate * average_win) + ((1 - win_rate) * average_loss)

    # Buy and hold return
    buy_hold_return = _calculate_buy_hold_return(signals_df, initial_capital, commission)

    return PerformanceMetrics(
        total_return=total_return,
        cagr=cagr,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        profit_factor=profit_factor,
        average_win=average_win,
        average_loss=average_loss,
        average_trade=average_trade,
        largest_win=largest_win,
        largest_loss=largest_loss,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        max_drawdown=drawdown_metrics['max_drawdown'],
        max_drawdown_duration=drawdown_metrics['max_drawdown_duration'],
        average_drawdown=drawdown_metrics['average_drawdown'],
        volatility=volatility,
        average_trade_duration=average_duration,
        max_trade_duration=max_duration,
        min_trade_duration=min_duration,
        expectancy=expectancy,
        final_portfolio_value=final_value,
        initial_portfolio_value=initial_capital,
        buy_hold_return=buy_hold_return
    )


def _simulate_portfolio(
    signals_df: pd.DataFrame,
    initial_capital: float,
    commission: float
) -> pd.DataFrame:
    """
    Simulate portfolio performance based on signals.

    Returns DataFrame with portfolio_value, position, cash, shares columns.
    """
    df = signals_df.copy()

    # Initialize portfolio state
    cash = initial_capital
    shares = 0
    portfolio_values = []
    positions = []
    cash_values = []
    shares_values = []

    for idx, row in df.iterrows():
        signal = row['signal']
        price = row['close']

        # Execute trades based on signals
        if signal == 1 and shares == 0:  # Buy signal
            # Buy with 10% of current cash (or parameter from strategy)
            investment = cash * 0.1
            commission_cost = investment * commission
            shares_to_buy = (investment - commission_cost) / price

            shares += shares_to_buy
            cash -= investment

        elif signal == -1 and shares > 0:  # Sell signal
            # Sell all shares
            proceeds = shares * price
            commission_cost = proceeds * commission

            cash += proceeds - commission_cost
            shares = 0

        # Calculate portfolio value
        portfolio_value = cash + (shares * price)
        portfolio_values.append(portfolio_value)
        positions.append(1 if shares > 0 else 0)
        cash_values.append(cash)
        shares_values.append(shares)

    # CRITICAL FIX: Force-liquidate any open position at end of period
    # This ensures Total Return matches completed trades count
    # If no trades were completed (shares still held), we close the position
    # and calculate the realized return (including commission)
    if shares > 0:
        final_price = df.iloc[-1]['close']
        proceeds = shares * final_price
        commission_cost = proceeds * commission
        cash += proceeds - commission_cost
        shares = 0

        # Update the final portfolio value to reflect forced liquidation
        portfolio_values[-1] = cash
        positions[-1] = 0
        cash_values[-1] = cash
        shares_values[-1] = shares

    df['portfolio_value'] = portfolio_values
    df['position'] = positions
    df['cash'] = cash_values
    df['shares'] = shares_values

    return df


def _extract_trades(portfolio_df: pd.DataFrame) -> list:
    """
    Extract individual trades from portfolio history.

    Only counts COMPLETED round-trips (buy → sell).
    Open positions (buy without sell) are NOT counted as trades.
    This ensures Total Trades metric is accurate.
    """
    trades = []
    in_position = False
    entry_idx = None
    entry_price = None
    entry_value = None

    for idx, row in portfolio_df.iterrows():
        if row['position'] == 1 and not in_position:
            # Entered position
            in_position = True
            entry_idx = idx
            entry_price = row['close']
            entry_value = row['portfolio_value']

        elif row['position'] == 0 and in_position:
            # Exited position - this is a COMPLETED trade
            in_position = False
            exit_price = row['close']
            exit_value = row['portfolio_value']

            profit = exit_value - entry_value
            duration = (idx - entry_idx).days if hasattr(idx - entry_idx, 'days') else len(portfolio_df.loc[entry_idx:idx])

            trades.append({
                'entry_date': entry_idx,
                'exit_date': idx,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit': profit,
                'return': (exit_price - entry_price) / entry_price,
                'duration': duration
            })

    # Note: Open positions (if in_position is still True) are NOT counted as completed trades
    # The Total Return metric will still reflect unrealized P&L from open positions
    # This is correct behavior: trades must be complete round-trips

    return trades


def _calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    """Calculate Sharpe Ratio."""
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    # Annualized
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = returns.std() * np.sqrt(252)

    return excess_returns / volatility if volatility != 0 else 0.0


def _calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    """Calculate Sortino Ratio (uses downside deviation instead of total volatility)."""
    if len(returns) == 0:
        return 0.0

    # Annualized
    excess_returns = returns.mean() * 252 - risk_free_rate

    # Downside deviation (only negative returns)
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0:
        return float('inf')

    downside_std = downside_returns.std() * np.sqrt(252)

    return excess_returns / downside_std if downside_std != 0 else 0.0


def _calculate_drawdown_metrics(portfolio_values: pd.Series) -> Dict[str, float]:
    """Calculate drawdown metrics."""
    # Calculate running maximum
    running_max = portfolio_values.expanding().max()

    # Calculate drawdown
    drawdown = (portfolio_values - running_max) / running_max

    # Max drawdown
    max_drawdown = drawdown.min()

    # Average drawdown (only drawdown periods)
    drawdown_periods = drawdown[drawdown < 0]
    average_drawdown = drawdown_periods.mean() if len(drawdown_periods) > 0 else 0

    # Max drawdown duration
    max_dd_duration = 0
    current_dd_duration = 0

    for dd in drawdown:
        if dd < 0:
            current_dd_duration += 1
            max_dd_duration = max(max_dd_duration, current_dd_duration)
        else:
            current_dd_duration = 0

    return {
        'max_drawdown': abs(max_drawdown),
        'average_drawdown': abs(average_drawdown),
        'max_drawdown_duration': max_dd_duration
    }


def _calculate_buy_hold_return(
    signals_df: pd.DataFrame,
    initial_capital: float,
    commission: float
) -> float:
    """
    Calculate buy and hold return with same position sizing as strategy.

    Uses 10% of capital (matching the strategy's position sizing) to buy
    at the first price, holds until the last price, then calculates
    the return on the total portfolio (invested + cash).

    Returns:
        Buy and hold return as decimal (e.g., 0.0235 for 2.35%)
    """
    if len(signals_df) < 2:
        return 0.0

    first_price = signals_df['close'].iloc[0]
    last_price = signals_df['close'].iloc[-1]

    # Use same position sizing as strategy (10% of capital)
    position_size_pct = 0.1
    investment_amount = initial_capital * position_size_pct

    # Buy at first price with commission
    buy_commission = investment_amount * commission
    shares_bought = (investment_amount - buy_commission) / first_price

    # Cash remaining (90% of capital not invested)
    cash = initial_capital - investment_amount

    # Sell at last price with commission
    proceeds = shares_bought * last_price
    sell_commission = proceeds * commission
    final_invested_value = proceeds - sell_commission

    # Total portfolio value at end = cash + invested value
    final_portfolio_value = cash + final_invested_value

    # Calculate return on total portfolio
    buy_hold_return = (final_portfolio_value - initial_capital) / initial_capital

    return buy_hold_return
