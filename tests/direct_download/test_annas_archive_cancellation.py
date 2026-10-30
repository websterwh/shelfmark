from threading import Event

from shelfmark.release_sources import BrowseRecord


def test_fetch_aa_page_urls_passes_cancellation_to_detail_fetch(monkeypatch):
    from shelfmark.release_sources.direct_download import annas_archive

    cancel_flag = Event()
    status_callback = lambda _status, _message: None
    captured: dict[str, object] = {}

    def fake_get_book_info(book_id, **kwargs):
        captured["book_id"] = book_id
        captured.update(kwargs)
        return BrowseRecord(
            id=book_id,
            title="Book",
            source="direct_download",
            download_urls=["https://example.com/slow_download/book"],
        )

    monkeypatch.setattr(annas_archive, "get_book_info", fake_get_book_info)
    monkeypatch.setitem(annas_archive._url_source_types, "https://example.com/slow_download/book", "aa-slow")

    urls_by_source: dict[str, list[str]] = {}
    annas_archive._fetch_aa_page_urls(
        BrowseRecord(id="book", title="Book", source="direct_download"),
        urls_by_source,
        cancel_flag,
        status_callback,
    )

    assert captured == {
        "book_id": "book",
        "fetch_download_count": False,
        "cancel_flag": cancel_flag,
        "status_callback": status_callback,
    }
    assert urls_by_source == {"aa-slow": ["https://example.com/slow_download/book"]}
