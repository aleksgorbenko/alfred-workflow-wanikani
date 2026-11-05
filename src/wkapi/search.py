"""Script Filter: WaniKani dictionary search (scrapes wanikani.com/search)."""

import json
import sys
import urllib.parse
from typing import Any

from alfred_items import TYPE_ICONS, emit, error_item, item
from async_view import finish, job_command, serve, settle
from cache import cache_dir
from wanikani_api import WanikaniError
from wanikani_search import search


def _title(entry: dict[str, str]) -> str:
    characters = entry["characters"] or urllib.parse.unquote(
        entry["href"].rsplit("/", 1)[-1]
    )
    return f"{characters} - {entry['meaning']}" if entry["meaning"] else characters


def _subtitle(entry: dict[str, str]) -> str:
    segments = [entry["type"].title(), entry["reading"]]
    return "・".join(segment for segment in segments if segment)


def build_items(entries: list[dict[str, str]]) -> list[dict[str, Any]]:
    if not entries:
        return [item(title="No results on WaniKani", valid=False)]
    return [
        item(
            title=_title(entry),
            subtitle=_subtitle(entry),
            arg=entry["href"],
            icon=TYPE_ICONS.get(entry["type"]),
        )
        for entry in entries
    ]


def rows(query: str) -> list[dict[str, Any]]:
    try:
        return build_items(search(query))
    except WanikaniError as error:
        return [error_item(str(error))]


def _job(query: str) -> None:
    if not settle(cache_dir(), query):
        return
    try:
        payload: dict[str, Any] = {"items": rows(query)}
    except Exception as error:  # noqa: BLE001
        payload = {"items": [error_item(str(error))]}
    finish(cache_dir(), query, payload)


def main(argv: list[str]) -> None:
    if argv[:1] == ["--job"]:
        _job(argv[1].strip() if len(argv) > 1 else "")
        return
    query = argv[0].strip() if argv else ""
    if not query:
        emit([item(title="Type to search WaniKani…", valid=False)])
        return
    payload = serve(
        query,
        directory=cache_dir(),
        command=job_command(__file__, query),
        label=f"Searching WaniKani for '{query}'…",
    )
    json.dump(payload, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
