from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from alfred_items import item

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from pages import PageHit

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
NO_TOKEN = "No WaniKani API token set - add it in the workflow configuration"  # noqa: S105
SEPARATOR = "・"
PAGE_MAX_AGE_SECONDS = 300
LOADING_RERUN_SECONDS = 0.5
STALE_RERUN_SECONDS = 1.0

Row = dict[str, Any]


@dataclass(frozen=True)
class Page:
    title: str
    subtitle: str
    icon: str


PAGES = {
    "summary": Page("Summary", "Lessons and reviews available right now", "summary"),
    "levels": Page("Levels", "Level history and time spent per level", "levels"),
    "stats": Page(
        "Stats",
        "SRS stage breakdown (Apprentice/Guru/Master/Enlightened/Burned)",
        "stats",
    ),
    "accuracy": Page(
        "Accuracy", "Overall, meaning, and reading review accuracy", "accuracy"
    ),
    "leeches": Page("Leeches", "Items you keep getting wrong", "leeches"),
    "lessons": Page(
        "Lessons", "Browse and search your current lesson queue", "lessons"
    ),
    "reviews": Page(
        "Reviews", "Browse and search your current review queue", "reviews"
    ),
}


class PageStore(Protocol):
    def read(self, name: str, max_age_seconds: int) -> PageHit | None: ...

    def write(self, name: str, data: dict[str, Any]) -> None: ...

    def claim_refresh(self, name: str) -> bool: ...

    def release_refresh(self, name: str) -> None: ...


@dataclass(frozen=True)
class Deps:
    token: str
    loaders: Mapping[str, Callable[[str], list[Row]]]
    pages: PageStore
    refresh: Callable[[str], None]


@dataclass(frozen=True)
class Screen:
    items: list[Row]
    rerun: float | None = None


def _icon(page: Page) -> str:
    return f"icons/icon_{page.icon}.png"


def _matches(row: Row, text: str) -> bool:
    wanted = text.casefold()
    return wanted in f"{row['title']} {row.get('subtitle', '')}".casefold()


def _menu(text: str) -> list[Row]:
    rows = [
        item(page.title, subtitle=page.subtitle, valid=False, icon=_icon(page))
        | {"autocomplete": f"{name} "}
        for name, page in PAGES.items()
    ]
    return [row for row in rows if _matches(row, text)] or [
        item(f"No page matches '{text}'", valid=False)
    ]


def _header(page: Page) -> Row:
    return item(
        page.title,
        subtitle=f"{page.subtitle} · ↩ Open dashboard",
        arg=DASHBOARD_URL,
        icon=_icon(page),
    ) | {"autocomplete": ""}


def _page(name: str, text: str, deps: Deps) -> Screen:
    page = PAGES[name]
    header = _header(page)
    if not deps.token:
        return Screen([header, item(NO_TOKEN, valid=False)])
    hit = deps.pages.read(name, PAGE_MAX_AGE_SECONDS)
    outdated = hit is None or hit.stale or "error" in hit.data
    if outdated and deps.pages.claim_refresh(name):
        deps.refresh(name)
    if hit is None:
        loading = item(f"Loading {page.title}…", valid=False, icon=_icon(page))
        return Screen([header, loading], LOADING_RERUN_SECONDS)
    rerun = STALE_RERUN_SECONDS if hit.stale else None
    if "error" in hit.data:
        return Screen([header, item(hit.data["error"], valid=False)], rerun)
    matching = [row for row in hit.data["rows"] if _matches(row, text)]
    nothing = [item(f"Nothing matches '{text}'", valid=False)]
    return Screen([header, *(matching or nothing)], rerun)


def refresh(name: str, deps: Deps) -> None:
    try:
        deps.pages.write(name, {"rows": deps.loaders[name](deps.token)})
    except Exception as error:  # noqa: BLE001
        deps.pages.write(name, {"error": str(error)})
    finally:
        deps.pages.release_refresh(name)


def run(query: str, deps: Deps) -> dict[str, Any]:
    words = query.split()
    name = words[0].casefold() if words else ""
    if name not in PAGES:
        return {"items": _menu(" ".join(words))}
    screen = _page(name, " ".join(words[1:]), deps)
    result: dict[str, Any] = {"items": screen.items}
    if screen.rerun is not None:
        result["rerun"] = screen.rerun
    return result
