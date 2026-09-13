import uuid
from datetime import datetime, timezone
from app.models.db import get_connection
from app.services.fetcher import fetch_and_extract
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_NOTE_LENGTH = 50_000


def create_item(item_type: str, content: str) -> dict:
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
    """Background pipeline. Steps 5-6 will extend this same function with
    chunking + embedding — the endpoint and DB writes above never change."""
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

        # --- chunking + embedding calls will be inserted here in Steps 5-6 ---

        with get_connection() as conn:
            conn.execute("UPDATE items SET status = 'ready' WHERE id = ?", (item_id,))
        log.info("item_ready")

    except Exception as exc:
        log.error("item_processing_failed", error=str(exc))
        with get_connection() as conn:
            conn.execute(
                "UPDATE items SET status = 'failed', error_reason = ? WHERE id = ?",
                (str(exc), item_id),
            )