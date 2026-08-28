"""Scrape https://www.wanikani.com/search results (public page, no API token)."""

import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from cache import cached
from wanikani_api import ONE_HOUR, WanikaniError

SEARCH_URL = "https://www.wanikani.com/search"


class _SearchResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.entries: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        classes = (attr_dict.get("class") or "").split()

        if tag == "a" and "subject-character--grid" in classes:
            subject_type = next(
                (
                    css_class.removeprefix("subject-character--")
                    for css_class in classes
                    if css_class.startswith("subject-character--")
                    and css_class
                    not in (
                        "subject-character--grid",
                        "subject-character--unlocked",
                        "subject-character--locked",
                    )
                ),
                "",
            )
            self._current = {
                "href": attr_dict.get("href") or "",
                "type": subject_type,
                "characters": "",
                "reading": "",
                "meaning": "",
            }
        elif self._current is not None and tag == "span":
            if "subject-character__characters-text" in classes:
                self._capture = "characters"
            elif "subject-character__reading" in classes:
                self._capture = "reading"
            elif "subject-character__meaning" in classes:
                self._capture = "meaning"

    def handle_data(self, data: str) -> None:
        if self._current is not None and self._capture is not None:
            self._current[self._capture] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "span":
            self._capture = None
        elif tag == "a" and self._current is not None:
            for field in ("characters", "reading", "meaning"):
                self._current[field] = self._current[field].strip()
            self.entries.append(self._current)
            self._current = None


def _fetch_html(query: str) -> str:
    url = f"{SEARCH_URL}?{urllib.parse.urlencode({'query': query})}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise WanikaniError(f"WaniKani search returned HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise WanikaniError(f"Could not reach WaniKani: {error.reason}") from error


def search(query: str, ttl_seconds: int = ONE_HOUR) -> list[dict[str, str]]:
    cache_key = f"{SEARCH_URL}?query={query}"
    html = cached(cache_key, ttl_seconds, lambda: _fetch_html(query))
    parser = _SearchResultParser()
    parser.feed(html)
    return parser.entries
