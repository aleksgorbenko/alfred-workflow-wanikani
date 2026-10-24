import stat

from cache import cache_dir
from pages import REFRESH_CLAIM_SECONDS, PageCache


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_missing_page_reads_none() -> None:
    assert PageCache(Clock(), "v1").read("summary", 60) is None


def test_written_page_reads_fresh_then_stale() -> None:
    clock = Clock()
    pages = PageCache(clock, "v1")
    pages.write("summary", {"rows": [{"title": "大"}]})
    hit = pages.read("summary", 60)
    assert hit is not None
    assert hit.data == {"rows": [{"title": "大"}]}
    assert hit.stale is False
    clock.now += 61
    stale = pages.read("summary", 60)
    assert stale is not None
    assert stale.stale is True


def test_new_code_version_ignores_old_pages() -> None:
    clock = Clock()
    PageCache(clock, "v1").write("summary", {"rows": []})
    assert PageCache(clock, "v2").read("summary", 60) is None


def test_page_file_is_private() -> None:
    PageCache(Clock(), "v1").write("summary", {"rows": []})
    modes = {stat.S_IMODE(path.stat().st_mode) for path in cache_dir().glob("page-*")}
    assert modes == {0o600}


def test_claim_is_exclusive_until_released() -> None:
    pages = PageCache(Clock(), "v1")
    assert pages.claim_refresh("summary") is True
    assert pages.claim_refresh("summary") is False
    pages.release_refresh("summary")
    assert pages.claim_refresh("summary") is True


def test_abandoned_claim_expires() -> None:
    clock = Clock()
    pages = PageCache(clock, "v1")
    assert pages.claim_refresh("summary") is True
    clock.now += REFRESH_CLAIM_SECONDS + 1
    assert pages.claim_refresh("summary") is True
