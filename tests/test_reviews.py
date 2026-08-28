from unittest.mock import patch

from reviews import main


@patch("reviews.get_subjects")
@patch("reviews.get_summary")
@patch("reviews.emit")
def test_uses_reviews_bucket_from_summary(
    mock_emit, mock_get_summary, mock_get_subjects
):
    mock_get_summary.return_value = {
        "reviews": [
            {
                "available_at": "2020-01-01T00:00:00.000000Z",
                "subject_ids": [7],
            }
        ]
    }
    mock_get_subjects.return_value = [
        {"id": 7, "subject_type": "vocabulary", "characters": "見物", "meanings": []},
    ]

    with patch.dict("os.environ", {"WANIKANI_API_TOKEN": "token"}):
        main()

    mock_get_subjects.assert_called_once_with("token", ttl_seconds=3 * 60 * 60, ids="7")
    items = mock_emit.call_args[0][0]
    assert len(items) == 1


@patch("reviews.emit")
def test_missing_token_emits_error(mock_emit):
    with patch.dict("os.environ", {"WANIKANI_API_TOKEN": ""}):
        main()

    items = mock_emit.call_args[0][0]
    assert items[0]["valid"] is False
