
"""Generate controlled, actionable nudges from detected signals."""

from datetime import datetime, timezone
from typing import Any


class NudgeEngine:
    """Apply confidence thresholds and suppress duplicate nudges."""

    def __init__(
        self,
        min_confidence: float = 0.70,
        cooldown_seconds: int = 30,
    ):
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")

        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative")

        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds
        self.last_emitted: dict[str, float] = {}

    def generate(
        self,
        signals: list[dict[str, Any]],
        now: float | None = None,
    ) -> list[dict[str, Any]]:
        """Return eligible nudges; `now` enables deterministic tests."""
        if now is None:
            now = datetime.now(timezone.utc).timestamp()

        nudges = []

        for signal in signals:
            confidence = float(signal.get("confidence", 1.0))

            if not 0.0 <= confidence <= 1.0:
                continue

            if confidence < self.min_confidence:
                continue

            name = signal.get("signal")
            nudge_text = signal.get("nudge")

            if not name or not nudge_text:
                continue

            previous = self.last_emitted.get(name)

            if (
                previous is not None
                and now - previous < self.cooldown_seconds
            ):
                continue

            nudges.append({
                "signal": name,
                "priority": signal.get("priority", "medium"),
                "confidence": confidence,
                "nudge": nudge_text,
                "method": signal.get("method", "unknown"),
                "created_at": datetime.fromtimestamp(
                    now, timezone.utc
                ).isoformat(),
            })

            self.last_emitted[name] = now

        return nudges
