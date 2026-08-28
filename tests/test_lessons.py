from unittest.mock import patch

from lessons import main


@patch("lessons.get_subjects")
@patch("lessons.get_summary")
@patch("lessons.emit")
def test_uses_lessons_bucket_from_summary(
    mock_emit, mock_get_summary, mock_get_subjects
):
    mock_get_summary.return_value = {
        "lessons": [
            {
                "available_at": "2020-01-01T00:00:00.000000Z",
                "subject_ids": [1, 2],
            }
        ]
    }
    mock_get_subjects.return_value = [
        {"id": 1, "subject_type": "kanji", "characters": "大", "meanings": []},
        {"id": 2, "subject_type": "kanji", "characters": "小", "meanings": []},
    ]

    with patch.dict("os.environ", {"WANIKANI_API_TOKEN": "token"}):
        main()

    mock_get_subjects.assert_called_once_with(
        "token", ttl_seconds=3 * 60 * 60, ids="1,2"
    )
    items = mock_emit.call_args[0][0]
    expected_count = 2
    assert len(items) == expected_count


@patch("lessons.emit")
def test_missing_token_emits_error(mock_emit):
    with patch.dict("os.environ", {"WANIKANI_API_TOKEN": ""}):
        main()

    items = mock_emit.call_args[0][0]
    assert items[0]["valid"] is False
