import re
from dataclasses import dataclass

TARGET_TOKENS = 300
OVERLAP_RATIO = 0.15
WORDS_PER_TOKEN = 0.75  # ~1.3 tokens per word for English

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

@dataclass
class Chunk:
    index: int
    content: str

def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]

def _word_count(s: str) -> int:
    return len(s.split())

def chunk_text(text: str, target_tokens: int = TARGET_TOKENS, overlap_ratio: float = OVERLAP_RATIO) -> list[Chunk]:
    """Greedy sentence-packing into ~target_tokens chunks with overlap.

    Overlap is achieved by re-including the trailing sentences of the previous
    chunk (by word budget) at the start of the next one, rather than a raw
    character-offset overlap — this keeps overlap sentence-aligned too.
    """
    sentences = split_sentences(text)
    if not sentences:
        return []

    target_words = int(target_tokens * WORDS_PER_TOKEN)
    overlap_words = int(target_words * overlap_ratio)

    chunks: list[Chunk] = []
    current: list[str] = []
    current_words = 0

    for sentence in sentences:
        sentence_words = _word_count(sentence)

        if current_words + sentence_words > target_words and current:
            chunks.append(Chunk(index=len(chunks), content=" ".join(current)))

            # carry over trailing sentences as overlap for the next chunk
            overlap: list[str] = []
            overlap_word_count = 0
            for s in reversed(current):
                w = _word_count(s)
                if overlap_word_count + w > overlap_words:
                    break
                overlap.insert(0, s)
                overlap_word_count += w

            current = overlap
            current_words = overlap_word_count

        current.append(sentence)
        current_words += sentence_words

    if current:
        chunks.append(Chunk(index=len(chunks), content=" ".join(current)))

    return chunks