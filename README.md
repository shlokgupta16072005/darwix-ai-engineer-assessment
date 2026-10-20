# Darwix AI Engineer Assessment

This repository contains four prototypes for the Darwix AI Engineer assessment.

## Project status

| Component | Current implementation | Important limitation |
|---|---|---|
| Q1 — Voice Agent | Local STT, conversation agent, local TTS, voice loop, and Q2 retrieval client | Recorded tests demonstrate safe fallback; speech-recognition errors remain possible, and human escalation does not initiate a real transfer or callback |
| Q2 — Knowledge Base | Document loading, cleaning, PII processing, chunking, retrieval, and RAG answer generation | Retrieval evaluation covers five queries; relevance and source-ranking errors remain possible. See the Q2 README for evidence and test instructions. |
| Q3 — Multilingual | Rule-based Filipino and Indonesian text routing, localized responses, and unit tests | Prerecorded audio demos exist, but they do not establish natural customer-call performance or regional-accent coverage. |
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

The project includes local Faster-Whisper speech recognition, a conversation agent, local text-to-speech, and a retrieval client connected to Q2. The recorded session `q1_voice_agent/evidence/recorded_calls/session_20261019T124049Z/` contains three turns, a transcript, and customer/assistant WAV files. The tested out-of-scope question received a safe fallback, although the first speech transcription was inaccurate. Microphone use depends on compatible Windows audio hardware and PyAudioWPatch.

### Q2 — Knowledge Base / RAG

See `q2_knowledge_base/README.md` for the ingestion pipeline, retrieval workflow, source documents, and evidence.

The implemented retrieval modules include source-document loading, cleaning, PII processing, chunking, search, and RAG answer generation. The standalone `ingestion/build_kb.py` builds the knowledge-base index. The three files in `q2_knowledge_base/tests/` contain automated tests for chunking, cleaning, and retrieval.

### Q3 — Multilingual Support

Run the text-based unit tests from the Q3 directory:

```powershell
cd .\q3_multilingual
python -m unittest discover -s tests -v
cd ..
```

The prototype supports Filipino life-insurance and Indonesian consumer-finance response patterns, with localization scripts, tests, and prerecorded audio demos. These are prototype demonstrations, not recordings of real customer calls. See the Philippines, Indonesia, and evidence directories under `q3_multilingual/` for details and limitations.

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

Each component contains its own README and, where available, test output, scenario results, screenshots, recorded audio/transcripts, or latency measurements. Q1's recorded session includes three repeated out-of-scope turns; do not treat these as three distinct scenarios. Q2's retrieval evaluation contains five queries, with four top-1 expected-source matches. Q3 audio demos use prerecorded inputs and do not prove real-customer or regional-accent performance. Q4 latency results come from prototype replay tests, not production traffic. Treat all evidence as snapshots of specific runs, not universal performance guarantees.

Before submission, verify all required scenarios from a clean environment, confirm that evidence matches the current code, and include the walkthrough video and a clear limitations section. In particular, document the absence of real telephony transfer, the limits of prerecorded multilingual audio, and Q4's lack of a live microphone/telephony stream.

## Production improvements

Potential next steps include stronger automated tests, calibrated signal confidence, better multilingual and noisy-audio evaluation, real streaming ASR, live audio/telephony integration, authentication and access controls for the dashboard, and reproducible latency and load testing.
