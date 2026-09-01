"""Shared Alfred item building for the WaniKani lesson/review subject queues."""

import datetime as dt

from alfred_items import TYPE_ICONS, item

DASHBOARD_URL = "https://www.wanikani.com/dashboard"
SUBJECTS_TTL = 3 * 60 * 60


def parse(timestamp: str) -> dt.datetime:
    return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def available_subject_ids(buckets: list[dict], now: dt.datetime) -> list[int]:
    ids = []
    for bucket in buckets:
        if parse(bucket["available_at"]) <= now:
            ids.extend(bucket["subject_ids"])
    return ids


def _primary_meaning(subject: dict) -> str:
    for meaning in subject.get("meanings", []):
        if meaning.get("primary"):
            return meaning["meaning"]
    return ""


_PART_OF_SPEECH_LABELS = {
    f"{kana} adjective": f"{kana}-adjective" for kana in ("な", "い", "の")
} | {
    "verbal noun": "verbal noun (する)",
}


def _format_part_of_speech(part_of_speech: str) -> str:
    return _PART_OF_SPEECH_LABELS.get(part_of_speech, part_of_speech)


def build_items(
    subject_ids: list[int], subjects_by_id: dict[int, dict], empty_message: str
) -> list[dict]:
    if not subject_ids:
        return [item(title=empty_message, valid=False)]

    items = []
    for subject_id in subject_ids:
        subject = subjects_by_id.get(subject_id, {})
        name = subject.get("characters") or subject.get("slug") or f"#{subject_id}"
        meaning = _primary_meaning(subject)
        title = f"{name} - {meaning}" if meaning else name

        subject_type = subject.get("subject_type", "").replace("_", " ").title()
        level = subject.get("level")
        segments = [f"W{level}" if level else "", subject_type]

        parts_of_speech = subject.get("parts_of_speech")
        if parts_of_speech:
            formatted = ", ".join(_format_part_of_speech(p) for p in parts_of_speech)
            segments.append(formatted)

        subtitle = "・".join(segment for segment in segments if segment)
        icon = TYPE_ICONS.get(subject.get("subject_type", ""))

        items.append(item(title=title, subtitle=subtitle, arg=DASHBOARD_URL, icon=icon))

    return items
