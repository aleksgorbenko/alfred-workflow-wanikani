#!/usr/bin/env python3
"""Render the row-icon set: solid rounded square + one centered glyph.

Colors match WaniKani's own subject-type colors (radical/kanji/vocabulary).
Adapted from alfred-workflow-nihongo/scripts/gen_icons.py.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FG = "#fcfcfc"
FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
SIZE = 512
SS = 4  # supersample factor
RADIUS = 0.22  # corner radius as fraction of size
GLYPH = 0.62  # glyph height as fraction of size
FIT_TOLERANCE = 2  # px; stop resizing once the glyph is this close to target

# subject_type -> (glyph, background color). Icon files are always named
# icon_{subject_type}.png so build_items() can look them up directly.
ICONS = {
    "radical": ("部", "#4CA8F8"),
    "kanji": ("字", "#EA33A7"),
    "vocabulary": ("語", "#9C1FF6"),
}


def fit_font(char: str, target: int) -> ImageFont.FreeTypeFont:
    size = target
    for _ in range(24):
        font = ImageFont.truetype(FONT, size)
        box = font.getbbox(char)
        height = box[3] - box[1]
        width = box[2] - box[0]
        longest = max(height, width)
        if abs(longest - target) <= FIT_TOLERANCE:
            return font
        size = max(1, round(size * target / longest))
    return ImageFont.truetype(FONT, size)


def render(char: str, bg: str, out: Path) -> None:
    canvas = SIZE * SS
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (0, 0, canvas - 1, canvas - 1), radius=RADIUS * canvas, fill=bg
    )

    font = fit_font(char, round(GLYPH * canvas))
    box = font.getbbox(char)
    x = (canvas - (box[2] + box[0])) / 2
    y = (canvas - (box[3] + box[1])) / 2
    draw.text((x, y), char, font=font, fill=FG)

    img.resize((SIZE, SIZE), Image.LANCZOS).save(out)


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "icons"
    wanted = sys.argv[1:] or list(ICONS)
    for key in wanted:
        if key not in ICONS:
            print(f"unknown key: {key}", file=sys.stderr)
            return 1
        glyph, bg = ICONS[key]
        path = out_dir / f"icon_{key}.png"
        render(glyph, bg, path)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
