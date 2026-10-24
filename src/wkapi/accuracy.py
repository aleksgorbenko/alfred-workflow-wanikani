"""Script Filter: WaniKani review accuracy (meaning/reading % correct)."""

from typing import Any

from alfred_items import item
from wanikani_api import get_review_statistics

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
ICON = "icons/icon_accuracy.png"


def _percentage(correct: int, total: int) -> int:
    return round(correct / total * 100) if total else 0


def build_items(statistics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    meaning_correct = sum(s["meaning_correct"] for s in statistics)
    meaning_incorrect = sum(s["meaning_incorrect"] for s in statistics)
    reading_correct = sum(s["reading_correct"] for s in statistics)
    reading_incorrect = sum(s["reading_incorrect"] for s in statistics)

    meaning_total = meaning_correct + meaning_incorrect
    reading_total = reading_correct + reading_incorrect
    overall_correct = meaning_correct + reading_correct
    overall_total = meaning_total + reading_total
    overall_percentage = _percentage(overall_correct, overall_total)

    return [
        item(
            title=f"🎯 Overall accuracy: {overall_percentage}%",
            subtitle=f"{overall_correct}/{overall_total} correct",
            arg=DASHBOARD_URL,
            icon=ICON,
        ),
        item(
            title=f"📖 Meaning: {_percentage(meaning_correct, meaning_total)}%",
            subtitle=f"{meaning_correct}/{meaning_total} correct",
            arg=DASHBOARD_URL,
            icon=ICON,
        ),
        item(
            title=f"🔤 Reading: {_percentage(reading_correct, reading_total)}%",
            subtitle=f"{reading_correct}/{reading_total} correct",
            arg=DASHBOARD_URL,
            icon=ICON,
        ),
    ]


def load(token: str) -> list[dict[str, Any]]:
    return build_items(get_review_statistics(token))
