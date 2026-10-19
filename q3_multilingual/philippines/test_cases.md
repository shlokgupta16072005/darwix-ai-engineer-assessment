# Philippines Test Cases

Target: Life insurance and bancassurance; Filipino with English-Filipino code-switching.

| Test | Example input | Expected behavior |
|---|---|---|
| Greeting | Kumusta po | Polite Filipino greeting |
| Insurance inquiry | Ano ang coverage ng life insurance? | Do not invent policy terms; offer verified information or human follow-up |
| Premium objection | Mahal ang premium. | Acknowledge concern; do not invent a premium amount |
| Code-switching | Ano ang requirements for life insurance? | Recognize mixed-language intent and respond in Filipino |
| Policy clarification | Is this policy required? | Do not make unsupported claims; offer human clarification |
| Human escalation | Gusto kong makipag-usap sa human agent. | Acknowledge request and explain that a human follow-up can be requested |
| Unknown query | Tell me today's weather in Mumbai | Use safe Filipino fallback |
| Empty input | Empty string | Return configured fallback |
| ASR variation | Filipino words with transcription errors | Normalize only known errors; otherwise use safe fallback |
| Regional speech | Representative regional-accent recording | Evaluate ASR and response accuracy; do not claim support without testing |

## Evidence requirements
Record the input, transcript, normalized transcript, bot response, language/voice configuration, and outcome for each executed scenario. Distinguish synthetic TTS tests from real customer-call recordings.

## Limitations
The current knowledge base contains business-loan content, not life-insurance policy details. Insurance coverage, exclusions, premiums, eligibility, waiting periods, and beneficiary rules require a verified source.
