import datetime as dt

from subject_queue import available_subject_ids, build_items

EMPTY_MESSAGE = "🎉 No lessons available"


def test_title_is_character_and_meaning_subtitle_has_level_type_and_part_of_speech():
    subjects_by_id = {
        2467: {
            "characters": "一",
            "subject_type": "vocabulary",
            "level": 5,
            "meanings": [{"meaning": "One", "primary": True}],
            "parts_of_speech": ["numeral"],
        }
    }

    items = build_items([2467], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["title"] == "一 - One"
    assert items[0]["subtitle"] == "W5・Vocabulary・numeral"


def test_kanji_has_no_part_of_speech_segment():
    subjects_by_id = {
        440: {
            "characters": "大",
            "subject_type": "kanji",
            "level": 1,
            "meanings": [{"meaning": "Big", "primary": True}],
        }
    }

    items = build_items([440], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["title"] == "大 - Big"
    assert items[0]["subtitle"] == "W1・Kanji"


def test_kana_vocabulary_type_is_two_words():
    subjects_by_id = {
        1: {
            "characters": "とても",
            "subject_type": "kana_vocabulary",
            "level": 12,
            "meanings": [{"meaning": "Very", "primary": True}],
        }
    }

    items = build_items([1], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["subtitle"] == "W12・Kana Vocabulary"


def test_hyphenates_na_i_no_adjectives():
    subjects_by_id = {
        1: {
            "characters": "静か",
            "subject_type": "vocabulary",
            "level": 3,
            "meanings": [{"meaning": "Quiet", "primary": True}],
            "parts_of_speech": ["な adjective", "い adjective", "の adjective"],
        }
    }

    items = build_items([1], subjects_by_id, EMPTY_MESSAGE)

    expected = "W3・Vocabulary・な-adjective, い-adjective, の-adjective"
    assert items[0]["subtitle"] == expected


def test_leaves_other_parts_of_speech_untouched():
    subjects_by_id = {
        1: {
            "characters": "静",
            "subject_type": "vocabulary",
            "level": 11,
            "meanings": [{"meaning": "Stillness", "primary": True}],
            "parts_of_speech": ["noun"],
        }
    }

    items = build_items([1], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["subtitle"] == "W11・Vocabulary・noun"


def test_relabels_verbal_noun_to_avoid_clash_with_suru_verb():
    subjects_by_id = {
        1: {
            "characters": "中止",
            "subject_type": "vocabulary",
            "level": 20,
            "meanings": [{"meaning": "Cancellation", "primary": True}],
            "parts_of_speech": ["noun", "verbal noun"],
        },
        2: {
            "characters": "対する",
            "subject_type": "vocabulary",
            "level": 20,
            "meanings": [{"meaning": "To Face", "primary": True}],
            "parts_of_speech": ["する verb"],
        },
    }

    items = build_items([1, 2], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["subtitle"] == "W20・Vocabulary・noun, verbal noun (する)"
    assert items[1]["subtitle"] == "W20・Vocabulary・する verb"


def test_falls_back_to_slug_then_id_when_no_meaning():
    subjects_by_id = {1: {"slug": "leaf", "subject_type": "radical", "level": 1}}

    items = build_items([1, 2], subjects_by_id, EMPTY_MESSAGE)

    assert items[0]["title"] == "leaf"
    assert items[1]["title"] == "#2"


def test_empty_subject_ids_shows_provided_message():
    items = build_items([], {}, "🎉 No reviews available")

    assert items == [
        {"title": "🎉 No reviews available", "subtitle": "", "valid": False}
    ]


NOW = dt.datetime(2026, 8, 3, 12, 0, tzinfo=dt.UTC)


def _bucket(hours_from_now: int, subject_ids: list[int]) -> dict:
    at = NOW + dt.timedelta(hours=hours_from_now)
    return {
        "available_at": at.isoformat().replace("+00:00", "Z"),
        "subject_ids": subject_ids,
    }


def test_available_subject_ids_only_includes_past_buckets():
    buckets = [_bucket(-1, [1, 2]), _bucket(2, [3])]

    ids = available_subject_ids(buckets, NOW)

    assert ids == [1, 2]
