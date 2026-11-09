from .base import ExtractionStrategy
from .strategy_raw import RawExtractionStrategy
from .strategy_sliding_window import SlidingWindowExtractionStrategy

STRATEGIES: dict[str, type[ExtractionStrategy]] = {
    "raw": RawExtractionStrategy,
    "sliding_window": SlidingWindowExtractionStrategy,
}

__all__ = [
    "ExtractionStrategy",
    "RawExtractionStrategy",
    "SlidingWindowExtractionStrategy",
    "STRATEGIES",
]
