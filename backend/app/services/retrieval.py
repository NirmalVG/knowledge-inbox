import cohere
import numpy as np
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db import get_connection, deserialize_embedding
from app.services.embeddings import embed_query

logger = get_logger(__name__)

_client = cohere.ClientV2(api_key=settings.cohere_api_key)
RERANK_MODEL = "rerank-english-v3.0"

RECALL_TOP_K = 20
FINAL_TOP_K = 4
MIN_RERANK_SCORE = 0.15  # floor below which we treat retrieval as "no relevant content"


@dataclass
class RetrievedChunk:
    chunk_id: str
    item_id: str
    item_title: str
    content: str
    score: float


def _cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    """query_vec: (d,), doc_vecs: (n, d) -> returns (n,) similarity scores."""
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-8)
    return doc_norms @ query_norm


def _recall(question: str) -> list[dict]:
    """Stage 1: cheap, wide cosine-similarity scan over every stored chunk."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT chunks.id as chunk_id, chunks.item_id, chunks.content, chunks.embedding,
                      items.title as item_title
               FROM chunks JOIN items ON items.id = chunks.item_id
               WHERE items.status = 'ready'"""
        ).fetchall()

    if not rows:
        return []

    query_vec = embed_query(question)
    doc_vecs = np.stack([deserialize_embedding(row["embedding"]) for row in rows])
    scores = _cosine_similarity(query_vec, doc_vecs)

    ranked_indices = np.argsort(-scores)[:RECALL_TOP_K]
    return [
        {
            "chunk_id": rows[i]["chunk_id"],
            "item_id": rows[i]["item_id"],
            "item_title": rows[i]["item_title"],
            "content": rows[i]["content"],
            "recall_score": float(scores[i]),
        }
        for i in ranked_indices
    ]


def _rerank(question: str, candidates: list[dict]) -> list[RetrievedChunk]:
    """Stage 2: precise cross-attention reranking, only over the recall candidates."""
    if not candidates:
        return []

    response = _client.rerank(
        model=RERANK_MODEL,
        query=question,
        documents=[c["content"] for c in candidates],
        top_n=min(FINAL_TOP_K, len(candidates)),
    )

    results = []
    for r in response.results:
        c = candidates[r.index]
        results.append(
            RetrievedChunk(
                chunk_id=c["chunk_id"],
                item_id=c["item_id"],
                item_title=c["item_title"],
                content=c["content"],
                score=r.relevance_score,
            )
        )
    return results


def retrieve(question: str) -> list[RetrievedChunk]:
    """Two-stage retrieval: cosine recall (top 20) -> Cohere rerank (top 4).
    Returns [] if nothing scores above MIN_RERANK_SCORE, signaling the caller
    should short-circuit rather than hallucinate an answer from weak context."""
    candidates = _recall(question)
    reranked = _rerank(question, candidates)

    strong_results = [r for r in reranked if r.score >= MIN_RERANK_SCORE]
    logger.info(
        "retrieval_complete",
        candidate_count=len(candidates),
        reranked_count=len(reranked),
        strong_count=len(strong_results),
    )
    return strong_results