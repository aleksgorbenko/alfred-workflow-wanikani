#!/usr/bin/env python3
"""Render the 'wk' List Filter row icons: emoji centered on a rounded blue square."""

import sys
from pathlib import Path

from gen_icons import RADIUS, SIZE, SS
from PIL import Image, ImageDraw, ImageFont

BG = "#9C1FF6"  # same purple as icon_vocabulary.png
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI_NATIVE_SIZE = 160  # largest embedded Apple Color Emoji bitmap strike
GLYPH = 0.62  # glyph height as fraction of size, matches gen_icons.py

# command (List Filter item `arg`) -> emoji
ICONS = {
    "summary": "📋",
    "levels": "🪜",
    "stats": "📊",
    "accuracy": "🎯",
    "leeches": "🪱",
    "lessons": "📚",
    "reviews": "🔁",
}


def render(emoji: str, out: Path) -> None:
    canvas = SIZE * SS
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (0, 0, canvas - 1, canvas - 1), radius=RADIUS * canvas, fill=BG
    )

    font = ImageFont.truetype(EMOJI_FONT, EMOJI_NATIVE_SIZE)
    glyph = Image.new("RGBA", (EMOJI_NATIVE_SIZE, EMOJI_NATIVE_SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(glyph).text((0, 0), emoji, font=font, embedded_color=True)

    target = round(GLYPH * canvas)
    glyph = glyph.resize((target, target), Image.Resampling.LANCZOS)  # pyright: ignore[reportUnknownMemberType]
    offset = ((canvas - target) // 2, (canvas - target) // 2)
    img.alpha_composite(glyph, offset)

    img.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(out)  # pyright: ignore[reportUnknownMemberType]


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "icons"
    wanted = sys.argv[1:] or list(ICONS)
    for key in wanted:
        if key not in ICONS:
            sys.stderr.write(f"unknown key: {key}\n")
            return 1
        path = out_dir / f"icon_{key}.png"
        render(ICONS[key], path)
        sys.stdout.write(f"{path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
