import httpx
import trafilatura
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_CONTENT_LENGTH = 50_000


async def fetch_and_extract(url: str) -> tuple[str, str]:
    """Fetch a URL and extract readable article text. Returns (title, content)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    html = response.text
    extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not extracted:
        raise ValueError("Could not extract readable content from this URL.")

    metadata = trafilatura.extract_metadata(html)
    title = metadata.title if metadata and metadata.title else url

    return title, extracted[:MAX_CONTENT_LENGTH]