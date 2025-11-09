"""
Universal Backtesting Engine

A strategy-agnostic backtesting engine that works with any asset type
(stocks, options, crypto, etc.) and any strategy.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BacktestResult:
    """
    Container for backtest results.

    Attributes:
        ticker: Asset ticker symbol
        strategy_name: Name of the strategy used
        signals: DataFrame with price data and signals
        portfolio_history: DataFrame with portfolio value over time
        trades: List of executed trades
        metrics: Performance metrics
        metadata: Additional metadata (dates, parameters, etc.)
    """
    ticker: str
    strategy_name: str
    signals: pd.DataFrame
    portfolio_history: pd.DataFrame
    trades: List[Dict[str, Any]]
    metrics: Any  # PerformanceMetrics object
    metadata: Dict[str, Any]


class BacktestEngine:
    """
    Universal backtesting engine that simulates trading strategies.

    Features:
    - Works with any asset type (stocks, crypto, options, etc.)
    - Strategy-agnostic (works with any strategy class)
    - Realistic simulation (commissions, slippage)
    - Multiple position sizing methods
    - Comprehensive trade tracking

    Example:
        engine = BacktestEngine(
            initial_capital=100000,
            commission=0.001,
            slippage=0.0005
        )

        result = engine.run_backtest(
            strategy=my_strategy,
            data=price_data,
            ticker='AAPL'
        )
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0,      # Additional slippage
        position_size_pct: float = 0.1,  # 10% of portfolio per trade
        risk_free_rate: float = 0.02  # 2% annual risk-free rate
    ):
        """
        Initialize the backtesting engine.

        Args:
            initial_capital: Starting capital
            commission: Commission rate as decimal (e.g., 0.001 = 0.1%)
            slippage: Slippage rate as decimal (e.g., 0.0005 = 0.05%)
            position_size_pct: Default position size as % of portfolio
            risk_free_rate: Annual risk-free rate for Sharpe calculation
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.position_size_pct = position_size_pct
        self.risk_free_rate = risk_free_rate

    def run_backtest(
        self,
        strategy,
        data: pd.DataFrame,
        ticker: str = "UNKNOWN",
        metadata: Optional[Dict[str, Any]] = None
    ) -> BacktestResult:
        """
        Run a backtest with the given strategy and data.

        Args:
            strategy: Strategy instance (must have setup() and generate_signals() methods)
            data: OHLCV DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
            ticker: Asset ticker symbol
            metadata: Additional metadata to store

        Returns:
            BacktestResult object with all results
        """
        # Validate data
        self._validate_data(data)

        # Setup strategy
        strategy.setup(data)

        # Generate signals
        signals = strategy.generate_signals(data.copy())

        # Simulate portfolio
        portfolio_history = self._simulate_portfolio(signals, strategy)

        # Extract trades
        trades = self._extract_trades(portfolio_history)

        # Calculate metrics
        from app.services.visualization import calculate_metrics
        metrics = calculate_metrics(
            signals,
            initial_capital=self.initial_capital,
            commission=self.commission,
            risk_free_rate=self.risk_free_rate
        )

        # Build metadata
        if metadata is None:
            metadata = {}

        metadata.update({
            'ticker': ticker,
            'strategy': strategy.name,
            'initial_capital': self.initial_capital,
            'commission': self.commission,
            'slippage': self.slippage,
            'start_date': data.index[0].strftime('%Y-%m-%d'),
            'end_date': data.index[-1].strftime('%Y-%m-%d'),
            'total_days': len(data),
            'backtest_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        return BacktestResult(
            ticker=ticker,
            strategy_name=strategy.name,
            signals=signals,
            portfolio_history=portfolio_history,
            trades=trades,
            metrics=metrics,
            metadata=metadata
        )

    def run_multi_asset_backtest(
        self,
        strategy,
        assets_data: Dict[str, pd.DataFrame],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, BacktestResult]:
        """
        Run backtests on multiple assets with the same strategy.

        Args:
            strategy: Strategy instance
            assets_data: Dictionary mapping ticker -> OHLCV DataFrame
            metadata: Additional metadata

        Returns:
            Dictionary mapping ticker -> BacktestResult
        """
        results = {}

        for ticker, data in assets_data.items():
            result = self.run_backtest(
                strategy=strategy,
                data=data,
                ticker=ticker,
                metadata=metadata
            )
            results[ticker] = result

        return results

    def _validate_data(self, data: pd.DataFrame) -> None:
        """Validate that data has required columns."""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_columns if col not in data.columns]

        if missing:
            raise ValueError(f"Data missing required columns: {missing}")

        if len(data) < 50:
            raise ValueError(f"Insufficient data: need at least 50 bars, got {len(data)}")

    def _simulate_portfolio(
        self,
        signals_df: pd.DataFrame,
        strategy
    ) -> pd.DataFrame:
        """
        Simulate portfolio performance based on signals.

        Returns DataFrame with portfolio state at each timestamp.
        """
        df = signals_df.copy()

        # Initialize portfolio state
        cash = self.initial_capital
        shares = 0
        portfolio_values = []
        positions = []
        cash_values = []
        shares_values = []

        for idx, row in df.iterrows():
            signal = row['signal']
            price = row['close']

            # Apply slippage to price
            if signal == 1:  # Buy - pay higher
                execution_price = price * (1 + self.slippage)
            elif signal == -1:  # Sell - receive lower
                execution_price = price * (1 - self.slippage)
            else:
                execution_price = price

            # Execute trades based on signals
            if signal == 1 and shares == 0:  # Buy signal
                # Use strategy's position size or default
                position_size = getattr(strategy, 'default_position_size', self.position_size_pct)
                investment = cash * position_size
                commission_cost = investment * self.commission
                shares_to_buy = (investment - commission_cost) / execution_price

                if shares_to_buy > 0:
                    shares += shares_to_buy
                    cash -= investment

            elif signal == -1 and shares > 0:  # Sell signal
                # Sell all shares
                proceeds = shares * execution_price
                commission_cost = proceeds * self.commission

                cash += proceeds - commission_cost
                shares = 0

            # Calculate portfolio value (use market price, not execution price)
            portfolio_value = cash + (shares * price)
            portfolio_values.append(portfolio_value)
            positions.append(1 if shares > 0 else 0)
            cash_values.append(cash)
            shares_values.append(shares)

        df['portfolio_value'] = portfolio_values
        df['position'] = positions
        df['cash'] = cash_values
        df['shares'] = shares_values

        return df

    def _extract_trades(self, portfolio_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract individual trades from portfolio history."""
        trades = []
        in_position = False
        entry_idx = None
        entry_price = None
        entry_value = None
        entry_shares = None

        for idx, row in portfolio_df.iterrows():
            if row['position'] == 1 and not in_position:
                # Entered position
                in_position = True
                entry_idx = idx
                entry_price = row['close']
                entry_value = row['portfolio_value']
                entry_shares = row['shares']

            elif row['position'] == 0 and in_position:
                # Exited position
                in_position = False
                exit_price = row['close']
                exit_value = row['portfolio_value']

                profit = exit_value - entry_value
                profit_pct = (profit / entry_value) * 100 if entry_value > 0 else 0

                duration = (idx - entry_idx).days if hasattr(idx - entry_idx, 'days') else 1

                trades.append({
                    'entry_date': entry_idx,
                    'exit_date': idx,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'shares': entry_shares,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'duration': duration,
                    'entry_value': entry_value,
                    'exit_value': exit_value
                })

        return trades


class MultiStrategyBacktest:
    """
    Run backtests comparing multiple strategies on the same data.

    Example:
        comparator = MultiStrategyBacktest(
            strategies=[strategy1, strategy2, strategy3],
            data=price_data,
            ticker='AAPL'
        )

        results = comparator.run()
    """

    def __init__(
        self,
        strategies: List,
        data: pd.DataFrame,
        ticker: str = "UNKNOWN",
        initial_capital: float = 100000.0,
        commission: float = 0.001
    ):
        """
        Initialize multi-strategy backtest.

        Args:
            strategies: List of strategy instances
            data: OHLCV DataFrame
            ticker: Asset ticker
            initial_capital: Starting capital
            commission: Commission rate
        """
        self.strategies = strategies
        self.data = data
        self.ticker = ticker
        self.engine = BacktestEngine(
            initial_capital=initial_capital,
            commission=commission
        )

    def run(self) -> Dict[str, BacktestResult]:
        """
        Run all strategies and return results.

        Returns:
            Dictionary mapping strategy name -> BacktestResult
        """
        results = {}

        for strategy in self.strategies:
            result = self.engine.run_backtest(
                strategy=strategy,
                data=self.data,
                ticker=self.ticker
            )
            results[strategy.name] = result

        return results
