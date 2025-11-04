"""Data Services Module"""
from .market_data import (
    fetch_stock_data,
    fetch_multiple_stocks,
    get_stock_info,
    get_popular_stocks,
    validate_data_quality,
    get_date_range_suggestion,
    fetch_demo_stock,
    load_csv_data
)

__all__ = [
    'fetch_stock_data',
    'fetch_multiple_stocks',
    'get_stock_info',
    'get_popular_stocks',
    'validate_data_quality',
    'get_date_range_suggestion',
    'fetch_demo_stock',
    'load_csv_data'
]
