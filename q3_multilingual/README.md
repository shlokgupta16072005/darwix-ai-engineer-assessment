# Q3 - Multilingual Voice Bot Prototype

## Overview

This project implements a rule-based multilingual customer-support bot prototype for a fictional business-loan service. It includes localized response scripts, basic language detection, prerecorded speech recognition, and localized speech synthesis for Filipino and Indonesian customer interactions.

The prototype focuses on common business-loan questions, including loan eligibility, required documents, and interest-rate enquiries. Sector-specific demonstration scenarios also test safe responses to life-insurance and consumer-finance questions.

## Supported Languages

- Filipino (`fil`) - Philippines
- Indonesian (`id`) - Indonesia

The speech-recognition evaluation uses Faster-Whisper with the Filipino language code `tl` and Indonesian language code `id`.

## Features

- Basic language detection using language-specific word markers.
- Country-specific bot configuration and localized greetings.
- Rule-based responses to common business-loan enquiries.
- Localized fallback messages for unclear or unsupported input.
- Cross-language and unknown-language rejection.
- Safe handling of current-interest-rate questions when live pricing is unavailable.
- Safe responses to sector-specific questions when policy or financing details are unavailable.
- Prerecorded speech-to-response-audio demonstrations using Faster-Whisper, the rule-based VoiceBot, and Edge TTS.
- ASR evaluation against reference transcripts, including word-level error counts and Word Error Rate (WER).
- Unit tests for language detection, response handling, code-switching, and fallback behavior.

## Project Structure

```text
q3_multilingual/
|-- common/
|   |-- config.py
|   |-- language_router.py
|   `-- voice_bot.py
|-- evidence/
|   |-- audio_demos/
|   |-- asr_evaluation.json
|   |-- q3_scenario_results.txt
|   `-- q3_unit_tests.txt
|-- indonesia/
|   |-- localization.md
|   |-- script.md
|   `-- test_cases.md
|-- philippines/
|   |-- localization.md
|   |-- script.md
|   `-- test_cases.md
|-- sample_inputs/
|   `-- sector_q3/
|       |-- ph_coverage.mp3
|       |-- ph_coverage.txt
|       |-- ph_premium_taglish.mp3
|       |-- ph_premium_taglish.txt
|       |-- id_colloquial.mp3
|       |-- id_colloquial.txt
|       |-- id_installment.mp3
|       `-- id_installment.txt
|-- screenshots/
|-- tests/
|   `-- test_voice_bot.py
|-- audio_demo.py
|-- evaluate_asr.py
`-- README.md
```

This is a representative structure of the main Q3 files; additional project files may be present.

## Requirements

- Python 3
- Installed project dependencies, including Faster-Whisper and Edge TTS for the audio demonstrations
- PowerShell on Windows, or another terminal that supports Python commands
- Internet access for Edge TTS speech synthesis

Run commands from the repository root unless otherwise specified. Activate the project's virtual environment before running the examples.

## Run the Unit Tests

From the repository root:

```powershell
python -m pytest .\q3_multilingual\tests -q
```

To save a detailed test report:

```powershell
python -m pytest .\q3_multilingual\tests -v 2>&1 |
    Tee-Object -FilePath .\q3_multilingual\evidence\q3_unit_tests.txt
```

The current pytest suite contains **29 tests** covering Filipino and Indonesian greetings, loan enquiries, eligibility, document requirements, rate fallbacks, unknown-language fallback, empty input, cross-language rejection, code-switching, sector-specific objections, and safe response behavior.

The latest recorded run passed all 29 tests. Rerun the command to verify the current code state.

## Prerecorded Speech Demonstrations

The `audio_demo.py` script demonstrates a prerecorded audio-to-response-audio pipeline:

1. Loads the Faster-Whisper `base` model.
2. Transcribes the supplied audio using the selected language.
3. Passes the transcript to the rule-based `VoiceBot`.
4. Generates localized response speech using Edge TTS.
5. Saves the response audio and a JSON result file under `evidence/audio_demos/`.

Example commands from the repository root:

```powershell
python .\q3_multilingual\audio_demo.py --language fil --audio .\q3_multilingual\filipino_male_test.mp3
python .\q3_multilingual\audio_demo.py --language id --audio .\q3_multilingual\indonesian_male_test.mp3
```

These examples require the referenced input audio files to exist. The script uses the language specified by the command; these examples do not demonstrate automatic language identification from audio.

The pipeline demonstrates prerecorded audio input and generated speech output. It is not a live microphone conversation or a production telephony integration.

## Prerecorded ASR Evaluation

The separate `evaluate_asr.py` script compares Faster-Whisper transcripts against reference transcripts for four prerecorded sector-specific audio samples.

Run the evaluation from the repository root:

```powershell
python .\q3_multilingual\evaluate_asr.py
```

The script saves its machine-readable report to:

`q3_multilingual/evidence/asr_evaluation.json`

### Evaluation Configuration

- Model: Faster-Whisper `base`
- Device: CPU
- Compute type: `int8`
- Beam size: 5
- Filipino language code: `tl`
- Indonesian language code: `id`
- Scoring normalization: lowercase text, remove punctuation, and normalize whitespace
- Lexical differences are counted as word errors; no spelling correction or translation is applied during scoring.

### ASR Results

| Test case | Reference words | Word errors | WER |
|---|---:|---:|---:|
| Filipino coverage | 15 | 1 | 6.67% |
| Filipino/Taglish premium objection | 13 | 2 | 15.38% |
| Indonesian colloquial cost objection | 9 | 0 | 0.00% |
| Indonesian installment question | 11 | 2 | 18.18% |
| **Overall micro-WER** | **48** | **5** | **10.42%** |

Word Error Rate is calculated as:

`WER = (substitutions + deletions + insertions) / reference word count`

The overall micro-WER is the total number of word errors divided by the total number of reference words across the four recordings.

### Interpretation

- The Filipino coverage recording had one word substitution.
- The Filipino/Taglish recording merged “Mahal ang” into “Mahalang,” producing a substitution and a deletion.
- The Indonesian colloquial cost-objection recording matched its reference transcript after punctuation normalization.
- The Indonesian installment recording had two word substitutions, including errors involving financing terminology.

These results identify code-switching and financial terminology as useful areas for additional evaluation. They do not establish general ASR accuracy for either market because the sample is small.

### ASR Evaluation Limitations

- Only four short prerecorded recordings were evaluated.
- The tested audio samples were generated using Edge TTS rather than collected from natural customers.
- Results do not establish robustness to natural speakers, regional accents, background noise, or production telephony.
- The ASR language is supplied explicitly for each recording; automatic language identification is not evaluated by this experiment.
- WER evaluates transcription against reference text. It does not measure whether the chatbot response is correct, whether a human handoff succeeds, or how quickly a live system responds.
- The evaluation does not measure live streaming ASR latency or end-to-end call latency.

## Knowledge and Safety Behavior

The bot uses a fictional business-loan knowledge base. It does not invent live interest rates or guarantee loan approval. When current pricing is requested, it explains that live pricing is unavailable and indicates that human follow-up may be needed.

Sector-specific demonstration scenarios also exercise safe handling of questions about life-insurance coverage, premiums, consumer-finance installments, and fees. When reliable product-specific information is unavailable, the bot avoids inventing policy terms, fees, penalties, or coverage details.

Human escalation is represented by the bot's response to a request for assistance. This prototype does not perform a real call transfer or guarantee that a callback has been scheduled.

## Current Scope and Limitations

This is a rule-based multilingual response prototype. Language detection relies on word markers and may fail on short, ambiguous, or mixed-language messages.

The prerecorded speech demonstration combines Faster-Whisper ASR, the rule-based VoiceBot, and Edge TTS to demonstrate audio input and localized audio output. It does not implement a continuous live microphone stream, production telephony, or an actual human-transfer mechanism.

The four-recording ASR evaluation is a small synthetic-sample experiment, not a representative real-customer benchmark. Native-speaker validation, regional-accent testing, broader noisy-audio testing, and measured live-call latency remain unverified.

The current 29-test suite primarily validates text-based routing and response behavior. Passing unit tests do not independently establish production readiness or end-to-end live-audio performance.

## Evidence

- Unit-test output: `evidence/q3_unit_tests.txt`
- Scenario results: `evidence/q3_scenario_results.txt`
- ASR evaluation report: `evidence/asr_evaluation.json`
- ASR evaluation script: `evaluate_asr.py`
- Prerecorded speech demo script: `audio_demo.py`
- Per-run audio demonstration results and response audio: `evidence/audio_demos/`
- Screenshots: `screenshots/`

## Future Improvements

- Expand ASR evaluation with natural recordings from multiple speakers in both markets.
- Test regional accents, noisy environments, and Filipino/English and Indonesian/English code-switching.
- Evaluate more utterances and report per-language WER over a larger, representative dataset.
- Validate localized responses with native speakers.
- Implement and test continuous live-audio capture and streaming ASR.
- Measure component-level and end-to-end latency under realistic call conditions.
- Improve language detection for short and mixed-language messages.
- Connect the response layer to the shared knowledge base and a real human-handoff workflow.
- Add integration tests for the complete live speech pipeline and its failure modes.
