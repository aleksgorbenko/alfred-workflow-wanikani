"""Script Filter: WaniKani review queue, one row per subject (live type-to-filter)."""

import datetime as dt
import os
import sys

from alfred_items import emit, error_item
from subject_queue import SUBJECTS_TTL, available_subject_ids, build_items
from wanikani_api import WanikaniError, get_subjects, get_summary


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
        now = dt.datetime.now(dt.UTC)
        subject_ids = available_subject_ids(summary["reviews"], now)
        subject_ids_param = ",".join(map(str, subject_ids))
        subjects = (
            get_subjects(token, ttl_seconds=SUBJECTS_TTL, ids=subject_ids_param)
            if subject_ids
            else []
        )
    except WanikaniError as error:
        emit([error_item(str(error))])
        return

    subjects_by_id = {s["id"]: s for s in subjects}
    emit(build_items(subject_ids, subjects_by_id, "🎉 No reviews available"))


if __name__ == "__main__":
    sys.exit(main())
