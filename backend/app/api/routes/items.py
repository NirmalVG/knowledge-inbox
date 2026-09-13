from fastapi import APIRouter, Query, Response
from typing import Optional
from app.models.db import get_connection
from app.models.schema import ItemOut
from app.core.logging import get_logger
from app.exceptions import AppError

logger = get_logger(__name__)
router = APIRouter()


@router.get("/items")
def list_items(status: Optional[str] = Query(default=None)):
    query = """SELECT id, type, title, source_url, status, char_count, created_at, error_reason,
                      SUBSTR(raw_content, 1, 200) as preview
               FROM items"""
    params = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return {"items": [dict(row) for row in rows]}


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str):
    """Delete an item and its associated chunks (cascade)."""
    logger.info("deleting_item", item_id=item_id)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        if cursor.rowcount == 0:
            logger.warning("item_not_found", item_id=item_id)
            raise AppError("NOT_FOUND", f"Item '{item_id}' not found", 404)
    logger.info("item_deleted", item_id=item_id)
    return Response(status_code=204)