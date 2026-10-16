# Q4 — Real-Time Call Insights and Agent Nudges

## 1. Overview

This project implements a prototype for detecting useful business-call signals and generating contextual nudges for a human agent.

The system supports two replay modes:

- **Incremental transcript replay:** processes text chunks and detects signals using rule-based keyword matching.
- **Prerecorded audio replay:** processes overlapping chunks from a WAV recording using Faster-Whisper for speech recognition, then passes the accumulated transcript through the signal detector and nudge engine.

The audio replay can optionally publish events to a local dashboard API. The prototype also includes audio-chunk buffering, duplicate-nudge suppression, cooldowns, unit tests, scenario tests, and latency measurements.

**Scope:** This is a local prototype, not a production-ready real-time speech analytics system. Audio replay uses prerecorded audio rather than live microphone or telephony capture. Its latency results do not establish production end-to-end performance.

## 2. Features

### Signal detection

The detector supports five signal categories:

- `compliance_gap`
- `rising_frustration`
- `payment_difficulty`
- `missed_cross_sell`
- `callback_needed`

### Nudge generation

- Generates contextual guidance for detected signals.
- Assigns priorities to nudges.
- Applies a configurable confidence threshold.
- Suppresses duplicate signals and applies cooldown logic.
- Includes negative tests to reduce unnecessary alerts for ordinary conversation and unrelated vehicle mentions.

The detector is primarily rule-based. Confidence values assigned to keyword matches are not calibrated probabilities of real-world correctness.

### Audio and transcript replay

- Replays transcript text incrementally.
- Reads prerecorded 16-bit PCM WAV audio at 16 kHz.
- Uses Faster-Whisper (`base.en` by default) for chunk-level speech recognition.
- Uses overlapping audio windows to provide additional context.
- Records chunk transcripts, accumulated transcript text, detected signals, nudges, and component latency measurements.

Chunked transcription is a prototype approach, not a native streaming ASR implementation. Short or ambiguous audio windows can produce inaccurate transcripts.

### Dashboard integration

- Provides a local HTTP dashboard server.
- Exposes a state endpoint at `/api/state`.
- Accepts replay events at `/api/events`.
- Supports optional event publishing from the audio replay.
- Continues replay if dashboard publishing is unavailable.

Dashboard publishing is local and does not represent integration with a live call-center platform.

## 3. Project Structure

The following is a representative structure. The exact repository contents may differ as implementation evolves.

```text
q4_live_insights/
├── app/
│   ├── audio_replay.py
│   ├── audio_stream.py
│   ├── dashboard.html
│   ├── dashboard_server.py
│   ├── latency_metrics.py
│   ├── live_replay.py
│   ├── nudge_engine.py
│   └── signal_detector.py
├── evidence/
│   ├── audio_replay_results.json
│   ├── latency_results.txt
│   ├── live_replay_results.json
│   ├── q4_replay_summary.txt
│   ├── q4_scenario_results.txt
│   ├── q4_unit_tests.txt
│   └── scenario_results.txt
├── samples/
│   └── run_scenarios.py
├── tests/
│   └── test_nudge_engine.py
└── README.md
```

Some evidence files are historical or overlapping snapshots. The current scenario runner writes to `evidence/scenario_results.txt`. The audio replay writes to `evidence/audio_replay_results.json`.

## 4. Requirements and Setup

- Python 3.10 or later is recommended.
- Run commands from the `q4_live_insights` directory.
- The text replay and core unit tests use Python standard-library functionality.
- Audio replay additionally requires the project's installed dependencies, including NumPy and Faster-Whisper.
- The local dashboard uses Python's standard-library HTTP server.

Activate the project's virtual environment and install the required dependencies according to the repository's root dependency instructions.

For example, from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
cd .\q4_live_insights
```

If the virtual environment is already active, change to the Q4 directory directly.

## 5. Run the Unit Tests

```powershell
python -m unittest discover -s tests -v
```

**Latest observed result: 13 tests passed.**

Coverage includes:

- Audio chunk validation and ordering.
- Callback, payment-difficulty, frustration, compliance, and cross-sell signal detection.
- Normal conversation producing no signals.
- A historical unrelated-vehicle false-positive case.
- Duplicate-nudge suppression.
- Explicit compliance-risk detection.

The recorded result is available in `evidence/q4_unit_tests.txt`. Re-run the tests to verify the current checkout rather than relying solely on saved output.

## 6. Run the Business Scenario Suite

```powershell
python .\samples\run_scenarios.py
```

The scenario runner covers six cases:

1. Payment difficulty.
2. Rising frustration.
3. Compliance gap.
4. Missed cross-sell opportunity.
5. Human callback request.
6. Normal conversation.

The latest observed run passed all six scenarios. Results are written to:

```text
evidence/scenario_results.txt
```

A separately saved snapshot may also exist at `evidence/q4_scenario_results.txt`.

These are predefined test examples. Passing them demonstrates expected behavior for those inputs, not general detection accuracy across real conversations.

## 7. Run Incremental Transcript Replay

```powershell
python .\app\live_replay.py
```

This mode replays transcript text and evaluates the four configured scenarios:

1. Payment difficulty, frustration, and callback.
2. Compliance gap.
3. Missed cross-sell.
4. Normal conversation.

Results are saved to:

```text
evidence/live_replay_results.json
```

This mode does **not** use ASR. Its latency figures measure local transcript-processing work rather than the complete audio pipeline.

## 8. Run Prerecorded Audio Replay

The audio replay uses the default WAV file:

```text
q1_voice_agent/transcripts/temp_audio.wav
```

Run it with dashboard publishing disabled:

```powershell
python .\app\audio_replay.py --no-dashboard --chunk-seconds 4 --overlap-seconds 0.5
```

The tested configuration uses four seconds of audio per window with 0.5 seconds of overlap. The input must be a 16 kHz, 16-bit PCM WAV file.

To specify another compatible WAV file:

```powershell
python .\app\audio_replay.py --audio "C:\path\to\recording.wav" --no-dashboard
```

The script uses Faster-Whisper on the CPU with the `base.en` model by default. The first model initialization may require downloading model files.

Audio replay results are saved to:

```text
evidence/audio_replay_results.json
```

The JSON includes the replay mode, ASR model, audio duration, chunk settings, transcripts, detected signals, nudges, latency measurements, and measurement-scope notes.

### Observed audio test

For the tested recording of approximately 4.99 seconds:

- Whole-file transcription produced: `What is today's interest rate?`
- Four-second chunk replay produced the same final transcript.
- The two-chunk replay took approximately 5.28 seconds in the observed run.

This demonstrates successful transcription of one short prerecorded clip. It does not establish reliable transcription for longer, noisy, multilingual, or live conversations.

## 9. Run the Local Dashboard

Open a separate PowerShell terminal and start the dashboard server:

```powershell
python .\app\dashboard_server.py
```

The server listens at:

```text
http://127.0.0.1:8765
```

Open that address in a browser on the same machine.

In another terminal, run audio replay with dashboard publishing enabled:

```powershell
python .\app\audio_replay.py --chunk-seconds 4 --overlap-seconds 0.5
```

The replay publishes events to the local `/api/events` endpoint. The dashboard polls `/api/state` to display the latest transcript and nudges.

Successful HTTP 200 responses from `POST /api/events` were observed during testing. This verifies local API communication; it does not verify remote deployment, telephony integration, or production availability.

## 10. Latency Measurement

The prototype records component-level measurements for:

- ASR processing per audio chunk.
- Local signal detection and nudge generation.
- Dashboard event publishing.
- Total replay wall-clock duration.

The text replay also records local transcript-processing latency.

### Observed audio replay measurements

In one run with a two-chunk, approximately 4.99-second recording:

| Measurement | Observed result |
|---|---:|
| ASR P50 | 1,130.758 ms |
| ASR P95 | 1,132.545 ms |
| Signal-processing P95 | 2.400 ms |
| Dashboard-delivery P50 | 1.473 ms |
| Dashboard-delivery P95 | 13.013 ms |
| Total elapsed time | 5.282 s |

These measurements describe one small local test run and can vary between runs. Two chunks are insufficient for a meaningful production P95 estimate.

The dashboard-delivery timings apply to local HTTP publishing under the tested conditions. They do not include live telephony transport or remote network conditions.

The text replay has a separate latency scope. Its measurements exclude ASR and dashboard delivery.

The project does not yet establish a validated, production end-to-end audio-to-display latency benchmark.

## 11. Evidence

| File | Contents |
|---|---|
| `evidence/q4_unit_tests.txt` | Saved unit-test output |
| `evidence/scenario_results.txt` | Business scenario results generated by the scenario runner |
| `evidence/q4_scenario_results.txt` | Additional scenario-output snapshot |
| `evidence/live_replay_results.json` | Structured transcript replay results |
| `evidence/audio_replay_results.json` | Structured prerecorded audio replay and component latency results |
| `evidence/latency_results.txt` | Scope notes for the earlier text-only latency report |
| `evidence/q4_replay_summary.txt` | Earlier text-replay summary; some limitations described there predate audio replay and dashboard integration |

Use the JSON result files and the corresponding current code when assessing the latest behavior. Historical summaries should not be treated as descriptions of every feature in the current checkout.

## 12. Limitations and Risks

- Signal detection relies primarily on keywords and regular expressions rather than full contextual language understanding.
- Negation, paraphrases, transcription errors, and ambiguous wording may cause false positives or missed signals.
- Rule-based confidence values are not calibrated probabilities.
- Audio replay re-transcribes overlapping prerecorded windows; it is not a native streaming ASR implementation.
- The tested audio sample is short and does not establish performance on noisy, long, or multilingual calls.
- Live microphone and telephony capture have not been demonstrated.
- Dashboard integration is local and is not a production agent desktop.
- Latency measurements use small sample sizes and do not establish production P50/P95 performance.
- High concurrency, sustained operation, service recovery, authentication, authorization, and deployment-level monitoring have not been validated.

## 13. Future Improvements

1. Integrate a genuine streaming ASR interface or a robust incremental transcription pipeline.
2. Add live microphone or telephony input with explicit consent and appropriate data handling.
3. Improve transcript overlap reconciliation and evaluate word-level transcription accuracy.
4. Replace or augment keyword rules with contextual, negation-aware signal detection.
5. Calibrate confidence scores against labeled examples.
6. Build a broader evaluation dataset covering false positives, false negatives, accents, noise, and paraphrases.
7. Measure end-to-end latency from audio receipt through transcription and signal detection to dashboard display.
8. Test longer recordings, higher replay rates, and concurrent sessions.
9. Add production-grade authentication, error handling, observability, and deployment configuration.
10. Validate the agent workflow with domain experts before using nudges in real customer interactions.

## 14. Conclusion

Q4 demonstrates a rule-based call-insights prototype with incremental transcript replay, prerecorded audio transcription using Faster-Whisper, contextual nudge generation, duplicate suppression, local dashboard API publishing, and preliminary latency measurements.

The implementation has passed 13 unit tests and six predefined business scenarios in the observed runs. These results support the prototype's demonstrated functionality, while live audio capture, broad transcription evaluation, and production end-to-end performance remain open work.

The system should not be represented as a fully deployed, production-ready real-time speech analytics platform.
