#!/usr/bin/env python3
"""Применение ручных решений все/всё + КРЫЖИЧНЫЙ. Только папка проекта."""
from pathlib import Path
import re

PROJ = Path("/home/v/projects/Красный хлеб")
P = PROJ / "2015.52429.Red-Bread_djvu.ru.txt"
t = P.read_text(encoding="utf-8")

dec = {}
for fn in ("vse_dec_b1.txt", "vse_dec_b2.txt", "vse_dec_b3.txt"):
    for line in open(PROJ / fn, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        k, v = line.split(":")
        dec[int(k)] = v
dec[44] = "vse"  # как все русские крестьяне

matches = [(m.start(), m.group(0)) for m in re.finditer(r"\b[Вв]се\b", t)]
assert max(dec) < len(matches), "индекс вне диапазона"

# сверка с пулом
pool = set()
for line in open(PROJ / "vse_ambig_round3.txt", encoding="utf-8"):
    m = re.match(r"### (\d+)", line)
    if m:
        pool.add(int(m.group(1)))
assert set(dec) == pool, f"расхождение: нет решений для {sorted(pool - set(dec))}, лишние {sorted(set(dec) - pool)}"

out, last = [], 0
n_vyo = 0
for idx, (pos, w) in enumerate(matches):
    if dec.get(idx) == "vyo":
        out.append(t[last:pos])
        out.append("Всё" if w[0] == "В" else "всё")
        last = pos + len(w)
        n_vyo += 1
out.append(t[last:])
t = "".join(out)

assert t.count("КРЫЖИЧНЫЙ") == 3
t = t.replace("КРЫЖИЧНЫЙ", "КРАСНЫЙ")

P.write_text(t, encoding="utf-8")
n_vse = sum(1 for v in dec.values() if v == "vse")
print(f"OK: всё={n_vyo}, все(подтв.)={n_vse}, КРЫЖИЧНЫЙ->КРАСНЫЙ x3")
