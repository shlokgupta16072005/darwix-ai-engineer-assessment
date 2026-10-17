================================================================================
AI ENGINEER ASSESSMENT
Q2 - KNOWLEDGE BASE / RAG SYSTEM
NOVAFIN BUSINESS LOAN PROTOTYPE
===============================

PROJECT:
AI Engineer Assessment - Question 2

BUSINESS DOMAIN:
Business Loan Qualification

PROTOTYPE COMPANY:
NovaFin

IMPORTANT:
NovaFin is a fictional lender created only for this prototype.
The loan amounts, eligibility rules, pricing information, and other business
information are illustrative training data and must not be treated as real
financial advice.

================================================================================

1. OBJECTIVE
   ================================================================================

STATUS:
COMPLETED

The objective of Q2 is to build a searchable knowledge base that can be used
by an AI system to answer business-loan questions using retrieved information
instead of relying only on information stored in the model prompt.

The system should:

1. Load information from different document formats.
2. Clean and normalize the source information.
3. Check documents for PII.
4. Split documents into searchable chunks.
5. Add metadata to the chunks.
6. Build a vector-based retrieval system.
7. Retrieve relevant knowledge for a user question.
8. Generate an answer using retrieved context.
9. Provide source information for the generated answer.
10. Avoid inventing information that is not available in the knowledge base.
11. Provide a human follow-up path when required information is unavailable.

SCREENSHOT / EVIDENCE:
Not required separately. The implementation outputs and Q2 evidence
screenshots provide supporting evidence.

================================================================================
2. HIGH-LEVEL ARCHITECTURE
==========================

STATUS:
COMPLETED

```
                SOURCE DOCUMENTS
                       |
                       v
              +------------------+
              | Document Loader  |
              +------------------+
                       |
                       v
              +------------------+
              | Cleaning /       |
              | Normalization    |
              +------------------+
                       |
                       v
              +------------------+
              | PII Detection    |
              +------------------+
                       |
                       v
              +------------------+
              | Chunking         |
              +------------------+
                       |
                       v
              +------------------+
              | Vector Store     |
              | TF-IDF Retrieval |
              +------------------+
                       |
                       v
                User Question
                       |
                       v
              +------------------+
              | Similarity Search|
              +------------------+
                       |
                       v
                Top-K Chunks
                       |
                       v
              +------------------+
              | RAG Answer       |
              | Generation       |
              +------------------+
                       |
                       v
                Answer + Sources
```

SCREENSHOT / EVIDENCE:
Optional - architecture is also described in the project README.

================================================================================
3. PROJECT STRUCTURE
====================

STATUS:
COMPLETED

Current Q2 project structure:

q2_knowledge_base/
|
+-- data/
|   |
|   +-- application_process.txt
|   +-- eligibility_rules.pdf
|   +-- faq.txt
|   +-- loan_products.pdf
|   +-- objection_handling.txt
|   +-- sample_application.csv
|
+-- ingestion/
|   |
|   +-- build_kb.py
|   +-- chunker.py
|   +-- cleaner.py
|   +-- document_loader.py
|   +-- pii_detector.py
|   +-- **init**.py
|
+-- retrieval/
|   |
|   +-- vector_store.py
|   +-- search.py
|   +-- test_retrieval.py
|   +-- retrieval_test_results.json
|   +-- rag_answer.py
|   +-- test_openai.py
|   +-- **init**.py
|
+-- tests/
|
+-- vector_store/
|
+-- docs/
|   |
|   +-- q2_test_results.md
|   +-- q2_test_results_backup.md
|
+-- screenshots/
|
+-- .env
+-- .env.example
+-- requirements.txt
+-- README.md

Additional Python cache files such as **pycache** and *.pyc may be generated
automatically during execution and are not part of the core implementation.

The actual .env file is local-only and contains the API credential. It must
not be committed to GitHub.

The .env.example file documents the required environment variables without
containing the real API key.

A .gitignore already exists at the parent assessment directory:

Darwix AI/.gitignore

This parent-level .gitignore is intended to be used later when Q1-Q4 are
combined into the final GitHub repository. A second Q2-specific .gitignore
is not required.

SCREENSHOT / EVIDENCE:
YES

Actual project-structure evidence:

01_01_Project_Structure.PNG
01_02_Project_Structure.PNG
01_03_Project_Structure.PNG

================================================================================
4. SOURCE DATA
==============

STATUS:
COMPLETED

The knowledge base contains six source files.

1. application_process.txt
2. eligibility_rules.pdf
3. faq.txt
4. loan_products.pdf
5. objection_handling.txt
6. sample_application.csv

---

## 4.1 application_process.txt

STATUS:
COMPLETED

Contains the loan application workflow.

Main information includes:

* Initial customer conversation
* Business type
* Business vintage
* Requested loan amount
* Intended use
* Human callback requirement
* Basic eligibility check
* Document collection
* Assessment
* Final decision
* Customer communication
* Voice-agent decision logic
* Fallback behaviour

Important business rules include:

* Business vintage must be at least 24 months.
* Requested loan amount must be between Rs. 2 lakh and Rs. 25 lakh.
* Final approval is subject to verification and internal assessment.
* The system must not fabricate approval, pricing, or disbursement information.

---

## 4.2 eligibility_rules.pdf

STATUS:
COMPLETED

Contains eligibility and document rules.

Important information includes:

* Applicant must be an adult and legally able to enter the agreement.
* Business must have operated continuously for at least 24 months.
* Sufficient identity, business and financial information is required.
* Requested loan amount must be within the available product range.

Typical documents include:

* Identity proof
* PAN or applicable tax identification
* Business proof or registration where applicable
* Recent business bank statements
* Other financial records requested during assessment

The document also contains prototype PII-handling rules.

---

## 4.3 faq.txt

STATUS:
COMPLETED

Contains frequently asked questions.

Examples include:

* Minimum loan amount
* Maximum loan amount
* Loan tenure
* Minimum business vintage
* Missing documents
* Collateral/security
* Permitted loan purposes
* Guaranteed approval
* Larger loan requests
* Current interest rates
* Human callback
* Post-application process

---

## 4.4 loan_products.pdf

STATUS:
COMPLETED

Contains product information for the fictional NovaFin Business Growth Loan.

Important information:

Loan amount:
Rs. 2 lakh to Rs. 25 lakh

Tenure:
12 to 60 months

Minimum business vintage:
24 months

Initial assessment:
Typically 1-2 business days after required information is received

Pricing:
Customer-specific and not guaranteed before assessment.

The product document also contains communication rules that prevent the
system from promising approval or quoting an unapproved interest rate.

---

## 4.5 objection_handling.txt

STATUS:
COMPLETED

Contains example responses to customer objections.

Examples include:

* Interest rate is too high.
* Customer does not want to share information.
* Customer does not trust online applications.
* Customer wants a larger loan amount.
* Business is only 18 months old.
* Customer wants human assistance.

The system should use these responses as contextual guidance rather than
making unsupported promises.

---

## 4.6 sample_application.csv

STATUS:
COMPLETED

Contains synthetic application information for prototype testing.

The data is synthetic and is not intended to represent real customer data.

PII-sensitive application information is not required for the general
knowledge retrieval process and is intentionally excluded from the searchable
knowledge-base vector store.

================================================================================
5. DOCUMENT INGESTION
=====================

STATUS:
COMPLETED

The ingestion pipeline loads the source documents using document_loader.py.

Supported source types in the current prototype include:

* TXT
* PDF
* CSV

Observed source sizes during the latest run:

application_process.txt:
1,724 characters

eligibility_rules.pdf:
1,785 characters

faq.txt:
3,107 characters

loan_products.pdf:
1,911 characters

objection_handling.txt:
3,232 characters

sample_application.csv:
3,551 characters

SCREENSHOT / EVIDENCE:
YES

Actual screenshots:

02_01_ingestion_document_loader.PNG
02_02_ingestion_document_loader.PNG

================================================================================
6. CLEANING
===========

STATUS:
COMPLETED

The cleaning stage normalizes the loaded documents before indexing.

Observed results during the latest run:

application_process.txt:
1,724 -> 1,691 characters

eligibility_rules.pdf:
1,785 -> 1,783 characters

faq.txt:
3,107 -> 3,106 characters

loan_products.pdf:
1,911 -> 1,910 characters

objection_handling.txt:
3,232 -> 3,031 characters

sample_application.csv:
3,551 -> 3,551 characters

The cleaning stage helps reduce unnecessary formatting, repeated content and
irrelevant text before retrieval.

SCREENSHOT / EVIDENCE:
YES

Actual screenshots:

03_01_ingestion_cleaning.png
03_02_ingestion_cleaning.PNG

================================================================================
7. PII DETECTION
================

STATUS:
COMPLETED

The ingestion pipeline checks every document for possible personally
identifiable information.

Latest result:

application_process.txt      [NO PII]
eligibility_rules.pdf        [NO PII]
faq.txt                      [NO PII]
loan_products.pdf            [NO PII]
objection_handling.txt       [NO PII]
sample_application.csv       [NO PII]

The sample application data is synthetic.

The system is designed not to unnecessarily expose sensitive customer fields
inside retrieval chunks or logs.

SCREENSHOT / EVIDENCE:
YES

Actual screenshot:

04_ingestion_pii_detection.png

================================================================================
8. CHUNKING
===========

STATUS:
COMPLETED

The documents are divided into smaller chunks before being indexed.

Latest chunking run:

application_process.txt      4 chunks
eligibility_rules.pdf        5 chunks
faq.txt                      9 chunks
loan_products.pdf            4 chunks
objection_handling.txt       8 chunks
sample_application.csv       6 chunks

TOTAL CHUNKS CREATED:
36 chunks

The chunking stage makes individual sections of the knowledge base searchable
rather than treating every document as one large block.

SCREENSHOT / EVIDENCE:
YES

Actual screenshots:

05_01_ingestion_chunking.png
05_02_ingestion_chunking.PNG
05_03_ingestion_chunking.PNG
05_04_ingestion_chunking.PNG

================================================================================
9. VECTOR STORE
===============

STATUS:
COMPLETED

The current prototype uses a local TF-IDF based vector store.

The vector store converts text into numerical representations and compares
the user's query against the stored knowledge-base chunks using cosine
similarity.

Latest build result:

Total chunks created during chunking:
36

Application-data chunks:
6

Knowledge-base chunks indexed:
30

Vocabulary size:
1520

Vector store location:

q2_knowledge_base/vector_store

The vector store was successfully created and saved locally.

IMPORTANT IMPLEMENTATION DETAIL:

The chunking stage creates 36 chunks across all six source files.

The sample_application.csv file produces 6 chunks categorized as:

application_data

The vector-store implementation intentionally excludes these chunks using
the following filtering logic:

knowledge_chunks = [
chunk
for chunk in chunks
if chunk["category"] != "application_data"
]

Therefore:

36 total chunks

* 6 application-data chunks
  = 30 knowledge-base chunks indexed

This separation prevents application/customer records from being included in
the general searchable knowledge base.

The 36-to-30 difference is therefore intentional and is not a vector-store
failure or unresolved discrepancy.

SCREENSHOT / EVIDENCE:
YES

Actual screenshots:

06_01_vector_store_build.png
06_02_vector_store_build.PNG

These show:

[VECTOR STORE] 30 chunks indexed
[VECTOR STORE] Vocabulary size: 1520
[VECTOR STORE] Saved to: ...

================================================================================
10. RETRIEVAL METHOD
====================

STATUS:
COMPLETED

The search system uses:

1. TF-IDF vectorization
2. Query transformation
3. Cosine similarity
4. Similarity ranking
5. Top-K retrieval

For each query, the system returns:

* Rank
* Similarity score
* Source
* Category
* Chunk ID
* Retrieved text

A small category-aware boost is applied to clearly identifiable eligibility
queries.

The retrieval implementation is intended as a lightweight local prototype.

================================================================================
11. RETRIEVAL EVALUATION
========================

STATUS:
COMPLETED

Five retrieval queries were tested.

---

## TEST 1

Query:

What is the minimum business vintage?

Top result:

faq.txt

Top adjusted score:

0.3535

Expected information:

Minimum business vintage is 24 months.

Result:

PASS

---

## TEST 2

Query:

What documents are required for the loan application?

Top result:

faq.txt

Top adjusted score:

0.2353

Relevant document information was also retrieved from:

* application_process.txt
* eligibility_rules.pdf

Result:

PASS

---

## TEST 3

Query:

What is the minimum and maximum loan amount?

Top result:

faq.txt

Top adjusted score:

0.5865

Relevant supporting information was also retrieved from:

* loan_products.pdf

Result:

PASS

---

## TEST 4

Query:

What should I say if the customer thinks the interest rate is too high?

Top result:

objection_handling.txt

Top adjusted score:

0.4505

Result:

PASS

---

## TEST 5

Query:

Can a business that has operated for only one year qualify?

Top result:

eligibility_rules.pdf

Top adjusted score:

0.2328

Relevant eligibility information was correctly retrieved.

Result:

PASS

================================================================================
12. RETRIEVAL EVALUATION SUMMARY
================================

STATUS:
COMPLETED

Tests performed:
5

Tests satisfying the implemented retrieval evaluation criteria:
5/5

Reported evaluation:
5/5 PASS

The five queries successfully retrieved relevant expected information from
the knowledge base according to the implemented evaluation criteria.

Important qualification:

This is a small prototype-specific evaluation and should not be described
as a formal benchmark or production retrieval-accuracy measurement.

The result should also not be described as 5/5 top-1 source accuracy because
some tests retrieved the expected information in supporting results rather
than having the expected source as the top-ranked result.

================================================================================
13. RAG ANSWER GENERATION
=========================

STATUS:
COMPLETED

The RAG pipeline connects retrieval with answer generation.

Pipeline:

User question
|
v
Vector retrieval
|
v
Top relevant chunks
|
v
Context supplied to answer generator
|
v
Grounded answer
|
v
Answer + Sources

The system is designed to answer using retrieved knowledge-base context.

If required information is unavailable, the system should not invent an
answer.

The current implementation uses the OpenAI Responses API for model-based
answer generation. The Responses API is the current OpenAI API interface
used by this implementation. The Assistants API was sunset by OpenAI on
August 26, 2026.

================================================================================
14. RAG TEST 1
==============

STATUS:
COMPLETED

Question:

What is the minimum business vintage?

Answer:

The stated minimum business vintage is 24 months of continuous operation.

Generation mode:

openai_rag

Sources:

* faq.txt
* eligibility_rules.pdf
* faq.txt

Result:

PASS

================================================================================
15. RAG TEST 2
==============

STATUS:
COMPLETED

Question:

What documents are required to apply for a business loan?

Answer:

Typical documents include:

* Identity proof
* PAN or applicable tax identification information
* Business proof or registration, where applicable
* Recent business bank statements or other financial records requested
  during assessment

Additional documents may be requested depending on the application.

Generation mode:

openai_rag

Sources:

* faq.txt
* application_process.txt
* eligibility_rules.pdf

Result:

PASS

================================================================================
16. RAG TEST 3 - UNAVAILABLE LIVE INFORMATION
=============================================

STATUS:
COMPLETED

Question:

What is today's interest rate?

Answer:

Today's live interest rates are not available in the current knowledge base.
Human follow-up can be arranged for current pricing.

Generation mode:

openai_rag

Sources:

* faq.txt
* faq.txt
* faq.txt

Important observation:

The knowledge base does not contain a live interest-rate table.

The system therefore avoids inventing a current interest rate.

This demonstrates fallback behaviour for unavailable information.

Result:

PASS

================================================================================
17. RAG TEST 4 - ELIGIBILITY
============================

STATUS:
COMPLETED

Question:

Can a business that has operated for only one year qualify?

Answer:

Based on the stated eligibility rules, a business must have operated
continuously for at least 24 months. A business operating for one year does
not meet that requirement. Applications are also subject to verification and
internal assessment. You can contact a support representative if you would
like help discussing your situation.

Generation mode:

openai_rag

Sources:

* eligibility_rules.pdf
* eligibility_rules.pdf
* eligibility_rules.pdf

Result:

PASS

================================================================================
18. RAG TEST 5 - OBJECTION HANDLING
===================================

STATUS:
COMPLETED

Question:

What should I say if the customer thinks the interest rate is too high?

Answer:

Acknowledge that pricing is important. Explain that final pricing is
customer-specific and depends on the application and assessment. Offer to
collect details for an assessment or arrange a callback with a representative
to discuss pricing. Do not promise a lower rate.

Generation mode:

openai_rag

Sources:

* objection_handling.txt
* faq.txt
* objection_handling.txt

Result:

PASS

================================================================================
19. RAG DESIGN DECISIONS
========================

STATUS:
COMPLETED

Decision 1:
Use a local TF-IDF vector store for the prototype.

Reason:

It is simple, transparent and sufficient for demonstrating retrieval
behaviour on the small prototype dataset without introducing unnecessary
infrastructure.

Decision 2:
Exclude application_data chunks from the general knowledge vector store.

Reason:

Application/customer sample records are not required for general knowledge
retrieval and should not be unnecessarily exposed through the searchable
knowledge base.

Decision 3:
Use top-K retrieval.

Reason:

Returning multiple relevant chunks provides the answer-generation stage
with additional context and allows supporting sources to be displayed.

Decision 4:
Include source metadata.

Reason:

The source information helps identify where the retrieved information
originated.

Decision 5:
Do not fabricate missing information.

Reason:

Business and financial information should not be invented when it is not
present in the knowledge base.

Decision 6:
Use human follow-up for unavailable information.

Reason:

Some information, such as current pricing, may require a live business
system or human representative.

================================================================================
20. Q2 CURRENT IMPLEMENTATION STATUS
====================================

STATUS:
COMPLETED

The main Q2 knowledge-base and RAG pipeline is implemented and working.

Completed components:

[COMPLETED] Document loading
[COMPLETED] TXT/PDF/CSV source handling
[COMPLETED] Cleaning and normalization
[COMPLETED] PII detection
[COMPLETED] Metadata generation
[COMPLETED] Document chunking
[COMPLETED] 36 total chunks created
[COMPLETED] Application-data filtering
[COMPLETED] 30 knowledge-base chunks indexed
[COMPLETED] Local TF-IDF vector store
[COMPLETED] Cosine-similarity retrieval
[COMPLETED] Top-K retrieval
[COMPLETED] Retrieval evaluation
[COMPLETED] RAG answer generation
[COMPLETED] Source reporting
[COMPLETED] Missing-information fallback
[COMPLETED] OpenAI API integration
[COMPLETED] Interactive RAG testing
[COMPLETED] Technical verification

================================================================================
21. VERIFIED CHUNK FILTERING BEHAVIOUR
======================================

STATUS:
COMPLETED

The latest chunking run reports:

36 chunks created

The vector-store build reports:

30 chunks indexed

Difference:

6 chunks

The difference has been verified from the vector_store.py implementation.

The 6 excluded chunks belong to:

sample_application.csv

and have the category:

application_data

The vector-store builder intentionally excludes application_data chunks from
the searchable knowledge base.

Therefore:

36 total chunks

* 6 application-data chunks
  = 30 searchable knowledge-base chunks

This is an intentional data-separation design decision.

The application/customer sample data is retained as source material for
prototype testing but is not indexed into the general knowledge retrieval
store.

Conclusion:

The 36-to-30 difference is expected behaviour and does not represent a
vector-store indexing error.

================================================================================
22. RETRIEVAL QUALITY OBSERVATION
=================================

STATUS:
COMPLETED

The retrieval system successfully returned relevant expected information for
all five evaluation queries under the implemented evaluation criteria.

The retrieval results show that:

* FAQ content is useful for common customer questions.
* Eligibility rules are retrieved for business-vintage questions.
* Product information is retrieved for loan amount questions.
* Objection handling content is retrieved for customer objections.

The retrieval system is a lightweight TF-IDF implementation and can be
improved later using embedding-based retrieval and reranking.

================================================================================
23. RAG SAFETY / HALLUCINATION CONTROL
======================================

STATUS:
COMPLETED

The RAG answer-generation prompt includes rules to:

1. Use only supplied knowledge-base context.
2. Never invent policies.
3. Never invent interest rates.
4. Never invent eligibility rules.
5. Never invent loan amounts.
6. Never claim final loan approval.
7. State when information is unavailable.
8. Offer human follow-up when appropriate.

The current-interest-rate test demonstrates this behaviour.

Additional interactive tests also demonstrated handling of:

* Unsupported live pricing questions.
* Unsupported approval guarantees.
* Attempts to confirm an unsupported interest rate.
* Out-of-domain questions such as current weather.

================================================================================
24. Q2 SCREENSHOTS / EVIDENCE
=============================

STATUS:
COMPLETED

The Q2 implementation evidence has been captured in the screenshots
directory.

The actual screenshot filenames are listed below.

---

## SCREENSHOT GROUP 1 - PROJECT STRUCTURE

Files:

01_01_Project_Structure.PNG
01_02_Project_Structure.PNG
01_03_Project_Structure.PNG

Shows:

* Q2 project directories.
* data/
* ingestion/
* retrieval/
* tests/
* docs/
* screenshots/
* vector_store/

---

## SCREENSHOT GROUP 2 - DOCUMENT INGESTION

Files:

02_01_ingestion_document_loader.PNG
02_02_ingestion_document_loader.PNG

Shows:

* Source documents loaded.
* TXT, PDF and CSV processing.
* Document character counts.

---

## SCREENSHOT GROUP 3 - CLEANING

Files:

03_01_ingestion_cleaning.png
03_02_ingestion_cleaning.PNG

Shows:

* Original character counts.
* Cleaned character counts.
* Cleaning and normalization results.

---

## SCREENSHOT GROUP 4 - PII DETECTION

File:

04_ingestion_pii_detection.png

Shows:

* PII detection results.
* [NO PII] results for the synthetic source documents.

---

## SCREENSHOT GROUP 5 - CHUNKING

Files:

05_01_ingestion_chunking.png
05_02_ingestion_chunking.PNG
05_03_ingestion_chunking.PNG
05_04_ingestion_chunking.PNG

Shows:

* Chunking results by document.
* Number of chunks per source.
* Total of 36 chunks created.
* Chunk metadata and categories.

---

## SCREENSHOT GROUP 6 - VECTOR STORE

Files:

06_01_vector_store_build.png
06_02_vector_store_build.PNG

Shows:

* 30 knowledge-base chunks indexed.
* Vocabulary size of 1520.
* Vector store successfully saved.

---

## SCREENSHOT GROUP 7 - RETRIEVAL EVALUATION

Files:

07_01_retrieval_test.png
07_02_retrieval_test.PNG
07_03_retrieval_test.PNG
07_04_retrieval_test.PNG
07_05_retrieval_test.PNG
07_06_retrieval_test.PNG
07_07_retrieval_test.PNG
07_08_retrieval_test.PNG
07_09_retrieval_test.PNG
07_10_retrieval_test.PNG

Shows:

* Retrieval queries.
* Retrieved sources.
* Similarity scores.
* Evaluation results.
* Five retrieval tests passing the implemented evaluation criteria.

---

## SCREENSHOT GROUP 8 - RAG ANSWER GENERATION

Files:

08_01_rag_answer_test.png
08_02_rag_answer_test.PNG
08_03_rag_answer_test.PNG
08_04_rag_answer_test.PNG

Shows:

* Questions.
* Generated answers.
* Generation mode.
* Retrieved sources.
* Source attribution.
* Missing-information handling.

---

## SCREENSHOT GROUP 9 - REQUIREMENTS

File:

09_Requirements.PNG

Shows:

* Python dependencies used by the prototype.

---

## SCREENSHOT GROUP 10 - INTERACTIVE RAG MODE

Files:

10_01_rag_interactive_mode.PNG
10_02_rag_interactive_mode.PNG
10_03_rag_interactive_mode.PNG
10_04_rag_interactive_mode.PNG

Shows interactive testing of:

* Current-interest-rate questions.
* Loan-approval guarantee questions.
* Unsupported rate confirmation.
* Unsupported external information such as weather.

These tests demonstrate that the RAG system does not invent unavailable
knowledge and instead indicates when information is outside the knowledge
base.

IMPORTANT:

Do not show:

* OPENAI_API_KEY
* passwords
* .env contents
* private credentials

Screenshots should contain only safe project information.

================================================================================
25. GITHUB REPOSITORY
=====================

STATUS:
TODO
PRIORITY:
HIGH

No GitHub repository has been created yet for the overall assessment.

The final GitHub repository will contain the complete assessment covering:

* Q1
* Q2
* Q3
* Q4

The repository should be created only after the four assessment questions
have been implemented and the final project structure has been verified.

Suggested final repository name:

darwix-ai-engineer-assessment

Alternative:

darwix-ai-assessment

The repository should contain the actual project code and documentation.

================================================================================
26. GITIGNORE
=============

STATUS:
LOCAL CONFIGURATION PRESENT
FINAL REPOSITORY VERIFICATION PENDING

A .gitignore already exists at:

C:\Users\Lenovo\Desktop\Darwix AI.gitignore

This is the parent directory that will eventually serve as the GitHub
repository root for the complete Q1-Q4 assessment.

The intended entries include:

.env
.venv/
**pycache**/
*.pyc
*.log
vector_store/

The exact final root .gitignore will be verified again before GitHub
initialization.

The actual .env file must never be committed because it may contain the
OpenAI API key.

No additional Q2-specific .gitignore is required.

================================================================================
27. ENVIRONMENT EXAMPLE
=======================

STATUS:
COMPLETED FOR Q2

The Q2 project contains:

.env.example

The example file documents the required environment variables without
containing the real API credential.

Expected structure:

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

The actual .env file is local-only and must never be uploaded to GitHub.

The .env.example file is safe to include in the eventual repository.

================================================================================
28. GIT INITIALIZATION
======================

STATUS:
TODO

Git has not yet been initialized for the overall assessment repository.

Git initialization will be performed later from:

C:\Users\Lenovo\Desktop\Darwix AI

This is intentional because the final repository must contain Q1, Q2, Q3
and Q4 together.

The final process will be:

git init

git status

Verify the files that must remain private are ignored.

Then:

git add .

Then:

git status

Then:

git commit -m "Initial AI Engineer Assessment implementation"

================================================================================
29. GITHUB REMOTE
=================

STATUS:
TODO

After the complete assessment repository is prepared, a GitHub repository
will be created.

The remote will then be configured using:

git remote add origin YOUR_GITHUB_REPOSITORY_URL

Verification:

git remote -v

================================================================================
30. PUSH TO GITHUB
==================

STATUS:
TODO

After the complete Q1-Q4 assessment has been committed:

git branch -M main

git push -u origin main

The GitHub repository will then be opened and verified.

The verification must confirm:

* README is visible.
* Q1 project files are visible.
* Q2 project files are visible.
* Q3 project files are visible.
* Q4 project files are visible.
* Required documentation is visible.
* .env is NOT visible.
* API keys are NOT visible.
* Unnecessary virtual-environment files are NOT visible.

================================================================================
31. Q2 README
=============

STATUS:
PRESENT
FINAL REVIEW PENDING

A Q2 README.md already exists in:

q2_knowledge_base/README.md

The README contains the Q2 project information and setup/documentation.

Before final submission, it should be reviewed against the final implementation
and updated if required.

The eventual assessment-level README at:

Darwix AI/README.md

will be created or finalized later so that it documents Q1, Q2, Q3 and Q4
together.

Therefore, Q2 README completion and final assessment README completion are
treated as separate tasks.

================================================================================
32. Q2 SETUP INSTRUCTIONS
=========================

STATUS:
PRESENT / FINAL REVIEW PENDING

The Q2 documentation should provide setup information covering:

1. Creating a Python virtual environment.
2. Installing requirements.
3. Creating .env from .env.example.
4. Adding an OpenAI API key when model-based RAG generation is required.
5. Building the vector store.
6. Running retrieval tests.
7. Running RAG tests.
8. Running interactive RAG mode.

The final setup instructions will be reviewed again when the complete
assessment repository is assembled.

================================================================================
33. Q1 - VOICE AI AGENT
=======================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

Q1 has not yet been implemented.

The intended business use case is:

NovaFin Business Loan Qualification.

The voice agent should collect information such as:

* Business type
* Business vintage
* Requested loan amount
* Intended use
* Human callback requirement

The agent should use the Q2 knowledge base for relevant business questions
rather than hardcoding all business information into the system prompt.

Q1 will be started after the Q2 local implementation and documentation are
finalized.

================================================================================
34. Q1 - VOICE AGENT TESTING
============================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

Required Q1 testing will be implemented according to the assessment
requirements.

Planned test scenarios include:

1. Cooperative customer
2. Customer objection
3. Incomplete information
4. Conflicting information
5. Out-of-scope question
6. Human escalation

At least three recorded calls should be captured if required by the
assessment specification.

No Q1 call recordings are being claimed at this stage.

================================================================================
35. Q3 - PHILIPPINES VOICE BOT
==============================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

Q3 has not yet been implemented.

The Philippines localized voice bot should consider:

* English
* Filipino / Taglish
* Natural conversational phrasing
* Localized tone
* Code switching
* Speech recognition quality
* Fallback behaviour

Test calls and evidence will be captured after implementation.

================================================================================
36. Q3 - INDONESIA VOICE BOT
============================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

The Indonesian localized voice bot has not yet been implemented.

The implementation should consider:

* Bahasa Indonesia
* Finance-related terminology
* Natural conversational style
* Regional/accent handling
* Speech recognition
* TTS quality
* Fallback behaviour

Test calls and evidence will be captured after implementation.

================================================================================
37. Q4 - REAL-TIME CALL ANALYSIS
================================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

Q4 has not yet been implemented.

Proposed pipeline:

Live / Real-Time-Speed Audio
|
v
Streaming Speech Recognition
|
v
Transcript
|
v
Signal Detection
|
v
Nudge Generation
|
v
Agent Dashboard / Output

================================================================================
38. Q4 - SIGNALS AND NUDGES
===========================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

Potential signals to implement according to the assessment requirements may
include:

1. Customer frustration
2. Missed cross-sell opportunity
3. Compliance gap
4. Payment difficulty
5. Need for escalation

Example nudge:

"Customer frustration detected. Acknowledge the concern before continuing."

Another example:

"Possible cross-sell opportunity detected. Ask whether the customer needs
information about the additional product."

No Q4 signal-detection results or nudge metrics are being claimed yet.

================================================================================
39. Q4 - NUDGE SUPPRESSION AND LATENCY
======================================

STATUS:
NOT COMPLETED
CURRENT COMPLETION:
0%

The nudge system should ideally include:

* Confidence threshold
* Duplicate suppression
* Cooldown period
* Nudge priority
* Expiry

Example:

If the same signal is detected repeatedly within a short period, the system
should avoid displaying the same nudge repeatedly.

Latency should be measured using:

* ASR latency
* Signal detection latency
* LLM/nudge generation latency
* End-to-end latency

The final report should include:

P50 latency
P95 latency

No latency values are being invented or claimed before actual measurement.

================================================================================
40. FINAL DOCUMENTATION
=======================

STATUS:
IN PROGRESS

The final submission should include:

Q1:
Voice AI agent

Q2:
Knowledge base / RAG system

Q3:
Localized voice bots

Q4:
Real-time call analysis and agent nudges

For each completed question, document:

* Objective
* Architecture
* Implementation
* Testing
* Results
* Screenshots / recordings
* Limitations
* Future improvements

Q2 documentation is substantially complete but final repository packaging is
still pending.

================================================================================
41. FINAL SUBMISSION CHECKLIST
==============================

STATUS:
IN PROGRESS

Q2 IMPLEMENTATION:

[YES] Document ingestion
[YES] TXT/PDF/CSV handling
[YES] Cleaning
[YES] PII detection
[YES] Chunking
[YES] Vector store
[YES] Retrieval
[YES] Five retrieval tests
[YES] RAG answer generation
[YES] Source reporting
[YES] Missing-information fallback
[YES] OpenAI integration
[YES] RAG test cases
[YES] Interactive RAG testing
[YES] 36-to-30 chunk filtering verified

Q2 EVIDENCE:

[YES] Document loading screenshots
[YES] Cleaning screenshots
[YES] PII screenshot
[YES] Chunking screenshots
[YES] Vector-store screenshots
[YES] Retrieval screenshots
[YES] RAG screenshots
[YES] Project structure screenshots
[YES] Requirements screenshot
[YES] Interactive RAG screenshots

Q2 DOCUMENTATION / PACKAGING:

[YES] Q2 README exists
[YES] .env.example exists
[YES] Parent-level .gitignore exists
[YES] Backup of q2_test_results.md created
[IN PROGRESS] Final Q2 README review
[IN PROGRESS] Final Q2 documentation review
[TODO] Final assessment-level README
[TODO] Git initialization
[TODO] GitHub repository
[TODO] Git commit/push
[TODO] Final GitHub verification
[TODO] Final submission URL

Q1:

[ ] Voice agent
[ ] Q2 knowledge base connected
[ ] Cooperative call
[ ] Objection call
[ ] Incomplete/conflicting case
[ ] Out-of-scope case
[ ] Human escalation
[ ] Required recordings

Q3:

[ ] Philippines bot
[ ] Indonesia bot
[ ] Localized interactions
[ ] Required calls per market
[ ] Fallback testing

Q4:

[ ] Real-time/replay pipeline
[ ] Streaming ASR
[ ] Signal detection
[ ] Nudge generation
[ ] Nudge suppression
[ ] Latency measurement
[ ] P50/P95 results

================================================================================
42. CURRENT WORK COMPLETION
===========================

STATUS:
CURRENT ESTIMATE

IMPORTANT:

This section describes implementation progress only. It is not a formal
assessment score.

Q2 KNOWLEDGE BASE / RAG:

Approximately 90-95% complete.

Completed:

* Source dataset
* TXT/PDF/CSV ingestion
* Cleaning and normalization
* PII detection
* Metadata generation
* Document chunking
* 36 total chunks created
* Intentional exclusion of 6 application-data chunks
* 30 knowledge-base chunks indexed
* Local TF-IDF vector store
* Cosine-similarity retrieval
* Top-K retrieval
* Five retrieval evaluation queries
* RAG answer generation
* Source reporting
* Missing-information fallback
* OpenAI API integration
* RAG test cases
* Interactive RAG testing
* Project structure evidence
* Requirements evidence
* Screenshot evidence
* Q2 README
* .env.example
* Technical implementation verification

Remaining for Q2:

* Final documentation review
* Final README review
* Final integration into the overall assessment repository
* Final GitHub packaging and verification

Q1 VOICE AI AGENT:

0% complete.

No Q1 implementation or call recordings are being counted at this stage.

Q3 MULTILINGUAL VOICE BOTS:

0% complete.

No Q3 implementation or localized call evidence is being counted at this
stage.

Q4 REAL-TIME CALL ANALYSIS:

0% complete.

No Q4 implementation or latency measurements are being counted at this
stage.

GITHUB:

0% complete.

The final GitHub repository has not yet been created.

OVERALL ASSESSMENT:

The current work is heavily concentrated on Q2.

Q1, Q3 and Q4 have not yet been implemented.

If the four questions are treated as approximately equal-weight sections,
Q2 being approximately 90-95% complete corresponds to approximately
22.5-23.75% of the four-question implementation work.

This is only a progress estimate, not an official assessment score.

The overall project should therefore NOT be described as completed.

================================================================================
43. KNOWN LIMITATIONS
=====================

STATUS:
DOCUMENTED

Current known Q2 limitations:

1. TF-IDF retrieval is a lightweight retrieval method.
2. The dataset is small and synthetic.
3. Retrieval has not been evaluated on a large benchmark.
4. The current system uses a local vector store rather than a production
   vector database.
5. Live interest-rate information is not available.
6. The prototype does not perform real loan approval.
7. NovaFin is fictional.
8. Business rules are illustrative training data.
9. The current prototype is not a production financial system.
10. Production authentication, monitoring and access control are not
    implemented.

The previously observed difference between 36 created chunks and 30 indexed
chunks has been investigated and verified as intentional filtering of the
6 application_data chunks from sample_application.csv.

================================================================================
44. FUTURE IMPROVEMENTS
=======================

STATUS:
DOCUMENTED

Potential improvements include:

* Embedding-based retrieval.
* Production vector database.
* Metadata filtering.
* Reranking.
* Better retrieval evaluation.
* Better chunking strategy.
* Improved PII redaction.
* Document versioning.
* Automated evaluation.
* Citation-level grounding.
* Live pricing integration.
* Production monitoring.
* Authentication and access control.
* Better multilingual support.
* Production voice infrastructure.

================================================================================
45. FINAL QUALITY CHECK
=======================

STATUS:
IN PROGRESS

Before final submission verify:

[ ] All Python files run without errors.
[YES] Retrieval test currently runs successfully.
[YES] RAG test currently runs successfully.
[YES] No API key is intentionally printed by the implementation.
[YES] .env exists locally and is intended to remain excluded from Git.
[YES] .env.example exists.
[YES] Q2 README is present.
[YES] Screenshots are captured.
[YES] Screenshots reviewed for secrets.
[YES] Test results correspond to recorded prototype runs.
[YES] No fake performance metrics are included.
[YES] No fake call recordings are claimed.
[YES] Incomplete Q1/Q3/Q4 features are marked as not completed.
[YES] NovaFin is clearly identified as fictional.
[ ] Final assessment-level README completed.
[ ] Final Q1-Q4 project structure verified.
[ ] Git initialized at final assessment root.
[ ] Final GitHub repository created.
[ ] Project committed.
[ ] Project pushed to GitHub.
[ ] GitHub repository opens correctly.
[ ] .env verified absent from GitHub.
[ ] API keys verified absent from GitHub.
[ ] Final GitHub URL ready for submission.

================================================================================
46. FINAL SUBMISSION STATUS
===========================

STATUS:
IN PROGRESS

Q2 CORE IMPLEMENTATION:
COMPLETED

Q2 TESTING:
COMPLETED

Q2 TECHNICAL VERIFICATION:
COMPLETED

Q2 SCREENSHOTS:
COMPLETED

Q2 DOCUMENTATION:
IN PROGRESS

Q2 README:
PRESENT / FINAL REVIEW PENDING

Q2 ENVIRONMENT EXAMPLE:
COMPLETED

GITIGNORE:
PRESENT AT FINAL ASSESSMENT PARENT ROOT / FINAL VERIFICATION PENDING

GITHUB:
TODO

Q1:
NOT COMPLETED

Q3:
NOT COMPLETED

Q4:
NOT COMPLETED

================================================================================
47. IMMEDIATE PRIORITIES
========================

STATUS:
HIGH PRIORITY

CURRENT Q2 PRIORITIES:

1. Review the updated Q2 documentation.
2. Verify the Q2 README against the final implementation.
3. Verify the parent-level .gitignore.
4. Verify that .env.example contains placeholders only.
5. Verify that the Q2 project runs successfully one final time.
6. Keep the Q2 backup until documentation is finalized.

IMPORTANT:

Do NOT initialize Git inside q2_knowledge_base.

The final Git repository should be initialized from:

C:\Users\Lenovo\Desktop\Darwix AI

because the final repository is intended to contain Q1, Q2, Q3 and Q4
together.

AFTER Q2 IS FINALIZED:

7. Inspect the assessment requirements for Q1.
8. Begin Q1 voice AI agent implementation.
9. Connect Q1 to the Q2 knowledge base.
10. Implement the required Q1 scenarios.
11. Capture the required Q1 recordings.

THEN:

12. Implement Q3 Philippines localized voice bot.
13. Implement Q3 Indonesia localized voice bot.
14. Capture the required Q3 test evidence.

THEN:

15. Implement Q4 real-time/replay call analysis.
16. Implement signal detection.
17. Implement nudge generation.
18. Implement nudge suppression.
19. Measure latency.
20. Record P50/P95 results.

FINAL STAGE:

21. Create/finalize assessment-level README.
22. Verify final Q1-Q4 directory structure.
23. Initialize Git at the parent assessment directory.
24. Review git status.
25. Verify secrets are ignored.
26. Commit the complete assessment.
27. Create the GitHub repository.
28. Add the remote.
29. Push to GitHub.
30. Verify the final repository.
31. Prepare the final submission URL.

================================================================================
48. FINAL NOTE
==============

STATUS:
DOCUMENTATION

The Q2 implementation demonstrates a functioning prototype knowledge-base
and RAG pipeline.

The current system:

* Loads multiple document formats.
* Cleans source data.
* Performs PII checking.
* Splits documents into chunks.
* Adds metadata to chunks.
* Separates application-data chunks from searchable knowledge chunks.
* Builds a local TF-IDF vector store.
* Performs cosine-similarity retrieval.
* Retrieves top-K context.
* Generates grounded RAG answers.
* Reports source documents.
* Avoids inventing unavailable current pricing.
* Provides a human follow-up path.
* Includes retrieval evaluation tests.
* Includes RAG answer-generation tests.
* Includes interactive RAG testing.
* Includes source attribution.
* Includes evidence screenshots.

The verified chunk counts are:

36 total chunks created
6 application-data chunks excluded
30 knowledge-base chunks indexed

The Q2 retrieval evaluation contains:

5 evaluation queries
5/5 passing the implemented evaluation criteria

This should not be represented as a formal production retrieval benchmark or
as 5/5 top-1 source accuracy.

The current Q2 state is approximately:

90-95% complete

The remaining Q2 work is primarily documentation review and final packaging
into the overall Q1-Q4 assessment repository.

The overall assessment is NOT complete.

Current overall implementation progress is approximately:

Q1: 0%
Q2: 90-95%
Q3: 0%
Q4: 0%

Assuming equal weighting of the four questions, this corresponds to
approximately 22.5-23.75% of the four-question implementation work.

GitHub and final submission packaging are still pending.

The final assessment should only claim functionality that has actually been
implemented, tested and evidenced.

================================================================================
END OF Q2 REPORT
================

================================================================================
CURRENT STATUS - 17 OCTOBER 2026
================================

This section supersedes outdated progress estimates and setup TODOs above.
Historical test logs and notes are retained for traceability.

Q2 RETRIEVAL EVALUATION
-----------------------
Five retrieval queries pass the implemented rule-based checks.
The expected source is ranked first for 4 of the 5 queries (80%).
The document-requirements query retrieves the expected eligibility source
at rank 3, so retrieval ranking still has room for improvement.

These results are a small prototype smoke test, not a production benchmark
or an independent human relevance evaluation.

AUTOMATED TESTS
---------------
The complete repository test suite last passed with:
82 passed in 6.36 seconds.

This result describes the test run on 17 October 2026 and should be updated
if subsequent code changes alter the test outcome.

REPOSITORY STATUS
-----------------
Local Git repository: initialized.
Configured Git remote: origin.
Remote URL: https://github.com/shlokgupta16072005/darwix-ai-engineer-assessment.git

The remote configuration does not, by itself, confirm that the latest local
changes have been pushed or that the remote repository has been verified.

Q1-Q4 ASSESSMENT STATUS
-----------------------
Q1: Prototype and recorded-call evidence exist; a completed live human handoff
    and three distinct recorded test calls have not been established here.
Q2: Knowledge-base pipeline, retrieval, answer generation and automated tests
    are implemented; final evidence and documentation review remain.
Q3: Multilingual prototype and automated tests exist; recorded end-to-end
    calls for both target markets remain to be verified.
Q4: Replay, signal detection, nudges, dashboard and prototype latency evidence
Q4: Replay, signal detection, nudges, dashboard and prototype latency evidence exist; live-stream behavior and production-level latency are not established.

Overall assessment: NOT YET VERIFIED AS COMPLETE.
Final packaging, evidence review and submission readiness remain pending.
Progress percentages are estimates, not official assessment scores.

================================================================================
END OF CURRENT STATUS
=====================

