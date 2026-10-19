# Indonesia Localization

## Target market
Indonesia — multifinance and consumer finance.

## Language
Indonesian (`id`), including natural colloquial speech and English finance terminology.

## Conversation style
Polite, helpful, conversational, and non-promotional. Terms such as "cicilan", "biaya", "angsuran", "kontrak", and "consumer financing" may be used where appropriate.

## Supported interaction patterns
- Greeting and customer intent clarification.
- Consumer-finance and installment inquiries.
- Questions or objections about fees and installments.
- Indonesian–English code-switching.
- Requests for a human representative.
- Unknown or unsupported questions.

## Grounding and safety
The current Q2 knowledge base contains business-loan information, not Indonesian consumer-finance contract terms. Do not invent installment amounts, fees, penalties, approval criteria, interest rates, or contract conditions.

For unsupported questions, state that verified product information is unavailable and offer human follow-up. Do not claim that a call has been transferred.

## Localization examples
1. Greeting: "Halo! Ada yang bisa saya bantu?"
2. Fee objection: "Saya mengerti bahwa biaya merupakan pertimbangan penting. Informasi biaya yang terverifikasi belum tersedia di sini. Anda dapat meminta tindak lanjut dari perwakilan."
3. Installment question: "Saya belum memiliki informasi kontrak yang terverifikasi untuk menghitung cicilan Anda. Silakan minta klarifikasi dari perwakilan."

## Regional speech and ASR limitations
The current demo does not establish accuracy for regional Indonesian accents or noisy real-world calls. Test colloquial Indonesian, mixed English finance terms, and regional speech before production use.
