
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
        "nudge": "Check the required disclosure before proceeding. Do not promise guaranteed approval or pricing.",
    },
    "rising_frustration": {
        "keywords": [
            "this is frustrating",
            "i am frustrated",
            "i am angry",
            "you are not listening",
            "i already told you",
        ],
        "priority": "high",
        "nudge": "Acknowledge the customer's concern, listen carefully, and respond calmly.",
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
        "nudge": "Explore approved payment-support options or offer a human callback.",
    },
    "missed_cross_sell": {
        "keywords": [
            "second vehicle",
            "another vehicle",
            "multiple vehicles",
            "second car",
        ],
        "priority": "medium",
        "nudge": "Check whether an approved multi-vehicle offer is relevant to the customer's needs.",
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


def detect_signals(transcript: str) -> list[dict[str, Any]]:
    """Return keyword-matched signals from the latest transcript text."""

    if not transcript or not transcript.strip():
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
