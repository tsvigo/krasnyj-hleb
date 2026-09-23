#!/usr/bin/env python3
"""Проход 10: раскулачивание + Шатокуа (решение пользователя). Только проект."""
from pathlib import Path

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
t = P.read_text(encoding="utf-8")

PAIRS = [
    ("декулакизация", "раскулачивание", 1),
    ("декулакизации", "раскулачивания", 2),
    ("декулакизированных", "раскулаченных", 1),
    ("декулакизированные", "раскулаченные", 1),
    ("декулакизировать", "раскулачивать", 2),
    ("чатоквск", "шатоквск", 7),
    ("чатоквы", "Шатокуи", 2),
]

errors, n = [], 0
for old, new, exp in PAIRS:
    c = t.count(old)
    if c != exp:
        errors.append(f"ОЖИДАЛОСЬ {exp}, НАЙДЕНО {c}: {old!r}")
        continue
    t = t.replace(old, new)
    n += c
if errors:
    print("ОШИБКИ (файл НЕ записан):")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
P.write_text(t, encoding="utf-8")
print(f"OK: {n} замен")
print("декулакиз* осталось:", sum(t.count(x) for x in ["декулакиз", "Декулакиз"]))
print("чатокв* осталось:", t.count("чатокв"))
