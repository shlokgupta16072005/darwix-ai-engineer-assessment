from pathlib import Path
import os
import re
import sys
from typing import List, Dict


# ============================================================
# PROJECT PATH
# ============================================================

# rag_answer.py is inside:
# q2_knowledge_base/retrieval/rag_answer.py
#
# Therefore:
# parent        = retrieval
# parent.parent = q2_knowledge_base

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORT
# ============================================================

from retrieval.search import search


# ============================================================
# ENVIRONMENT LOADER
# ============================================================

def load_env_file() -> None:
    """
    Load simple KEY=VALUE pairs from the project's .env file.

    The API key is never printed.
    Existing environment variables are not overwritten.
    """

    env_path = PROJECT_ROOT / ".env"

    if not env_path.exists():
        return

    try:
        with open(
            env_path,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                # Ignore empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split(
                    "=",
                    1
                )

                key = key.strip()

                value = (
                    value
                    .strip()
                    .strip('"')
                    .strip("'")
                )

                if key and value:
                    os.environ.setdefault(
                        key,
                        value
                    )

    except Exception:
        # .env loading failure should not crash
        # the retrieval-only fallback system.
        pass


# Load environment variables before using the API.
load_env_file()


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_context(
    results: List[Dict]
) -> str:
    """
    Convert retrieved chunks into a single context block
    for the answer-generation step.
    """

    if not results:
        return ""

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
SOURCE: {result.get('source', 'Unknown')}

CATEGORY: {result.get('category', 'Unknown')}

RELEVANCE SCORE: {result.get('score', 0.0):.4f}

CONTENT:
{result.get('text', '')}
""".strip()
        )

    return "\n\n".join(context_parts)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def contains_any(
    text: str,
    terms: List[str]
) -> bool:
    """
    Return True if any term appears in the text.
    """

    text_lower = text.lower()

    return any(
        term.lower() in text_lower
        for term in terms
    )


def extract_business_vintage(
    results: List[Dict]
) -> str | None:
    """
    Extract the minimum business-vintage requirement
    from retrieved knowledge-base chunks.

    Handles examples such as:
        24 months
        2 years
    """

    context = build_context(results)

    patterns = [
        (
            r"business[-\s]?vintage[^.\n]{0,100}?"
            r"(\d+)\s*(months?|years?)"
        ),

        (
            r"business[^.\n]{0,80}?"
            r"at least\s+(\d+)\s*(months?|years?)"
        ),

        (
            r"operated[^.\n]{0,80}?"
            r"at least\s+(\d+)\s*(months?|years?)"
        ),

        (
            r"minimum[^.\n]{0,80}?"
            r"business[^.\n]{0,80}?"
            r"(\d+)\s*(months?|years?)"
        ),
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            context,
            re.IGNORECASE
        )

        if match:

            number = match.group(1)
            unit = match.group(2)

            return f"{number} {unit}"

    # Final simple fallback
    match = re.search(
        r"(\d+)\s*(months?|years?)"
        r"[^\n]{0,80}"
        r"(?:business|operat)",
        context,
        re.IGNORECASE
    )

    if match:

        return (
            f"{match.group(1)} "
            f"{match.group(2)}"
        )

    return None


def extract_loan_amounts(
    results: List[Dict]
) -> List[str]:
    """
    Extract loan amount values from retrieved context.
    """

    context = build_context(results)

    amounts = []

    patterns = [

        # ₹2,00,000
        r"₹\s*[\d,]+",

        # Rs 2,00,000
        r"\bRs\.?\s*[\d,]+",

        # 2 lakh / 25 lakh
        r"\b\d+(?:\.\d+)?\s*lakhs?\b",

        # 2 crore
        r"\b\d+(?:\.\d+)?\s*crores?\b",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            context,
            re.IGNORECASE
        )

        for match in matches:

            cleaned = " ".join(
                match.split()
            )

            if cleaned not in amounts:
                amounts.append(cleaned)

    return amounts


def extract_document_information(
    results: List[Dict]
) -> List[str]:
    """
    Extract sentences containing common document requirements.
    """

    document_keywords = [
        "identity proof",
        "government-issued identity",
        "pan",
        "tax identification",
        "business proof",
        "business existence",
        "registration",
        "bank statement",
        "financial record",
        "documents",
    ]

    sentences_found = []

    for result in results:

        text = result.get(
            "text",
            ""
        )

        # Split on sentence boundaries and bullet-like structures.
        sentences = re.split(
            r"(?<=[.!?])\s+|(?<=:)\s+",
            text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_lower = sentence.lower()

            if any(
                keyword in sentence_lower
                for keyword in document_keywords
            ):

                if sentence not in sentences_found:
                    sentences_found.append(sentence)

    return sentences_found


# ============================================================
# LOCAL FALLBACK ANSWER
# ============================================================

def fallback_answer(
    question: str,
    results: List[Dict]
) -> str:
    """
    Deterministic knowledge-base-only fallback.

    This function is used when:
    - OpenAI is unavailable
    - API credits are unavailable
    - API package is missing
    - API request fails

    It does NOT invent information.
    """

    if not results:

        return (
            "I could not find relevant information in the "
            "knowledge base. Please contact a human "
            "representative for further assistance."
        )

    best_score = float(
        results[0].get(
            "score",
            0.0
        )
    )

    # Very low retrieval confidence.
    if best_score < 0.05:

        return (
            "I could not find this information in the "
            "knowledge base. I can arrange human "
            "follow-up for this question."
        )

    question_lower = question.lower()

    context = build_context(
        results
    )

    context_lower = context.lower()


    # ========================================================
    # BUSINESS VINTAGE
    # ========================================================

    if (
        "business vintage" in question_lower
        or (
            "business" in question_lower
            and "how old" in question_lower
        )
        or (
            "minimum" in question_lower
            and "business" in question_lower
        )
        or (
            "business" in question_lower
            and "operated" in question_lower
        )
    ):

        vintage = extract_business_vintage(
            results
        )

        if vintage:

            return (
                "The knowledge base states that the "
                f"minimum business vintage requirement is "
                f"{vintage}."
            )


    # ========================================================
    # ONE-YEAR BUSINESS
    # ========================================================

    if (
        "one year" in question_lower
        or "1 year" in question_lower
        or "12 months" in question_lower
        or "only one" in question_lower
    ):

        if (
            "24 months" in context_lower
            or "24-month" in context_lower
        ):

            return (
                "The knowledge base states a minimum "
                "business vintage requirement of 24 months. "
                "Therefore, a business operating for only "
                "one year does not meet that stated "
                "business-vintage requirement."
            )


    # ========================================================
    # LOAN AMOUNT
    # ========================================================

    if (
        "loan amount" in question_lower
        or (
            "minimum" in question_lower
            and "maximum" in question_lower
            and "loan" in question_lower
        )
        or (
            "how much" in question_lower
            and "loan" in question_lower
        )
    ):

        amounts = extract_loan_amounts(
            results
        )

        # Prefer the known Business Growth Loan range
        # when both endpoints are present.

        if (
            "₹2,00,000" in amounts
            and "₹25,00,000" in amounts
        ):

            return (
                "The knowledge base lists the Business "
                "Growth Loan amount as ₹2,00,000 to "
                "₹25,00,000."
            )

        if (
            "2 lakh" in context_lower
            and "25 lakh" in context_lower
        ):

            return (
                "The knowledge base lists the Business "
                "Growth Loan amount as ₹2 lakh to "
                "₹25 lakh."
            )

        if len(amounts) >= 2:

            return (
                "The knowledge base lists the loan amount "
                f"range as {amounts[0]} to {amounts[1]}."
            )


    # ========================================================
    # DOCUMENTS
    # ========================================================

    if contains_any(
        question_lower,
        [
            "document",
            "documents",
            "paperwork",
            "required papers",
        ],
    ):
        document_text = " ".join(
            result.get("text", "")
            for result in results
        )
        document_text_lower = document_text.lower()

        # Handle incomplete-document concerns before listing requirements.
        incomplete_document_phrases = [
            "don't have",
            "do not have",
            "missing",
            "don't have all",
            "do not have all",
            "not have all",
            "incomplete",
        ]

        if any(
            phrase in question_lower
            for phrase in incomplete_document_phrases
        ):
            if (
                "additional documents can be requested"
                in document_text_lower
                or "additional documents may be requested"
                in document_text_lower
            ):
                return (
                    "That's okay for the initial conversation. "
                    "Let me identify which information you already have "
                    "and which items may still be required. "
                    "Additional documents can be requested during assessment."
                )

            return (
                "Let me identify which information you already have "
                "and which items may still be required. "
                "I can arrange human follow-up if you need help "
                "confirming the documentation."
            )

        requirements = []

        if (
            "identity proof" in document_text_lower
            or "government-issued identity" in document_text_lower
        ):
            requirements.append("identity proof")

        if (
            "pan" in document_text_lower
            or "tax identification" in document_text_lower
        ):
            requirements.append(
                "PAN or applicable tax identification information"
            )

        if (
            "business proof" in document_text_lower
            or "business existence" in document_text_lower
            or "registration" in document_text_lower
        ):
            requirements.append(
                "business proof or registration, where applicable"
            )

        if (
            "bank statement" in document_text_lower
            or "financial record" in document_text_lower
        ):
            requirements.append(
                "recent business bank statements or other requested financial records"
            )

        if requirements:
            answer = (
                "Typical requirements mentioned in the knowledge base include "
                + ", ".join(requirements)
                + "."
            )

            if (
                "additional documents may be requested"
                in document_text_lower
                or "additional documents can be requested"
                in document_text_lower
            ):
                answer += (
                    " Additional documents may be requested "
                    "depending on the application."
                )

            return answer

    # ========================================================
    # INTEREST RATE / PRICING
    # ========================================================

    if contains_any(
        question_lower,
        [
            "interest rate",
            "interest",
            "current rate",
            "today's rate",
            "today rate",
            "live rate",
            "pricing",
        ]
    ):

        # If this is specifically the objection-handling
        # question, return the documented response.

        if (
            "too high" in question_lower
            or "high" in question_lower
        ):

            for result in results:

                if result.get(
                    "category"
                ) == "objection_handling":

                    return (
                        "I understand that pricing is an "
                        "important part of the decision. "
                        "The final pricing is customer-specific "
                        "and depends on the application and "
                        "assessment. I can help collect the "
                        "details needed for an assessment, "
                        "or arrange a callback if you want "
                        "to discuss pricing with a representative."
                    )

        return (
            "The knowledge base does not provide a live "
            "or current interest rate. Pricing is "
            "customer-specific and depends on the "
            "application and assessment. I can arrange "
            "human follow-up for current pricing."
        )


    # ========================================================
    # REQUIRED DOCUMENT / BANK STATEMENT OBJECTION
    # ========================================================

    if (
        "bank statement" in question_lower
        and (
            "don't want" in question_lower
            or "do not want" in question_lower
            or "not share" in question_lower
        )
    ):

        return (
            "I understand the concern. Recent financial "
            "records may be requested as part of the "
            "assessment. I can explain the information "
            "currently listed as required, or arrange "
            "human assistance to discuss the documentation."
        )


    # ========================================================
    # GUARANTEED APPROVAL
    # ========================================================

    if (
        "guaranteed approval" in question_lower
        or (
            "guarantee" in question_lower
            and "approval" in question_lower
        )
    ):

        if (
            "no guarantee" in context_lower
            or "final approval" in context_lower
            or "subject to verification" in context_lower
        ):

            return (
                "The knowledge base states that final "
                "approval is subject to verification and "
                "internal assessment, so guaranteed approval "
                "should not be promised."
            )


    # ========================================================
    # HUMAN CALLBACK
    # ========================================================

    if (
        "speak to a person" in question_lower
        or "human" in question_lower
        or "representative" in question_lower
        or "callback" in question_lower
        or "call back" in question_lower
    ):

        return (
            "The knowledge base supports a human "
            "callback or escalation path. I can arrange "
            "human follow-up for this request."
        )


    # ========================================================
    # GENERIC EXTRACTIVE FALLBACK
    # ========================================================

    query_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            question_lower
        )
    )

    candidate_sentences = []

    for result in results:

        text = result.get(
            "text",
            ""
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            words = set(
                re.findall(
                    r"\b[a-zA-Z]{4,}\b",
                    sentence.lower()
                )
            )

            overlap = len(
                query_words.intersection(
                    words
                )
            )

            if overlap > 0:

                candidate_sentences.append(
                    (
                        overlap,
                        sentence
                    )
                )

    candidate_sentences.sort(
        key=lambda item: item[0],
        reverse=True
    )

    if candidate_sentences:

        answer_sentences = []

        for _, sentence in candidate_sentences:

            if sentence not in answer_sentences:

                answer_sentences.append(
                    sentence
                )

            if len(answer_sentences) >= 2:
                break

        return (
            "Based on the available knowledge base: "
            + " ".join(answer_sentences)
        )

    return (
        "I found related information in the knowledge base, "
        "but I could not confidently determine the answer. "
        "I can arrange human follow-up for this question."
    )


# ============================================================
# OPENAI ANSWER GENERATION
# ============================================================

def generate_openai_answer(
    question: str,
    results: List[Dict]
) -> str:
    """
    Generate an answer using OpenAI with retrieved
    knowledge-base context.

    The model is explicitly instructed to use only
    the retrieved context.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    try:

        from openai import OpenAI

    except ImportError:

        raise RuntimeError(
            "OpenAI Python package is not installed. "
            "Install it with: pip install openai"
        )

    context = build_context(
        results
    )

    if not context.strip():

        raise RuntimeError(
            "No knowledge-base context was retrieved."
        )

    client = OpenAI(
        api_key=api_key
    )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini"
    )

    system_prompt = """
You are a business-loan customer support assistant
for a fictional training/prototype system.

You MUST answer using ONLY the supplied knowledge-base
context.

IMPORTANT RULES:

1. Never invent a policy, rule, rate, amount, document,
   eligibility condition, processing time, or product feature.

2. If the answer is not present in the supplied context,
   say clearly that the information is not available in
   the current knowledge base.

3. Do not provide live/current interest rates unless an
   explicit rate is present in the supplied context.

4. Never promise loan approval.

5. Final approval is subject to verification and internal
   assessment when stated by the knowledge base.

6. If the customer needs information that is unavailable,
   offer human follow-up.

7. Keep answers concise and customer-friendly.

8. Do not mention that you are an AI unless the customer
   specifically asks.

9. Do not expose internal relevance scores or retrieval
   implementation details to the customer.

10. Do not use information from your general knowledge when
    it is absent from the supplied knowledge-base context.

11. When the context contains a specific documented
    objection-handling response, use that information
    faithfully rather than inventing a different policy.

12. This is fictional training/prototype content and should
    not be presented as real financial advice.
"""

    user_prompt = f"""
KNOWLEDGE BASE CONTEXT
======================

{context}

CUSTOMER QUESTION
=================

{question}

TASK
====

Answer the customer's question using only the supplied
knowledge-base context.

If the knowledge base does not contain enough information,
say so clearly and offer human follow-up.
"""

    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_prompt
    )

    answer = response.output_text.strip()

    if not answer:

        raise RuntimeError(
            "OpenAI returned an empty answer."
        )

    return answer


# ============================================================
# MAIN RAG FUNCTION
# ============================================================

def answer_question(
    question: str,
    top_k: int = 3
) -> Dict:
    """
    Complete RAG pipeline:

        Question
           ↓
        Retrieval
           ↓
        Retrieved context
           ↓
        OpenAI generation
           ↓
        Local fallback if API unavailable
    """

    question = question.strip()

    if not question:

        return {
            "answer": (
                "Please provide a question."
            ),
            "mode": "validation",
            "sources": []
        }

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    try:

        results = search(
            question,
            top_k=top_k
        )

    except Exception as error:

        return {
            "answer": (
                "The knowledge-base retrieval system "
                "encountered an error. Please try again."
            ),
            "mode": "retrieval_error",
            "sources": [],
            "error": str(error)
        }

    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not results:

        return {
            "answer": (
                "I could not find this information in the "
                "knowledge base. I can arrange human "
                "follow-up for this question."
            ),
            "mode": "retrieval_only",
            "sources": []
        }

    # --------------------------------------------------------
    # OPENAI GENERATION
    # --------------------------------------------------------

    try:

        answer = generate_openai_answer(
            question,
            results
        )

        return {
            "answer": answer,
            "mode": "openai_rag",
            "sources": results
        }

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    except Exception as error:

        error_text = str(
            error
        )

        print(
            "\n[INFO] OpenAI generation unavailable."
        )

        lower_error = error_text.lower()

        if (
            "429" in error_text
            or "quota" in lower_error
            or "insufficient_quota" in lower_error
            or "credit_balance_exhausted" in lower_error
        ):

            print(
                "[INFO] API credits/quota are unavailable."
            )

        elif (
            "api key" in lower_error
            or "api_key" in lower_error
        ):

            print(
                "[INFO] OpenAI API key is not configured "
                "correctly."
            )

        else:

            print(
                f"[INFO] Reason: {error_text}"
            )

        print(
            "[INFO] Using local knowledge-base fallback."
        )

        answer = fallback_answer(
            question,
            results
        )

        return {
            "answer": answer,
            "mode": "local_fallback",
            "sources": results
        }


# ============================================================
# PRINT RESULT
# ============================================================

def print_answer(
    question: str,
    result: Dict
) -> None:
    """
    Print one RAG answer and its sources.
    """

    print(
        "\n" + "=" * 80
    )

    print(
        "Q2 KNOWLEDGE BASE - RAG ANSWER"
    )

    print(
        "=" * 80
    )

    print(
        "\nQuestion:"
    )

    print(
        question
    )

    print(
        "\nAnswer:"
    )

    print(
        result.get(
            "answer",
            ""
        )
    )

    print(
        "\nGeneration mode:"
    )

    print(
        result.get(
            "mode",
            "unknown"
        )
    )

    print(
        "\nSources:"
    )

    sources = result.get(
        "sources",
        []
    )

    if not sources:

        print(
            "No sources found."
        )

        return

    for source in sources:

        print(
            f"- {source.get('source', 'Unknown')} "
            f"("
            f"{source.get('category', 'Unknown')}, "
            f"score="
            f"{source.get('score', 0.0):.4f}"
            f")"
        )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 80
    )

    print(
        "Q2 KNOWLEDGE BASE - RAG SYSTEM"
    )

    print(
        "=" * 80
    )

    print(
        "\nProject root:"
    )

    print(
        PROJECT_ROOT
    )

    print(
        "\nRunning retrieval + answer-generation tests..."
    )

    # --------------------------------------------------------
    # Automated test questions
    # --------------------------------------------------------

    test_questions = [

        "What is the minimum business vintage?",

        "What documents are required to apply for a business loan?",

        "What is today's interest rate?",

        "Can a business that has operated for only one year qualify?",

        "What should I say if the customer thinks the interest rate is too high?",
    ]

    # --------------------------------------------------------
    # Run automated tests
    # --------------------------------------------------------

    for question in test_questions:

        result = answer_question(
            question,
            top_k=3
        )

        print_answer(
            question,
            result
        )

    print(
        "\n" + "=" * 80
    )

    print(
        "RAG TEST COMPLETE"
    )

    print(
        "=" * 80
    )

    # --------------------------------------------------------
    # Interactive question mode
    # --------------------------------------------------------

    print(
        "\nInteractive RAG mode"
    )

    print(
        "Type a question to query the knowledge base."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    print(
        "-" * 80
    )

    while True:

        try:

            question = input(
                "\nAsk a question: "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print(
                "\nExiting interactive mode."
            )

            break

        if question.lower() in {
            "exit",
            "quit"
        }:

            print(
                "\nExiting interactive mode."
            )

            break

        if not question:

            print(
                "Please enter a question."
            )

            continue

        result = answer_question(
            question,
            top_k=3
        )

        print_answer(
            question,
            result
        )