"""Minimal WaniKani API v2 client (stdlib only, no third-party deps)."""

import http
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from cache import cached

API_BASE = "https://api.wanikani.com/v2"
API_REVISION = "20170710"

ONE_HOUR = 3600
ONE_DAY = 86400
ONE_MONTH = 30 * ONE_DAY


class WanikaniError(Exception):
    """Raised for any WaniKani API failure."""


class WanikaniAuthError(WanikaniError):
    """Raised when the API token is missing or rejected (401)."""


def _get(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Wanikani-Revision": API_REVISION,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == http.HTTPStatus.UNAUTHORIZED:
            msg = "Invalid or missing WaniKani API token"
            raise WanikaniAuthError(msg) from error
        msg = f"WaniKani API returned HTTP {error.code}"
        raise WanikaniError(msg) from error
    except urllib.error.URLError as error:
        msg = f"Could not reach WaniKani API: {error.reason}"
        raise WanikaniError(msg) from error


def get_summary(token: str, ttl_seconds: int = ONE_HOUR) -> dict[str, Any]:
    """Fetch GET /v2/summary and return the parsed `data` object."""
    url = f"{API_BASE}/summary"
    return cached(url, ttl_seconds, lambda: _get(url, token))["data"]


def get_user(token: str) -> dict[str, Any]:
    """Fetch GET /v2/user and return the parsed `data` object."""
    url = f"{API_BASE}/user"
    return cached(url, ONE_HOUR, lambda: _get(url, token))["data"]


def _fetch_collection(
    path: str, token: str, params: dict[str, str]
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}" + (f"?{query}" if query else "")
    while url:
        body = _get(url, token)
        entries.extend(entry["data"] for entry in body["data"])
        url = body["pages"]["next_url"]
    return entries


def _get_collection(
    path: str, token: str, ttl_seconds: int, **params: str
) -> list[dict[str, Any]]:
    """Fetch all pages of a GET /v2/<path> collection, unwrapped to plain dicts."""
    query = urllib.parse.urlencode(params)
    cache_key = f"{API_BASE}/{path}" + (f"?{query}" if query else "")

    def fetch() -> list[dict[str, Any]]:
        return _fetch_collection(path, token, params)

    return cached(cache_key, ttl_seconds, fetch)


def get_level_progressions(token: str) -> list[dict[str, Any]]:
    """Fetch all pages of GET /v2/level_progressions, unwrapped to plain dicts."""
    return _get_collection("level_progressions", token, ONE_HOUR)


def get_assignments(token: str, **params: str) -> list[dict[str, Any]]:
    """Fetch all pages of GET /v2/assignments, unwrapped to plain dicts."""
    return _get_collection("assignments", token, ONE_HOUR, **params)


def get_review_statistics(token: str, **params: str) -> list[dict[str, Any]]:
    """Fetch all pages of GET /v2/review_statistics, unwrapped to plain dicts."""
    return _get_collection("review_statistics", token, ONE_HOUR, **params)


def get_spaced_repetition_systems(
    token: str, ttl_seconds: int = ONE_DAY
) -> list[dict[str, Any]]:
    """Fetch all pages of GET /v2/spaced_repetition_systems, including id."""

    def fetch() -> list[dict[str, Any]]:
        systems: list[dict[str, Any]] = []
        url = f"{API_BASE}/spaced_repetition_systems"
        while url:
            body = _get(url, token)
            systems.extend(
                {"id": entry["id"], **entry["data"]} for entry in body["data"]
            )
            url = body["pages"]["next_url"]
        return systems

    cache_key = f"{API_BASE}/spaced_repetition_systems"
    return cached(cache_key, ttl_seconds, fetch)


def get_subjects(
    token: str, ttl_seconds: int = ONE_DAY, **params: str
) -> list[dict[str, Any]]:
    """Fetch all pages of GET /v2/subjects, including id and subject type."""

    def fetch() -> list[dict[str, Any]]:
        subjects: list[dict[str, Any]] = []
        query = urllib.parse.urlencode(params)
        url = f"{API_BASE}/subjects" + (f"?{query}" if query else "")
        while url:
            body = _get(url, token)
            subjects.extend(
                {"id": entry["id"], "subject_type": entry["object"], **entry["data"]}
                for entry in body["data"]
            )
            url = body["pages"]["next_url"]
        return subjects

    query = urllib.parse.urlencode(params)
    cache_key = f"{API_BASE}/subjects" + (f"?{query}" if query else "")
    return cached(cache_key, ttl_seconds, fetch)
