import json
import os
import subprocess
import sys
import time
from pathlib import Path

import accuracy
import leeches
import lessons
import levels
import reviews
import stats
import summary
from app import Deps, refresh, run
from pages import PageCache

LOADERS = {
    "summary": summary.load,
    "levels": levels.load,
    "stats": stats.load,
    "accuracy": accuracy.load,
    "leeches": leeches.load,
    "lessons": lessons.load,
    "reviews": reviews.load,
}


def code_version() -> str:
    sources = Path(__file__).resolve().parent.glob("*.py")
    return str(max(source.stat().st_mtime for source in sources))


def spawn_refresh(name: str) -> None:
    subprocess.Popen(  # noqa: S603
        [sys.executable, __file__, "--refresh", name],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def build_deps() -> Deps:
    return Deps(
        os.environ.get("WANIKANI_API_TOKEN", "").strip(),
        LOADERS,
        PageCache(time.time, code_version()),
        spawn_refresh,
    )


def main(argv: list[str]) -> None:
    deps = build_deps()
    if argv[:1] == ["--refresh"]:
        refresh(argv[1], deps)
        return
    query = argv[0] if argv else ""
    sys.stdout.write(json.dumps(run(query, deps), ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
