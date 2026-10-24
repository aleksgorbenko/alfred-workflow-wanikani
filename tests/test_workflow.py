import json
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import accuracy
import leeches
import levels
import stats
import summary
from app import PAGES
from pages import PageCache
from workflow import LOADERS, code_version, main, spawn_refresh

if TYPE_CHECKING:
    import pytest


def test_every_page_has_a_loader() -> None:
    assert set(LOADERS) == set(PAGES)


def test_main_prints_menu(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("WANIKANI_API_TOKEN", raising=False)
    main([])
    assert len(json.loads(capsys.readouterr().out)["items"]) == len(PAGES)


def _one_row(_token: str) -> list[dict[str, str]]:
    return [{"title": "大"}]


def test_main_refresh_stores_page(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WANIKANI_API_TOKEN", "token")
    monkeypatch.setitem(LOADERS, "summary", _one_row)
    main(["--refresh", "summary"])
    hit = PageCache(time.time, code_version()).read("summary", 60)
    assert hit is not None
    assert hit.data == {"rows": [{"title": "大"}]}


@patch("subprocess.Popen")
def test_spawn_refresh_runs_detached(popen: MagicMock) -> None:
    spawn_refresh("summary")
    command = popen.call_args.args[0]
    assert command[-2:] == ["--refresh", "summary"]
    assert popen.call_args.kwargs["start_new_session"] is True


@patch("summary.get_user", return_value={"level": 3})
@patch("summary.get_summary", return_value={"lessons": [], "reviews": []})
def test_summary_load(*_mocks: MagicMock) -> None:
    assert summary.load("token")[0]["title"] == "🎓 Level 3"


@patch("stats.get_assignments", return_value=[{"srs_stage": 9}])
def test_stats_load(*_mocks: MagicMock) -> None:
    assert stats.load("token")[-1]["title"] == "⚪ Burned: 1"


@patch("accuracy.get_review_statistics", return_value=[])
def test_accuracy_load(*_mocks: MagicMock) -> None:
    assert accuracy.load("token")[0]["title"] == "🎯 Overall accuracy: 0%"


@patch("leeches.get_spaced_repetition_systems", return_value=[])
@patch("leeches.get_review_statistics", return_value=[])
def test_leeches_load_without_leeches(*_mocks: MagicMock) -> None:
    assert leeches.load("token")[0]["valid"] is False


@patch("levels.get_spaced_repetition_systems", return_value=[])
@patch("levels.get_assignments", return_value=[])
@patch("levels.get_subjects", return_value=[])
@patch("levels.get_user", return_value={"level": 1})
@patch("levels.get_level_progressions", return_value=[])
def test_levels_load(*_mocks: MagicMock) -> None:
    assert levels.load("token")[0]["title"] == "🎉 Ready to level up!"
