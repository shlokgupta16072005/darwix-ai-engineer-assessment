"""Detect whether a message is in Filipino or Indonesian."""

import re
from typing import Optional

from common.config import PHILIPPINES_CONFIG, INDONESIA_CONFIG


FILIPINO_MARKERS = {
    "ako", "ikaw", "kami", "kayo", "siya", "hindi",
    "opo", "salamat", "kumusta", "magkano", "paano",
    "kailangan", "utang", "pautang", "buwan", "negosyo",
    "gaano", "dokumento", "dokumento", "kailangang",
}

INDONESIAN_MARKERS = {
    "saya", "anda", "kami", "tidak", "terima", "kasih",
    "halo", "berapa", "bagaimana", "butuh", "pinjaman",
    "bunga", "bulan", "usaha", "rekening",
    "dokumen", "diperlukan", "persyaratan", "apa",
    "saja", "yang", "untuk", "bisnis",
}


def detect_language(text: str) -> Optional[str]:
    """Return 'fil', 'id', or None when the language is unclear."""
    if not text or not text.strip():
        return None

    words = set(re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower()))

    filipino_score = len(words & FILIPINO_MARKERS)
    indonesian_score = len(words & INDONESIAN_MARKERS)

    if filipino_score == indonesian_score:
        return None

    return "fil" if filipino_score > indonesian_score else "id"


def get_bot_config(text: str):
    """Return the matching bot configuration, or None if uncertain."""
    language_code = detect_language(text)

    if language_code == PHILIPPINES_CONFIG.language_code:
        return PHILIPPINES_CONFIG

    if language_code == INDONESIA_CONFIG.language_code:
        return INDONESIA_CONFIG

    return None