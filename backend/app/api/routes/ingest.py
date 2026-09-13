from fastapi import APIRouter, BackgroundTasks
from urllib.parse import urlparse
from app.models.schema import IngestRequest, ItemOut
from app.services.ingestion import create_item, process_item, MAX_NOTE_LENGTH
from app.exceptions import EmptyContentError, InvalidURLError, ContentTooLargeError

router = APIRouter()

def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if not (parsed.scheme in ("http", "https") and parsed.netloc):
        raise InvalidURLError(url)

@router.post("/ingest", response_model=ItemOut, status_code=202)
async def ingest(payload: IngestRequest, background_tasks: BackgroundTasks):
    content = payload.content.strip()

    if not content:
        raise EmptyContentError()
    if len(content) > MAX_NOTE_LENGTH:
        raise ContentTooLargeError(MAX_NOTE_LENGTH)
    if payload.type == "url":
        _validate_url(content)

    item = create_item(payload.type, content)
    background_tasks.add_task(process_item, item["id"], payload.type, content)
    return item