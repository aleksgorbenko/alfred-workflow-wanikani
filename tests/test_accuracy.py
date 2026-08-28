from accuracy import build_items


def _stat(meaning_correct, meaning_incorrect, reading_correct, reading_incorrect):
    return {
        "meaning_correct": meaning_correct,
        "meaning_incorrect": meaning_incorrect,
        "reading_correct": reading_correct,
        "reading_incorrect": reading_incorrect,
    }


def test_computes_overall_meaning_and_reading_percentages():
    statistics = [
        _stat(8, 2, 9, 1),
        _stat(6, 4, 10, 0),
    ]

    items = build_items(statistics)

    assert items[0]["title"] == "🎯 Overall accuracy: 82%"
    assert items[0]["subtitle"] == "33/40 correct"
    assert items[1]["title"] == "📖 Meaning: 70%"
    assert items[2]["title"] == "🔤 Reading: 95%"


def test_handles_no_statistics():
    items = build_items([])

    assert items[0]["title"] == "🎯 Overall accuracy: 0%"
