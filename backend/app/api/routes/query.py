from fastapi import APIRouter
from app.models.schema import QueryRequest, QueryResponse
from app.models.db import get_connection
from app.services.retrieval import retrieve
from app.services.generation import generate_answer
from app.exceptions import EmptyQuestionError, NoContentError, UpstreamUnavailableError
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

NO_CONTEXT_ANSWER = "I don't have enough information in your saved content to answer that."


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    question = payload.question.strip()
    if not question:
        raise EmptyQuestionError()

    with get_connection() as conn:
        ready_count = conn.execute(
            "SELECT COUNT(*) as n FROM items WHERE status = 'ready'"
        ).fetchone()["n"]
    if ready_count == 0:
        raise NoContentError()

    chunks = retrieve(question)
    if not chunks:
        return QueryResponse(answer=NO_CONTEXT_ANSWER, sources=[])

    try:
        result = generate_answer(question, chunks)
    except Exception as exc:
        logger.error("generation_failed", error=str(exc))
        raise UpstreamUnavailableError(str(exc))

    return QueryResponse(**result)