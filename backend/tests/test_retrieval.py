from app.services.retrieval import RetrievedChunk, _select_unique_items


def _chunk(chunk_id: str, item_id: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(chunk_id, item_id, item_id, "content", score)


def test_select_unique_items_keeps_only_best_chunk_per_item():
    chunks = [
        _chunk("a-1", "a", 0.99),
        _chunk("a-2", "a", 0.95),
        _chunk("b-1", "b", 0.90),
    ]

    selected = _select_unique_items(chunks)

    assert [chunk.chunk_id for chunk in selected] == ["a-1", "b-1"]
