# Q1 — Voice Agent

## Overview

This module implements a local voice-agent workflow for the Darwix AI Engineer Assessment. It integrates microphone capture, local speech recognition, the Q2 knowledge-base retrieval pipeline, and local text-to-speech.

The recorded RAG-backed voice workflow is:

**Microphone ? Faster-Whisper STT ? ConversationAgent ? Q2 RAGClient ? pyttsx3 TTS**

The repository also contains separate deterministic offline and OpenAI response clients. These are alternative response backends, not interchangeable descriptions of the same recorded workflow.

## Architecture

```text
Customer Speech
      |
      v
MicrophoneInput
      |
      v
LocalSTT (Faster-Whisper)
      |
      v
ConversationAgent
      |
      v
RAGClient
      |
      v
Q2 Knowledge Base Retrieval
      |
      v
Response + Source Metadata
      |
      v
LocalTTS (pyttsx3)
      |
      v
Assistant Speech
```

The voice loop records customer audio, assistant audio, recognized text, the assistant response, and available retrieval-source metadata.

## Components

### `app/microphone.py`

Captures microphone audio using PyAudioWPatch.

The documented configuration uses:
- Sample rate: 16 kHz
- Channels: 1
- Sample format: 16-bit PCM
- Configurable recording duration

### `app/local_stt.py`

Uses Faster-Whisper for local speech-to-text. The documented local model is `base.en`.

Speech recognition may misrecognize words, particularly in noisy conditions or with uncommon terms. These errors can affect downstream retrieval and response quality.

### `app/agent.py`

Contains `ConversationAgent`, which manages conversation history and delegates response generation to a configured client.

### `app/rag_client.py`

Adapts the Q2 retrieval pipeline to the conversation-agent interface.

The client:
- Passes the customer's question to the Q2 `answer_question` function.
- Retains retrieval results and source metadata.
- Detects explicit human or callback requests before querying the knowledge base.
- Returns a transparent human-follow-up message when such a request is detected.

**Escalation limitation:** The prototype records the request but does not automatically connect the customer to a representative or place a callback. The current implementation does not complete a real human handoff.

### `app/demo_client.py`

Provides deterministic offline demonstration responses through the same general response-client interface. It is useful for testing the voice components without requiring a paid AI API request.

The offline `DemoClient` workflow is distinct from the RAG-backed recorded sessions.

### `app/openai_client.py`

Contains an integration with the OpenAI Responses API using the official Python client.

The implementation submits the configured model, system instructions, user message, and optional conversation context. Its presence does not mean the recorded local RAG demonstration uses OpenAI generation.

Actual use requires valid API configuration and available API access.

### `app/local_tts.py`

Uses pyttsx3 to speak assistant responses and save audio to files.

### `app/voice_loop.py`

Connects microphone input, local speech recognition, `ConversationAgent`, `RAGClient`, and local text-to-speech.

The voice loop can run multiple turns and saves structured evidence for each session.

## Evidence Recording

Recorded sessions are saved under:

```text
q1_voice_agent/evidence/recorded_calls/
```

Each session directory can contain:

```text
session_<timestamp>/
+-- transcript.json
+-- turn_01_customer.wav
+-- turn_01_assistant.wav
+-- turn_02_customer.wav
+-- turn_02_assistant.wav
+-- ...
```

The actual files present depend on the session and whether speech was detected and assistant audio was generated successfully.

The structured transcript records:
- Session start and update timestamps
- Recognized customer text
- Assistant responses
- Per-turn status
- Customer and assistant audio filenames
- RAG mode
- Retrieved source names, categories, and scores when available

Retrieval scores are ranking metadata; they are not, by themselves, proof that an answer is correct.

## Local Setup

The project has been tested on Windows with a Python virtual environment.

The documented environment includes:
- Python 3.14
- Faster-Whisper
- PyAudioWPatch
- pyttsx3
- A compatible PyAV version

Versions previously recorded during testing include:

```text
av 18.1.0
faster-whisper 1.2.1
```

Install the project's required dependencies according to the repository's setup files. Keep API credentials in the local `.env` file and do not commit secrets. The `.env.example` file provides a safe configuration template.

## Running the RAG-Backed Voice Demo

From the repository root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python .\q1_voice_agent\app\voice_loop.py
```

The current entry point runs a three-turn conversation by default and uses a five-second recording duration per turn.

The workflow:
1. Captures microphone audio.
2. Transcribes the audio with Faster-Whisper.
3. Sends recognized text to `ConversationAgent`.
4. Retrieves a response through Q2 `RAGClient`.
5. Generates and plays local speech with pyttsx3.
6. Saves audio files and structured transcript evidence.

Microphone access, model availability, installed dependencies, and audio-device configuration are required for a successful local run.

## Alternative Response Backends

The repository includes three response clients:

| Client | Purpose |
|---|---|
| `RAGClient` | Uses the Q2 knowledge-base retrieval pipeline; used by the recorded voice loop |
| `DemoClient` | Provides deterministic offline demonstration responses |
| `OpenAIClient` | Integrates with the OpenAI Responses API when configured |

These backends have different behavior. Test results and recorded evidence should identify which backend was used.

## Testing

Run the Q1 test suite from the repository root:

```powershell
python -m pytest .\q1_voice_agent\tests -q
```

The test baseline most recently observed during development was **30 passed**. Rerun the command after code changes to verify the current result.

Passing tests demonstrate the tested code paths; they do not establish production-level speech-recognition accuracy or prove that every recorded conversation is correct.

## Current Limitations

- The local STT model can misrecognize speech, and errors can propagate into retrieval.
- Recording uses a fixed duration per turn.
- The offline `DemoClient` is deterministic rather than a full generative conversation system.
- OpenAI generation requires valid API configuration and available API access.
- The RAG-backed voice workflow depends on the Q2 retrieval pipeline and its source data.
- A retrieved response may be incorrect or insufficiently relevant; retrieval scores alone do not establish correctness.
- Human escalation records a request but does not execute a live transfer or callback.
- The local demonstration is intended for development and assessment, not production telephony deployment.

## Summary

Q1 provides a modular local voice-agent implementation with microphone capture, speech recognition, conversation-state management, Q2 knowledge-base integration, local speech output, and structured call evidence. It also includes alternative offline and OpenAI response clients.

The recorded RAG workflow demonstrates integration between voice processing and the knowledge base. Its limitations—particularly speech-recognition errors, retrieval quality, and the absence of an operational human handoff—should remain explicit in the final assessment submission.
