"""
Data API Endpoints

Endpoints for fetching stock market data, company information,
and searching for stock symbols.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
import pandas as pd

from app.api.v1.schemas import (
    StockInfo,
    StockSearchResult,
    StockDataResponse,
    StockDataRequest,
    OHLCVData,
    ChartDataPoint,
    ErrorResponse
)
from app.services.data import (
    get_stock_info,
    fetch_stock_data,
    get_popular_stocks
)

router = APIRouter()


@router.get("/stocks/search", response_model=List[StockSearchResult])
async def search_stocks(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search for stock symbols by name or ticker.

    Currently returns popular stocks that match the query.
    In production, this would query a stock symbols database.
    """
    try:
        query = q.upper()

        # Get popular stocks
        popular = get_popular_stocks()
        results = []

        # Search through all categories
        for category, symbols in popular.items():
            for symbol in symbols:
                if query in symbol:
                    # Get basic info (limited to avoid rate limiting)
                    results.append(StockSearchResult(
                        symbol=symbol,
                        name=symbol,  # In production, fetch actual name
                        exchange="NASDAQ/NYSE"
                    ))

                    # Limit results to 10
                    if len(results) >= 10:
                        break

            if len(results) >= 10:
                break

        # If exact match not found, try fetching info
        if query not in [r.symbol for r in results]:
            try:
                info = get_stock_info(query)
                if info['name'] != query:  # Valid symbol found
                    results.insert(0, StockSearchResult(
                        symbol=info['symbol'],
                        name=info['name'],
                        exchange="NASDAQ/NYSE"
                    ))
            except:
                pass

        if not results:
            # Return the query as a potential symbol
            results.append(StockSearchResult(
                symbol=query,
                name=f"{query} (Symbol)",
                exchange="Unknown"
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{symbol}/info", response_model=StockInfo)
async def get_stock_information(symbol: str):
    """
    Get detailed company information for a stock symbol.
    """
    try:
        symbol = symbol.upper()
        info = get_stock_info(symbol)

        return StockInfo(
            symbol=info['symbol'],
            name=info['name'],
            sector=info['sector'],
            industry=info['industry'],
            market_cap=info['market_cap'],
            description=info['description']
        )

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{symbol}' not found or data unavailable: {str(e)}"
        )


@router.post("/stocks/ohlcv", response_model=StockDataResponse)
async def get_stock_ohlcv(request: StockDataRequest):
    """
    Get OHLCV (Open, High, Low, Close, Volume) historical data for a stock.

    This is the primary endpoint for fetching price data for backtesting
    and chart visualization.
    """
    try:
        # Fetch data
        df = fetch_stock_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval.value
        )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {request.symbol} in the specified date range"
            )

        # Convert DataFrame to list of OHLCV objects
        data_points = []
        for date_idx, row in df.iterrows():
            data_points.append(OHLCVData(
                date=date_idx.strftime('%Y-%m-%d'),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            ))

        return StockDataResponse(
            symbol=request.symbol,
            data=data_points,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval.value
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/stocks/{symbol}/ohlcv", response_model=StockDataResponse)
async def get_stock_ohlcv_get(
    symbol: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    interval: str = Query(default="1d", description="Data interval (1d, 1h, 1wk, 1mo)")
):
    """
    GET version of OHLCV endpoint for convenience.
    Same as POST /stocks/ohlcv but uses query parameters.
    """
    request = StockDataRequest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    return await get_stock_ohlcv(request)


@router.get("/stocks/{symbol}/chart", response_model=List[ChartDataPoint])
async def get_chart_data(
    symbol: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get chart-ready data in TradingView Lightweight Charts format.

    Returns OHLCV data with Unix timestamps suitable for direct use
    in TradingView charts.
    """
    try:
        # Fetch data
        df = fetch_stock_data(
            symbol=symbol.upper(),
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol}"
            )

        # Convert to TradingView format
        chart_data = []
        for date_idx, row in df.iterrows():
            chart_data.append(ChartDataPoint(
                time=int(date_idx.timestamp()),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            ))

        return chart_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")


@router.get("/popular", response_model=dict)
async def get_popular_stocks_list():
    """
    Get a curated list of popular stocks by category.
    Useful for quick selection in the UI.
    """
    try:
        return get_popular_stocks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
