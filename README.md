# Darwix AI Engineer Assessment

This repository contains four prototypes for the Darwix AI Engineer assessment.

## Project status

| Component | Current implementation | Important limitation |
|---|---|---|
| Q1 — Voice Agent | Local STT, conversation agent, local TTS, voice loop, and Q2 retrieval client | Validate the complete required call scenarios and recorded-call evidence |
| Q2 — Knowledge Base | Document loading, cleaning, PII processing, chunking, retrieval, and RAG answer generation | The `ingestion/build_kb.py` entry point and three files in `tests/` are empty; use the implemented modules and retrieval tests |
| Q3 — Multilingual | Rule-based Filipino and Indonesian text routing, localized responses, and unit tests | No demonstrated end-to-end multilingual ASR/TTS pipeline |
| Q4 — Live Insights | Transcript replay, prerecorded WAV replay using Faster-Whisper, rule-based signals, nudge cooldowns, dashboard API, and tests | No demonstrated live microphone or telephony stream; latency results are prototype measurements |

These are prototype status descriptions, not claims of production readiness or assessment scores.

## Repository structure

- `q1_voice_agent/` — voice-agent pipeline and tests
- `q2_knowledge_base/` — ingestion, retrieval, source documents, and test evidence
- `q3_multilingual/` — Filipino and Indonesian text bot prototype
- `q4_live_insights/` — audio/transcript replay, signal detection, nudges, dashboard, tests, and evidence
- `docs/` — assessment and supporting documentation
- `requirements.txt` — root Python dependencies
- `.env.example` — environment-variable template without real credentials

## Setup

Use Python 3.10 or later. On Windows, run commands from the repository root in PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy `.env.example` to a local `.env` only if you need the shared OpenAI configuration. Populate it with your own values. Do not commit real credentials.

Some modules load environment variables from component-specific `.env` files. Check each component's README and configuration before running it. The local Q1 demo client, Q3 text bot, and Q4 transcript replay can be tested without making a live telephony connection.

## Running the components

### Q1 — Voice Agent

See `q1_voice_agent/README.md` for architecture, configuration, and usage.

The project includes local Faster-Whisper speech recognition, a conversation agent, local text-to-speech, and a retrieval client connected to Q2. Microphone use depends on compatible Windows audio hardware and PyAudioWPatch.

### Q2 — Knowledge Base / RAG

See `q2_knowledge_base/README.md` for the ingestion pipeline, retrieval workflow, source documents, and evidence.

The implemented retrieval modules include source-document loading, cleaning, PII processing, chunking, search, and RAG answer generation. The standalone `ingestion/build_kb.py` and three files in `q2_knowledge_base/tests/` are currently empty; do not rely on those files as runnable entry points or tests.

### Q3 — Multilingual Support

Run the text-based unit tests from the Q3 directory:

```powershell
cd .\q3_multilingual
python -m unittest discover -s tests -v
cd ..
```

The prototype supports Filipino and Indonesian text interactions. It does not yet demonstrate integrated multilingual speech recognition and synthesis.

### Q4 — Live Insights

Run the Q4 unit tests:

```powershell
cd .\q4_live_insights
python -m unittest discover -s tests -v
python .\samples\run_scenarios.py
```

To replay a prerecorded WAV file, provide its path explicitly:

```powershell
python .\app\audio_replay.py --audio "PATH_TO_AUDIO.wav" --no-dashboard
```

To launch the local dashboard in one terminal:

```powershell
python .\app\dashboard_server.py
```

In a second terminal, activate the same virtual environment and run the audio replay without `--no-dashboard` to publish events to the dashboard.

Audio replay uses overlapping chunks and Faster-Whisper. Chunk-level transcription may be inaccurate, and measurements from a short prerecorded clip are not proof of production real-time performance.

## Security and privacy

- Never commit `.env` files, API keys, passwords, or customer personal information.
- Use `.env.example` for placeholders only.
- Use fictional or appropriately anonymized test data.
- Review evidence, screenshots, transcripts, and audio before sharing them externally.

## Evidence and limitations

Each component contains its own README and, where available, test output, scenario results, screenshots, or latency measurements. Treat generated evidence files as snapshots of specific runs, not universal performance guarantees.

Before submission, verify that all required scenarios run from a clean environment, the evidence matches the current code, and the final repository includes setup instructions and a clear list of known limitations.

## Production improvements

Potential next steps include stronger automated tests, calibrated signal confidence, better multilingual and noisy-audio evaluation, real streaming ASR, live audio/telephony integration, authentication and access controls for the dashboard, and reproducible latency and load testing.
