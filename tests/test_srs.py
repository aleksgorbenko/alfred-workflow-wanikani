import datetime as dt

from srs import eta_to_burn, format_days_until

SYSTEM = {
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


def test_sums_remaining_intervals_up_to_burn():
    eta = eta_to_burn("2024-01-01T00:00:00.000000Z", 8, SYSTEM)
    assert eta == dt.datetime(2024, 1, 1, tzinfo=dt.UTC)


def test_adds_enlightened_interval_when_at_master():
    eta = eta_to_burn("2024-01-01T00:00:00.000000Z", 7, SYSTEM)
    assert eta == dt.datetime(2024, 1, 1, tzinfo=dt.UTC) + dt.timedelta(seconds=7776000)


def test_returns_none_when_already_burned():
    assert eta_to_burn("2024-01-01T00:00:00.000000Z", 9, SYSTEM) is None


def test_format_days_until_rounds_down():
    now = dt.datetime(2024, 1, 1, tzinfo=dt.UTC)
    eta = now + dt.timedelta(days=5, hours=3)
    assert format_days_until(eta, now) == "burns in ~5d"


def test_format_days_until_handles_under_a_day():
    now = dt.datetime(2024, 1, 1, tzinfo=dt.UTC)
    eta = now + dt.timedelta(hours=3)
    assert format_days_until(eta, now) == "burns in <1d"
