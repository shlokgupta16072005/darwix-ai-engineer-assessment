
"""Detect business-call signals from partial transcript text."""

import re
from typing import Any


SIGNALS = {
    "compliance_gap": {
        "keywords": [
            "didn't disclose",
            "did not disclose",
            "forgot to mention",
            "without telling the customer",
            "guaranteed approval",
            "guaranteed rate",
        ],
        "priority": "high",
        "nudge": (
            "Check the required disclosure before proceeding. "
            "Do not promise guaranteed approval or pricing."
        ),
    },
    "rising_frustration": {
        "keywords": [
            "this is frustrating",
            "i am frustrated",
            "i'm frustrated",
            "i am angry",
            "i'm angry",
            "you are not listening",
            "i already told you",
        ],
        "priority": "high",
        "nudge": (
            "Acknowledge the customer's concern, listen carefully, "
            "and respond calmly."
        ),
    },
    "payment_difficulty": {
        "keywords": [
            "cannot afford",
            "can't afford",
            "missed my payment",
            "unable to pay",
            "payment difficulty",
        ],
        "priority": "medium",
        "nudge": (
            "Explore approved payment-support options or offer a human callback."
        ),
    },
    "missed_cross_sell": {
         "keywords": [
            "interested in a second vehicle",
            "interested in another vehicle",
            "looking to buy another vehicle",
            "planning to buy another vehicle",
            "wants to purchase another vehicle",
            "needs financing for another vehicle",
            "buying a second car",
        ],
        "priority": "medium",
        "nudge": (
            "Check whether an approved multi-vehicle offer is relevant "
            "to the customer's needs."
        ),
    },
    "callback_needed": {
        "keywords": [
            "call me back",
            "speak to a human",
            "talk to a person",
            "speak to an agent",
            "human representative",
        ],
        "priority": "high",
        "nudge": "Arrange a human follow-up according to the approved workflow.",
    },
}


def _is_negated(text: str, keyword: str) -> bool:
    """Detect a nearby negation before a matched keyword.

    This is a conservative rule-based safeguard, not full language
    understanding. It intentionally checks a short window before a match.
    """
    for match in re.finditer(
        r"(?<!\w)" + re.escape(keyword) + r"(?!\w)",
        text,
    ):
        prefix = text[max(0, match.start() - 45):match.start()]
        if re.search(
            r"\b(?:not|never|no longer|did not|didn't|does not|doesn't|"
            r"was not|wasn't|were not|weren't|without)\b"
            r"(?:\s+\w+){0,5}\s*$",
            prefix,
        ):
            return True

    return False


def detect_signals(transcript: str) -> list[dict[str, Any]]:
    """Return keyword-matched signals from transcript text."""

    if not isinstance(transcript, str) or not transcript.strip():
        return []

    text = re.sub(r"\s+", " ", transcript.lower()).strip()
    detected = []

    for signal_name, rule in SIGNALS.items():
        matched = [
            keyword
            for keyword in rule["keywords"]
            if re.search(
                r"(?<!\w)" + re.escape(keyword) + r"(?!\w)",
                text,
            )
        ]

        # Suppress matches that are negated in their local context.
        matched = [
            keyword
            for keyword in matched
            if not _is_negated(text, keyword)
        ]

        # Suppress historical vehicle mentions that are not current opportunities.
        if signal_name == "missed_cross_sell" and re.search(
            r"\b(sold|disposed of|no longer own|used to own)\b"
            r".{0,60}\b(second vehicle|another vehicle|multiple vehicles|second car)\b",
            text,
        ):
            matched = []

        if matched:
            detected.append({
                "signal": signal_name,
                "priority": rule["priority"],
                "matched_terms": matched,
                "nudge": rule["nudge"],
                "method": "keyword_rule",
            })

    return detected
