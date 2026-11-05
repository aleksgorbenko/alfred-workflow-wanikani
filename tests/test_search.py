from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

from search import build_items, main
from wanikani_api import WanikaniError

if TYPE_CHECKING:
    import pytest


def test_build_items_formats_radical_without_reading() -> None:
    entries = [
        {
            "href": "https://www.wanikani.com/radicals/substitute",
            "type": "radical",
            "characters": "代",
            "reading": "",
            "meaning": "Substitute",
        }
    ]

    items = build_items(entries)

    assert items[0]["title"] == "代 - Substitute"
    assert items[0]["arg"] == "https://www.wanikani.com/radicals/substitute"
    assert "だい" not in items[0]["subtitle"]


def test_build_items_formats_kanji_with_reading() -> None:
    entries = [
        {
            "href": "https://www.wanikani.com/kanji/%E4%BB%A3",
            "type": "kanji",
            "characters": "代",
            "reading": "だい",
            "meaning": "Substitute",
        }
    ]

    items = build_items(entries)

    assert "だい" in items[0]["subtitle"]


def test_build_items_handles_no_results() -> None:
    items = build_items([])
    assert items[0]["valid"] is False


@patch("search.emit")
def test_main_shows_placeholder_for_empty_query(mock_emit: MagicMock) -> None:
    main([])

    items = mock_emit.call_args[0][0]
    assert items[0]["valid"] is False


HIT = {
    "href": "https://www.wanikani.com/kanji/%E4%BB%A3",
    "type": "kanji",
    "characters": "代",
    "reading": "だい",
    "meaning": "Substitute",
}


def stored_by(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    stored: dict[str, Any] = {}

    def store(_directory: object, query: str, payload: dict[str, Any]) -> None:
        stored[query] = payload

    monkeypatch.setattr("search.finish", store)
    return stored


@patch("search.search")
def test_job_stores_search_results(
    mock_search: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_search.return_value = [HIT]
    stored = stored_by(monkeypatch)
    main(["--job", "substitute"])
    mock_search.assert_called_once_with("substitute")
    assert len(stored["substitute"]["items"]) == 1


@patch("search.search")
def test_job_stores_an_error_row_on_failure(
    mock_search: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_search.side_effect = WanikaniError("boom")
    stored = stored_by(monkeypatch)
    main(["--job", "substitute"])
    assert stored["substitute"]["items"][0]["title"] == "boom"


@patch("search.rows")
def test_job_stores_an_error_row_on_unexpected_failure(
    mock_rows: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_rows.side_effect = RuntimeError("crash")
    stored = stored_by(monkeypatch)
    main(["--job", "substitute"])
    assert stored["substitute"]["items"][0]["title"] == "crash"


def served(*_args: object, **_kwargs: object) -> dict[str, Any]:
    return {"items": [{"title": "x"}]}


def test_main_serves_the_view(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("search.serve", served)
    main(["substitute"])
    assert '"x"' in capsys.readouterr().out


def test_main_labels_the_wait_with_the_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    labels: list[str] = []

    def serve(*_args: object, label: str, **_kwargs: object) -> dict[str, Any]:
        labels.append(label)
        return {"items": []}

    monkeypatch.setattr("search.serve", serve)
    main(["食べる"])
    assert labels == ["Searching WaniKani for '食べる'…"]
