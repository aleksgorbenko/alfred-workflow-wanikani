from unittest.mock import patch

from search import build_items, main
from wanikani_api import WanikaniError


def test_build_items_formats_radical_without_reading():
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


def test_build_items_formats_kanji_with_reading():
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


def test_build_items_handles_no_results():
    items = build_items([])
    assert items[0]["valid"] is False


@patch("search.emit")
def test_main_shows_placeholder_for_empty_query(mock_emit):
    main([])

    items = mock_emit.call_args[0][0]
    assert items[0]["valid"] is False


@patch("search.search")
@patch("search.emit")
def test_main_emits_search_results(mock_emit, mock_search):
    mock_search.return_value = [
        {
            "href": "https://www.wanikani.com/kanji/%E4%BB%A3",
            "type": "kanji",
            "characters": "代",
            "reading": "だい",
            "meaning": "Substitute",
        }
    ]

    main(["substitute"])

    mock_search.assert_called_once_with("substitute")
    items = mock_emit.call_args[0][0]
    expected_count = 1
    assert len(items) == expected_count


@patch("search.search")
@patch("search.emit")
def test_main_emits_error_on_failure(mock_emit, mock_search):
    mock_search.side_effect = WanikaniError("boom")

    main(["substitute"])

    items = mock_emit.call_args[0][0]
    assert items[0]["valid"] is False
