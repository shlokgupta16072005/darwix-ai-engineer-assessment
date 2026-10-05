# Darwix AI Engineer Assessment

This repository contains my implementation of the Darwix AI Engineer Assessment.

The assessment is organized into four components covering voice interaction, knowledge-base retrieval, multilingual support, and live information retrieval.

> **Current status:** Q2 is implemented and tested. Q1, Q3, and Q4 are currently pending development.

---

## Project Structure

    Darwix AI/
    ├── q1_voice_agent/
    │   └── README.md
    │
    ├── q2_knowledge_base/
    │   ├── data/
    │   │   ├── application_process.txt
    │   │   ├── eligibility_rules.pdf
    │   │   ├── faq.txt
    │   │   ├── loan_products.pdf
    │   │   ├── objection_handling.txt
    │   │   └── sample_application.csv
    │   │
    │   ├── docs/
    │   │   └── q2_test_results.md
    │   │
    │   ├── ingestion/
    │   │   ├── build_kb.py
    │   │   ├── chunker.py
    │   │   ├── cleaner.py
    │   │   ├── document_loader.py
    │   │   └── pii_detector.py
    │   │
    │   ├── retrieval/
    │   │   ├── rag_answer.py
    │   │   ├── search.py
    │   │   ├── test_openai.py
    │   │   ├── test_retrieval.py
    │   │   └── vector_store.py
    │   │
    │   ├── screenshots/
    │   ├── tests/
    │   ├── README.md
    │   └── requirements.txt
    │
    ├── q3_multilingual/
    │   └── README.md
    │
    ├── q4_live_insights/
    │   └── README.md
    │
    ├── recordings/
    ├── docs/
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── requirements.txt

---

## Assessment Status

| Question | Component | Status |
|---|---|---|
| Q1 | Voice Agent | Pending |
| Q2 | Knowledge Base / RAG System | Implemented and tested |
| Q3 | Multilingual Support | Pending |
| Q4 | Live Insights | Pending |

The four components are maintained in a single repository because they form one overall assessment.

---

# Q1 — Voice Agent

**Status:** Pending

The Q1 component will contain the voice-agent implementation required by the assessment.

Planned location:

    q1_voice_agent/

The implementation and documentation will be added as development progresses.

---

# Q2 — Knowledge Base / RAG System

**Status:** Implemented and tested**

Q2 implements a prototype knowledge-base and Retrieval-Augmented Generation (RAG) system for the business-loan qualification domain.

The prototype uses a fictional lender named **NovaFin**.

NovaFin, its loan products, eligibility rules, sample applications, customer questions, and related business information are fictional data created specifically for this assessment prototype.

---

## Q2 Pipeline

The implemented pipeline follows this flow:

    Raw Documents
          |
          v
    Document Loading
          |
          v
    Text Extraction
          |
          v
    Cleaning and Normalization
          |
          v
    PII Detection
          |
          v
    Chunking
          |
          v
    Metadata Creation
          |
          v
    Vectorization
          |
          v
    Local Vector Store
          |
          v
    Similarity Retrieval
          |
          v
    Retrieved Context
          |
          v
    RAG Answer Generation
          |
          v
    Answer + Source Attribution

---

## Q2 Source Dataset

A small and realistic source dataset was created instead of using a large external banking knowledge base.

The dataset contains different types of information.

### Loan Products

    q2_knowledge_base/data/loan_products.pdf

Contains information such as:

- Business loan amount range
- Loan tenure
- Basic product eligibility

### Eligibility Rules

    q2_knowledge_base/data/eligibility_rules.pdf

Contains information such as:

- Minimum business vintage
- Required applicant documents
- Eligibility conditions

### FAQ

    q2_knowledge_base/data/faq.txt

Contains common customer questions and answers.

### Objection Handling

    q2_knowledge_base/data/objection_handling.txt

Contains example customer objections and suggested responses.

### Application Process

    q2_knowledge_base/data/application_process.txt

Contains information about the application and assessment process.

### Sample Application Data

    q2_knowledge_base/data/sample_application.csv

Contains sample structured application records used to demonstrate handling of application data separately from the general knowledge base.

---

## Q2 Document Ingestion

The document loader supports the following source types:

- TXT
- PDF
- CSV

Implementation:

    q2_knowledge_base/ingestion/document_loader.py

The ingestion stage extracts usable text or structured content from source documents before further processing.

---

## Q2 Data Cleaning

The cleaning stage performs basic preprocessing before indexing.

The implemented cleaning process includes:

- Header and footer removal where applicable
- Whitespace normalization
- Duplicate-section removal
- Terminology normalization
- Removal of irrelevant repeated content

Implementation:

    q2_knowledge_base/ingestion/cleaner.py

The goal is to keep the knowledge base focused on useful information rather than indexing navigation text, repeated sections, or unnecessary formatting.

---

## Q2 PII Detection

The pipeline includes a PII-detection stage before content is used for retrieval.

Implementation:

    q2_knowledge_base/ingestion/pii_detector.py

The purpose is to identify potentially sensitive information in source data and reduce the risk of exposing sensitive information through the retrieval pipeline.

---

## Q2 Chunking

Cleaned documents are divided into smaller chunks before vectorization.

Implementation:

    q2_knowledge_base/ingestion/chunker.py

The resulting chunks contain metadata identifying their source document and information needed for retrieval and source attribution.

The current source dataset produces a total of 36 chunks before application-data exclusion from the general knowledge-base index.

---

## Q2 Vector Retrieval

The prototype uses a local TF-IDF based vector representation with cosine similarity.

Implementation:

    q2_knowledge_base/retrieval/vector_store.py

and:

    q2_knowledge_base/retrieval/search.py

The retrieval process:

1. Converts knowledge-base chunks into TF-IDF vectors.
2. Converts the user query into the same vector space.
3. Calculates cosine similarity.
4. Retrieves the most relevant chunks.
5. Passes the retrieved context to the answer-generation layer.

The generated vector-store artifacts are kept local and excluded from Git using `.gitignore`.

---

## Q2 Retrieval Evaluation

A retrieval test suite was created to verify that representative questions retrieve the intended knowledge.

The evaluation covers:

1. Minimum business vintage
2. Required application documents
3. Loan amount range
4. Interest-rate objections
5. One-year business eligibility

Current local evaluation:

**5 / 5 intended retrieval tests passed**

This is a prototype evaluation against the created dataset. It should not be interpreted as a production benchmark or real-world model accuracy measurement.

Detailed results:

    q2_knowledge_base/docs/q2_test_results.md

---

## Q2 RAG Answer Generation

The RAG answer layer uses retrieved context to generate grounded responses.

Implementation:

    q2_knowledge_base/retrieval/rag_answer.py

The answer-generation layer is designed to:

- Use retrieved knowledge as context
- Provide source attribution
- Avoid inventing unsupported information
- State when information is unavailable
- Handle questions requiring information outside the knowledge base
- Avoid presenting unavailable live information as known facts

---

## Q2 Example Test Cases

### Business Vintage

Question:

    What is the minimum business vintage required?

The prototype knowledge base specifies:

    24 months

### Required Documents

Question:

    What documents are required?

The system retrieves eligibility information covering:

- Identity documentation
- PAN or tax identification
- Business proof or registration
- Recent bank statements or financial records

### Live Interest Rate

Question:

    What is today's interest rate?

The prototype does not contain a live pricing feed.

The system therefore avoids inventing a current rate and indicates that live pricing information is unavailable in the current knowledge base.

### One-Year Business

Question:

    My business is only one year old. Can I qualify?

The system retrieves the minimum business-vintage requirement and explains that a one-year business does not meet the 24-month requirement in the prototype dataset.

### Interest-Rate Objection

Question:

    The interest rate is too high. What should I do?

The system retrieves the objection-handling guidance and provides a response based on customer-specific pricing and assessment rather than promising a lower rate.

---

## Q2 Interactive Mode

An interactive RAG mode is included.

It allows a user to enter questions and receive answers based on retrieved knowledge-base context.

Screenshots demonstrating the implementation are available under:

    q2_knowledge_base/screenshots/

---

## Q2 Testing

The Q2 implementation includes tests for:

- Cleaning
- Chunking
- Retrieval

Test files are located under:

    q2_knowledge_base/tests/

Additional retrieval and RAG evaluation scripts are available under:

    q2_knowledge_base/retrieval/

---

# Q3 — Multilingual Support

**Status:** Pending

The Q3 component will contain the multilingual functionality required by the assessment.

Planned location:

    q3_multilingual/

The implementation and documentation will be added as development progresses.

---

# Q4 — Live Insights

**Status:** Pending

The Q4 component will contain the live-insights functionality required by the assessment.

Planned location:

    q4_live_insights/

The implementation and documentation will be added as development progresses.

---

# Environment Setup

The project uses environment variables for configuration where required.

A template is provided at:

    .env.example

The Q2 component also contains:

    q2_knowledge_base/.env.example

Example configuration:

    OPENAI_API_KEY=your_api_key_here
    OPENAI_MODEL=gpt-4o-mini

Replace the placeholder API key locally when required.

**Never commit a real API key or other secret to the repository.**

Actual `.env` files are excluded through `.gitignore`.

---

# Running Q2

From the project root:

    cd q2_knowledge_base

The Q2 ingestion pipeline is available under:

    ingestion/

The retrieval and RAG components are available under:

    retrieval/

Tests are available under:

    tests/

Detailed Q2 implementation and test information is documented in:

    docs/q2_test_results.md

---

# Repository Security

The repository intentionally excludes local secrets and generated artifacts.

The `.gitignore` configuration excludes items such as:

    .env
    .venv/
    __pycache__/
    vector_store/

The repository contains `.env.example` files instead of real API credentials.

---

# Documentation

Detailed Q2 documentation:

    q2_knowledge_base/docs/q2_test_results.md

Q2 screenshots:

    q2_knowledge_base/screenshots/

Q2 component documentation:

    q2_knowledge_base/README.md

---

# Development Status

This repository is being developed incrementally as a single Darwix AI Engineer Assessment project.

Current implementation status:

    Q1  → Pending
    Q2  → Implemented and tested
    Q3  → Pending
    Q4  → Pending

The status will be updated as the remaining assessment components are implemented.

---

# Disclaimer

This repository is an assessment prototype.

The NovaFin lender, loan products, eligibility rules, sample application records, and other business information used in Q2 are fictional and illustrative.

They must not be interpreted as real financial products, real lender policies, or financial advice.