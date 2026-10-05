# Q2 - Knowledge Base / RAG System

## NovaFin Business Loan Prototype

This project implements Question 2 of the Darwix AI Engineer Assessment.

NovaFin is a fictional lender created only for this prototype. The loan products, eligibility rules, application information, and other business details in this project are synthetic training data and must not be treated as real financial products or policies.


## 1. Objective

The objective of this project is to build a small but realistic Knowledge Base / Retrieval-Augmented Generation (RAG) system for a business-loan qualification use case.

The system demonstrates:

- Loading documents from multiple file formats
- Text extraction
- Data cleaning and normalization
- Duplicate-content handling
- PII detection
- Text chunking
- Metadata creation
- Vector-based retrieval
- Retrieval evaluation
- Grounded answer generation
- Fallback responses when information is unavailable

The system is intentionally kept small because the purpose is to demonstrate the complete RAG pipeline rather than build a production-scale banking knowledge base.


## 2. Project Structure

q2_knowledge_base/
│
├── data/
│   ├── loan_products.pdf
│   ├── eligibility_rules.pdf
│   ├── faq.txt
│   ├── objection_handling.txt
│   ├── application_process.txt
│   └── sample_application.csv
│
├── ingestion/
│   ├── document_loader.py
│   ├── cleaner.py
│   ├── pii_detector.py
│   ├── chunker.py
│   ├── build_kb.py
│   └── __init__.py
│
├── retrieval/
│   ├── vector_store.py
│   ├── search.py
│   ├── test_retrieval.py
│   ├── retrieval_test_results.json
│   ├── rag_answer.py
│   ├── test_openai.py
│   └── __init__.py
│
├── vector_store/
│
├── screenshots/
│
├── docs/
│
├── tests/
│
├── .env
├── .env.example
├── requirements.txt
└── README.md


## 3. Source Dataset

The knowledge base uses a small synthetic dataset containing different types of business information.

### loan_products.pdf

Contains information about the fictional business-loan product, including:

- Loan amount range
- Tenure
- Basic eligibility information

### eligibility_rules.pdf

Contains qualification requirements such as:

- Minimum business vintage
- Required documents
- Basic application requirements

### faq.txt

Contains frequently asked questions and answers related to:

- Approval timelines
- Documentation
- Eligibility
- Application-related questions

### objection_handling.txt

Contains sample customer objections and suggested responses.

Examples include:

- Customer thinks the interest rate is too high
- Customer asks about pricing
- Customer asks about approval certainty

### application_process.txt

Contains the fictional loan application process and the main steps involved.

### sample_application.csv

Contains sample application records used to demonstrate handling of application data.

Application data is treated separately from the searchable knowledge content and is not indexed into the main knowledge vector store.


## 4. Data Ingestion Pipeline

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
Cleaning / Normalization
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
Vector Store
     |
     v
Similarity Retrieval
     |
     v
RAG Answer Generation


## 5. Document Loading

ingestion/document_loader.py loads the supported source files.

The implementation handles:

- PDF documents
- TXT documents
- CSV documents

PDF text is extracted using pypdf.

TXT files are read directly.

CSV data is loaded using pandas.

Each loaded document is represented with information such as:

- Source filename
- File type
- Extracted content
- Basic document metadata


## 6. Data Cleaning

ingestion/cleaner.py performs basic preprocessing before documents are chunked.

The cleaning stage includes:

- Removing unnecessary headers
- Removing unnecessary footers
- Normalizing whitespace
- Removing repeated content
- Removing duplicate sections where detected
- Normalizing common terminology

The goal is to reduce noise before retrieval.

The implementation is intentionally simple and transparent so that each cleaning operation can be inspected and demonstrated.


## 7. PII Detection

ingestion/pii_detector.py checks the extracted document text for common personally identifiable information patterns.

The implementation checks for patterns such as:

- Email addresses
- Phone numbers
- PAN-like identifiers
- Aadhaar-like numeric identifiers
- Other common sensitive identifier patterns

The purpose of this stage is to identify potentially sensitive information before content is added to the searchable knowledge base.

The supplied synthetic dataset was checked during ingestion and did not contain detected PII in the final ingestion results.


## 8. Chunking

ingestion/chunker.py divides cleaned documents into smaller pieces.

Chunking is required because retrieving an entire document for every question would introduce unnecessary context and reduce retrieval precision.

Each chunk contains metadata such as:

- Source document
- Chunk ID
- Category
- Text content

The final ingestion run produced:

Total chunks created: 36

The six chunks generated from sample_application.csv are classified as application data and are intentionally excluded from the searchable knowledge vector store.

Therefore:

36 total chunks
      |
      +-- 6 application-data chunks excluded
      |
      +-- 30 knowledge chunks indexed


## 9. Vector Store

retrieval/vector_store.py creates the searchable vector representation.

The current implementation uses:

- TF-IDF vectorization
- Scikit-learn
- Cosine similarity

The vector store contains the 30 knowledge chunks after excluding application-data chunks.

The resulting vector vocabulary contains approximately 1,520 terms for the current synthetic dataset.

The vector store is saved in the local:

vector_store/

directory.


## 10. Retrieval

retrieval/search.py performs similarity-based retrieval.

For a user question:

1. The query is converted into the same TF-IDF representation.
2. Similarity is calculated against the indexed knowledge chunks.
3. The highest-scoring relevant chunks are returned.
4. The retrieved chunks are passed to the answer-generation stage.

The retrieval system returns source information along with the retrieved content so that the generated answer can be grounded in the knowledge base.


## 11. Retrieval Testing

Retrieval tests are implemented in:

retrieval/test_retrieval.py

The test set covers different information categories rather than testing only one type of question.

Examples include:

- Minimum business vintage
- Required application documents
- Loan product information
- Application process
- Customer objections
- Questions that should not have a supported answer

The retrieval results are saved in:

retrieval/retrieval_test_results.json

This provides evidence that the retrieval layer can locate relevant knowledge from the synthetic dataset.


## 12. RAG Answer Generation

retrieval/rag_answer.py combines retrieval with answer generation.

The process is:

User Question
     |
     v
Retrieve relevant chunks
     |
     v
Build context
     |
     v
Generate grounded answer
     |
     v
Return answer + sources

The OpenAI API can be used for answer generation.

The configured model is:

gpt-4o-mini

The model is instructed to answer only using the supplied knowledge-base context.

The prompt specifically prevents the system from:

- Inventing loan policies
- Inventing eligibility rules
- Inventing interest rates
- Guaranteeing loan approval
- Claiming unsupported business information as fact


## 13. Environment Configuration

The actual API key is stored locally in:

.env

The .env file must never be committed to GitHub.

A safe template is provided as:

.env.example

Example:

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

To configure the project locally, create a .env file containing the user's own API key.

Do not place real API keys inside source code.


## 14. Fallback Handling

A key requirement of the system is to avoid inventing information when the knowledge base does not contain an answer.

The system therefore includes fallback handling.

For example, if a user asks:

"What is today's interest rate?"

the system does not invent a current rate.

Instead, it explains that the current live rate is not available in the knowledge base and recommends human follow-up.

Similarly, questions such as:

"Can you guarantee that my loan will be approved?"

are not answered with an approval guarantee.

The system explains that final approval is subject to verification and internal assessment.

Out-of-scope questions also trigger an appropriate fallback rather than fabricated information.


## 15. Example RAG Questions

The following types of questions were tested.

### Question 1

What is the minimum business vintage?

Expected knowledge:

24 months of continuous operation.


### Question 2

What documents are required?

The answer is grounded in the eligibility and application information contained in the knowledge base.


### Question 3

What is today's interest rate?

The system should not invent a current rate because the synthetic knowledge base does not contain live pricing information.


### Question 4

Can a business that has operated for only one year qualify?

The system uses the minimum business-vintage requirement from the knowledge base.


### Question 5

What should I say if the customer thinks the interest rate is too high?

The system retrieves the relevant objection-handling information and provides a grounded response.


## 16. Unsupported Information

The system was also tested with questions outside the knowledge base.

For example:

"What is the weather in Mumbai today?"

The knowledge base does not contain live weather information.

The system therefore returns a fallback response rather than attempting to answer using unrelated information.

This demonstrates the difference between:

Known information

and:

Unavailable / out-of-scope information.


## 17. Design Decision: Application Data

The sample application CSV is intentionally not included in the main searchable knowledge vector store.

This separation is useful because:

- General business knowledge can be searched independently.
- Customer/application records should not automatically become general knowledge.
- It reduces the chance of exposing application-specific information through normal knowledge retrieval.
- It keeps the knowledge base focused on policies, products, FAQs, and processes.

For this prototype, the application CSV is therefore processed during ingestion but excluded from the searchable knowledge index.


## 18. Security Considerations

This project uses fictional training data.

Nevertheless, the implementation demonstrates basic security practices:

- API keys are stored in .env
- .env should not be committed
- .env.example contains only placeholders
- PII detection is performed during ingestion
- Application data is separated from general knowledge
- The RAG prompt is designed to prevent unsupported claims

No real customer banking information should be placed into this prototype.


## 19. How to Run

### Step 1: Activate the virtual environment

From the project directory:

.venv\Scripts\Activate.ps1

If the environment is already active, the terminal will show:

(.venv)


### Step 2: Install dependencies

pip install -r requirements.txt


### Step 3: Configure the environment

Create:

.env

with:

OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-4o-mini

Do not share or commit the actual API key.


### Step 4: Run the ingestion pipeline

From the project root:

py ingestion/build_kb.py

The ingestion pipeline performs:

Load
  ↓
Clean
  ↓
PII detection
  ↓
Chunk
  ↓
Metadata


### Step 5: Build the vector store

Run:

py retrieval/vector_store.py

This creates the TF-IDF based searchable vector store.


### Step 6: Run retrieval tests

Run:

py retrieval/test_retrieval.py

The results are saved to:

retrieval/retrieval_test_results.json


### Step 7: Run RAG answers

Run:

py retrieval/rag_answer.py

The program enters interactive mode.

Example:

Ask a question:

Enter a question and the system retrieves relevant context and generates a grounded response.

Type:

exit

to leave interactive mode.


## 20. Main Components

File                         Purpose
----------------------------------------------------------------
document_loader.py           Loads PDF, TXT and CSV documents
cleaner.py                   Cleans and normalizes text
pii_detector.py              Detects common PII patterns
chunker.py                   Splits documents into chunks and adds metadata
build_kb.py                  Runs the ingestion pipeline
vector_store.py              Creates the TF-IDF vector store
search.py                    Retrieves relevant chunks
test_retrieval.py            Tests retrieval quality
rag_answer.py                Generates grounded RAG answers
retrieval_test_results.json  Stores retrieval test results


## 21. Evidence / Screenshots

The project includes screenshots demonstrating the main stages of the Q2 implementation.

Evidence covers:

1. Document loading
2. Cleaning and normalization
3. PII detection
4. Chunk creation
5. Vector-store creation
6. Retrieval testing
7. RAG answer generation
8. Fallback and out-of-scope handling

The screenshots are stored under:

screenshots/


## 22. Limitations

This is a prototype implementation and not a production banking system.

Current limitations include:

- The dataset is small and synthetic.
- NovaFin is fictional.
- TF-IDF is used instead of a production embedding model.
- The vector store is local.
- No production database is used.
- No live banking or financial data is connected.
- Current interest rates and other real-time information are not available.
- PII detection is pattern-based and should not be considered a complete production privacy solution.
- The RAG system should not be used to make real lending decisions.


## 23. Future Improvements

Possible improvements include:

- Using a production-grade embedding model
- Using a managed vector database
- Adding hybrid keyword + semantic retrieval
- Adding reranking
- Adding document versioning
- Adding stronger PII redaction
- Adding evaluation metrics such as retrieval precision and recall
- Adding automated regression tests
- Adding source citation formatting
- Connecting the knowledge base to the Q1 voice agent


## 24. Summary

This Q2 implementation demonstrates a complete small-scale RAG pipeline:

Multiple Documents
       ↓
Document Loading
       ↓
Cleaning
       ↓
PII Detection
       ↓
Chunking + Metadata
       ↓
TF-IDF Vectorization
       ↓
Vector Store
       ↓
Similarity Retrieval
       ↓
Grounded Answer Generation
       ↓
Fallback for Unsupported Information

The implementation focuses on traceability and correctness rather than building an unnecessarily large knowledge base.

NovaFin, its products, rules, and application data are fictional and exist only for this assessment prototype.