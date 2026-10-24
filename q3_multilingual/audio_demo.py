"""Q3 multilingual speech-to-speech demo using Faster-Whisper and Edge TTS."""

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel

from common.config import PHILIPPINES_CONFIG, INDONESIA_CONFIG
from common.voice_bot import VoiceBot


ROOT = Path(__file__).resolve().parent

LANGUAGES = {
    "fil": {
        "config": PHILIPPINES_CONFIG,
        "whisper_language": "tl",
        "voice": "fil-PH-BlessicaNeural",
    },
    "id": {
        "config": INDONESIA_CONFIG,
        "whisper_language": "id",
        "voice": "id-ID-GadisNeural",
    },
}


def normalize_transcript(text, language):
    """Normalize specific ASR spelling errors observed in demo recordings."""
    text = text.strip()

    if language == "fil":
        replacements = [
            (r"\bkung\s*musta\b", "kumusta"),
            (r"\bma[- ]?tutulungan\b", "matutulungan"),
            (r"\bka\s+ilangan\b", "kailangan"),
            (r"\bnigos\b", "negosyo"),
            (r"\bnakatagaldapat\b", "na katagal dapat"),
        ]

        for pattern, corrected in replacements:
            text = re.sub(
                pattern,
                corrected,
                text,
                flags=re.IGNORECASE,
            )

    return re.sub(r"\s+", " ", text).strip()


async def synthesize(text, voice, output_path):
    communicator = edge_tts.Communicate(text, voice)
    await communicator.save(str(output_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=LANGUAGES, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    args = parser.parse_args()

    if not args.audio.is_file():
        parser.error(f"Audio file not found: {args.audio}")

    settings = LANGUAGES[args.language]
    config = settings["config"]

    print("[1/3] Loading multilingual Whisper...")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    print("[2/3] Transcribing audio...")
    segments, info = model.transcribe(
        str(args.audio),
        language=settings["whisper_language"],
        beam_size=5,
    )

    raw_transcript = " ".join(
        segment.text.strip() for segment in segments
    ).strip()

    normalized_transcript = normalize_transcript(
        raw_transcript,
        args.language,
    )

    bot = VoiceBot(config)
    response = bot.respond(normalized_transcript)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = ROOT / "evidence" / "audio_demos" / f"{args.language}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_output = output_dir / "assistant_response.mp3"

    print("[3/3] Generating localized speech...")
    asyncio.run(
        synthesize(response, settings["voice"], audio_output)
    )

    result = {
        "language": args.language,
        "country": config.country,
        "input_audio": args.audio.resolve().relative_to(ROOT.parent).as_posix(),
        "whisper_model": "base",
        "whisper_language": settings["whisper_language"],
        "raw_transcript": raw_transcript,
        "normalized_transcript": normalized_transcript,
        "bot_response": response,
        "tts_engine": "edge-tts",
        "tts_voice": settings["voice"],
        "output_audio": audio_output.relative_to(ROOT.parent).as_posix(),
        "timestamp_utc": timestamp,
        "limitations": [
            "Prerecorded audio input; not a live microphone call.",
            "Input language supplied explicitly.",
            "Rule-based localized bot; not a generative conversation.",
            "Edge TTS requires an internet connection.",
        ],
    }

    (output_dir / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("Language:", config.language_name)
    print("Raw transcript:", raw_transcript)
    print("Normalized transcript:", normalized_transcript)
    print("Bot response:", response)
    print("Output audio:", audio_output)
    print("Evidence JSON:", output_dir / "result.json")


if __name__ == "__main__":
    main()
