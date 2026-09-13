from fastapi import APIRouter, Query
from typing import Optional
from app.models.db import get_connection
from app.models.schema import ItemOut

router = APIRouter()

@router.get("/items")
def list_items(status: Optional[str] = Query(default=None)):
    query = "SELECT id, type, title, source_url, status, char_count, created_at, error_reason FROM items"
    params = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return {"items": [dict(row) for row in rows]}