"""Script Filter: WaniKani lesson queue, one row per subject (live type-to-filter)."""

from typing import Any

from subject_queue import queue_items


def load(token: str) -> list[dict[str, Any]]:
    return queue_items(token, "lessons", "🎉 No lessons available")
