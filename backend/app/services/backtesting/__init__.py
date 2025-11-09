"""
Backtesting Module

Provides a universal backtesting engine that works with any strategy.
"""
from .engine import BacktestEngine, BacktestResult

__all__ = ['BacktestEngine', 'BacktestResult']
