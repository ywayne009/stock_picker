"""Base Strategy Class"""
from typing import Dict, Any, Optional
import pandas as pd
from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get('name', 'Unnamed Strategy')
        self.parameters = config.get('parameters', {})
        self.indicators = []

    @abstractmethod
    def setup(self, data: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def calculate_position_size(self, signal: int, portfolio_value: float, current_price: float) -> float:
        if signal == 0:
            return 0.0
        position_value = portfolio_value * 0.1
        shares = position_value / current_price
        return shares if signal == 1 else -shares

    def risk_management(self, position: Dict[str, Any], current_price: float) -> Optional[str]:
        if not position:
            return None
        entry_price = position.get('entry_price', current_price)
        stop_loss = self.parameters.get('stop_loss', 0.05)
        take_profit = self.parameters.get('take_profit', 0.15)
        pct_change = (current_price - entry_price) / entry_price
        if position['quantity'] > 0:
            if pct_change <= -stop_loss or pct_change >= take_profit:
                return 'close'
        return None
