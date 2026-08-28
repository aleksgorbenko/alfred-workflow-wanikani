"""Minimal WaniKani API v2 client (stdlib only, no third-party deps)."""

import http
import json
import urllib.error
import urllib.parse
import urllib.request

from cache import cached

API_BASE = "https://api.wanikani.com/v2"
API_REVISION = "20170710"

ONE_HOUR = 3600
ONE_DAY = 86400


class WanikaniError(Exception):
    """Raised for any WaniKani API failure."""


class WanikaniAuthError(WanikaniError):
    """Raised when the API token is missing or rejected (401)."""


def _get(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Wanikani-Revision": API_REVISION,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == http.HTTPStatus.UNAUTHORIZED:
            raise WanikaniAuthError("Invalid or missing WaniKani API token") from error
        raise WanikaniError(f"WaniKani API returned HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise WanikaniError(f"Could not reach WaniKani API: {error.reason}") from error


def get_summary(token: str, ttl_seconds: int = ONE_HOUR) -> dict:
    """Fetch GET /v2/summary and return the parsed `data` object."""
    url = f"{API_BASE}/summary"
    return cached(url, ttl_seconds, lambda: _get(url, token))["data"]


def get_user(token: str) -> dict:
    """Fetch GET /v2/user and return the parsed `data` object."""
    url = f"{API_BASE}/user"
    return cached(url, ONE_HOUR, lambda: _get(url, token))["data"]


def _fetch_collection(path: str, token: str, params: dict[str, str]) -> list[dict]:
    entries = []
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}" + (f"?{query}" if query else "")
    while url:
        body = _get(url, token)
        entries.extend(entry["data"] for entry in body["data"])
        url = body["pages"]["next_url"]
    return entries


def _get_collection(
    path: str, token: str, ttl_seconds: int, **params: str
) -> list[dict]:
    """Fetch all pages of a GET /v2/<path> collection, unwrapped to plain dicts."""
    query = urllib.parse.urlencode(params)
    cache_key = f"{API_BASE}/{path}" + (f"?{query}" if query else "")

    def fetch() -> list[dict]:
        return _fetch_collection(path, token, params)

    return cached(cache_key, ttl_seconds, fetch)


def get_level_progressions(token: str) -> list[dict]:
    """Fetch all pages of GET /v2/level_progressions, unwrapped to plain dicts."""
    return _get_collection("level_progressions", token, ONE_HOUR)


def get_assignments(token: str, **params: str) -> list[dict]:
    """Fetch all pages of GET /v2/assignments, unwrapped to plain dicts."""
    return _get_collection("assignments", token, ONE_HOUR, **params)


def get_review_statistics(token: str, **params: str) -> list[dict]:
    """Fetch all pages of GET /v2/review_statistics, unwrapped to plain dicts."""
    return _get_collection("review_statistics", token, ONE_HOUR, **params)


def get_spaced_repetition_systems(token: str, ttl_seconds: int = ONE_DAY) -> list[dict]:
    """Fetch all pages of GET /v2/spaced_repetition_systems, including id."""

    def fetch() -> list[dict]:
        systems = []
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


def get_subjects(token: str, ttl_seconds: int = ONE_DAY, **params: str) -> list[dict]:
    """Fetch all pages of GET /v2/subjects, including id and subject type."""

    def fetch() -> list[dict]:
        subjects = []
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
