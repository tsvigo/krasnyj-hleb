#!/usr/bin/env python3
"""Проход 14: разделы 5-6 — порядок глав XV, ярлык VII, шапка ТОС. Только проект."""
from pathlib import Path
import re

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
lines = P.read_text(encoding="utf-8").splitlines()

# --- перестановка главы XV на место (после XIV, перед XVI) ---
assert lines[164] == "ГЛАВА XV", lines[164]
assert lines[253] == "ГЛАВА I", lines[253]
assert lines[3712] == "ГЛАВА XVI", lines[3712]
block = lines[164:253]
assert block[-1] == "" and block[-5] == "КРАСНЫЙ ХЛЕБ", (block[-5], block[-1])
new = lines[:164] + lines[253:3712] + block + lines[3712:]

# проверка порядка глав
heads = [(i + 1, l.strip()) for i, l in enumerate(new) if re.fullmatch(r"ГЛАВА [IVXLCDM]+ ?", l.strip())]
order = [h[1].split()[1].rstrip() for h in heads]
assert order == ["I", "II", "III", "IV", "V", "VI", "VIII", "IX", "X", "XI",
                 "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"], order
print("порядок глав:", "OK (VII ярлык следующим шагом)")

t = "\n".join(new)

PAIRS = [
    ("ГЛАВА ЛИЦО", "ГЛАВА — СТР.", 1),
    ("120 \n\nЕЖЕДНЕВНОЕ ИСПЫТАНИЕ", "120 \n\nГЛАВА VII\n\n\nЕЖЕДНЕВНОЕ ИСПЫТАНИЕ", 1),
    ("НОВОЙ ДЕВУШКА", "НОВАЯ ДЕВУШКА", 3),
]
errors = []
for old, new_, exp in PAIRS:
    c = t.count(old)
    if c != exp:
        errors.append(f"ОЖИДАЛОСЬ {exp}, НАЙДЕНО {c}: {old[:60]!r}")
        continue
    t = t.replace(old, new_)
if errors:
    print("ОШИБКИ (файл НЕ записан):")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
P.write_text(t, encoding="utf-8")
print("OK: перестановка + 3 правки")
