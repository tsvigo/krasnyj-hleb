#!/usr/bin/env python3
"""Охота за пропусками: оборванные концы строк + короткие обрывки. Только проект."""
from pathlib import Path
import re

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
lines = P.read_text(encoding="utf-8").splitlines()

DANGLE = """на в с к о у от до для без под над при про через между среди против
кроме вместо ради и или а но же ли бы не ни как что когда пока хотя чтобы
потому поэтому так тоже также или который которая которое которые чей чья
чьё чьи этот эта это эти тот та то те мой моя моё мои твой твоя твоё твои
свой своя своё свои наш наша наше наши ваш ваша ваше ваши каждый каждая
каждое каждые всякий всякая всякое всякие сам сама само сами весь вся всё
который-то если то""".split()
DANGLE = set(DANGLE)

print("== строки, обрывающиеся на предлог/союз/местоимение ==")
for i, l in enumerate(lines):
    s = l.strip()
    if not s or len(s) < 15:
        continue
    last = re.findall(r"[А-Яа-яЁё]+", s)
    if not last:
        continue
    if last[-1].lower() in DANGLE:
        nxt = ""
        for j in range(i + 1, min(i + 4, len(lines))):
            if lines[j].strip():
                nxt = lines[j].strip()[:80]
                break
        print(f"{i + 1}: ...{s[-90:]} || СЛЕД: {nxt}")

print()
print("== короткие непустые строки (<25 символов), не заголовки/номера ==")
for i, l in enumerate(lines):
    s = l.strip()
    if 0 < len(s) < 25 and not re.fullmatch(r"[0-9 \-–—*»«\"'.IVXLCDM*]+", s) and not re.fullmatch(r"[А-ЯЁ ]+", s):
        print(f"{i + 1}: [{s}]")
