import pytest
from romaji import to_hiragana


@pytest.mark.parametrize(
    ("romaji", "kana"),
    [
        ("taberu", "たべる"),
        ("kitte", "きって"),
        ("konnichiwa", "こんにちわ"),
        ("onna", "おんな"),
        ("kannji", "かんじ"),
        ("san'ya", "さんや"),
        ("shuukan", "しゅうかん"),
        ("chotto", "ちょっと"),
        ("ryokou", "りょこう"),
        ("hon", "ほん"),
        ("ra-men", "らーめん"),
        ("x1", "x1"),
    ],
)
def test_converts_romaji(romaji: str, kana: str) -> None:
    assert to_hiragana(romaji) == kana
