from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.models.db import init_db

configure_logging(settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title="Knowledge Inbox API")

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("startup_complete", database_path=settings.database_path)

@app.get("/health")
def health():
    return {"status": "ok"}