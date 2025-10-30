"""Base Data Provider"""
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd
from datetime import datetime

class DataProvider(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    def fetch_historical(self, symbol: str, start_date: datetime, end_date: datetime, interval: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_live_quote(self, symbol: str) -> dict:
        pass

    @abstractmethod
    def subscribe_realtime(self, symbols: List[str], callback):
        pass
