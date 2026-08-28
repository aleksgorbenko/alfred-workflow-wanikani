from unittest.mock import patch

import pytest
from wanikani_api import WanikaniError
from wanikani_search import _SearchResultParser, search

_RADICAL_CLASSES = (
    "subject-character subject-character--radical "
    "subject-character--grid subject-character--unlocked"
)
_KANJI_CLASSES = (
    "subject-character subject-character--kanji "
    "subject-character--grid subject-character--unlocked"
)

SAMPLE_HTML = f"""
<a class="{_RADICAL_CLASSES}" title="Substitute" href="https://www.wanikani.com/radicals/substitute">
  <div class="subject-character__content">
    <span class="subject-character__characters">
      <span class="subject-character__characters-text" lang="ja">
        代
      </span>
    </span>
      <div class="subject-character__info">
        <span class="subject-character__meaning">Substitute</span>
      </div>
  </div>
</a>
<a class="{_KANJI_CLASSES}" title="だい" href="https://www.wanikani.com/kanji/%E4%BB%A3">
  <div class="subject-character__content">
    <span class="subject-character__characters">
      <span class="subject-character__characters-text" lang="ja">
        代
      </span>
    </span>
      <div class="subject-character__info">
        <span class="subject-character__reading">だい</span>
        <span class="subject-character__meaning">Substitute</span>
      </div>
  </div>
</a>
"""


def test_parses_radical_and_kanji_entries():
    parser = _SearchResultParser()
    parser.feed(SAMPLE_HTML)

    expected_count = 2
    assert len(parser.entries) == expected_count

    radical, kanji = parser.entries
    assert radical == {
        "href": "https://www.wanikani.com/radicals/substitute",
        "type": "radical",
        "characters": "代",
        "reading": "",
        "meaning": "Substitute",
    }
    assert kanji == {
        "href": "https://www.wanikani.com/kanji/%E4%BB%A3",
        "type": "kanji",
        "characters": "代",
        "reading": "だい",
        "meaning": "Substitute",
    }


@patch("wanikani_search._fetch_html")
def test_search_returns_parsed_entries(mock_fetch_html):
    mock_fetch_html.return_value = SAMPLE_HTML

    entries = search("substitute")

    expected_count = 2
    assert len(entries) == expected_count
    mock_fetch_html.assert_called_once_with("substitute")


@patch("wanikani_search._fetch_html")
def test_search_propagates_wanikani_error(mock_fetch_html):
    mock_fetch_html.side_effect = WanikaniError("boom")

    with pytest.raises(WanikaniError, match="boom"):
        search("substitute")
