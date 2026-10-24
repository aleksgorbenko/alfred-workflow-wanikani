"""Script Filter: WaniKani SRS stage breakdown."""

from typing import Any

from alfred_items import item
from wanikani_api import get_assignments

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
ICON = "icons/icon_stats.png"

STAGE_BUCKETS = [
    ("Apprentice", "🌸", range(5)),
    ("Guru", "🟣", range(5, 7)),
    ("Master", "🔵", range(7, 8)),
    ("Enlightened", "🔷", range(8, 9)),
    ("Burned", "⚪", range(9, 10)),
]


def build_items(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
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


def load(token: str) -> list[dict[str, Any]]:
    return build_items(get_assignments(token, started="true"))
