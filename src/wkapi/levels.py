"""Script Filter: WaniKani level history (from level_progressions)."""

import datetime as dt
import math
import os
import sys

from alfred_items import emit, error_item, item
from srs import eta_to_pass
from wanikani_api import (
    WanikaniError,
    get_assignments,
    get_level_progressions,
    get_spaced_repetition_systems,
    get_subjects,
    get_user,
)

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
ICON = "icons/icon_levels.png"
REQUIRED_KANJI_FRACTION = 0.9


def _parse(timestamp: str) -> dt.datetime:
    return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _duration(start: str, end: str | None, now: dt.datetime) -> str:
    started = _parse(start)
    ended = _parse(end) if end else now
    days = (ended - started).days
    return f"{days}d"


def next_level_item(
    kanji_subjects: list[dict],
    kanji_assignments: list[dict],
    systems_by_id: dict[int, dict],
    now: dt.datetime,
) -> dict:
    total = len(kanji_subjects)
    assignments_by_subject = {a["subject_id"]: a for a in kanji_assignments}
    passed = sum(1 for a in kanji_assignments if a.get("passed_at") is not None)
    started = sum(
        1
        for a in kanji_assignments
        if a.get("passed_at") is None and (a.get("srs_stage") or 0) > 0
    )
    locked = total - len(assignments_by_subject)
    required = math.ceil(total * REQUIRED_KANJI_FRACTION) if total else 0

    if total == 0 or passed >= required:
        return item(
            title="🎉 Ready to level up!",
            subtitle="Open dashboard",
            arg=DASHBOARD_URL,
            icon=ICON,
        )

    etas = []
    for subject in kanji_subjects:
        assignment = assignments_by_subject.get(subject["id"])
        if not assignment or assignment.get("passed_at") is not None:
            continue
        available_at = assignment.get("available_at")
        srs_stage = assignment.get("srs_stage")
        system = systems_by_id.get(subject.get("spaced_repetition_system_id"))
        if not available_at or srs_stage is None or not system:
            continue
        eta = eta_to_pass(available_at, srs_stage, system)
        if eta is not None:
            etas.append(eta)

    needed = required - passed
    if len(etas) < needed:
        return item(
            title="⏳ Next level: finish Kanji lessons to see ETA",
            subtitle=(
                f"total kanji: {total}・guru: {passed}"
                f"・started: {started}・locked: {locked}"
            ),
            arg=DASHBOARD_URL,
            icon=ICON,
        )

    etas.sort()
    next_level_eta = etas[needed - 1]
    days = (next_level_eta - now).days
    duration = "<1d" if days < 1 else f"~{days}d"
    return item(
        title=f"⏫ Next level in {duration}",
        subtitle=f"{passed}/{required} kanji guru'd, if no mistakes",
        arg=DASHBOARD_URL,
        icon=ICON,
    )


def build_items(progressions: list[dict], now: dt.datetime) -> list[dict]:
    items = []
    for progression in sorted(progressions, key=lambda p: p["level"], reverse=True):
        started_at = progression.get("started_at")
        if not started_at:
            continue

        passed_at = progression.get("passed_at")
        status = "✅" if passed_at else "⏳"
        duration = _duration(started_at, passed_at, now)

        subtitle = f"Started {_parse(started_at).date().isoformat()}"
        if passed_at:
            subtitle += f" → Passed {_parse(passed_at).date().isoformat()}"

        items.append(
            item(
                title=f"Level {progression['level']} - {duration} {status}",
                subtitle=subtitle,
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
        progressions = get_level_progressions(token)
        level = get_user(token)["level"]
        kanji_subjects = get_subjects(token, levels=str(level), types="kanji")
        kanji_assignments = get_assignments(
            token, levels=str(level), subject_types="kanji"
        )
        systems = get_spaced_repetition_systems(token)
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    systems_by_id = {s["id"]: s for s in systems}
    now = dt.datetime.now(dt.UTC)
    items = [next_level_item(kanji_subjects, kanji_assignments, systems_by_id, now)]
    items.extend(build_items(progressions, now))
    emit(items)


if __name__ == "__main__":
    sys.exit(main())
