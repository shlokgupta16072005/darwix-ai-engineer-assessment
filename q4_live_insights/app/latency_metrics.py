
"""Measure processing latency for the live-insights prototype."""

from time import perf_counter
from typing import Any, Callable


def measure_latency(
    operation: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> tuple[Any, float]:
    """Run an operation and return (result, elapsed_ms).

    The elapsed time covers only the supplied operation.
    """
    start = perf_counter()

    try:
        result = operation(*args, **kwargs)
    finally:
        elapsed_ms = (perf_counter() - start) * 1000

    return result, elapsed_ms


class LatencyRecorder:
    """Collect latency samples and summarize observed timings."""

    def __init__(self) -> None:
        self.samples_ms: list[float] = []

    def record(self, elapsed_ms: float) -> None:
        if elapsed_ms < 0:
            raise ValueError("Latency cannot be negative")
        self.samples_ms.append(float(elapsed_ms))

    def summary(self) -> dict[str, float | int]:
        if not self.samples_ms:
            return {
                "count": 0,
                "mean_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
            }

        return {
            "count": len(self.samples_ms),
            "mean_ms": round(
                sum(self.samples_ms) / len(self.samples_ms), 3
            ),
            "min_ms": round(min(self.samples_ms), 3),
            "max_ms": round(max(self.samples_ms), 3),
        }
