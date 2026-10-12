# Indonesia Test Cases

| Test               | Input                                 | Expected behavior                        |
| ------------------ | ------------------------------------- | ---------------------------------------- |
| Greeting           | Halo                                  | Indonesian greeting/response             |
| Loan inquiry       | Saya butuh pinjaman untuk usaha       | Respond in Indonesian                    |
| Eligibility        | Berapa lama usaha harus berjalan?     | State 24-month requirement               |
| Documents          | Dokumen apa yang diperlukan?          | Explain required documents               |
| Current rate       | Berapa suku bunga saat ini?           | Do not invent a live rate                |
| Unknown query      | [unrelated question]                  | Use Indonesian fallback or human handoff |
| Empty input        | Empty string                          | Return Indonesian fallback               |
| Language detection | Halo, saya butuh pinjaman untuk usaha | Detect `id`                              |
