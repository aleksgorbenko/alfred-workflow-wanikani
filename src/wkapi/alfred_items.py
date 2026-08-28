"""Helpers for building Alfred Script Filter JSON output."""

import json
import sys

_BOLD_UPPER_A = 0x1D400
_BOLD_DIGIT_0 = 0x1D7CE

TYPE_ICONS = {
    "radical": "icons/icon_radical.png",
    "kanji": "icons/icon_kanji.png",
    "vocabulary": "icons/icon_vocabulary.png",
}


def bold(text: str) -> str:
    """Render ASCII uppercase letters/digits as Mathematical Bold Unicode.

    Alfred's subtitle field has no markup support, so this is the only way
    to make part of a subtitle visually stand out.
    """
    chars = []
    for ch in text:
        if ch.isascii() and "A" <= ch <= "Z":
            chars.append(chr(_BOLD_UPPER_A + (ord(ch) - ord("A"))))
        elif ch.isascii() and ch.isdigit():
            chars.append(chr(_BOLD_DIGIT_0 + (ord(ch) - ord("0"))))
        else:
            chars.append(ch)
    return "".join(chars)


def item(
    title: str,
    subtitle: str = "",
    arg: str | None = None,
    valid: bool = True,
    icon: str | None = None,
) -> dict:
    result: dict = {"title": title, "subtitle": subtitle, "valid": valid}
    if arg is not None:
        result["arg"] = arg
    if icon is not None:
        result["icon"] = {"path": icon}
    return result


def error_item(message: str) -> dict:
    return item(title=message, valid=False)


def emit(items: list[dict]) -> None:
    json.dump({"items": items}, sys.stdout)
