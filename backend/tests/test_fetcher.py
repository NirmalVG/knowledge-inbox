from app.services.fetcher import _is_readable_text


def test_readable_text_accepts_normal_prose():
    assert _is_readable_text("Next.js caching lets you control how route data is reused.")


def test_readable_text_rejects_mojibake_with_replacement_characters():
    assert not _is_readable_text("0 $\ufffd\ufffd\ufffd,\ufffd\ufffd\ufffd\u02bf\ufffd\ufffdGX\ufffd\ufffd\ufffd7{y8@$nt")


def test_readable_text_rejects_printable_binary_like_data():
    assert not _is_readable_text("@#$%~^|`<>[]{};:+=*/" * 20)
