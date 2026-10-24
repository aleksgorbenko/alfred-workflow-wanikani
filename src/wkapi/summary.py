"""Script Filter: WaniKani summary (lessons/reviews available now)."""

import datetime as dt
from typing import Any

from alfred_items import item
from wanikani_api import get_summary, get_user

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
LESSONS_URL = "https://www.wanikani.com/subject-lessons/start"
REVIEWS_URL = "https://www.wanikani.com/subjects/review"
ICON = "icons/icon_summary.png"


def _parse(timestamp: str) -> dt.datetime:
    return dt.datetime.fromisoformat(timestamp)


def _available_count(buckets: list[dict[str, Any]], now: dt.datetime) -> int:
    return sum(
        len(bucket["subject_ids"])
        for bucket in buckets
        if _parse(bucket["available_at"]) <= now
    )


def build_items(
    summary: dict[str, Any], level: int, now: dt.datetime
) -> list[dict[str, Any]]:
    lessons_available = _available_count(summary["lessons"], now)
    reviews_available = _available_count(summary["reviews"], now)

    items = [
        item(
            title=f"🎓 Level {level}",
            subtitle="Open dashboard",
            arg=DASHBOARD_URL,
            icon=ICON,
        ),
        item(
            title=f"📚 Lessons available: {lessons_available}",
            subtitle="Open lesson queue",
            arg=LESSONS_URL,
            icon=ICON,
        )
        | {"autocomplete": "lessons "},
        item(
            title=f"🔁 Reviews available: {reviews_available}",
            subtitle="Open review queue",
            arg=REVIEWS_URL,
            icon=ICON,
        )
        | {"autocomplete": "reviews "},
    ]

    next_reviews_at = summary.get("next_reviews_at")
    if reviews_available == 0 and next_reviews_at:
        next_at = _parse(next_reviews_at)
        items.append(
            item(
                title=f"⏰ Next reviews at: {next_at.astimezone().strftime('%H:%M')}",
                subtitle="Open dashboard",
                arg=DASHBOARD_URL,
                icon=ICON,
            )
        )

    return items


def load(token: str) -> list[dict[str, Any]]:
    summary = get_summary(token)
    level = get_user(token)["level"]
    return build_items(summary, level, dt.datetime.now(dt.UTC))
