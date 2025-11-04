"""
Base Strategy Class

This module provides the abstract base class that all trading strategies must inherit from.
It defines the interface and default implementations for strategy behavior.
"""
from typing import Dict, Any, Optional, List
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.

    All concrete strategy implementations must inherit from this class and implement
    the required abstract methods: setup() and generate_signals().

    Attributes:
        name (str): Human-readable name of the strategy
        parameters (Dict[str, Any]): Strategy-specific parameters
        description (str): Optional description of the strategy
        version (str): Strategy version for tracking changes
        created_at (datetime): Timestamp when strategy was created
        indicators (List[str]): List of technical indicators used

    Example:
        class MyStrategy(Strategy):
            def setup(self, data):
                self.sma_period = self.parameters.get('sma_period', 20)

            def generate_signals(self, data):
                data['signal'] = 0
                # Strategy logic here
                return data
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy with configuration.

        Args:
            config: Dictionary containing strategy configuration including:
                - name: Strategy name (required)
                - parameters: Strategy parameters (optional)
                - description: Strategy description (optional)
                - version: Strategy version (optional)

        Raises:
            ValueError: If required configuration is missing
        """
        self.name = config.get('name')
        if not self.name:
            raise ValueError("Strategy name is required in config")

        self.parameters = config.get('parameters', {})
        self.description = config.get('description', '')
        self.version = config.get('version', '1.0.0')
        self.created_at = datetime.now()
        self.indicators: List[str] = []

        # Position sizing defaults
        self.default_position_size = self.parameters.get('position_size', 0.1)  # 10% of portfolio

        # Risk management defaults
        self.default_stop_loss = self.parameters.get('stop_loss', 0.05)  # 5%
        self.default_take_profit = self.parameters.get('take_profit', 0.15)  # 15%

        # Validate parameters
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """
        Validate strategy parameters.

        Override this method in subclasses to add custom parameter validation.

        Raises:
            ValueError: If parameters are invalid
        """
        if not 0 < self.default_position_size <= 1:
            raise ValueError(f"Position size must be between 0 and 1, got {self.default_position_size}")

        if self.default_stop_loss < 0 or self.default_stop_loss > 1:
            raise ValueError(f"Stop loss must be between 0 and 1, got {self.default_stop_loss}")

        if self.default_take_profit < 0:
            raise ValueError(f"Take profit must be positive, got {self.default_take_profit}")

    @abstractmethod
    def setup(self, data: pd.DataFrame) -> None:
        """
        Setup method called before strategy execution.

        Use this method to:
        - Initialize indicators
        - Validate required columns in data
        - Set up any stateful variables
        - Pre-calculate any lookback periods

        Args:
            data: Historical OHLCV data with columns: ['open', 'high', 'low', 'close', 'volume']

        Raises:
            ValueError: If required columns are missing
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data.

        This is the core strategy logic that produces buy/sell signals.

        Args:
            data: OHLCV DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']

        Returns:
            DataFrame with added 'signal' column where:
                1 = Buy signal
                0 = Hold/No signal
                -1 = Sell signal

        Note:
            - Ensure no look-ahead bias (only use data available at each timestamp)
            - Handle NaN values appropriately
            - Maintain the same index as input data
        """
        pass

    def calculate_position_size(
        self,
        signal: int,
        portfolio_value: float,
        current_price: float,
        volatility: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on signal and portfolio value.

        Default implementation uses fixed fractional position sizing.
        Override this method for custom position sizing logic (e.g., Kelly Criterion,
        volatility-based sizing, etc.).

        Args:
            signal: Trading signal (1=buy, 0=hold, -1=sell)
            portfolio_value: Current total portfolio value
            current_price: Current price of the asset
            volatility: Optional volatility measure for dynamic sizing

        Returns:
            Number of shares to buy (positive) or sell (negative)
            Returns 0 for hold signals

        Example:
            >>> strategy.calculate_position_size(1, 100000, 50)
            200.0  # Buy 200 shares ($10,000 worth at $50/share)
        """
        if signal == 0:
            return 0.0

        # Calculate position value as fraction of portfolio
        position_value = portfolio_value * self.default_position_size

        # Adjust for volatility if provided (lower size for higher volatility)
        if volatility is not None and volatility > 0:
            volatility_adjustment = min(1.0, 0.02 / volatility)  # Scale based on 2% target volatility
            position_value *= volatility_adjustment

        # Convert to shares
        shares = position_value / current_price

        # Return positive for buy, negative for sell
        return shares if signal == 1 else -shares

    def risk_management(
        self,
        position: Dict[str, Any],
        current_price: float,
        data: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        """
        Check if position should be closed based on risk management rules.

        Default implementation uses stop-loss and take-profit levels.
        Override for custom risk management (trailing stops, time-based exits, etc.).

        Args:
            position: Dictionary containing:
                - quantity: Number of shares (positive=long, negative=short)
                - entry_price: Price at which position was entered
                - entry_date: Date when position was entered
            current_price: Current market price
            data: Optional recent price data for advanced risk management

        Returns:
            'close' if position should be closed, None otherwise

        Example:
            >>> position = {'quantity': 100, 'entry_price': 50}
            >>> strategy.risk_management(position, 45)  # 10% loss
            'close'
        """
        if not position or position.get('quantity', 0) == 0:
            return None

        entry_price = position.get('entry_price')
        if entry_price is None:
            return None

        quantity = position['quantity']

        # Calculate percentage change
        pct_change = (current_price - entry_price) / entry_price

        # For long positions
        if quantity > 0:
            # Hit stop loss (loss limit)
            if pct_change <= -self.default_stop_loss:
                return 'close'
            # Hit take profit (profit target)
            if pct_change >= self.default_take_profit:
                return 'close'

        # For short positions
        elif quantity < 0:
            # Hit stop loss (price went up)
            if pct_change >= self.default_stop_loss:
                return 'close'
            # Hit take profit (price went down)
            if pct_change <= -self.default_take_profit:
                return 'close'

        return None

    def get_required_history(self) -> int:
        """
        Get the minimum number of historical bars required for this strategy.

        Override this method to specify how much historical data is needed
        before the strategy can generate valid signals.

        Returns:
            Number of historical bars required (default: 50)
        """
        return 50

    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate that input data has required columns and format.

        Args:
            data: DataFrame to validate

        Raises:
            ValueError: If data is invalid or missing required columns
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            raise ValueError(f"Data missing required columns: {missing_columns}")

        if len(data) < self.get_required_history():
            raise ValueError(
                f"Insufficient data: strategy requires {self.get_required_history()} bars, "
                f"got {len(data)}"
            )

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize strategy configuration to dictionary.

        Returns:
            Dictionary containing strategy configuration
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'parameters': self.parameters,
            'indicators': self.indicators,
            'created_at': self.created_at.isoformat()
        }
