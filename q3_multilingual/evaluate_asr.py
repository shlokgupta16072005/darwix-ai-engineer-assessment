"""Evaluate Faster-Whisper ASR against Q3 reference transcripts."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
SAMPLE_DIR = ROOT / "sample_inputs" / "sector_q3"
OUTPUT_DIR = ROOT / "evidence"
OUTPUT_FILE = OUTPUT_DIR / "asr_evaluation.json"

CASES = [
    ("ph_coverage", "tl", "Filipino"),
    ("ph_premium_taglish", "tl", "Filipino/Taglish"),
    ("id_colloquial", "id", "Indonesian"),
    ("id_installment", "id", "Indonesian"),
]


def normalize_for_scoring(text):
    """Normalize case and punctuation while preserving word differences."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def word_error_counts(reference, hypothesis):
    """Return word-level substitutions, deletions, insertions and WER."""
    ref = normalize_for_scoring(reference).split()
    hyp = normalize_for_scoring(hypothesis).split()

    # Levenshtein dynamic programming with edit-operation counts.
    rows, cols = len(ref) + 1, len(hyp) + 1
    dp = [[0] * cols for _ in range(rows)]
    back = [[None] * cols for _ in range(rows)]

    for i in range(1, rows):
        dp[i][0] = i
        back[i][0] = "D"
    for j in range(1, cols):
        dp[0][j] = j
        back[0][j] = "I"

    for i in range(1, rows):
        for j in range(1, cols):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                back[i][j] = "M"
            else:
                options = [
                    (dp[i - 1][j - 1] + 1, "S"),
                    (dp[i - 1][j] + 1, "D"),
                    (dp[i][j - 1] + 1, "I"),
                ]
                dp[i][j], back[i][j] = min(options, key=lambda item: item[0])

    substitutions = deletions = insertions = 0
    i, j = len(ref), len(hyp)
    while i > 0 or j > 0:
        operation = back[i][j]
        if operation == "M":
            i -= 1
            j -= 1
        elif operation == "S":
            substitutions += 1
            i -= 1
            j -= 1
        elif operation == "D":
            deletions += 1
            i -= 1
        elif operation == "I":
            insertions += 1
            j -= 1

    errors = substitutions + deletions + insertions
    wer = errors / len(ref) if ref else (0.0 if not hyp else None)

    return {
        "reference_word_count": len(ref),
        "hypothesis_word_count": len(hyp),
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "word_errors": errors,
        "wer": wer,
        "wer_percent": round(wer * 100, 2) if wer is not None else None,
    }


def main():
    missing = []
    for name, _, _ in CASES:
        for suffix in (".mp3", ".txt"):
            path = SAMPLE_DIR / f"{name}{suffix}"
            if not path.is_file():
                missing.append(str(path))

    if missing:
        raise FileNotFoundError("Missing evaluation files:\n" + "\n".join(missing))

    print("Loading Faster-Whisper base model (CPU, int8)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    results = []
    for name, language, label in CASES:
        audio_path = SAMPLE_DIR / f"{name}.mp3"
        reference_path = SAMPLE_DIR / f"{name}.txt"
        reference = reference_path.read_text(encoding="utf-8").strip()

        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
        )
        hypothesis = " ".join(segment.text.strip() for segment in segments).strip()
        scores = word_error_counts(reference, hypothesis)

        result = {
            "case": name,
            "language_group": label,
            "audio_file": audio_path.relative_to(ROOT.parent).as_posix(),
            "reference_file": reference_path.relative_to(ROOT.parent).as_posix(),
            "requested_language": language,
            "detected_language": info.language,
            "language_probability": info.language_probability,
            "reference_transcript": reference,
            "hypothesis_transcript": hypothesis,
            **scores,
        }
        results.append(result)

        wer_text = (
            f"{scores['wer_percent']:.2f}%"
            if scores["wer_percent"] is not None
            else "N/A"
        )
        print(f"\n{name} ({label})")
        print("  Reference:  ", reference)
        print("  Recognized: ", hypothesis)
        print(
            f"  WER: {wer_text} | "
            f"S={scores['substitutions']} "
            f"D={scores['deletions']} I={scores['insertions']}"
        )

    groups = {}
    for label in sorted({item["language_group"] for item in results}):
        group_results = [item for item in results if item["language_group"] == label]
        total_ref_words = sum(item["reference_word_count"] for item in group_results)
        total_errors = sum(item["word_errors"] for item in group_results)
        groups[label] = {
            "recording_count": len(group_results),
            "reference_word_count": total_ref_words,
            "word_errors": total_errors,
            "micro_wer": total_errors / total_ref_words if total_ref_words else None,
            "micro_wer_percent": round(100 * total_errors / total_ref_words, 2)
            if total_ref_words else None,
        }

    total_ref_words = sum(item["reference_word_count"] for item in results)
    total_errors = sum(item["word_errors"] for item in results)

    report = {
        "evaluation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": "faster-whisper base",
        "device": "cpu",
        "compute_type": "int8",
        "beam_size": 5,
        "scoring_normalization": (
            "Lowercase and remove punctuation; whitespace normalized. "
            "No spelling correction or translation."
        ),
        "overall": {
            "recording_count": len(results),
            "reference_word_count": total_ref_words,
            "word_errors": total_errors,
            "micro_wer": total_errors / total_ref_words if total_ref_words else None,
            "micro_wer_percent": round(100 * total_errors / total_ref_words, 2)
            if total_ref_words else None,
        },
        "by_language_group": groups,
        "results": results,
        "limitations": [
            "Only four prerecorded, synthetic test recordings were evaluated.",
            "WER on this small sample is not a general measure of real-customer accuracy.",
            "Filipino/Taglish and Indonesian results are reported separately.",
            "Punctuation and letter case are ignored; lexical differences count as errors.",
            "This measures ASR transcription, not chatbot response quality or live-call latency.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("\nSummary")
    print(f"  Overall micro-WER: {report['overall']['micro_wer_percent']}%")
    for label, summary in groups.items():
        print(f"  {label} micro-WER: {summary['micro_wer_percent']}%")
    print(f"\nEvidence saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
