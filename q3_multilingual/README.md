# Q3 - Multilingual Voice Bot Prototype

## Overview

This project implements a rule-based multilingual customer-support bot prototype for a fictional business-loan service. It includes localized response scripts and basic language detection for Filipino and Indonesian customer messages.

The prototype focuses on common business-loan questions, including loan eligibility, required documents, and interest-rate enquiries.

## Supported Languages

- Filipino (`fil`) - Philippines
- Indonesian (`id`) - Indonesia

## Features

- Basic language detection using language-specific word markers.
- Country-specific bot configuration and localized greetings.
- Rule-based responses to common business-loan enquiries.
- Localized fallback messages for unclear or unsupported input.
- Cross-language and unknown-language rejection.
- Safe handling of current-interest-rate questions when live pricing is unavailable.
- Unit tests for language detection, response handling, and fallback behavior.

## Project Structure

```text
q3_multilingual/
|-- common/
|   |-- config.py
|   |-- language_router.py
|   `-- voice_bot.py
|-- evidence/
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
|-- screenshots/
|-- tests/
|   `-- test_voice_bot.py
|-- transcripts/
`-- README.md
```

## Requirements

- Python 3
- PowerShell on Windows, or another terminal that supports Python commands

## Run the Unit Tests

Open PowerShell in the `q3_multilingual` directory and run:

```powershell
python -m unittest discover -s tests -v
```

To save the test output to the evidence folder:

```powershell
python -m unittest discover -s tests -v *> .\evidence\q3_unit_tests.txt
```

The current test suite contains 13 unit tests covering Filipino and Indonesian greetings, loan enquiries, eligibility, document requirements, rate fallbacks, unknown-language fallback, empty input, and cross-language rejection.

## Knowledge and Safety Behavior

The bot uses a fictional business-loan knowledge base. It does not invent live interest rates or guarantee loan approval. When current pricing is requested, it explains that live pricing is unavailable and indicates that human follow-up may be needed.

## Current Scope and Limitations

This is a rule-based multilingual response prototype. Language detection relies on word markers and may fail on short, ambiguous, or mixed-language messages.

The current Q3 implementation has not yet been demonstrated as a complete end-to-end multilingual speech system with integrated speech recognition and speech synthesis. The unit tests validate text-based routing and responses, not live audio performance.

## Evidence

- Unit-test output: `evidence/q3_unit_tests.txt`
- Scenario results: `evidence/q3_scenario_results.txt`
- Screenshots: `screenshots/`

## Future Improvements

- Integrate language-specific speech recognition and text-to-speech.
- Improve language detection for short and mixed-language messages.
- Add more test cases for ambiguous, unsupported, and noisy inputs.
- Connect the response layer to the shared knowledge base and human-handoff workflow.
