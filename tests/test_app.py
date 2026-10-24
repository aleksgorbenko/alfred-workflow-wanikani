from typing import Any

from app import (
    LOADING_RERUN_SECONDS,
    NO_TOKEN,
    PAGES,
    STALE_RERUN_SECONDS,
    Deps,
    refresh,
    run,
)
from pages import PageHit
from wanikani_api import WanikaniError

ROWS: list[dict[str, Any]] = [
    {"title": "大 - big", "subtitle": "W1・Kanji", "valid": True},
    {"title": "小 - small", "subtitle": "W1・Kanji", "valid": True},
]


class FakePages:
    def __init__(
        self, stored: dict[str, dict[str, Any]], *, stale: bool = False
    ) -> None:
        self.stored = stored
        self.stale = stale
        self.claimed: set[str] = set()
        self.released: list[str] = []

    def read(self, name: str, max_age_seconds: int) -> PageHit | None:
        del max_age_seconds
        data = self.stored.get(name)
        return None if data is None else PageHit(data, self.stale)

    def write(self, name: str, data: dict[str, Any]) -> None:
        self.stored[name] = data

    def claim_refresh(self, name: str) -> bool:
        if name in self.claimed:
            return False
        self.claimed.add(name)
        return True

    def release_refresh(self, name: str) -> None:
        self.claimed.discard(name)
        self.released.append(name)


def _rows(_token: str) -> list[dict[str, Any]]:
    return ROWS


def _fails(_token: str) -> list[dict[str, Any]]:
    message = "API down"
    raise WanikaniError(message)


def _crashes(_token: str) -> list[dict[str, Any]]:
    message = "unexpected"
    raise ValueError(message)


def cached_pages() -> FakePages:
    return FakePages({name: {"rows": ROWS} for name in PAGES})


def deps(
    pages: FakePages | None = None,
    account: str = "account",
    refreshed: list[str] | None = None,
) -> Deps:
    loaders = dict.fromkeys(PAGES, _rows) | {"stats": _fails, "levels": _crashes}
    spawned = refreshed if refreshed is not None else []
    return Deps(account, loaders, pages or cached_pages(), spawned.append)


def titles(query: str, account: str = "account") -> list[str]:
    return [row["title"] for row in run(query, deps(account=account))["items"]]


def test_menu_lists_every_page_and_drills() -> None:
    rows = run("", deps())["items"]
    assert [row["title"] for row in rows] == [page.title for page in PAGES.values()]
    assert rows[0]["autocomplete"] == "summary "
    assert rows[0]["valid"] is False
    assert rows[0]["icon"] == {"path": "icons/icon_summary.png"}


def test_menu_filters_and_reports_no_match() -> None:
    assert titles("leech") == ["Leeches"]
    assert titles("zzz") == ["No page matches 'zzz'"]


def test_page_has_header_that_goes_back() -> None:
    rows = run("Lessons", deps())["items"]
    header = rows[0]
    assert header["title"] == "Lessons"
    assert header["autocomplete"] == ""
    assert header["arg"] == "https://www.wanikani.com/dashboard"
    assert [row["title"] for row in rows[1:]] == ["大 - big", "小 - small"]


def test_page_filters_rows() -> None:
    assert titles("lessons small") == ["Lessons", "小 - small"]
    assert titles("lessons zzz") == ["Lessons", "Nothing matches 'zzz'"]


def test_page_without_token_does_not_load() -> None:
    refreshed: list[str] = []
    result = run("summary", deps(FakePages({}), account="", refreshed=refreshed))
    assert [row["title"] for row in result["items"]] == ["Summary", NO_TOKEN]
    assert refreshed == []


def test_fresh_page_shows_rows_without_rerun() -> None:
    refreshed: list[str] = []
    result = run("summary", deps(refreshed=refreshed))
    assert "rerun" not in result
    assert refreshed == []


def test_uncached_page_shows_loading_row_and_starts_one_refresh() -> None:
    pages = FakePages({})
    refreshed: list[str] = []
    first = run("summary", deps(pages, refreshed=refreshed))
    second = run("summary", deps(pages, refreshed=refreshed))
    assert [row["title"] for row in first["items"]] == ["Summary", "Loading Summary…"]
    assert first["items"][1]["valid"] is False
    assert first["rerun"] == second["rerun"] == LOADING_RERUN_SECONDS
    assert refreshed == ["summary"]


def test_stale_page_shows_rows_and_refreshes() -> None:
    pages = FakePages({"summary": {"rows": ROWS}}, stale=True)
    refreshed: list[str] = []
    result = run("summary", deps(pages, refreshed=refreshed))
    assert [row["title"] for row in result["items"]] == [
        "Summary",
        "大 - big",
        "小 - small",
    ]
    assert result["rerun"] == STALE_RERUN_SECONDS
    assert refreshed == ["summary"]


def test_refresh_stores_rows_and_releases_claim() -> None:
    pages = FakePages({})
    refresh("summary", deps(pages))
    assert pages.stored["summary"] == {"rows": ROWS}
    assert pages.released == ["summary"]


def test_refresh_stores_api_error_shown_on_page() -> None:
    pages = FakePages({})
    refresh("stats", deps(pages))
    rows = run("stats", deps(pages))["items"]
    assert [row["title"] for row in rows] == ["Stats", "API down"]


def test_refresh_stores_unexpected_error_and_releases_claim() -> None:
    pages = FakePages({})
    refresh("levels", deps(pages))
    assert pages.stored["levels"] == {"error": "unexpected"}
    assert pages.released == ["levels"]


def test_cached_error_retries_on_next_open() -> None:
    refreshed: list[str] = []
    pages = FakePages({"stats": {"error": "API down"}})
    result = run("stats", deps(pages, refreshed=refreshed))
    assert [row["title"] for row in result["items"]] == ["Stats", "API down"]
    assert "rerun" not in result
    assert refreshed == ["stats"]
