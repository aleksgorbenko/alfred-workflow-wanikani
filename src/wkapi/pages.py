"""Page rows cached between Script Filter runs, refreshed in the background."""

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cache import cache_dir

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

REFRESH_CLAIM_SECONDS = 120
PRIVATE_FILE = 0o600


@dataclass(frozen=True)
class PageHit:
    data: dict[str, Any]
    stale: bool


class PageCache:
    def __init__(self, clock: Callable[[], float], version: str) -> None:
        self._clock = clock
        self._version = version

    def read(self, name: str, max_age_seconds: int) -> PageHit | None:
        try:
            stored = json.loads(self._path(name, "json").read_text())
        except FileNotFoundError, ValueError:
            return None
        if stored.get("version") != self._version:
            return None
        age = self._clock() - stored["written_at"]
        return PageHit(stored["data"], age > max_age_seconds)

    def write(self, name: str, data: dict[str, Any]) -> None:
        stored = {"written_at": self._clock(), "version": self._version, "data": data}
        self._write(self._path(name, "json"), json.dumps(stored, ensure_ascii=False))

    def claim_refresh(self, name: str) -> bool:
        lock = self._path(name, "lock")
        try:
            claimed_at = float(lock.read_text())
        except FileNotFoundError, ValueError:
            claimed_at = float("-inf")
        if self._clock() - claimed_at < REFRESH_CLAIM_SECONDS:
            return False
        self._write(lock, str(self._clock()))
        return True

    def release_refresh(self, name: str) -> None:
        self._path(name, "lock").unlink(missing_ok=True)

    def _write(self, path: Path, text: str) -> None:
        partial = path.with_suffix(path.suffix + ".partial")
        descriptor = os.open(
            partial, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, PRIVATE_FILE
        )
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
        partial.chmod(PRIVATE_FILE)
        partial.replace(path)

    def _path(self, name: str, suffix: str) -> Path:
        return cache_dir() / f"page-{name}.{suffix}"
