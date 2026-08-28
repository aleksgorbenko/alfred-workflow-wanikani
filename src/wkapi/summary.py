"""Script Filter: WaniKani summary (lessons/reviews available now)."""

import datetime as dt
import os
import sys

from alfred_items import emit, error_item, item
from wanikani_api import WanikaniError, get_summary, get_user

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
LESSONS_URL = "https://www.wanikani.com/subject-lessons/start"
REVIEWS_URL = "https://www.wanikani.com/subjects/review"
ICON = "icons/icon_summary.png"


def _parse(timestamp: str) -> dt.datetime:
    return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _available_count(buckets: list[dict], now: dt.datetime) -> int:
    return sum(
        len(bucket["subject_ids"])
        for bucket in buckets
        if _parse(bucket["available_at"]) <= now
    )


def build_items(summary: dict, level: int, now: dt.datetime) -> list[dict]:
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
        ),
        item(
            title=f"🔁 Reviews available: {reviews_available}",
            subtitle="Open review queue",
            arg=REVIEWS_URL,
            icon=ICON,
        ),
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
        summary = get_summary(token)
        level = get_user(token)["level"]
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    emit(build_items(summary, level, dt.datetime.now(dt.UTC)))


if __name__ == "__main__":
    sys.exit(main())
