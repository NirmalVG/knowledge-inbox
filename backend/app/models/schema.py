from pydantic import BaseModel
from typing import Literal, Optional

class IngestRequest(BaseModel):
    type: Literal["note", "url"]
    content: str

class ItemOut(BaseModel):
    id: str
    type: str
    status: str
    created_at: str

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4


class SourceOut(BaseModel):
    ref: int
    item_id: str
    item_title: str
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceOut]