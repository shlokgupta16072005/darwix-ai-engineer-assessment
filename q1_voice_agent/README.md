# Q1 - Voice Agent

## Overview

This module implements a local voice-agent pipeline for the Darwix AI Engineer Assessment.

The pipeline is:

**Microphone → Speech-to-Text → Conversation Agent → Text-to-Speech**

The implementation is designed so that the core voice workflow can be tested locally without requiring paid OpenAI API credits.

---

## Architecture

```text
User Speech
    |
    v
MicrophoneInput
    |
    v
Raw PCM Audio
    |
    v
LocalSTT
(Faster-Whisper)
    |
    v
User Text
    |
    v
ConversationAgent
    |
    v
DemoClient
    |
    v
Assistant Response
    |
    v
LocalTTS
(pyttsx3)
    |
    v
Speaker
```

The components are separated so that microphone input, speech recognition, conversation logic, AI response generation, and speech output can be tested independently.

---

## Components

### `app/microphone.py`

Captures microphone input using **PyAudioWPatch**.

Current configuration:

* Sample rate: 16 kHz
* Channels: 1
* Sample format: 16-bit PCM
* Configurable recording duration

The module returns a `RecordedAudio` object containing the raw audio bytes and audio metadata.

### `app/local_stt.py`

Provides local speech-to-text using **Faster-Whisper**.

Current local model:

```text
base.en
```

The module accepts microphone PCM data, converts it into a WAV representation, and sends the audio to Faster-Whisper for transcription.

### `app/agent.py`

Contains the `ConversationAgent`.

Responsibilities:

* Maintain conversation history
* Send user messages to the configured response client
* Store user/assistant exchanges
* Limit stored conversation turns
* Support conversation reset

The agent is independent of microphone and speaker hardware.

### `app/demo_client.py`

Provides deterministic offline responses.

It follows the same `generate_response()` interface used by the OpenAI client, allowing the complete voice pipeline to be tested without making external API calls.

This is the client used for the demonstrated local assessment workflow.

### `app/local_tts.py`

Provides local text-to-speech using **pyttsx3**.

It can:

* Speak responses through the local speaker
* Save generated speech to an audio file

### `app/openai_client.py`

Contains the real OpenAI text-generation integration.

The local demonstration does not require this client because the `DemoClient` provides deterministic offline responses.

When API access is available, the `ConversationAgent` can use the OpenAI client instead.

### `app/voice_loop.py`

Connects the local components into the complete voice workflow:

```text
MicrophoneInput
      |
      v
LocalSTT
      |
      v
ConversationAgent
      |
      v
DemoClient
      |
      v
LocalTTS
```

The current demonstration supports multiple turns in a single conversation and prints the stored conversation history at the end.

---

## Local Setup

The project was tested on:

* Windows
* Python 3.14
* Python virtual environment
* Faster-Whisper
* PyAudioWPatch
* pyttsx3

The local Faster-Whisper setup uses a compatible PyAV version.

Installed versions used during testing:

```text
av 18.1.0
faster-whisper 1.2.1
```

---

## Running the Voice Demo

From the repository root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python .\q1_voice_agent\app\voice_loop.py
```

The demo:

1. Loads the local Whisper model.
2. Records microphone audio.
3. Converts speech to text.
4. Sends the text to the conversation agent.
5. Generates a local demonstration response.
6. Sends the response to the local text-to-speech component.
7. Continues for multiple conversation turns.
8. Prints the stored conversation history.

---

## Tested Workflow

The complete local voice pipeline has been tested end-to-end.

### Test 1 - Microphone Capture

The microphone successfully captured raw PCM audio.

Example:

```text
Captured bytes: 159744
Sample rate: 16000
Channels: 1
Sample width: 2
```

### Test 2 - Local Speech Recognition

A microphone recording was successfully converted to text using Faster-Whisper.

Example:

```text
TRANSCRIPTION: "Hello, I'm testing that animal's voice assistant."
```

The transcription pipeline completed successfully.

Speech recognition can occasionally misrecognize uncommon words or names.

### Test 3 - Single-Turn Voice Interaction

The complete pipeline successfully processed:

```text
Microphone
    |
    v
Faster-Whisper
    |
    v
ConversationAgent
    |
    v
DemoClient
    |
    v
LocalTTS
```

Example:

```text
USER: Hello hello
ASSISTANT: Hello! I am the Darwix Voice Assistant demo. How can I help you today?
```

### Test 4 - Multi-Turn Conversation

A three-turn local conversation was successfully completed.

The system stored:

```text
Total turns stored: 3
```

Example conversation:

```text
1. USER: Hello hello
   ASSISTANT: Hello! I am the Darwix Voice Assistant demo. How can I help you today?

2. USER: What is your name?
   ASSISTANT: I am the Darwix Voice Assistant demo.

3. USER: Tell me about long
   ASSISTANT: I understood your message: "Tell me about long". This is a local demonstration response, so no paid API call was made.
```

The third turn demonstrates that speech-recognition errors can affect downstream intent matching.

This is treated as an STT accuracy limitation rather than a failure of the overall voice pipeline.

---

## OpenAI Integration

The project also contains an OpenAI client for the real AI-powered implementation.

The demonstrated local workflow uses `DemoClient` so that the complete voice pipeline can be tested without making paid API requests.

This separation allows the voice pipeline to be demonstrated and tested locally without depending on external API availability.

When API access is available, `ConversationAgent` can use the OpenAI client instead of `DemoClient`.

---

## Configuration

Environment variables are stored locally in:

```text
.env
```

The real `.env` file should **not** be committed to Git because it may contain API credentials.

A safe template is provided as:

```text
.env.example
```

The real `.env` file should remain excluded through `.gitignore`.

---

## Current Limitations

* The local STT model can occasionally misrecognize uncommon words or names.
* The current microphone implementation records for a fixed duration per turn.
* The offline `DemoClient` provides deterministic demonstration responses rather than full generative AI responses.
* Real OpenAI responses require API access.
* The current local STT implementation writes a temporary WAV file during transcription.
* The local demonstration is intended for assessment and development purposes rather than production deployment.

---

## Project Structure

```text
q1_voice_agent/
|
+-- app/
|   +-- __init__.py
|   +-- agent.py
|   +-- audio_client.py
|   +-- demo_client.py
|   +-- local_stt.py
|   +-- local_tts.py
|   +-- microphone.py
|   +-- openai_client.py
|   +-- voice_loop.py
|
+-- config/
|   +-- __init__.py
|   +-- settings.py
|
+-- tests/
|   +-- test_openai_client.py
|
+-- transcripts/
|
+-- .env.example
+-- README.md
```

The real `.env` file is intentionally omitted from the documented project structure because it contains local configuration and may contain credentials.

---

## Status

The local Q1 voice-agent pipeline is operational and has been tested end-to-end.

```text
Microphone: PASS
Speech-to-Text: PASS
Conversation Agent: PASS
Conversation History: PASS
Local Text-to-Speech: PASS
Multi-turn Voice Loop: PASS
Offline Demo: PASS
OpenAI Integration Code: PRESENT
```

The OpenAI integration code is present, while the tested demonstration uses the offline `DemoClient` so that no paid API request is required.

---

## Summary

The Q1 implementation demonstrates a modular local voice-agent architecture with:

* Microphone audio capture
* Local speech recognition
* Conversation-state management
* Offline response generation
* Local text-to-speech
* Multi-turn conversation handling
* Optional OpenAI integration

The architecture separates the individual components so that the system can be tested locally and the response-generation backend can be replaced without changing the microphone, STT, conversation, or TTS interfaces.