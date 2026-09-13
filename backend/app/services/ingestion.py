import uuid
from datetime import datetime, timezone

from app.models.db import get_connection, serialize_embedding
from app.services.fetcher import fetch_and_extract
from app.services.chunking import chunk_text
from app.services.embeddings import embed_documents
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_NOTE_LENGTH = 50_000


def create_item(item_type: str, content: str) -> dict:
    """Insert a new item row immediately (status='processing') so the client
    gets a fast response. Actual content extraction / chunking / embedding
    happens afterward in process_item(), run as a background task."""
    item_id = f"itm_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """INSERT INTO items (id, type, title, source_url, raw_content, status, char_count, created_at)
               VALUES (?, ?, ?, ?, ?, 'processing', ?, ?)""",
            (
                item_id,
                item_type,
                content if item_type == "note" else None,
                content if item_type == "url" else None,
                content if item_type == "note" else None,
                len(content) if item_type == "note" else 0,
                now,
            ),
        )
    return {"id": item_id, "type": item_type, "status": "processing", "created_at": now}


async def process_item(item_id: str, item_type: str, source: str) -> None:
    """Background pipeline: (1) resolve raw content — fetch+extract for URLs,
    read back for notes — (2) chunk it, (3) embed the chunks, (4) persist
    chunks+embeddings, (5) flip status to ready. Any failure at any stage
    marks the item 'failed' with a human-readable error_reason instead of
    leaving it stuck or crashing the process."""
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