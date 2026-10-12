
"""Shared configuration for the Philippines and Indonesia voice bots."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BotConfig:
    """Configuration for one localized voice bot."""

    country: str
    language_name: str
    language_code: str
    greeting: str
    fallback_message: str


PHILIPPINES_CONFIG = BotConfig(
    country="Philippines",
    language_name="Filipino",
    language_code="fil",
    greeting="Kumusta! Paano kita matutulungan?",
    fallback_message=(
        "Pasensya na, hindi ko lubos na naintindihan. "
        "Maaari mo bang ulitin?"
    ),
)

INDONESIA_CONFIG = BotConfig(
    country="Indonesia",
    language_name="Indonesian",
    language_code="id",
    greeting="Halo! Ada yang bisa saya bantu?",
    fallback_message=(
        "Maaf, saya belum memahami maksud Anda. "
        "Bisakah Anda mengulanginya?"
    ),
)