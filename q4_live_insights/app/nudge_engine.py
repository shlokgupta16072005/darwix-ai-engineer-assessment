
"""Generate controlled, actionable nudges from detected signals.

Keyword-rule detections are handled by an explicit rule-based policy.
Signals carrying a confidence score are checked against the configured
confidence threshold. Rule matches are not presented as probabilities.
"""

from datetime import datetime, timezone
from typing import Any


class NudgeEngine:
    """Apply signal validation, confidence checks, and cooldowns."""

    def __init__(
        self,
        min_confidence: float = 0.70,
        cooldown_seconds: int = 30,
    ):
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(
                "min_confidence must be between 0 and 1"
            )

        if cooldown_seconds < 0:
            raise ValueError(
                "cooldown_seconds cannot be negative"
            )

        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds
        self.last_emitted: dict[str, float] = {}

    def _is_eligible(self, signal: dict[str, Any]) -> bool:
        """Validate a signal without inventing a confidence score."""

        name = signal.get("signal")
        nudge_text = signal.get("nudge")
        method = signal.get("method")

        if not isinstance(name, str) or not name.strip():
            return False

        if not isinstance(nudge_text, str) or not nudge_text.strip():
            return False

        # Explicit rule-based detections use a rule policy, not a
        # fabricated probability.
        if method == "keyword_rule":
            return True

        # Other signal sources must supply an explicit confidence.
        raw_confidence = signal.get("confidence")

        if raw_confidence is None:
            return False

        try:
            confidence = float(raw_confidence)
        except (TypeError, ValueError):
            return False

        if not 0.0 <= confidence <= 1.0:
            return False

        return confidence >= self.min_confidence

    def generate(
        self,
        signals: list[dict[str, Any]],
        now: float | None = None,
    ) -> list[dict[str, Any]]:
        """Return eligible nudges, suppressing repeats during cooldown."""

        if now is None:
            now = datetime.now(timezone.utc).timestamp()

        nudges = []

        for signal in signals:
            if not isinstance(signal, dict):
                continue

            if not self._is_eligible(signal):
                continue

            name = signal["signal"]
            method = signal.get("method", "unknown")
            previous = self.last_emitted.get(name)

            if (
                previous is not None
                and now - previous < self.cooldown_seconds
            ):
                continue

            nudge = {
                "signal": name,
                "priority": signal.get("priority", "medium"),
                "nudge": signal["nudge"],
                "method": method,
                "created_at": datetime.fromtimestamp(
                    now,
                    timezone.utc,
                ).isoformat(),
            }

            # Only report confidence when the input actually supplied it.
            if signal.get("confidence") is not None:
                nudge["confidence"] = float(signal["confidence"])

            nudges.append(nudge)
            self.last_emitted[name] = now

        return nudges
