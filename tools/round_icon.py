#!/usr/bin/env python3
"""Round an existing PNG's corners to match the generated icon set's radius."""

import sys
from pathlib import Path

from gen_icons import RADIUS, SS
from PIL import Image, ImageChops, ImageDraw


def round_corners(input_path: Path, output_path: Path) -> None:
    img = Image.open(input_path).convert("RGBA")
    size = img.size[0]
    canvas = size * SS

    img_ss = img.resize((canvas, canvas), Image.LANCZOS)
    mask = Image.new("L", (canvas, canvas), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, canvas - 1, canvas - 1), radius=RADIUS * canvas, fill=255
    )

    alpha = ImageChops.multiply(img_ss.getchannel("A"), mask)
    img_ss.putalpha(alpha)
    img_ss.resize((size, size), Image.LANCZOS).save(output_path)


_EXPECTED_ARGC = 3


def main() -> int:
    if len(sys.argv) != _EXPECTED_ARGC:
        print("usage: round_icon.py <input.png> <output.png>", file=sys.stderr)
        return 1
    round_corners(Path(sys.argv[1]), Path(sys.argv[2]))
    print(sys.argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
