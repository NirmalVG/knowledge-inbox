import numpy as np
import cohere
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client = cohere.ClientV2(api_key=settings.cohere_api_key)
EMBED_MODEL = "embed-english-v3.0"

def embed_documents(texts: list[str]) -> list[np.ndarray]:
    """Embed chunk texts for storage. Uses input_type='search_document'."""
    if not texts:
        return []
    response = _client.embed(
        texts=texts,
        model=EMBED_MODEL,
        input_type="search_document",
        embedding_types=["float"],
    )
    return [np.array(e, dtype=np.float32) for e in response.embeddings.float_]

def embed_query(text: str) -> np.ndarray:
    """Embed a user's question. Uses input_type='search_query' — deliberately
    different from embed_documents: Cohere v3 embeddings are trained
    asymmetrically for query-vs-document, and using the matching input_type
    is what actually makes cosine similarity meaningful here."""
    response = _client.embed(
        texts=[text],
        model=EMBED_MODEL,
        input_type="search_query",
        embedding_types=["float"],
    )
    return np.array(response.embeddings.float_[0], dtype=np.float32)