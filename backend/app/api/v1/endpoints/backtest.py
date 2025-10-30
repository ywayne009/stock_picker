"""Backtest API Endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/run")
async def run_backtest(config: dict):
    return {"message": "Backtest started", "job_id": "test-123"}

@router.get("/{backtest_id}/results")
async def get_results(backtest_id: str):
    return {"backtest_id": backtest_id, "status": "completed", "metrics": {}}
