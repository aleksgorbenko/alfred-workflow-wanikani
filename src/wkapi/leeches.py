"""Script Filter: WaniKani leeches (low-accuracy items you keep missing)."""

import datetime as dt
import os
import sys
from typing import Any

from alfred_items import TYPE_ICONS, emit, error_item, item
from srs import eta_to_burn, format_days_until
from wanikani_api import (
    WanikaniError,
    get_assignments,
    get_review_statistics,
    get_spaced_repetition_systems,
    get_subjects,
)

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
MAX_PERCENTAGE = 80
MIN_ATTEMPTS = 8
MAX_RESULTS = 10


def _attempts(statistic: dict[str, Any]) -> int:
    return (
        statistic["meaning_correct"]
        + statistic["meaning_incorrect"]
        + statistic["reading_correct"]
        + statistic["reading_incorrect"]
    )


def select_leeches(statistics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (s for s in statistics if _attempts(s) >= MIN_ATTEMPTS),
        key=lambda s: s["percentage_correct"],
    )[:MAX_RESULTS]


def _burn_eta_subtitle(
    subject: dict[str, Any],
    assignment: dict[str, Any] | None,
    systems_by_id: dict[int, dict[str, Any]],
    now: dt.datetime,
) -> str:
    if not assignment or assignment.get("srs_stage") is None:
        return ""
    system = systems_by_id.get(subject.get("spaced_repetition_system_id", -1))
    if not system:
        return ""
    eta = eta_to_burn(assignment["available_at"], assignment["srs_stage"], system)
    if eta is None:
        return ""
    return format_days_until(eta, now)


def build_items(
    leeches: list[dict[str, Any]],
    subjects_by_id: dict[int, dict[str, Any]],
    assignments_by_id: dict[int, dict[str, Any]],
    systems_by_id: dict[int, dict[str, Any]],
    now: dt.datetime,
) -> list[dict[str, Any]]:
    if not leeches:
        return [item(title="🎉 No leeches - great accuracy!", valid=False)]

    items: list[dict[str, Any]] = []
    for statistic in leeches:
        subject_id = statistic["subject_id"]
        subject = subjects_by_id.get(subject_id, {})
        name = subject.get("characters") or subject.get("slug") or f"#{subject_id}"
        meaning_total = statistic["meaning_correct"] + statistic["meaning_incorrect"]
        reading_total = statistic["reading_correct"] + statistic["reading_incorrect"]
        meaning = f"{statistic['meaning_correct']}/{meaning_total}"
        reading = f"{statistic['reading_correct']}/{reading_total}"

        segments = [f"meaning {meaning}", f"reading {reading}"]
        eta_text = _burn_eta_subtitle(
            subject, assignments_by_id.get(subject_id), systems_by_id, now
        )
        if eta_text:
            segments.append(eta_text)

        items.append(
            item(
                title=f"{statistic['percentage_correct']}% {name}",
                subtitle=" · ".join(segments),
                arg=DASHBOARD_URL,
                icon=TYPE_ICONS.get(subject.get("subject_type", "")),
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
        statistics = get_review_statistics(
            token, percentages_less_than=str(MAX_PERCENTAGE)
        )
        leeches = select_leeches(statistics)
        subject_ids = ",".join(str(s["subject_id"]) for s in leeches)
        subjects = get_subjects(token, ids=subject_ids) if subject_ids else []
        assignments = (
            get_assignments(token, subject_ids=subject_ids) if subject_ids else []
        )
        systems = get_spaced_repetition_systems(token)
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    subjects_by_id = {s["id"]: s for s in subjects}
    assignments_by_id = {a["subject_id"]: a for a in assignments}
    systems_by_id = {s["id"]: s for s in systems}
    emit(
        build_items(
            leeches,
            subjects_by_id,
            assignments_by_id,
            systems_by_id,
            dt.datetime.now(dt.UTC),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
