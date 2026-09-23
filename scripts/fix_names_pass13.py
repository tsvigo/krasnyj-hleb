#!/usr/bin/env python3
"""Проход 13: раздел 4 — имена собственные. Только папка проекта."""
from pathlib import Path

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
t = P.read_text(encoding="utf-8")

PAIRS = [
    ("Адария", "Дарья", 5),
    ("Адарию", "Дарью", 2),
    ("Адарии", "Дарье", 1),
    ("Аврам", "Абрам", 4),
    ("Ефдокина", "Евдокима", 1),
    ("подобно Исаку", "подобно Исааку", 1),
]

errors, n = [], 0
for old, new, exp in PAIRS:
    c = t.count(old)
    if c != exp:
        errors.append(f"ОЖИДАЛОСЬ {exp}, НАЙДЕНО {c}: {old!r}")
        continue
    t = t.replace(old, new)
    n += c

# Петр (именит., без ё) -> Пётр; косвенные уже с ё где надо
import re
c = len(re.findall(r"\bПетр\b", t))
if c != 5:
    errors.append(f"Петр: ОЖИДАЛОСЬ 5, НАЙДЕНО {c}")
else:
    t = re.sub(r"\bПетр\b", "Пётр", t)
    n += c

if errors:
    print("ОШИБКИ (файл НЕ записан):")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
P.write_text(t, encoding="utf-8")
print(f"OK: {n} замен")
