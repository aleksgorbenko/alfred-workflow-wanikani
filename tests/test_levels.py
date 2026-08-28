import datetime as dt

from levels import build_items, next_level_item

NOW = dt.datetime(2026, 8, 3, 12, 0, tzinfo=dt.UTC)

SYSTEM = {
    "passing_stage_position": 5,
    "burning_stage_position": 9,
    "stages": [
        {"position": 0, "interval": None},
        {"position": 1, "interval": 14400},
        {"position": 2, "interval": 28800},
        {"position": 3, "interval": 82800},
        {"position": 4, "interval": 169200},
        {"position": 5, "interval": 604800},
        {"position": 6, "interval": 1209600},
        {"position": 7, "interval": 2592000},
        {"position": 8, "interval": 7776000},
        {"position": 9, "interval": None},
    ],
}


def _kanji(subject_id, system_id=1):
    return {"id": subject_id, "spaced_repetition_system_id": system_id}


def _assignment(
    subject_id, srs_stage, available_at="2026-08-03T00:00:00.000000Z", passed_at=None
):
    return {
        "subject_id": subject_id,
        "srs_stage": srs_stage,
        "available_at": available_at,
        "passed_at": passed_at,
    }


def test_shows_passed_level_with_duration():
    progressions = [
        {
            "level": 1,
            "started_at": "2026-07-01T00:00:00.000000Z",
            "passed_at": "2026-07-08T00:00:00.000000Z",
        }
    ]

    items = build_items(progressions, NOW)

    assert items[0]["title"] == "Level 1 - 7d ✅"
    assert items[0]["subtitle"] == "Started 2026-07-01 → Passed 2026-07-08"


def test_shows_in_progress_level_using_now():
    progressions = [
        {
            "level": 2,
            "started_at": "2026-08-01T00:00:00.000000Z",
            "passed_at": None,
        }
    ]

    items = build_items(progressions, NOW)

    assert items[0]["title"] == "Level 2 - 2d ⏳"
    assert items[0]["subtitle"] == "Started 2026-08-01"


def test_skips_unlocked_but_not_started_levels():
    progressions = [
        {"level": 3, "started_at": None, "passed_at": None},
    ]

    items = build_items(progressions, NOW)

    assert items == []


def test_sorted_highest_level_first():
    progressions = [
        {"level": 1, "started_at": "2026-07-01T00:00:00.000000Z", "passed_at": None},
        {"level": 2, "started_at": "2026-08-01T00:00:00.000000Z", "passed_at": None},
    ]

    items = build_items(progressions, NOW)

    assert items[0]["title"].startswith("Level 2")
    assert items[1]["title"].startswith("Level 1")


def test_next_level_ready_when_enough_kanji_already_passed():
    kanji_subjects = [_kanji(i) for i in range(10)]
    kanji_assignments = [
        _assignment(i, 6, passed_at="2026-08-01T00:00:00.000000Z") for i in range(9)
    ] + [_assignment(9, 2)]

    result = next_level_item(kanji_subjects, kanji_assignments, {1: SYSTEM}, NOW)

    assert result["title"] == "🎉 Ready to level up!"


def test_next_level_asks_for_lessons_when_not_enough_in_progress():
    kanji_subjects = [_kanji(i) for i in range(10)]
    kanji_assignments = [
        _assignment(0, 2),
        _assignment(1, 0),
        _assignment(2, 0),
    ]

    result = next_level_item(kanji_subjects, kanji_assignments, {1: SYSTEM}, NOW)

    assert result["title"] == "⏳ Next level: finish Kanji lessons to see ETA"
    assert result["subtitle"] == "total kanji: 10・guru: 0・started: 1・locked: 7"


def test_next_level_eta_uses_slowest_of_the_needed_kanji():
    kanji_subjects = [_kanji(1), _kanji(2)]
    kanji_assignments = [_assignment(1, 4), _assignment(2, 1)]

    result = next_level_item(kanji_subjects, kanji_assignments, {1: SYSTEM}, NOW)

    assert result["title"].startswith("⏫ Next level in")
