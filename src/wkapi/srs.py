"""ETA-to-burn math from WaniKani's spaced_repetition_systems interval tables."""

import datetime as dt


def _parse(timestamp: str) -> dt.datetime:
    return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def _eta_to_stage(
    available_at: str, srs_stage: int, srs_system: dict, target_position: int
) -> dt.datetime | None:
    """Optimistic ETA to reach `target_position` if every review is passed on time."""
    if srs_stage >= target_position:
        return None

    stages_by_position = {stage["position"]: stage for stage in srs_system["stages"]}
    eta = _parse(available_at)
    for position in range(srs_stage + 1, target_position):
        stage = stages_by_position.get(position)
        if stage is None or stage["interval"] is None:
            return None
        eta += dt.timedelta(seconds=stage["interval"])
    return eta


def eta_to_burn(
    available_at: str, srs_stage: int, srs_system: dict
) -> dt.datetime | None:
    """Optimistic burn date if every remaining review is passed on time."""
    return _eta_to_stage(
        available_at, srs_stage, srs_system, srs_system["burning_stage_position"]
    )


def eta_to_pass(
    available_at: str, srs_stage: int, srs_system: dict
) -> dt.datetime | None:
    """Optimistic Guru (passing) date if every remaining review is passed on time."""
    return _eta_to_stage(
        available_at, srs_stage, srs_system, srs_system["passing_stage_position"]
    )


def format_days_until(eta: dt.datetime, now: dt.datetime) -> str:
    days = (eta - now).days
    return "burns in <1d" if days < 1 else f"burns in ~{days}d"
