"""
Backtest API Endpoints

Endpoints for running backtests and retrieving results.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import sys
from pathlib import Path
import uuid
from datetime import datetime
import traceback

# Add backtesting_system to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backtesting_system"))

from app.api.v1.schemas import (
    BacktestRequest,
    BacktestResults,
    BacktestStatusResponse,
    PerformanceMetrics,
    Trade,
    TradeSignal,
    EquityPoint,
    SignalType,
    BatchBacktestRequest,
    BatchBacktestResponse,
    BacktestSummary
)
from app.services.backtesting.engine import BacktestEngine
from app.services.strategy.examples.ma_crossover import MovingAverageCrossover
from app.services.data import fetch_stock_data

# Import strategy configurations
try:
    from strategies_config import STRATEGY_PRESETS, get_strategy_config
except ImportError:
    STRATEGY_PRESETS = {}
    def get_strategy_config(name: str) -> dict:
        raise ImportError("strategies_config module not found")

router = APIRouter()

# In-memory storage for backtest results (in production, use Redis or database)
_backtest_results: Dict[str, Any] = {}


def _create_strategy_instance(strategy_config: dict):
    """
    Create a strategy instance from configuration.

    Args:
        strategy_config: Strategy configuration with 'type' and 'parameters'

    Returns:
        Strategy instance
    """
    strategy_type = strategy_config.get('type', 'ma_crossover')
    parameters = strategy_config.get('parameters', {})

    # For now, we primarily use MovingAverageCrossover
    # In the future, we can map different strategy types to different classes
    config = {
        'name': strategy_config.get('name', 'Custom Strategy'),
        'parameters': parameters
    }

    return MovingAverageCrossover(config)


def _convert_metrics_to_schema(metrics) -> PerformanceMetrics:
    """Convert PerformanceMetrics object to Pydantic schema."""
    import math

    # Helper to convert inf/nan to safe values
    def safe_float(value, default=0.0):
        if value is None or math.isnan(value) or math.isinf(value):
            return default
        return float(value)

    # Calculate total_return_pct and max_drawdown_pct
    total_return_pct = metrics.total_return * 100
    max_drawdown_pct = metrics.max_drawdown * 100

    return PerformanceMetrics(
        total_return=safe_float(metrics.total_return),
        total_return_pct=safe_float(total_return_pct),
        cagr=safe_float(metrics.cagr),
        sharpe_ratio=safe_float(metrics.sharpe_ratio),
        sortino_ratio=safe_float(metrics.sortino_ratio),
        max_drawdown=safe_float(metrics.max_drawdown),
        max_drawdown_pct=safe_float(max_drawdown_pct),
        volatility=safe_float(metrics.volatility),
        total_trades=int(metrics.total_trades),
        winning_trades=int(metrics.winning_trades),
        losing_trades=int(metrics.losing_trades),
        win_rate=safe_float(metrics.win_rate),
        profit_factor=safe_float(metrics.profit_factor, default=0.0),  # Can be inf
        avg_win=safe_float(metrics.average_win),
        avg_loss=safe_float(metrics.average_loss),
        avg_trade=safe_float(metrics.average_trade),
        largest_win=safe_float(metrics.largest_win),
        largest_loss=safe_float(metrics.largest_loss),
        avg_holding_period=safe_float(metrics.average_trade_duration) if metrics.average_trade_duration else None,
        expectancy=safe_float(metrics.expectancy),
        risk_free_rate=0.02
    )


def _extract_signals(signals_df) -> list:
    """Extract trade signals from DataFrame."""
    trade_signals = []

    for date_idx, row in signals_df.iterrows():
        if row['signal'] != 0:
            signal_type = SignalType.BUY if row['signal'] == 1 else SignalType.SELL

            trade_signals.append(TradeSignal(
                date=date_idx.strftime('%Y-%m-%d'),
                signal_type=signal_type,
                price=float(row['close']),
                shares=None,  # Would need to track from portfolio
                position_value=None,
                reason=f"{'Buy' if row['signal'] == 1 else 'Sell'} signal generated"
            ))

    return trade_signals


def _extract_trades(trades_list) -> list:
    """Extract trades from backtest result."""
    trade_objects = []

    for trade in trades_list:
        # Convert Timestamp to string if needed
        entry_date = trade['entry_date']
        if hasattr(entry_date, 'isoformat'):
            entry_date = entry_date.isoformat()
        elif hasattr(entry_date, 'strftime'):
            entry_date = entry_date.strftime('%Y-%m-%d')

        exit_date = trade.get('exit_date')
        if exit_date:
            if hasattr(exit_date, 'isoformat'):
                exit_date = exit_date.isoformat()
            elif hasattr(exit_date, 'strftime'):
                exit_date = exit_date.strftime('%Y-%m-%d')

        trade_objects.append(Trade(
            entry_date=str(entry_date),
            exit_date=str(exit_date) if exit_date else None,
            entry_price=float(trade['entry_price']),
            exit_price=float(trade['exit_price']) if trade.get('exit_price') else None,
            shares=float(trade['shares']),
            profit_loss=float(trade['profit_loss']) if trade.get('profit_loss') else None,
            profit_loss_pct=float(trade['profit_loss_pct']) if trade.get('profit_loss_pct') else None,
            duration_days=int(trade['duration_days']) if trade.get('duration_days') else None
        ))

    return trade_objects


def _extract_equity_curve(portfolio_history) -> list:
    """Extract equity curve from portfolio history."""
    equity_points = []

    # Calculate peak for drawdown
    peak = portfolio_history['portfolio_value'].expanding().max()

    for date_idx, row in portfolio_history.iterrows():
        current_value = row['portfolio_value']
        current_peak = peak.loc[date_idx]
        drawdown = current_peak - current_value
        drawdown_pct = (drawdown / current_peak * 100) if current_peak > 0 else 0

        equity_points.append(EquityPoint(
            date=date_idx.strftime('%Y-%m-%d'),
            portfolio_value=float(current_value),
            cash=float(row['cash']),
            position_value=float(current_value - row['cash']),
            drawdown=float(drawdown),
            drawdown_pct=float(drawdown_pct)
        ))

    return equity_points


async def _run_backtest_task(
    backtest_id: str,
    request: BacktestRequest
):
    """
    Background task to run backtest.

    Updates _backtest_results with status and results.
    """
    try:
        # Update status to running
        _backtest_results[backtest_id]['status'] = 'running'
        _backtest_results[backtest_id]['progress'] = 0.1

        # Fetch stock data
        data = fetch_stock_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            interval='1d'
        )

        _backtest_results[backtest_id]['progress'] = 0.3

        # Create strategy instance
        strategy = _create_strategy_instance(request.strategy.dict())

        _backtest_results[backtest_id]['progress'] = 0.4

        # Create backtest engine
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=0.0005  # Default slippage
        )

        _backtest_results[backtest_id]['progress'] = 0.5

        # Run backtest
        result = engine.run_backtest(
            strategy=strategy,
            data=data,
            ticker=request.symbol
        )

        _backtest_results[backtest_id]['progress'] = 0.8

        # Convert to API schema
        metrics = _convert_metrics_to_schema(result.metrics)
        signals = _extract_signals(result.signals)
        trades = _extract_trades(result.trades)
        equity_curve = _extract_equity_curve(result.portfolio_history)

        _backtest_results[backtest_id]['progress'] = 0.9

        # Build final result
        final_value = result.portfolio_history['portfolio_value'].iloc[-1]

        backtest_result = BacktestResults(
            backtest_id=backtest_id,
            symbol=request.symbol,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            final_value=float(final_value),
            metrics=metrics,
            signals=signals,
            trades=trades,
            equity_curve=equity_curve,
            created_at=_backtest_results[backtest_id]['created_at'],
            status='completed',
            error_message=None
        )

        # Store result
        _backtest_results[backtest_id]['status'] = 'completed'
        _backtest_results[backtest_id]['progress'] = 1.0
        _backtest_results[backtest_id]['result'] = backtest_result

    except Exception as e:
        # Handle errors
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        _backtest_results[backtest_id]['status'] = 'failed'
        _backtest_results[backtest_id]['error'] = error_msg
        print(f"Backtest {backtest_id} failed: {error_msg}")


@router.post("/run", response_model=BacktestStatusResponse)
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """
    Run a backtest with the specified configuration.

    This endpoint starts a backtest and returns immediately with a backtest ID.
    Use the GET /backtest/{id}/results endpoint to retrieve results when complete.

    For now, we run synchronously for simplicity. In production, this would
    use Celery or similar for true background processing.
    """
    try:
        # Generate unique backtest ID
        backtest_id = str(uuid.uuid4())

        # Initialize result entry
        _backtest_results[backtest_id] = {
            'status': 'pending',
            'progress': 0.0,
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }

        # For simplicity, run synchronously (in production, use background task)
        # background_tasks.add_task(_run_backtest_task, backtest_id, request)

        # Run immediately for faster response
        await _run_backtest_task(backtest_id, request)

        return BacktestStatusResponse(
            backtest_id=backtest_id,
            status=_backtest_results[backtest_id]['status'],
            progress=_backtest_results[backtest_id]['progress'],
            message="Backtest completed" if _backtest_results[backtest_id]['status'] == 'completed' else "Backtest started"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting backtest: {str(e)}"
        )


@router.get("/{backtest_id}/status", response_model=BacktestStatusResponse)
async def get_backtest_status(backtest_id: str):
    """
    Get the status of a running or completed backtest.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    result = _backtest_results[backtest_id]

    return BacktestStatusResponse(
        backtest_id=backtest_id,
        status=result['status'],
        progress=result.get('progress', 0.0),
        message=result.get('error') if result['status'] == 'failed' else None
    )


@router.get("/{backtest_id}/results", response_model=BacktestResults)
async def get_backtest_results(backtest_id: str):
    """
    Get the complete results of a backtest.

    Returns all metrics, trades, signals, and equity curve data.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    result = _backtest_results[backtest_id]

    if result['status'] == 'failed':
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {result.get('error', 'Unknown error')}"
        )

    if result['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Backtest not yet completed. Status: {result['status']}"
        )

    return result['result']


@router.get("/{backtest_id}/metrics", response_model=PerformanceMetrics)
async def get_backtest_metrics(backtest_id: str):
    """
    Get only the performance metrics for a backtest.

    Useful for quick performance checks without loading full results.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    result = _backtest_results[backtest_id]

    if result['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Backtest not yet completed. Status: {result['status']}"
        )

    return result['result'].metrics


@router.get("/{backtest_id}/trades", response_model=list)
async def get_backtest_trades(backtest_id: str):
    """
    Get only the trade history for a backtest.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    result = _backtest_results[backtest_id]

    if result['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Backtest not yet completed. Status: {result['status']}"
        )

    return result['result'].trades


@router.delete("/{backtest_id}")
async def delete_backtest(backtest_id: str):
    """
    Delete a backtest from memory.

    Useful for cleaning up old backtests.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    del _backtest_results[backtest_id]

    return {"message": f"Backtest '{backtest_id}' deleted successfully"}


@router.get("/list/all")
async def list_all_backtests():
    """
    List all backtests in memory.

    Useful for debugging and seeing backtest history.
    """
    backtests = []

    for backtest_id, data in _backtest_results.items():
        backtests.append({
            'backtest_id': backtest_id,
            'status': data['status'],
            'created_at': data['created_at'],
            'symbol': data['result'].symbol if data.get('result') else None,
            'strategy': data['result'].strategy.name if data.get('result') else None
        })

    return {'backtests': backtests, 'total': len(backtests)}


@router.post("/batch", response_model=BatchBacktestResponse)
async def run_batch_backtest(request: BatchBacktestRequest):
    """
    Run multiple backtests in parallel for comparison matrix.

    This endpoint runs backtests for multiple stock-strategy combinations
    and returns compact summaries for display in the comparison matrix.

    Example request:
    {
        "items": [
            {"symbol": "AAPL", "strategy": {...}},
            {"symbol": "MSFT", "strategy": {...}}
        ],
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 100000,
        "commission": 0.001
    }
    """
    import concurrent.futures

    batch_id = str(uuid.uuid4())
    summaries = []

    def run_single_backtest(item):
        """Run a single backtest and return summary"""
        backtest_id = str(uuid.uuid4())

        try:
            print(f"Running backtest for {item.symbol} with strategy {item.strategy.name}")

            # Fetch data
            data = fetch_stock_data(
                symbol=item.symbol,
                start_date=request.start_date,
                end_date=request.end_date,
                interval='1d'
            )
            first_close = float(data['close'].iloc[0])
            last_close = float(data['close'].iloc[-1])
            print(f"Fetched {len(data)} bars for {item.symbol}, first close={first_close:.2f}, last close={last_close:.2f}")

            # Create strategy instance
            strategy = _create_strategy_instance(item.strategy.dict())

            # Create backtest engine
            engine = BacktestEngine(
                initial_capital=request.initial_capital,
                commission=request.commission,
                slippage=0.0005
            )

            # Run backtest (make a copy to avoid data mutation issues)
            result = engine.run_backtest(
                strategy=strategy,
                data=data.copy(),
                ticker=item.symbol
            )

            # Convert metrics
            metrics = _convert_metrics_to_schema(result.metrics)
            signals = _extract_signals(result.signals)
            trades = _extract_trades(result.trades)
            equity_curve = _extract_equity_curve(result.portfolio_history)
            final_value = float(result.portfolio_history['portfolio_value'].iloc[-1])

            # Store full result
            backtest_result = BacktestResults(
                backtest_id=backtest_id,
                symbol=item.symbol,
                strategy=item.strategy,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital,
                final_value=final_value,
                metrics=metrics,
                signals=signals,
                trades=trades,
                equity_curve=equity_curve,
                created_at=datetime.now().isoformat(),
                status='completed',
                error_message=None
            )

            _backtest_results[backtest_id] = {
                'status': 'completed',
                'progress': 1.0,
                'created_at': datetime.now().isoformat(),
                'result': backtest_result,
                'error': None
            }

            # Return compact summary
            summary = BacktestSummary(
                backtest_id=backtest_id,
                symbol=item.symbol,
                strategy_name=item.strategy.name,
                status='completed',
                total_return_pct=metrics.total_return_pct,
                sharpe_ratio=metrics.sharpe_ratio,
                max_drawdown_pct=metrics.max_drawdown_pct,
                total_trades=metrics.total_trades,
                win_rate=metrics.win_rate,
                error_message=None
            )
            print(f"Completed {item.symbol} - {item.strategy.name}: return={metrics.total_return_pct:.2f}%, sharpe={metrics.sharpe_ratio:.2f}")
            return summary

        except Exception as e:
            error_msg = f"{str(e)}"
            print(f"Batch backtest failed for {item.symbol} - {item.strategy.name}: {error_msg}")

            return BacktestSummary(
                backtest_id=backtest_id,
                symbol=item.symbol,
                strategy_name=item.strategy.name,
                status='failed',
                total_return_pct=None,
                sharpe_ratio=None,
                max_drawdown_pct=None,
                total_trades=None,
                win_rate=None,
                error_message=error_msg
            )

    # Run backtests sequentially to avoid yfinance thread-safety issues
    # Note: ThreadPoolExecutor causes yfinance to return same data for all symbols
    summaries = [run_single_backtest(item) for item in request.items]

    return BatchBacktestResponse(
        batch_id=batch_id,
        total_items=len(request.items),
        summaries=summaries,
        created_at=datetime.now().isoformat()
    )


@router.get("/{backtest_id}/summary", response_model=BacktestSummary)
async def get_backtest_summary(backtest_id: str):
    """
    Get a compact summary of a backtest (for matrix display).

    Returns only the key metrics needed for the comparison matrix,
    much faster than fetching full results.
    """
    if backtest_id not in _backtest_results:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest '{backtest_id}' not found"
        )

    result = _backtest_results[backtest_id]

    if result['status'] == 'failed':
        return BacktestSummary(
            backtest_id=backtest_id,
            symbol=result.get('symbol', 'UNKNOWN'),
            strategy_name=result.get('strategy_name', 'UNKNOWN'),
            status='failed',
            error_message=result.get('error', 'Unknown error')
        )

    if result['status'] != 'completed':
        return BacktestSummary(
            backtest_id=backtest_id,
            symbol=result['result'].symbol if result.get('result') else 'UNKNOWN',
            strategy_name=result['result'].strategy.name if result.get('result') else 'UNKNOWN',
            status=result['status'],
        )

    # Extract key metrics from full result
    full_result = result['result']
    metrics = full_result.metrics

    return BacktestSummary(
        backtest_id=backtest_id,
        symbol=full_result.symbol,
        strategy_name=full_result.strategy.name,
        status='completed',
        total_return_pct=metrics.total_return_pct,
        sharpe_ratio=metrics.sharpe_ratio,
        max_drawdown_pct=metrics.max_drawdown_pct,
        total_trades=metrics.total_trades,
        win_rate=metrics.win_rate,
        error_message=None
    )
