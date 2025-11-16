"""
Strategy Factory

Provides a factory pattern for creating strategy instances from configurations.
Makes it easy to instantiate strategies without knowing their specific classes.
"""
from __future__ import annotations
from typing import Dict, Any, Type, Optional, List
from .base_strategy import Strategy
from .strategy_types import StrategyType, StrategyMetadata


class StrategyFactory:
    """
    Factory for creating strategy instances.

    Maintains a registry of strategy classes and their metadata,
    allowing easy instantiation by strategy name or type.

    Example:
        # Register a strategy
        factory = StrategyFactory()
        factory.register('ma_crossover', MovingAverageCrossover, metadata)

        # Create instance
        strategy = factory.create('ma_crossover', config)

        # List all strategies
        all_strategies = factory.list_all()
    """

    def __init__(self):
        """Initialize empty factory."""
        self._strategies: Dict[str, Type[Strategy]] = {}
        self._metadata: Dict[str, StrategyMetadata] = {}
        self._type_index: Dict[StrategyType, list] = {}

    def register(
        self,
        name: str,
        strategy_class: Type[Strategy],
        metadata: Optional[StrategyMetadata] = None
    ) -> None:
        """
        Register a strategy class with the factory.

        Args:
            name: Unique identifier for the strategy
            strategy_class: The strategy class (must inherit from Strategy)
            metadata: Optional metadata describing the strategy

        Raises:
            ValueError: If name already exists or class doesn't inherit from Strategy
        """
        if name in self._strategies:
            raise ValueError(f"Strategy '{name}' is already registered")

        if not issubclass(strategy_class, Strategy):
            raise TypeError(f"Strategy class must inherit from Strategy base class")

        self._strategies[name] = strategy_class

        if metadata:
            self._metadata[name] = metadata

            # Index by type for faster lookup
            strategy_type = metadata.strategy_type
            if strategy_type not in self._type_index:
                self._type_index[strategy_type] = []
            self._type_index[strategy_type].append(name)

    def unregister(self, name: str) -> None:
        """Remove a strategy from the registry."""
        if name in self._strategies:
            del self._strategies[name]

            if name in self._metadata:
                metadata = self._metadata[name]
                strategy_type = metadata.strategy_type

                if strategy_type in self._type_index:
                    self._type_index[strategy_type].remove(name)

                del self._metadata[name]

    def create(self, name: str, config: Dict[str, Any]) -> Strategy:
        """
        Create a strategy instance from configuration.

        Args:
            name: Strategy name (must be registered)
            config: Strategy configuration dictionary

        Returns:
            Instantiated strategy object

        Raises:
            KeyError: If strategy name not found

        Example:
            config = {
                'name': 'My MA Strategy',
                'parameters': {'fast_period': 20, 'slow_period': 50}
            }
            strategy = factory.create('ma_crossover', config)
        """
        if name not in self._strategies:
            available = ', '.join(self._strategies.keys())
            raise KeyError(
                f"Strategy '{name}' not found. Available: {available}"
            )

        strategy_class = self._strategies[name]
        return strategy_class(config)

    def get_class(self, name: str) -> Type[Strategy]:
        """
        Get the strategy class by name.

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
                f"Strategy '{name}' not found. Available: {available}"
            )

        return self._strategies[name]

    def get_metadata(self, name: str) -> Optional[StrategyMetadata]:
        """
        Get metadata for a strategy.

        Args:
            name: Strategy name

        Returns:
            StrategyMetadata if available, None otherwise
        """
        return self._metadata.get(name)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all registered strategies with their metadata.

        Returns:
            List of dictionaries containing strategy info
        """
        result = []

        for name, strategy_class in self._strategies.items():
            info = {
                'name': name,
                'class': strategy_class.__name__,
                'module': strategy_class.__module__
            }

            if name in self._metadata:
                metadata = self._metadata[name]
                info.update({
                    'type': metadata.strategy_type.value,
                    'category': metadata.category.value,
                    'complexity': metadata.complexity,
                    'description': metadata.description,
                    'suitable_for_beginners': metadata.suitable_for_beginners,
                    'tags': metadata.tags
                })

            result.append(info)

        return result

    def list_by_type(self, strategy_type: StrategyType) -> List[str]:
        """
        Get all strategy names of a specific type.

        Args:
            strategy_type: The type to filter by

        Returns:
            List of strategy names
        """
        return self._type_index.get(strategy_type, [])

    def search(
        self,
        strategy_type: Optional[StrategyType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        beginner_friendly: Optional[bool] = None
    ) -> List[str]:
        """
        Search for strategies matching criteria.

        Args:
            strategy_type: Filter by strategy type
            category: Filter by category
            tags: Filter by tags (matches if any tag matches)
            beginner_friendly: Filter by beginner suitability

        Returns:
            List of matching strategy names
        """
        matches = []

        for name, metadata in self._metadata.items():
            # Check type
            if strategy_type and metadata.strategy_type != strategy_type:
                continue

            # Check category
            if category and metadata.category.value != category:
                continue

            # Check tags
            if tags:
                if not any(tag in metadata.tags for tag in tags):
                    continue

            # Check beginner friendly
            if beginner_friendly is not None:
                if metadata.suitable_for_beginners != beginner_friendly:
                    continue

            matches.append(name)

        return matches

    def clear(self) -> None:
        """Clear all registered strategies."""
        self._strategies.clear()
        self._metadata.clear()
        self._type_index.clear()


# Global factory instance
_global_factory = StrategyFactory()


def register_strategy(
    name: str,
    metadata: Optional[StrategyMetadata] = None
):
    """
    Decorator to register a strategy class.

    Example:
        @register_strategy('my_strategy', metadata)
        class MyStrategy(Strategy):
            pass
    """
    def decorator(cls: Type[Strategy]):
        _global_factory.register(name, cls, metadata)
        return cls
    return decorator


def get_factory() -> StrategyFactory:
    """Get the global strategy factory."""
    return _global_factory


def create_strategy(name: str, config: Dict[str, Any]) -> Strategy:
    """Create a strategy from the global factory."""
    return _global_factory.create(name, config)


def list_strategies() -> List[Dict[str, Any]]:
    """List all strategies in the global factory."""
    return _global_factory.list_all()
