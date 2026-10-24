from unittest.mock import MagicMock, patch

import lessons
import reviews

BUCKET = {"available_at": "2020-01-01T00:00:00.000000Z", "subject_ids": [1, 2]}
SUBJECTS: list[dict[str, object]] = [
    {"id": 1, "subject_type": "kanji", "characters": "大", "meanings": []},
    {"id": 2, "subject_type": "kanji", "characters": "小", "meanings": []},
]
SUMMARY = {"lessons": [BUCKET], "reviews": []}


@patch("subject_queue.get_subjects", return_value=SUBJECTS)
@patch("subject_queue.get_summary", return_value=SUMMARY)
def test_lessons_use_lessons_bucket(
    mock_get_summary: MagicMock, mock_get_subjects: MagicMock
) -> None:
    rows = lessons.load("token")
    mock_get_summary.assert_called_once_with("token")
    mock_get_subjects.assert_called_once_with(
        "token", ttl_seconds=3 * 60 * 60, ids="1,2"
    )
    assert [row["title"] for row in rows] == ["大", "小"]


@patch("subject_queue.get_subjects")
@patch("subject_queue.get_summary", return_value=SUMMARY)
def test_empty_reviews_skip_subject_fetch(
    mock_get_summary: MagicMock, mock_get_subjects: MagicMock
) -> None:
    rows = reviews.load("token")
    mock_get_summary.assert_called_once_with("token")
    mock_get_subjects.assert_not_called()
    assert rows[0]["title"] == "🎉 No reviews available"
