VOWELS = "aiueo"
ROWS = {
    "": "あいうえお",
    "k": "かきくけこ",
    "g": "がぎぐげご",
    "s": "さしすせそ",
    "z": "ざじずぜぞ",
    "t": "たちつてと",
    "d": "だぢづでど",
    "n": "なにぬねの",
    "h": "はひふへほ",
    "b": "ばびぶべぼ",
    "p": "ぱぴぷぺぽ",
    "m": "まみむめも",
    "r": "らりるれろ",
    "w": "わゐうゑを",
}
YOON = {
    "ky": "き",
    "gy": "ぎ",
    "sh": "し",
    "j": "じ",
    "ch": "ち",
    "ny": "に",
    "hy": "ひ",
    "by": "び",
    "py": "ぴ",
    "my": "み",
    "ry": "り",
}
SMALL = {"a": "ゃ", "u": "ゅ", "o": "ょ"}
SPECIAL = {
    "shi": "し",
    "chi": "ち",
    "tsu": "つ",
    "fu": "ふ",
    "ji": "じ",
    "ya": "や",
    "yu": "ゆ",
    "yo": "よ",
    "-": "ー",
}
LONGEST = 3


def _table() -> dict[str, str]:
    table = dict(SPECIAL)
    for consonant, kana in ROWS.items():
        table.update({consonant + vowel: kana[i] for i, vowel in enumerate(VOWELS)})
    for prefix, kana in YOON.items():
        table.update({prefix + vowel: kana + SMALL[vowel] for vowel in SMALL})
    table.update({"sha": "しゃ", "shu": "しゅ", "sho": "しょ"})
    table.update({"cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ"})
    table.update({"ja": "じゃ", "ju": "じゅ", "jo": "じょ"})
    return table


TABLE = _table()


def _nasal(text: str, index: int) -> bool:
    following = text[index + 1 : index + 2]
    return following == "" or (following not in VOWELS and following != "y")


def _nasal_width(text: str, index: int) -> int:
    following = text[index + 1 : index + 2]
    after = text[index + 2 : index + 3]
    if following == "'" or (following == "n" and after not in (*VOWELS, "y")):
        return 2
    return 1


def to_hiragana(text: str) -> str:
    text = text.lower()
    out: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "n" and _nasal(text, index):
            out.append("ん")
            index += _nasal_width(text, index)
            continue
        following = text[index + 1 : index + 2]
        if char == following and char.isalpha() and char not in VOWELS:
            out.append("っ")
            index += 1
            continue
        for size in range(LONGEST, 0, -1):
            kana = TABLE.get(text[index : index + size])
            if kana is not None:
                out.append(kana)
                index += size
                break
        else:
            out.append(char)
            index += 1
    return "".join(out)
