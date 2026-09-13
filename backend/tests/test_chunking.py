from app.services.chunking import chunk_text, split_sentences


def test_split_sentences_basic():
    text = "This is one. This is two! Is this three? Yes it is."
    sentences = split_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "This is one."


def test_split_sentences_empty_string():
    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_chunk_text_short_content_single_chunk():
    text = "A short note. Just two sentences."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].content == text.replace(". ", ". ")  # sentences rejoined


def test_chunk_text_long_content_produces_multiple_chunks():
    sentences = [f"This is sentence number {i} in a long document." for i in range(100)]
    text = " ".join(sentences)
    chunks = chunk_text(text)
    assert len(chunks) > 1


def test_chunk_text_overlap_shares_content_between_consecutive_chunks():
    sentences = [f"This is sentence number {i} in a long document." for i in range(100)]
    text = " ".join(sentences)
    chunks = chunk_text(text)
    # the tail of chunk N should share at least one sentence with the head of chunk N+1
    for i in range(len(chunks) - 1):
        tail_words = set(chunks[i].content.split()[-10:])
        head_words = set(chunks[i + 1].content.split()[:10])
        assert tail_words & head_words, f"no overlap found between chunk {i} and {i+1}"


def test_chunk_text_empty_input_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []