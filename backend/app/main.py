import uuid
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.models.db import init_db
from app.exceptions import AppError
from app.api.routes.ingest import router as ingest_router
from app.api.routes.query import router as query_router
from app.api.routes.items import router as items_router

configure_logging(settings.log_level)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("startup_complete", database_path=settings.database_path)
    yield
    logger.info("shutdown_complete")

app = FastAPI(title="Knowledge Inbox API", lifespan=lifespan)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(items_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    structlog.contextvars.clear_contextvars()
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    body = {"error": {"code": exc.code, "message": exc.message}}
    if exc.details:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=body)


@app.get("/health")
def health():
    return {"status": "ok"}