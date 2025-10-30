"""Strategy API Endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def list_strategies():
    return {"strategies": []}

@router.post("/")
async def create_strategy(strategy_data: dict):
    return {"message": "Strategy created", "id": 1}

@router.get("/{strategy_id}")
async def get_strategy(strategy_id: int):
    return {"id": strategy_id, "name": "Sample Strategy"}

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int):
    return {"message": "Strategy deleted"}
