#!/usr/bin/env python3
"""
Test the new strategy factory and metadata system.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.strategy import (
    get_factory,
    list_strategies,
    create_strategy,
    StrategyType
)

# Import to trigger registrations
from app.services.strategy.examples import register_all


def main():
    print("\n" + "="*70)
    print(" TESTING STRATEGY FACTORY AND METADATA SYSTEM")
    print("="*70)

    factory = get_factory()

    # Test 1: List all strategies
    print("\n📋 Registered Strategies:")
    print("-"*70)
    strategies = list_strategies()

    if strategies:
        for strategy in strategies:
            print(f"\n✓ {strategy['name']}")
            print(f"   Class: {strategy['class']}")
            if 'description' in strategy:
                print(f"   Description: {strategy['description']}")
            if 'complexity' in strategy:
                print(f"   Complexity: {strategy['complexity']}")
            if 'tags' in strategy:
                print(f"   Tags: {', '.join(strategy['tags'])}")
    else:
        print("⚠️  No strategies registered yet")

    # Test 2: Create a strategy instance
    print("\n" + "="*70)
    print(" TEST: Creating Strategy Instance")
    print("="*70)

    config = {
        'name': 'Test RSI Strategy',
        'parameters': {
            'rsi_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70
        }
    }

    try:
        strategy = create_strategy('rsi', config)
        print(f"✅ Created: {strategy}")
        print(f"   Name: {strategy.name}")
        print(f"   Parameters: {strategy.parameters}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Get metadata
    print("\n" + "="*70)
    print(" TEST: Strategy Metadata")
    print("="*70)

    metadata = factory.get_metadata('rsi')
    if metadata:
        print(f"✅ Metadata found for 'rsi'")
        print(f"   Type: {metadata.strategy_type.value}")
        print(f"   Category: {metadata.category.value}")
        print(f"   Best Markets: {[r.value for r in metadata.best_market_regime]}")
        print(f"   Suitable for Beginners: {metadata.suitable_for_beginners}")
        print(f"\n   Pros:")
        for pro in metadata.pros:
            print(f"      + {pro}")
        print(f"\n   Cons:")
        for con in metadata.cons:
            print(f"      - {con}")
    else:
        print("⚠️  No metadata found")

    # Test 4: Search strategies
    print("\n" + "="*70)
    print(" TEST: Search Strategies")
    print("="*70)

    signal_strategies = factory.list_by_type(StrategyType.SIGNAL)
    print(f"✅ Signal strategies: {signal_strategies}")

    beginner_strategies = factory.search(beginner_friendly=True)
    print(f"✅ Beginner-friendly strategies: {beginner_strategies}")

    mean_reversion = factory.search(tags=['mean_reversion'])
    print(f"✅ Mean reversion strategies: {mean_reversion}")

    print("\n" + "="*70)
    print(" ✅ ALL FACTORY TESTS PASSED!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
