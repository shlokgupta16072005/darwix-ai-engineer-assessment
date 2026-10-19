# Indonesia Test Cases

Target: Multifinance and consumer finance; Indonesian with colloquial speech and Indonesian-English code-switching.

| Test | Example input | Expected behavior |
|---|---|---|
| Greeting | Halo | Polite Indonesian greeting |
| Consumer-finance inquiry | Apa saja syarat consumer financing? | Recognize mixed-language intent; avoid unsupported contract claims |
| Fee objection | Biaya pembiayaan terlalu mahal. | Acknowledge concern; do not invent fees or discounts |
| Installment question | Berapa cicilan saya setiap bulan? | Request verified contract details or offer human follow-up |
| Code-switching | Apa saja requirements untuk consumer financing? | Recognize mixed-language intent and respond in Indonesian |
| Human escalation | Saya ingin berbicara dengan petugas. | Acknowledge request and explain that a human follow-up can be requested |
| Unknown query | Tolong beri tahu skor pertandingan hari ini | Use safe Indonesian fallback |
| Empty input | Empty string | Return configured fallback |
| ASR variation | Colloquial Indonesian with transcription errors | Normalize only validated errors; otherwise use safe fallback |
| Regional speech | Representative regional-accent recording | Evaluate ASR and response accuracy; do not claim support without testing |

## Evidence requirements
Record the input, transcript, normalized transcript, bot response, language/voice configuration, and outcome for each executed scenario. Distinguish synthetic TTS tests from real customer-call recordings.

## Limitations
The current knowledge base contains business-loan content, not Indonesian consumer-finance contract terms. Fees, installment amounts, penalties, eligibility, interest rates, and contract conditions require a verified source.
