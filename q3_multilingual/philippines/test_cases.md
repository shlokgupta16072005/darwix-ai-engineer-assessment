# Philippines Test Cases

| Test               | Input                                  | Expected behavior                      |
| ------------------ | -------------------------------------- | -------------------------------------- |
| Greeting           | Kumusta                                | Filipino greeting/response             |
| Loan inquiry       | Kailangan ko ng business loan          | Respond in Filipino                    |
| Eligibility        | Gaano na katagal dapat ang negosyo ko? | State 24-month requirement             |
| Documents          | Ano ang mga dokumentong kailangan?     | Explain required documents             |
| Current rate       | Magkano ang interest rate ngayon?      | Do not invent a live rate              |
| Unknown query      | [unrelated question]                   | Use Filipino fallback or human handoff |
| Empty input        | Empty string                           | Return Filipino fallback               |
| Language detection | Kumusta, kailangan ko ng pautang       | Detect `fil`                           |
