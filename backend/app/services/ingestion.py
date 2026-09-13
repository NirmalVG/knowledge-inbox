import uuid
from datetime import datetime, timezone

from app.models.db import get_connection, serialize_embedding
from app.services.fetcher import fetch_and_extract
from app.services.chunking import chunk_text, split_sentences
from app.services.embeddings import embed_documents
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_NOTE_LENGTH = 50_000
TITLE_MAX_LENGTH = 80


def derive_title(content: str, max_length: int = TITLE_MAX_LENGTH) -> str:
    """Short, human-readable title for a note: first sentence, truncated at
    a word boundary if still too long. URL items get their real page title
    from fetch_and_extract() instead — this is note-only."""
    sentences = split_sentences(content)
    first = sentences[0] if sentences else content
    if len(first) <= max_length:
        return first
    return first[:max_length].rsplit(" ", 1)[0] + "..."


def create_item(item_type: str, content: str) -> dict:
    item_id = f"itm_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    title = derive_title(content) if item_type == "note" else None

    with get_connection() as conn:
        conn.execute(
            """INSERT INTO items (id, type, title, source_url, raw_content, status, char_count, created_at)
               VALUES (?, ?, ?, ?, ?, 'processing', ?, ?)""",
            (
                item_id,
                item_type,
                title,
                content if item_type == "url" else None,
                content if item_type == "note" else None,
                len(content) if item_type == "note" else 0,
                now,
            ),
        )
    return {"id": item_id, "type": item_type, "status": "processing", "created_at": now}


async def process_item(item_id: str, item_type: str, source: str) -> None:
    log = logger.bind(item_id=item_id, item_type=item_type)
    try:
        if item_type == "url":
            title, content = await fetch_and_extract(source)
            with get_connection() as conn:
                conn.execute(
                    "UPDATE items SET title = ?, raw_content = ?, char_count = ? WHERE id = ?",
                    (title, content, len(content), item_id),
                )
            log.info("url_fetched", char_count=len(content))
        else:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT raw_content FROM items WHERE id = ?", (item_id,)
                ).fetchone()
            content = row["raw_content"]

        chunks = chunk_text(content)
        if not chunks:
            raise ValueError("No content to chunk after extraction.")

        embeddings = embed_documents([c.content for c in chunks])
        log.info("chunks_embedded", chunk_count=len(chunks))

        with get_connection() as conn:
            for chunk, embedding in zip(chunks, embeddings):
                conn.execute(
                    """INSERT INTO chunks (id, item_id, chunk_index, content, embedding)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        f"chk_{uuid.uuid4().hex[:12]}",
                        item_id,
                        chunk.index,
                        chunk.content,
                        serialize_embedding(embedding),
                    ),
                )
            conn.execute("UPDATE items SET status = 'ready' WHERE id = ?", (item_id,))
        log.info("item_ready")

    except Exception as exc:
        log.error("item_processing_failed", error=str(exc))
        with get_connection() as conn:
            conn.execute(
                "UPDATE items SET status = 'failed', error_reason = ? WHERE id = ?",
                (str(exc), item_id),
            )