#!/usr/bin/env python3
"""1) Вставить СОДЕРЖАНИЕ (названия глав Gemini + страницы из главного файла).
2) Разбить длинный диалоговый абзац «Коровник» на абзацы."""
from pathlib import Path
import re

PROJ = Path("/home/v/projects/Красный хлеб")
P = PROJ / "gemini/RED-BREAD-gemini-ru.txt"
MAIN = PROJ / "2015.52429.Red-Bread_djvu.ru.txt"

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"]

# страницы из СОДЕРЖАНИЯ главного файла
m = MAIN.read_text(encoding="utf-8")
block = m[m.find("СОДЕРЖАНИЕ"): m.find("СОДЕРЖАНИЕ") + 2500]
pages = {}
for r in ROMAN:
    mm = re.search(r"^" + r + r"\s+.+?\s+(\d+)\s*$", block, re.M)
    pages[r] = int(mm.group(1))
assert len(pages) == 19, pages

# заголовки глав из Gemini-файла
g = P.read_text(encoding="utf-8")
titles = dict(re.findall(r"^ГЛАВА ([IVX]+)\n\n([^\n]+)", g, re.M))
assert len(titles) == 19, titles

toc = ["СОДЕРЖАНИЕ", "", "", "ГЛАВА — СТР.", ""]
for r in ROMAN:
    toc += [f"{r} {titles[r]} {pages[r]}", ""]
toc_block = "\n".join(toc).rstrip("\n") + "\n\n\n"

assert g.startswith("ГЛАВА I\n"), g[:30]
assert "СОДЕРЖАНИЕ" not in g
g = toc_block + g

SPLITS = [
    ("Но я сохранял спокойствие. Когда мы дошли до коровника",
     "Но я сохранял спокойствие.\n\nКогда мы дошли до коровника"),
    ('"Конечно", — признал я. "Значит, она корова',
     '"Конечно", — признал я.\n\n"Значит, она корова'),
    ('пока не отелится". "А когда это будет?"',
     'пока не отелится".\n\n"А когда это будет?"'),
    ('когда её покрыли". Больше ничего не было сказано',
     'когда её покрыли".\n\nБольше ничего не было сказано'),
    ("Господи, как она говорила! Она его обзывала",
     "Господи, как она говорила!\n\nОна его обзывала"),
    ("вставить ни слова. Однажды она даже плюнула",
     "вставить ни слова.\n\nОднажды она даже плюнула"),
    ("совсем ничего. Каждый раз, когда он открывал рот",
     "совсем ничего.\n\nКаждый раз, когда он открывал рот"),
]
for old, new in SPLITS:
    assert g.count(old) == 1, (g.count(old), old[:50])
    g = g.replace(old, new)

P.write_text(g, encoding="utf-8")
print(f"OK: СОДЕРЖАНИЕ (19 позиций, стр. {pages['I']}–{pages['XIX']}) + {len(SPLITS)} абзацев")
