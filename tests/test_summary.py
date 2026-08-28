import datetime as dt

from summary import build_items

NOW = dt.datetime(2026, 8, 3, 12, 0, tzinfo=dt.UTC)
LEVEL = 12


def _bucket(hours_from_now: int, subject_ids: list[int]) -> dict:
    at = NOW + dt.timedelta(hours=hours_from_now)
    return {
        "available_at": at.isoformat().replace("+00:00", "Z"),
        "subject_ids": subject_ids,
    }


def test_shows_level_lessons_and_reviews():
    summary = {
        "lessons": [_bucket(0, [1, 2, 3])],
        "reviews": [_bucket(-1, [4, 5]), _bucket(2, [6, 7, 8])],
        "next_reviews_at": None,
    }

    items = build_items(summary, LEVEL, NOW)

    assert items[0]["title"] == "🎓 Level 12"
    assert items[1]["title"] == "📚 Lessons available: 3"
    assert items[2]["title"] == "🔁 Reviews available: 2"


def test_shows_next_reviews_at_when_none_available_now():
    summary = {
        "lessons": [],
        "reviews": [_bucket(2, [1])],
        "next_reviews_at": (NOW + dt.timedelta(hours=2))
        .isoformat()
        .replace("+00:00", "Z"),
    }

    items = build_items(summary, LEVEL, NOW)

    expected_item_count = 4
    assert len(items) == expected_item_count
    assert items[3]["title"].startswith("⏰ Next reviews at:")


def test_omits_next_reviews_at_when_reviews_available_now():
    summary = {
        "lessons": [],
        "reviews": [_bucket(0, [1])],
        "next_reviews_at": (NOW + dt.timedelta(hours=1))
        .isoformat()
        .replace("+00:00", "Z"),
    }

    items = build_items(summary, LEVEL, NOW)

    expected_item_count = 3
    assert len(items) == expected_item_count
