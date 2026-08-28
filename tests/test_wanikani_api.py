import urllib.error
from unittest.mock import patch

import pytest
from wanikani_api import (
    WanikaniAuthError,
    WanikaniError,
    get_assignments,
    get_level_progressions,
    get_review_statistics,
    get_subjects,
    get_summary,
    get_user,
)


@patch("wanikani_api.urllib.request.urlopen")
def test_get_summary_returns_data_object(mock_urlopen):
    payload = {"object": "report", "data": {"lessons": [], "reviews": []}}
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_summary("token")
    assert result == {"lessons": [], "reviews": []}
    assert mock_urlopen.called


@patch("wanikani_api.urllib.request.urlopen")
def test_get_summary_sends_auth_header(mock_urlopen):
    payload = {"data": {}}
    with patch("wanikani_api.json.load", return_value=payload):
        get_summary("secret-token")

    request = mock_urlopen.call_args[0][0]
    assert request.get_header("Authorization") == "Bearer secret-token"
    assert request.get_header("Wanikani-revision") == "20170710"


@patch("wanikani_api.urllib.request.urlopen")
def test_get_summary_raises_auth_error_on_401(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="", code=401, msg="Unauthorized", hdrs=None, fp=None
    )
    with pytest.raises(WanikaniAuthError):
        get_summary("bad-token")


@patch("wanikani_api.urllib.request.urlopen")
def test_get_summary_raises_wanikani_error_on_other_http_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="", code=500, msg="Server Error", hdrs=None, fp=None
    )
    with pytest.raises(WanikaniError):
        get_summary("token")


@patch("wanikani_api.urllib.request.urlopen")
def test_get_summary_raises_wanikani_error_on_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("no network")
    with pytest.raises(WanikaniError):
        get_summary("token")


@patch("wanikani_api.urllib.request.urlopen")
def test_get_user_returns_data_object(mock_urlopen):
    payload = {"object": "user", "data": {"username": "aleks", "level": 12}}
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_user("token")
    assert result == {"username": "aleks", "level": 12}
    assert mock_urlopen.called


@patch("wanikani_api.urllib.request.urlopen")
def test_get_level_progressions_unwraps_collection(mock_urlopen):
    payload = {
        "object": "collection",
        "pages": {"next_url": None},
        "data": [
            {"object": "level_progression", "data": {"level": 1}},
            {"object": "level_progression", "data": {"level": 2}},
        ],
    }
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_level_progressions("token")
    assert result == [{"level": 1}, {"level": 2}]
    assert mock_urlopen.called


@patch("wanikani_api.urllib.request.urlopen")
def test_get_level_progressions_follows_pagination(mock_urlopen):
    page_one = {
        "pages": {"next_url": "https://api.wanikani.com/v2/level_progressions?page=2"},
        "data": [{"object": "level_progression", "data": {"level": 1}}],
    }
    page_two = {
        "pages": {"next_url": None},
        "data": [{"object": "level_progression", "data": {"level": 2}}],
    }
    with patch("wanikani_api.json.load", side_effect=[page_one, page_two]):
        result = get_level_progressions("token")

    assert result == [{"level": 1}, {"level": 2}]
    urls_requested = [call.args[0].full_url for call in mock_urlopen.call_args_list]
    assert urls_requested == [
        "https://api.wanikani.com/v2/level_progressions",
        "https://api.wanikani.com/v2/level_progressions?page=2",
    ]


@patch("wanikani_api.urllib.request.urlopen")
def test_get_assignments_sends_query_params(mock_urlopen):
    payload = {"pages": {"next_url": None}, "data": []}
    with patch("wanikani_api.json.load", return_value=payload):
        get_assignments("token", started="true")

    request = mock_urlopen.call_args[0][0]
    assert request.full_url == "https://api.wanikani.com/v2/assignments?started=true"


@patch("wanikani_api.urllib.request.urlopen")
def test_get_assignments_unwraps_collection(mock_urlopen):
    payload = {
        "pages": {"next_url": None},
        "data": [{"object": "assignment", "data": {"srs_stage": 3}}],
    }
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_assignments("token")
    assert result == [{"srs_stage": 3}]
    assert mock_urlopen.called


@patch("wanikani_api.urllib.request.urlopen")
def test_get_review_statistics_unwraps_collection(mock_urlopen):
    payload = {
        "pages": {"next_url": None},
        "data": [{"object": "review_statistic", "data": {"percentage_correct": 60}}],
    }
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_review_statistics("token", percentages_less_than="80")
    assert result == [{"percentage_correct": 60}]

    request = mock_urlopen.call_args[0][0]
    assert request.full_url == (
        "https://api.wanikani.com/v2/review_statistics?percentages_less_than=80"
    )


@patch("wanikani_api.urllib.request.urlopen")
def test_get_subjects_includes_id_and_subject_type(mock_urlopen):
    payload = {
        "pages": {"next_url": None},
        "data": [
            {"id": 440, "object": "kanji", "data": {"characters": "大", "slug": "big"}}
        ],
    }
    with patch("wanikani_api.json.load", return_value=payload):
        result = get_subjects("token", ids="440")

    assert result == [
        {"id": 440, "subject_type": "kanji", "characters": "大", "slug": "big"}
    ]
    assert mock_urlopen.called
