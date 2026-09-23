#!/usr/bin/env python3
"""Проход 11: раздел 2 — о/об (по границам слов) + также. Только проект."""
from pathlib import Path
import re

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
t = P.read_text(encoding="utf-8")

pat = re.compile(r"(?<!\S)о(?=\s+[аеёиоуыэюя]\w*)")
found = [(m.start(), m.group(0), t[m.start():m.start() + 30].split("\n")[0]) for m in pat.finditer(t)]
print(f"кандидатов о->об: {len(found)}")
for pos, _, ctx in found:
    print(f"  {ctx[:60]!r}")

# междометия (о боже/ужас/чудо) не трогаем
bad = [c for _, _, c in found if re.search(r"^о (боже|ужас|чудо|горе|радость)", c)]
assert not bad, f"междометия: {bad}"
assert len(found) == 21, f"ожидалось 21, найдено {len(found)}"

t = pat.sub("об", t)

old, new = "и так же книги", "и также книги"
assert t.count(old) == 1
t = t.replace(old, new)

P.write_text(t, encoding="utf-8")
print("OK: 21 об + 1 также")
