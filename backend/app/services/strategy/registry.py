"""
Strategy Registry

Central registry for managing and accessing strategies.
Makes it easy to switch between strategies without code changes.
"""
from typing import Dict, List, Any, Type, Optional
from .base_strategy import Strategy


class StrategyRegistry:
    """
    Registry for managing trading strategies.

    Allows easy registration, retrieval, and listing of strategies.

    Example:
        # Register a strategy
        registry = StrategyRegistry()
        registry.register('ma_crossover', MovingAverageCrossover)

        # Get a strategy by name
        strategy_class = registry.get('ma_crossover')
        strategy = strategy_class(config)

        # List all strategies
        all_strategies = registry.list_all()
    """

    def __init__(self):
        """Initialize empty registry."""
        self._strategies: Dict[str, Type[Strategy]] = {}
        self._descriptions: Dict[str, str] = {}
        self._categories: Dict[str, str] = {}

    def register(
        self,
        name: str,
        strategy_class: Type[Strategy],
        description: str = "",
        category: str = "general"
    ) -> None:
        """
        Register a strategy class.

        Args:
            name: Unique name for the strategy
            strategy_class: Strategy class (not instance)
            description: Human-readable description
            category: Category (e.g., 'trend', 'mean_reversion', 'ml')
        """
        if name in self._strategies:
            raise ValueError(f"Strategy '{name}' already registered")

        if not issubclass(strategy_class, Strategy):
            raise TypeError(f"Strategy must inherit from Strategy base class")

        self._strategies[name] = strategy_class
        self._descriptions[name] = description
        self._categories[name] = category

    def get(self, name: str) -> Type[Strategy]:
        """
        Get a strategy class by name.

        Args:
            name: Strategy name

        Returns:
            Strategy class

        Raises:
            KeyError: If strategy not found
        """
        if name not in self._strategies:
            available = ', '.join(self._strategies.keys())
            raise KeyError(
                f"Strategy '{name}' not found. "
                f"Available strategies: {available}"
            )

        return self._strategies[name]

    def create_instance(
        self,
        name: str,
        config: Dict[str, Any]
    ) -> Strategy:
        """
        Create a strategy instance with configuration.

        Args:
            name: Strategy name
            config: Strategy configuration

        Returns:
            Strategy instance
        """
        strategy_class = self.get(name)
        return strategy_class(config)

    def list_all(self) -> List[Dict[str, str]]:
        """
        List all registered strategies.

        Returns:
            List of dicts with strategy info
        """
        return [
            {
                'name': name,
                'class': cls.__name__,
                'description': self._descriptions.get(name, ''),
                'category': self._categories.get(name, 'general')
            }
            for name, cls in self._strategies.items()
        ]

    def list_by_category(self, category: str) -> List[str]:
        """
        List strategies in a specific category.

        Args:
            category: Category name

        Returns:
            List of strategy names
        """
        return [
            name for name, cat in self._categories.items()
            if cat == category
        ]

    def unregister(self, name: str) -> None:
        """Remove a strategy from the registry."""
        if name in self._strategies:
            del self._strategies[name]
            del self._descriptions[name]
            del self._categories[name]

    def clear(self) -> None:
        """Clear all registered strategies."""
        self._strategies.clear()
        self._descriptions.clear()
        self._categories.clear()


# Global registry instance
_global_registry = StrategyRegistry()


def register_strategy(
    name: str,
    description: str = "",
    category: str = "general"
):
    """
    Decorator to register a strategy class.

    Example:
        @register_strategy('my_strategy', 'My awesome strategy', 'trend')
        class MyStrategy(Strategy):
            pass
    """
    def decorator(cls: Type[Strategy]):
        _global_registry.register(name, cls, description, category)
        return cls
    return decorator


def get_strategy(name: str) -> Type[Strategy]:
    """Get a strategy from the global registry."""
    return _global_registry.get(name)


def create_strategy(name: str, config: Dict[str, Any]) -> Strategy:
    """Create a strategy instance from the global registry."""
    return _global_registry.create_instance(name, config)


def list_strategies() -> List[Dict[str, str]]:
    """List all strategies in the global registry."""
    return _global_registry.list_all()


def get_registry() -> StrategyRegistry:
    """Get the global strategy registry."""
    return _global_registry
