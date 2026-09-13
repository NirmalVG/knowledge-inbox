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