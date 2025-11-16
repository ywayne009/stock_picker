"""
Technical Indicators Module

Pure pandas implementation of common technical indicators.
This module provides a ta-lib alternative using only pandas and numpy.
"""
import pandas as pd
import numpy as np
from typing import Tuple


def sma(data: pd.Series, period: int) -> pd.Series:
    """
    Simple Moving Average.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average

    Returns:
        Series with SMA values
    """
    # Ensure we have a Series (handle DataFrame with single column)
    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0] if len(data.columns) == 1 else data.squeeze()

    return data.rolling(window=period, min_periods=period).mean()


def ema(data: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the EMA

    Returns:
        Series with EMA values
    """
    # Ensure we have a Series (handle DataFrame with single column)
    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0] if len(data.columns) == 1 else data.squeeze()

    return data.ewm(span=period, adjust=False, min_periods=period).mean()


def rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for RSI calculation (default: 14)

    Returns:
        Series with RSI values (0-100)
    """
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period, min_periods=period).mean()
    avg_losses = losses.rolling(window=period, min_periods=period).mean()

    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi_values = 100 - (100 / (1 + rs))

    return rsi_values


def macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Moving Average Convergence Divergence.

    Args:
        data: Price series (typically close prices)
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    # Calculate fast and slow EMAs
    fast_ema = ema(data, fast_period)
    slow_ema = ema(data, slow_period)

    # MACD line
    macd_line = fast_ema - slow_ema

    # Signal line
    signal_line = ema(macd_line, signal_period)

    # Histogram
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def bollinger_bands(
    data: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average (default: 20)
        std_dev: Number of standard deviations for bands (default: 2.0)

    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    middle_band = sma(data, period)
    std = data.rolling(window=period, min_periods=period).std()

    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)

    return upper_band, middle_band, lower_band


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Average True Range (volatility indicator).

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Number of periods for ATR calculation (default: 14)

    Returns:
        Series with ATR values
    """
    # Calculate True Range
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Calculate ATR as moving average of True Range
    atr_values = true_range.rolling(window=period, min_periods=period).mean()

    return atr_values


def stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """
    Stochastic Oscillator.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        k_period: Number of periods for %K calculation (default: 14)
        d_period: Number of periods for %D smoothing (default: 3)

    Returns:
        Tuple of (%K, %D)
    """
    # Calculate %K
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()

    k_values = 100 * (close - lowest_low) / (highest_high - lowest_low)

    # Calculate %D (smoothed %K)
    d_values = k_values.rolling(window=d_period, min_periods=d_period).mean()

    return k_values, d_values


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On-Balance Volume.

    Args:
        close: Close prices
        volume: Volume

    Returns:
        Series with OBV values
    """
    # Calculate price direction
    direction = np.where(close.diff() > 0, 1, np.where(close.diff() < 0, -1, 0))

    # Calculate OBV
    obv_values = (direction * volume).cumsum()

    return pd.Series(obv_values, index=close.index)


def vwap(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series
) -> pd.Series:
    """
    Volume Weighted Average Price.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        volume: Volume

    Returns:
        Series with VWAP values
    """
    typical_price = (high + low + close) / 3
    vwap_values = (typical_price * volume).cumsum() / volume.cumsum()

    return vwap_values


def adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Average Directional Index (trend strength indicator).

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Number of periods for ADX calculation (default: 14)

    Returns:
        Series with ADX values (0-100)
    """
    # Calculate +DM and -DM
    high_diff = high.diff()
    low_diff = -low.diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    # Calculate ATR
    atr_values = atr(high, low, close, period)

    # Calculate +DI and -DI
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr_values)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr_values)

    # Calculate DX and ADX
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx_values = dx.rolling(window=period).mean()

    return adx_values


def calculate_returns(close: pd.Series, periods: int = 1) -> pd.Series:
    """
    Calculate percentage returns.

    Args:
        close: Close prices
        periods: Number of periods for return calculation (default: 1)

    Returns:
        Series with percentage returns
    """
    return close.pct_change(periods=periods)


def calculate_volatility(close: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate rolling volatility (standard deviation of returns).

    Args:
        close: Close prices
        period: Number of periods for volatility calculation (default: 20)

    Returns:
        Series with annualized volatility values
    """
    returns = calculate_returns(close)
    volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized

    return volatility


def donchian_channel(
    high: pd.Series,
    low: pd.Series,
    period: int = 20
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Donchian Channel (price channel based on highest high and lowest low).

    Args:
        high: High prices
        low: Low prices
        period: Number of periods for channel calculation (default: 20)

    Returns:
        Tuple of (upper_channel, middle_channel, lower_channel)
    """
    upper_channel = high.rolling(window=period, min_periods=period).max()
    lower_channel = low.rolling(window=period, min_periods=period).min()
    middle_channel = (upper_channel + lower_channel) / 2

    return upper_channel, middle_channel, lower_channel


# ============================================================================
# Volume-Based Indicators (Phase 3)
# ============================================================================

def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On-Balance Volume (OBV).

    Cumulative volume indicator that adds volume on up days and subtracts on down days.
    Rising OBV confirms uptrend, falling OBV confirms downtrend.
    Divergences between price and OBV can signal reversals.

    Args:
        close: Close prices
        volume: Volume data

    Returns:
        Series with OBV values
    """
    # Calculate price direction
    price_change = close.diff()

    # Create signed volume (positive on up days, negative on down days, zero on unchanged)
    signed_volume = pd.Series(index=close.index, dtype=float)
    signed_volume[price_change > 0] = volume[price_change > 0]
    signed_volume[price_change < 0] = -volume[price_change < 0]
    signed_volume[price_change == 0] = 0

    # Cumulative sum
    obv_values = signed_volume.cumsum()

    return obv_values


def accumulation_distribution(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series
) -> pd.Series:
    """
    Accumulation/Distribution Line (A/D Line).

    Volume-weighted indicator that measures buying/selling pressure.
    Uses the close location value (CLV) relative to the high-low range.
    Rising A/D suggests accumulation, falling A/D suggests distribution.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        volume: Volume data

    Returns:
        Series with A/D line values
    """
    # Money Flow Multiplier (MFM)
    # MFM = [(Close - Low) - (High - Close)] / (High - Low)
    # Ranges from -1 (close at low) to +1 (close at high)
    clv = ((close - low) - (high - close)) / (high - low)

    # Handle division by zero (high == low)
    clv = clv.fillna(0)

    # Money Flow Volume = MFM * Volume
    mfv = clv * volume

    # A/D Line is cumulative sum of Money Flow Volume
    ad_line = mfv.cumsum()

    return ad_line


def vwma(close: pd.Series, volume: pd.Series, period: int) -> pd.Series:
    """
    Volume-Weighted Moving Average (VWMA).

    A moving average that gives more weight to periods with higher volume.
    More responsive to high-volume price moves than simple MA.

    Args:
        close: Close prices
        volume: Volume data
        period: Number of periods for the moving average

    Returns:
        Series with VWMA values
    """
    # Calculate price * volume
    pv = close * volume

    # Sum of (price * volume) over period
    pv_sum = pv.rolling(window=period, min_periods=period).sum()

    # Sum of volume over period
    volume_sum = volume.rolling(window=period, min_periods=period).sum()

    # VWMA = sum(price * volume) / sum(volume)
    vwma_values = pv_sum / volume_sum

    return vwma_values
