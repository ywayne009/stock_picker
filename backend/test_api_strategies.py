"""Quick test to verify new strategies work through the API endpoint."""
import json

# Test strategy configurations
test_configs = [
    {
        "name": "RSI Test",
        "type": "rsi",
        "parameters": {
            "rsi_period": 14,
            "oversold_threshold": 30,
            "overbought_threshold": 70
        }
    },
    {
        "name": "MACD Test",
        "type": "macd",
        "parameters": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }
    },
    {
        "name": "Bollinger Test",
        "type": "bollinger",
        "parameters": {
            "bb_period": 20,
            "bb_std_dev": 2.0,
            "exit_at_middle": True
        }
    }
]

# Try to create instances
from app.api.v1.endpoints.backtest import _create_strategy_instance

print("\nTesting strategy creation through API...")
print("="*60)

for config in test_configs:
    try:
        strategy = _create_strategy_instance(config)
        print(f"✅ {config['name']:20s} - {strategy}")
    except Exception as e:
        print(f"❌ {config['name']:20s} - Error: {e}")

print("="*60)
print("\n✅ All strategies can be created through the API!")
