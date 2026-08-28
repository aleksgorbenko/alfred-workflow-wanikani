"""Script Filter: WaniKani dictionary search (scrapes wanikani.com/search)."""

import sys
import urllib.parse

from alfred_items import TYPE_ICONS, bold, emit, error_item, item
from wanikani_api import WanikaniError
from wanikani_search import search


def _title(entry: dict[str, str]) -> str:
    characters = entry["characters"] or urllib.parse.unquote(
        entry["href"].rsplit("/", 1)[-1]
    )
    return f"{characters} - {entry['meaning']}" if entry["meaning"] else characters


def _subtitle(entry: dict[str, str]) -> str:
    segments = [bold(entry["type"].title()), entry["reading"]]
    return "・".join(segment for segment in segments if segment)


def build_items(entries: list[dict[str, str]]) -> list[dict]:
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


def main(argv: list[str]) -> None:
    query = argv[0].strip() if argv else ""
    if not query:
        emit([item(title="Type to search WaniKani…", valid=False)])
        return

    try:
        entries = search(query)
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    emit(build_items(entries))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
