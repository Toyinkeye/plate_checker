import re

FORMATS = {
    "UK current": r"[A-Z]{2}\d{2}[A-Z]{3}",
    "UK prefix": r"[A-Z]\d{1,3}[A-Z]{3}",
    "UK suffix": r"[A-Z]{3}\d{1,3}[A-Z]",
    "UK dateless": r"[A-Z]{1,3}\d{1,4}|\d{1,4}[A-Z]{1,3}",
    "India": r"[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}",
}

TO_DIGIT = {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1", "Z": "2", "S": "5", "G": "6", "B": "8"}
TO_LETTER = {"0": "O", "1": "I", "2": "Z", "5": "S", "6": "G", "8": "B"}


def normalize(text):
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def match_format(plate):
    for name, rx in FORMATS.items():
        if re.fullmatch(rx, plate):
            return name
    return None


def fix_uk_current(plate):
    """AB12CDE: letters in positions 0,1,4,5,6 and digits in 2,3."""
    if len(plate) != 7:
        return plate
    out = []
    for ch, kind in zip(plate, "LLDDLLL"):
        out.append(TO_DIGIT.get(ch, ch) if kind == "D" else TO_LETTER.get(ch, ch))
    return "".join(out)


def resolve(raw):
    """Returns (plate, format_name or None, was_corrected)."""
    plate = normalize(raw)
    fmt = match_format(plate)
    if fmt:
        return plate, fmt, False
    fixed = fix_uk_current(plate)
    fmt = match_format(fixed)
    if fmt and fixed != plate:
        return fixed, fmt, True
    return plate, None, False


def distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def nearest(plate, saved):
    """First saved plate that differs by exactly one character."""
    for row in saved:
        if distance(plate, row["plate"]) == 1:
            return row
    return None