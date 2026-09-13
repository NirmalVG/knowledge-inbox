from app.services.ingestion import derive_title

def test_derive_title_short_note_returns_first_sentence():
    content = "This is a short note. It has a second sentence too."
    assert derive_title(content) == "This is a short note."


def test_derive_title_long_first_sentence_truncates_at_word_boundary():
    long_sentence = "This is a very long first sentence that goes on and on well past the eighty character limit we set for note titles in this application."
    title = derive_title(long_sentence, max_length=80)
    assert len(title) <= 83  # 80 + "..."
    assert title.endswith("...")
    assert not title[:-3].endswith(" ")  # didn't cut mid-word, trailing space stripped


def test_derive_title_no_sentence_boundary_falls_back_to_raw_content():
    content = "just some words with no terminal punctuation"
    assert derive_title(content) == content