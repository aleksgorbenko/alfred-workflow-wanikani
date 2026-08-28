"""Script Filter: WaniKani SRS stage breakdown."""

import os
import sys

from alfred_items import emit, error_item, item
from wanikani_api import WanikaniError, get_assignments

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
ICON = "icons/icon_stats.png"

STAGE_BUCKETS = [
    ("Apprentice", "🌸", range(0, 5)),
    ("Guru", "🟣", range(5, 7)),
    ("Master", "🔵", range(7, 8)),
    ("Enlightened", "🔷", range(8, 9)),
    ("Burned", "⚪", range(9, 10)),
]


def build_items(assignments: list[dict]) -> list[dict]:
    counts = dict.fromkeys((name for name, _, _ in STAGE_BUCKETS), 0)
    for assignment in assignments:
        stage = assignment.get("srs_stage")
        if stage is None:
            continue
        for name, _, stages in STAGE_BUCKETS:
            if stage in stages:
                counts[name] += 1
                break

    return [
        item(
            title=f"{stage_icon} {name}: {counts[name]}",
            subtitle="Open dashboard",
            arg=DASHBOARD_URL,
            icon=ICON,
        )
        for name, stage_icon, _ in STAGE_BUCKETS
    ]


def main() -> None:
    token = os.environ.get("WANIKANI_API_TOKEN", "").strip()
    if not token:
        emit(
            [
                error_item(
                    "No WaniKani API token set - add it in the workflow configuration"
                )
            ]
        )
        return

    try:
        assignments = get_assignments(token, started="true")
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    emit(build_items(assignments))


if __name__ == "__main__":
    sys.exit(main())
