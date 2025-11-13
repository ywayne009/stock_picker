#!/bin/bash
# Test script for batch backtest endpoint
# Usage: ./test_batch_endpoint.sh

echo "🧪 Testing Batch Backtest Endpoint"
echo "=================================="
echo ""

# Test batch backtest with 2 stocks and 2 strategies
echo "📊 Running batch backtest: AAPL and MSFT with 2 strategies"
echo ""

curl -X POST http://localhost:8000/api/v1/backtest/batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "symbol": "AAPL",
        "strategy": {
          "name": "MA Crossover 20/50 SMA",
          "type": "ma_crossover",
          "parameters": {
            "fast_period": 20,
            "slow_period": 50,
            "ma_type": "sma",
            "position_size": 0.1,
            "stop_loss": 0.05,
            "take_profit": 0.15
          }
        }
      },
      {
        "symbol": "MSFT",
        "strategy": {
          "name": "MA Crossover 20/50 SMA",
          "type": "ma_crossover",
          "parameters": {
            "fast_period": 20,
            "slow_period": 50,
            "ma_type": "sma",
            "position_size": 0.1,
            "stop_loss": 0.05,
            "take_profit": 0.15
          }
        }
      }
    ],
    "start_date": "2024-01-01",
    "end_date": "2024-11-12",
    "initial_capital": 100000,
    "commission": 0.001
  }' | python3 -m json.tool

echo ""
echo "✅ Test complete!"
echo ""
echo "Expected response:"
echo "  - batch_id: UUID"
echo "  - total_items: 2"
echo "  - summaries: Array with 2 BacktestSummary objects"
echo "  - Each summary should have: backtest_id, symbol, strategy_name, status, metrics"
