from stats import build_items


def _assignment(srs_stage: int) -> dict:
    return {"srs_stage": srs_stage}


def test_buckets_stages_into_named_groups():
    assignments = [
        _assignment(1),
        _assignment(4),
        _assignment(5),
        _assignment(6),
        _assignment(7),
        _assignment(8),
        _assignment(9),
        _assignment(9),
    ]

    items = build_items(assignments)

    assert items[0]["title"] == "🌸 Apprentice: 2"
    assert items[1]["title"] == "🟣 Guru: 2"
    assert items[2]["title"] == "🔵 Master: 1"
    assert items[3]["title"] == "🔷 Enlightened: 1"
    assert items[4]["title"] == "⚪ Burned: 2"


def test_ignores_assignments_without_srs_stage():
    items = build_items([{"subject_id": 1}])

    assert items[0]["title"] == "🌸 Apprentice: 0"


def test_empty_assignments_gives_zero_counts():
    items = build_items([])

    assert [i["title"] for i in items] == [
        "🌸 Apprentice: 0",
        "🟣 Guru: 0",
        "🔵 Master: 0",
        "🔷 Enlightened: 0",
        "⚪ Burned: 0",
    ]
