"""Script Filter: WaniKani review accuracy (meaning/reading % correct)."""

import os
import sys

from alfred_items import emit, error_item, item
from wanikani_api import WanikaniError, get_review_statistics

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
ICON = "icons/icon_accuracy.png"


def _percentage(correct: int, total: int) -> int:
    return round(correct / total * 100) if total else 0


def build_items(statistics: list[dict]) -> list[dict]:
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
        statistics = get_review_statistics(token)
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    emit(build_items(statistics))


if __name__ == "__main__":
    sys.exit(main())
