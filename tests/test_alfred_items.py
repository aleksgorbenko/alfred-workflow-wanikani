from alfred_items import bold, item


def test_bolds_uppercase_letters_and_digits() -> None:
    assert bold("W5") == "𝐖𝟓"


def test_bolds_multi_digit_numbers() -> None:
    assert bold("W12") == "𝐖𝟏𝟐"


def test_leaves_lowercase_and_punctuation_unchanged() -> None:
    assert bold("a-b") == "a-b"


def test_item_omits_icon_by_default() -> None:
    assert "icon" not in item(title="Title")


def test_item_wraps_icon_path_in_alfred_icon_object() -> None:
    result = item(title="Title", icon="icons/icon_kanji.png")
    assert result["icon"] == {"path": "icons/icon_kanji.png"}
