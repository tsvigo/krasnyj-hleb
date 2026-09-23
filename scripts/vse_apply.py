#!/usr/bin/env python3
"""Применение все/всё по индексам + гардрейлы. Только папка проекта."""
from pathlib import Path
import re

PROJ = Path("/home/v/projects/Красный хлеб")
P = PROJ / "2015.52429.Red-Bread_djvu.ru.txt"
t = P.read_text(encoding="utf-8")

d = {}
for line in open("/tmp/opencode/vse_auto.txt", encoding="utf-8"):
    k, v = line.strip().split(":")
    d[k] = [int(x) for x in v.split(",") if x]

matches = [(m.start(), m.group(0)) for m in re.finditer(r"\b[Вв]се\b", t)]

decide = {}   # idx -> 'vyo' | 'vse'
manual = set()

for idx in d["VY0"]:
    pos, w = matches[idx]
    after = t[pos + len(w):]
    m = re.match(r"\s*([А-Яа-яЁё]+)", after)
    nxt = m.group(1).lower() if m else ""
    gap = after[:m.start(1)] if m else after[:10]
    if re.search(r"[.!?…\"'»]", gap):
        manual.add(idx)  # граница предложения — глазами
        continue
    if nxt == "равно" and re.search(r"\b(мы|вы|они)\b", t[max(0, pos - 25):pos], re.I):
        decide[idx] = "vse"  # 'мы все равно будем' = все
        continue
    if nxt == "что":
        tail = after[m.end(1):m.end(1) + 20] if m else ""
        m2 = re.match(r"\s*([А-Яа-яЁё]+)", tail)
        nn = m2.group(1).lower() if m2 else ""
        if nn in ("угодно", "нибудь"):
            decide[idx] = "vyo"
        else:
            manual.add(idx)
        continue
    decide[idx] = "vyo"

for idx in d["VSE"]:
    decide[idx] = "vse"

# пересборка по индексам
out = []
last = 0
for idx, (pos, w) in enumerate(matches):
    if idx in decide and decide[idx] == "vyo":
        out.append(t[last:pos])
        out.append("Всё" if w[0] == "В" else "всё")
        last = pos + len(w)
out.append(t[last:])
P.write_text("".join(out), encoding="utf-8")

n_vyo = sum(1 for v in decide.values() if v == "vyo")
n_vse = sum(1 for v in decide.values() if v == "vse")

# остаток на следующий раунд: двусмысленные из classify + отведённые гардрейлами
amb = []
seen = set(decide) | manual
all_idx = set(range(len(matches)))
for line in open("/tmp/opencode/vse_ambig.txt", encoding="utf-8"):
    pass
# ambig-индексы = все нерешённые
for idx in sorted(all_idx - set(i for i in decide)):
    pos, w = matches[idx]
    m = re.match(r"\s*([А-Яа-яЁё]+)", t[pos + len(w):])
    nxt = m.group(1).lower() if m else ""
    s0 = t.rfind("\n", 0, pos - 500)
    s1 = t.find("\n", pos + 200)
    amb.append((idx, w, nxt, t[s0 + 1:s1].replace("\n", " ")))

with open(PROJ / "vse_ambig_round2.txt", "w", encoding="utf-8") as f:
    for idx, w, nxt, ctx in amb:
        f.write(f"### {idx} | слово={w} | след={nxt}\n{ctx}\n\n")

print(f"применено: всё={n_vyo}, все(подтверждено)={n_vse}")
print(f"в ручной остаток: {len(amb)}")
print("остаток сохранён: vse_ambig_round2.txt")
