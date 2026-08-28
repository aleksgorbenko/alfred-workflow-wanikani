import datetime as dt

from leeches import build_items, select_leeches

NOW = dt.datetime(2024, 1, 1, tzinfo=dt.UTC)

DEFAULT_SYSTEM = {
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


def _stat(subject_id, percentage_correct, counts=(3, 3, 3, 3)):
    meaning_correct, meaning_incorrect, reading_correct, reading_incorrect = counts
    return {
        "subject_id": subject_id,
        "percentage_correct": percentage_correct,
        "meaning_correct": meaning_correct,
        "meaning_incorrect": meaning_incorrect,
        "reading_correct": reading_correct,
        "reading_incorrect": reading_incorrect,
    }


def test_sorts_worst_accuracy_first():
    statistics = [_stat(1, 70), _stat(2, 40), _stat(3, 60)]
    subjects_by_id = {
        1: {"characters": "一"},
        2: {"characters": "二"},
        3: {"characters": "三"},
    }

    leeches = select_leeches(statistics)
    items = build_items(leeches, subjects_by_id, {}, {}, NOW)

    assert items[0]["title"] == "40% 二"
    assert items[1]["title"] == "60% 三"
    assert items[2]["title"] == "70% 一"


def test_falls_back_to_slug_then_id_when_no_characters():
    statistics = [_stat(1, 50), _stat(2, 50)]
    subjects_by_id = {1: {"slug": "some-radical"}}

    leeches = select_leeches(statistics)
    items = build_items(leeches, subjects_by_id, {}, {}, NOW)

    assert items[0]["title"] == "50% some-radical"
    assert items[1]["title"] == "50% #2"


def test_excludes_low_attempt_items():
    statistics = [_stat(1, 20, counts=(1, 1, 0, 0))]

    leeches = select_leeches(statistics)
    items = build_items(leeches, {}, {}, {}, NOW)

    assert items[0]["title"] == "🎉 No leeches - great accuracy!"


def test_limits_to_ten_results():
    statistics = [_stat(i, 50) for i in range(15)]

    leeches = select_leeches(statistics)
    items = build_items(leeches, {}, {}, {}, NOW)

    max_results = 10
    assert len(items) == max_results


def test_no_leeches_shows_friendly_message():
    items = build_items([], {}, {}, {}, NOW)

    assert items == [
        {"title": "🎉 No leeches - great accuracy!", "subtitle": "", "valid": False}
    ]


def test_appends_burn_eta_when_assignment_and_system_known():
    statistics = [_stat(1, 50)]
    subjects_by_id = {1: {"characters": "一", "spaced_repetition_system_id": 1}}
    assignments_by_id = {
        1: {"srs_stage": 8, "available_at": "2024-01-01T00:00:00.000000Z"}
    }
    systems_by_id = {1: DEFAULT_SYSTEM}

    leeches = select_leeches(statistics)
    items = build_items(leeches, subjects_by_id, assignments_by_id, systems_by_id, NOW)

    assert "burns in" in items[0]["subtitle"]


def test_omits_burn_eta_when_assignment_missing():
    statistics = [_stat(1, 50)]
    subjects_by_id = {1: {"characters": "一", "spaced_repetition_system_id": 1}}

    leeches = select_leeches(statistics)
    items = build_items(leeches, subjects_by_id, {}, {1: DEFAULT_SYSTEM}, NOW)

    assert "burns in" not in items[0]["subtitle"]
