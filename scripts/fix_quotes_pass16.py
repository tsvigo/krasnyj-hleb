#!/usr/bin/env python3
"""Проход 16: унификация кавычек на «» (вложенные — „ "). Только проект."""
from pathlib import Path

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
t = P.read_text(encoding="utf-8")

FIXES = [
    ("себя неудачником. В противном случае он такой обаятельный человек.\nВы должны посетить",
     "себя неудачником. В противном случае он такой обаятельный человек.\n‘Вы должны посетить", 1),
    ("Ах, Николай Борисоныч, как вы стали красноречивы!’",
     "‘Ах, Николай Борисоныч, как вы стали красноречивы!’", 1),
    ("переполнены едой и всё из нашего имения - всё наше…",
     "переполнены едой и всё из нашего имения - всё наше…’", 1),
    ("Это была безнадёжная ситуация.",
     "Это была безнадёжная ситуация.’", 1),
    ("будучи буржуем,'", "будучи буржуем,’", 1),
    ("называют это свадьбой, Ах!", "называют это свадьбой, Ах!’", 1),
    ("Они всегда могли найти много работы, потому что",
     "Они всегда могли найти много работы, потому что […]’", 1),
]
errors = []
for old, new, exp in FIXES:
    c = t.count(old)
    if c != exp:
        errors.append(f"ОЖИДАЛОСЬ {exp}, НАЙДЕНО {c}: {old[:60]!r}")
        continue
    t = t.replace(old, new)
if errors:
    print("ОШИБКИ (стоп до конверсии):")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

assert t.count("„В колхозе") == 1 and t.count("крестинах“.") == 1
t = t.replace("„В колхозе", "\ue000В колхозе").replace("крестинах“.", "крестинах\ue001.")
assert t.count("„Возлюби ближнего") == 1 and t.count("самого себя“?»") == 1
t = t.replace("„Возлюби ближнего", "\ue002Возлюби ближнего").replace("самого себя“?»", "самого себя\ue003?»")

out = []
stack = []  # ('s'|'g'|'D', nested?)
stats = {"nest": 0, "stray": 0}
for ch in t:
    if ch == "‘":
        if stack and stack[-1][0] == "s":
            out.append("«")  # абзац-продолжение
        else:
            stack.append(("s", len(stack) > 0))
            out.append("«")
    elif ch == "“":
        if stack and stack[-1][0] == "D":
            out.append("«")  # абзац-продолжение
        elif len(stack) > 0:
            stack.append(("D", True))
            out.append("„")
            stats["nest"] += 1
        else:
            stack.append(("D", False))
            out.append("«")
    elif ch == "«":
        if stack and stack[-1][0] == "g":
            out.append("«")  # абзац-продолжение
        else:
            stack.append(("g", len(stack) > 0))
            out.append("«")
    elif ch in "’”»":
        if stack:
            typ, nested = stack.pop()
            out.append("“" if (typ == "D" and nested) else "»")
        else:
            out.append("»")
            stats["stray"] += 1
    else:
        out.append(ch)

t2 = "".join(out)
t2 = t2.replace("\ue000", "„").replace("\ue001", "“").replace("\ue002", "„").replace("\ue003", "“")
left = {c: t2.count(c) for c in ["‘", "’", '"', "'"]}
assert t2.count("“") == t2.count("„"), (t2.count("“"), t2.count("„"))
print("остатки:", left)
print("вложенных „ :", stats["nest"], "| strays:", stats["stray"])
print("«:", t2.count("«"), "»:", t2.count("»"), "„:", t2.count("„"), "“: ", t2.count("“"))
assert all(v == 0 for v in left.values()), left
P.write_text(t2, encoding="utf-8")
print("OK: конверсия выполнена")
