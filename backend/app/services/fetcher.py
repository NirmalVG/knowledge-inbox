import httpx
import trafilatura
from app.core.logging import get_logger

logger = get_logger(__name__)
MAX_CONTENT_LENGTH = 50_000


def _is_readable_text(text: str, threshold: float = 0.9) -> bool:
    """Reject binary garbage that slipped through extraction.

    Checks that at least `threshold` fraction of chars are printable ASCII,
    common Unicode letters, or standard whitespace. Embedding blobs and
    undecoded Brotli payloads fail this check immediately.
    """
    if not text:
        return False
    sample = text[:500]
    # U+FFFD is what Python emits when binary data has been decoded as UTF-8.
    # It is printable, so a printable-only check would let mojibake through.
    if "\ufffd" in sample:
        return False

    printable = sum(1 for c in sample if c.isprintable() or c in "\n\r\t")
    if printable / len(sample) < threshold:
        return False

    # Compressed bytes can occasionally decode to printable Unicode characters.
    # Real prose has a meaningful proportion of letters and whitespace; binary
    # blobs do not. Keep this deliberately permissive for technical docs.
    text_like = sum(1 for c in sample if c.isalpha() or c.isspace())
    return text_like / len(sample) >= 0.35


async def fetch_and_extract(url: str) -> tuple[str, str]:
    """Fetch a URL and extract readable article text. Returns (title, content).

    Note: Accept-Encoding deliberately excludes 'br' (Brotli) because httpx
    cannot decompress it without the optional `brotli` package. If the server
    returns Brotli-compressed content, httpx silently passes raw bytes through
    response.text, producing garbled binary stored as 'content'.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "").lower()
    if content_type and not any(
        media_type in content_type
        for media_type in ("text/html", "application/xhtml+xml")
    ):
        raise ValueError("The URL did not return an HTML page that can be read.")

    html = response.text
    logger.info("url_fetched", url=url, content_length=len(html), encoding=response.encoding)

    extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not extracted:
        raise ValueError("Could not extract readable content from this URL.")

    if not _is_readable_text(extracted):
        raise ValueError(
            "Extracted content appears to be binary or corrupted data, not readable text."
        )

    metadata = trafilatura.extract_metadata(html)
    title = metadata.title if metadata and metadata.title else url

    logger.info("url_extracted", url=url, title=title, text_length=len(extracted))
    return title, extracted[:MAX_CONTENT_LENGTH]
