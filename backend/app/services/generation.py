from groq import Groq
from app.core.config import settings
from app.core.logging import get_logger
from app.services.retrieval import RetrievedChunk

logger = get_logger(__name__)
_client = Groq(api_key=settings.groq_api_key)

# llama-3.3-70b-versatile has been deprecated on Groq since this project's
# original design — confirmed via GET /openai/v1/models against this account.
# openai/gpt-oss-120b was the documented fallback (see PRD §3.6) and is now
# the primary model: 131k context, active, priced for free-tier use.
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a precise assistant answering questions using ONLY the numbered \
sources provided below. Follow these rules strictly:

1. Answer only using information contained in the sources. Do not use outside knowledge.
2. If the sources do not contain enough information to answer, say exactly: \
"I don't have enough information in your saved content to answer that."
3. When you use a fact from a source, cite it inline using PLAIN ASCII square brackets \
around the source number only — for example: [1] or [2]. Do NOT use fullwidth brackets, \
parentheses, or any other citation style.
4. Be concise and direct. Do not restate the question."""


def _build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[Source {i + 1}] (from: {c.item_title})\n{c.content}"
        for i, c in enumerate(chunks)
    )


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> dict:
    """Builds a grounded prompt from retrieved chunks and calls Groq.
    Citation mapping (ref number -> actual item/chunk) is done here,
    server-side and deterministically -- never trusted to the LLM's
    free-text output."""
    context = _build_context(chunks)
    user_prompt = f"Sources:\n\n{context}\n\nQuestion: {question}"

    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    answer = response.choices[0].message.content

    sources = [
        {
            "ref": i + 1,
            "item_id": c.item_id,
            "item_title": c.item_title,
            "snippet": c.content[:200],
            "score": round(c.score, 3),
        }
        for i, c in enumerate(chunks)
    ]

    logger.info("answer_generated", chunk_count=len(chunks), answer_length=len(answer))
    return {"answer": answer, "sources": sources}