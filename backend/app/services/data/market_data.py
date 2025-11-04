"""
Market Data Fetcher

Utility functions to fetch real-world market data from various sources.
Currently supports Yahoo Finance via yfinance library and CSV files.
"""
import pandas as pd
import yfinance as yf
from typing import Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os


def fetch_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = '1d'
) -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        interval: Data interval - '1d' (daily), '1h' (hourly), '1wk' (weekly), etc.

    Returns:
        DataFrame with OHLCV data (open, high, low, close, volume)

    Raises:
        ValueError: If data cannot be fetched or symbol is invalid

    Example:
        >>> data = fetch_stock_data('AAPL', '2022-01-01', '2024-01-01')
        >>> print(data.head())
    """
    try:
        # Suppress SSL warnings
        import warnings
        warnings.filterwarnings('ignore')

        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Fetch historical data using download for better reliability
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True  # Adjust for splits and dividends
        )

        if data.empty:
            raise ValueError(f"No data found for symbol '{symbol}' in the specified date range")

        # Handle MultiIndex columns (yfinance 0.2.66+ returns MultiIndex for single symbols)
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten MultiIndex by taking the first level
            data.columns = data.columns.get_level_values(0)

        # Standardize column names to lowercase
        data.columns = data.columns.str.lower()

        # Ensure we have the required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            raise ValueError(f"Data is missing required columns: {missing_columns}")

        # Keep only OHLCV columns
        data = data[required_columns]

        # Remove any rows with NaN values
        data = data.dropna()

        return data

    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")


def fetch_multiple_stocks(
    symbols: list,
    start_date: str,
    end_date: str,
    interval: str = '1d'
) -> dict:
    """
    Fetch data for multiple stocks.

    Args:
        symbols: List of ticker symbols
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        interval: Data interval

    Returns:
        Dictionary mapping symbol to DataFrame

    Example:
        >>> data = fetch_multiple_stocks(['AAPL', 'MSFT'], '2022-01-01', '2024-01-01')
        >>> aapl_data = data['AAPL']
    """
    results = {}
    errors = []

    for symbol in symbols:
        try:
            results[symbol] = fetch_stock_data(symbol, start_date, end_date, interval)
        except ValueError as e:
            errors.append(f"{symbol}: {str(e)}")

    if errors and not results:
        raise ValueError(f"Failed to fetch data for all symbols:\n" + "\n".join(errors))

    if errors:
        print(f"⚠️  Warning: Some symbols failed:\n" + "\n".join(errors))

    return results


def get_stock_info(symbol: str) -> dict:
    """
    Get company information for a stock.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with company info (name, sector, industry, etc.)

    Example:
        >>> info = get_stock_info('AAPL')
        >>> print(info['longName'])  # 'Apple Inc.'
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'description': info.get('longBusinessSummary', 'N/A')
        }
    except Exception as e:
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'market_cap': 0,
            'description': f'Error: {str(e)}'
        }


def get_popular_stocks() -> dict:
    """
    Get a dictionary of popular stocks for testing.

    Returns:
        Dictionary mapping category to list of symbols

    Example:
        >>> stocks = get_popular_stocks()
        >>> tech_stocks = stocks['Tech']
    """
    return {
        'Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
        'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK'],
        'Consumer': ['WMT', 'HD', 'NKE', 'MCD', 'SBUX', 'DIS'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
        'Indices': ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, Nasdaq, Russell 2000
    }


def validate_data_quality(data: pd.DataFrame, symbol: str = "Stock") -> Tuple[bool, list]:
    """
    Validate the quality of fetched data.

    Args:
        data: DataFrame with OHLCV data
        symbol: Symbol name for error messages

    Returns:
        Tuple of (is_valid, list of warnings/errors)

    Example:
        >>> data = fetch_stock_data('AAPL', '2022-01-01', '2024-01-01')
        >>> is_valid, messages = validate_data_quality(data, 'AAPL')
        >>> if not is_valid:
        >>>     print(messages)
    """
    issues = []
    is_valid = True

    # Check minimum data points
    if len(data) < 100:
        issues.append(f"⚠️  Warning: Only {len(data)} data points (recommended: 100+)")

    # Check for gaps in dates (assuming daily data)
    if len(data) > 1:
        date_diffs = data.index.to_series().diff()[1:]
        large_gaps = date_diffs[date_diffs > pd.Timedelta(days=5)]  # More than 5 days gap

        if len(large_gaps) > 0:
            issues.append(f"⚠️  Warning: {len(large_gaps)} date gaps larger than 5 days")

    # Check for zero volume days
    zero_volume_days = (data['volume'] == 0).sum()
    if zero_volume_days > 0:
        issues.append(f"⚠️  Warning: {zero_volume_days} days with zero volume")

    # Check for invalid OHLC relationships
    invalid_ohlc = (
        (data['high'] < data['low']) |
        (data['high'] < data['open']) |
        (data['high'] < data['close']) |
        (data['low'] > data['open']) |
        (data['low'] > data['close'])
    ).sum()

    if invalid_ohlc > 0:
        issues.append(f"❌ Error: {invalid_ohlc} bars with invalid OHLC relationships")
        is_valid = False

    # Check for extreme price movements (>50% in one day) - possible split issues
    if len(data) > 1:
        price_changes = data['close'].pct_change().abs()
        extreme_moves = (price_changes > 0.5).sum()

        if extreme_moves > 0:
            issues.append(f"⚠️  Warning: {extreme_moves} days with >50% price moves (check for splits)")

    # Check for NaN values
    nan_count = data.isna().sum().sum()
    if nan_count > 0:
        issues.append(f"❌ Error: {nan_count} NaN values found in data")
        is_valid = False

    # Summary
    if not issues:
        issues.append(f"✓ Data quality looks good for {symbol}")

    return is_valid, issues


def get_date_range_suggestion(years_back: int = 2) -> Tuple[str, str]:
    """
    Get suggested start and end dates for data fetching.

    Args:
        years_back: Number of years of historical data to fetch

    Returns:
        Tuple of (start_date, end_date) in 'YYYY-MM-DD' format

    Example:
        >>> start, end = get_date_range_suggestion(2)
        >>> print(f"{start} to {end}")
    """
    # Use a fixed recent date range that we know has data
    # This avoids issues with future dates or very recent dates
    # For demo purposes, use 2022-01-01 to 2024-01-01
    if years_back >= 2:
        return '2022-01-01', '2024-10-01'  # ~2.75 years of data
    else:
        return '2023-01-01', '2024-10-01'  # ~1.75 years of data


def load_csv_data(
    filepath: str,
    symbol: str = None
) -> pd.DataFrame:
    """
    Load stock data from a CSV file.

    Args:
        filepath: Path to CSV file with OHLCV data
        symbol: Optional symbol name for error messages

    Returns:
        DataFrame with OHLCV data

    Raises:
        ValueError: If file not found or invalid format

    Expected CSV format:
        Date,Open,High,Low,Close,Volume
        2022-01-01,100.0,105.0,99.0,103.0,1000000
        ...

    Example:
        >>> data = load_csv_data('data/AAPL.csv', 'AAPL')
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            raise ValueError(f"CSV file not found: {filepath}")

        # Load CSV
        data = pd.read_csv(filepath, index_col=0, parse_dates=True)

        # Standardize column names to lowercase
        data.columns = data.columns.str.lower()

        # Ensure we have the required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            raise ValueError(f"CSV missing required columns: {missing_columns}")

        # Keep only OHLCV columns
        data = data[required_columns]

        # Remove any rows with NaN values
        data = data.dropna()

        # Sort by date
        data = data.sort_index()

        symbol_name = symbol or 'CSV'
        print(f"   ✓ Loaded {len(data)} days from CSV file")

        return data

    except Exception as e:
        raise ValueError(f"Error loading CSV data: {str(e)}")


# Convenience function for demo
def fetch_demo_stock(
    symbol: str = 'AAPL',
    years_back: int = 2
) -> Tuple[pd.DataFrame, dict]:
    """
    Fetch stock data for demo purposes with automatic date range.

    Args:
        symbol: Stock ticker symbol (default: 'AAPL')
        years_back: Years of historical data (default: 2)

    Returns:
        Tuple of (data DataFrame, stock info dict)

    Example:
        >>> data, info = fetch_demo_stock('AAPL', years_back=2)
        >>> print(f"Fetched {len(data)} days of {info['name']} data")
    """
    start_date, end_date = get_date_range_suggestion(years_back)

    # First, try to fetch from Yahoo Finance
    print(f"📊 Fetching {symbol} data from {start_date} to {end_date}...")

    try:
        data = fetch_stock_data(symbol, start_date, end_date)
        info = get_stock_info(symbol)

        # Validate data quality
        is_valid, messages = validate_data_quality(data, symbol)
        for msg in messages:
            print(f"   {msg}")

        if not is_valid:
            raise ValueError("Data quality validation failed")

        print(f"   ✓ Successfully fetched {len(data)} days from Yahoo Finance")
        print(f"   ✓ Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

        return data, info

    except Exception as e:
        # If Yahoo Finance fails, try to load from CSV file
        print(f"   ⚠️  Yahoo Finance failed: {str(e)}")
        print(f"   🔄 Trying to load from local CSV file...")

        try:
            # Try to load from data directory
            csv_path = f"data/{symbol}.csv"
            data = load_csv_data(csv_path, symbol)

            # Create basic stock info
            info = {
                'symbol': symbol,
                'name': f"{symbol} (from CSV)",
                'sector': 'N/A',
                'industry': 'N/A',
                'market_cap': 0,
                'description': f'Data loaded from {csv_path}'
            }

            # Validate data quality
            is_valid, messages = validate_data_quality(data, symbol)
            for msg in messages:
                print(f"   {msg}")

            print(f"   ✓ Successfully loaded from CSV")
            print(f"   ✓ Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   ✓ Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

            return data, info

        except Exception as csv_error:
            raise ValueError(
                f"Failed to fetch data from both Yahoo Finance and CSV.\n"
                f"  Yahoo Finance error: {str(e)}\n"
                f"  CSV error: {str(csv_error)}\n"
                f"  Tip: Place a CSV file at 'data/{symbol}.csv' with OHLCV data."
            )
