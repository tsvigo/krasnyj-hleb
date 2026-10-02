#!/usr/bin/env python3
"""Разбор все/всё для Gemini-перевода: автоклассификация + выгрузка двусмысленных.
Логика повторяет scripts/vse_classify.py + vse_apply.py главного файла,
но работает с gemini/RED-BREAD-gemini-ru.txt и своими временными файлами."""
from pathlib import Path
import re

P = Path("/home/v/projects/Красный хлеб/gemini/RED-BREAD-gemini-ru.txt")
AUTO = Path("/tmp/opencode/vse_gemini_auto.txt")
AMB_OUT = Path("/home/v/projects/Красный хлеб/vse_gemini_ambig.txt")
t = P.read_text(encoding="utf-8")

VYO_NEXT = """время временем равно еще ещё же таки больше меньше лучше хуже
чаще реже это остальное остальным вокруг дело кончено понятно готово решено
сказано сделано пропало погибло прошло изменилось смешалось кончилось началось
удалось получилось вышло случилось произошло было будет есть станет стало
оказалось кажется ясно видно слышно известно сильнее раньше позже дальше ближе
старше младше выше ниже дольше скорее ярче громче тише сильнее слабее
останется остается осталось""".split()

VSE_NEXT = """люди крестьян крестьяне мужики женщины мужчины дети ребята солдаты
рабочие члены гости девушки парни старики товарищи мальчики девочки мы вы они
эти те остальные разом вместе дружно хором знали знают говорили говорят думали
думают хотели хотят пошли пришли смеялись смеются молчали молчат согласились
разошлись собрались ждали ждут смотрят смотрели стали были будут будут живут
жили пошли идут сидят стоят поют кричат плачут работают""".split()

matches = [(m.start(), m.group(0)) for m in re.finditer(r"\b[Вв]се\b", t)]
print(f"всего вхождений «все»: {len(matches)}")

auto_vyo, auto_vse, ambig = [], [], []
for idx, (pos, w) in enumerate(matches):
    after = t[pos + len(w):]
    m = re.match(r"\s*([А-Яа-яЁё]+)", after)
    nxt = m.group(1).lower() if m else ""
    if nxt in VYO_NEXT:
        auto_vyo.append(idx)
    elif nxt in VSE_NEXT:
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+(?:ли|ут|ют|ат|ят)", nxt) and nxt != "тут":
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+ые", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+щие", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+(?:их|ых)", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"(?:мои|твои|свои|наши|ваши|моих|твоих|своих|наших|ваших|моими|твоими|своими|нашими|вашими)", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"(?:два|две|три|четыре|пять|шесть|семь|оба|обе|несколько|много|мало|столько|сколько)", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+(?:ло|лось|но|то)", nxt) and nxt not in ("село", "тепло", "дело", "лицо", "пятно", "окно", "поле", "море", "горе", "тело"):
        auto_vyo.append(idx)
    else:
        s0 = t.rfind("\n", 0, pos - 600)
        s1 = t.find("\n", pos + 200)
        ctx = t[s0 + 1:s1].replace("\n", " ")
        ambig.append((idx, pos, w, nxt, ctx))

print(f"авто-всё: {len(auto_vyo)}, авто-все: {len(auto_vse)}, двусмысленных: {len(ambig)}")
AUTO.write_text("VYO:" + ",".join(map(str, auto_vyo)) + "\nVSE:" + ",".join(map(str, auto_vse)) + "\n", encoding="utf-8")

# ---- применение (как vse_apply.py) ----
d = {}
for line in AUTO.read_text(encoding="utf-8").splitlines():
    k, v = line.strip().split(":")
    d[k] = [int(x) for x in v.split(",") if x]

decide, manual = {}, set()
for idx in d["VYO"]:
    pos, w = matches[idx]
    after = t[pos + len(w):]
    m = re.match(r"\s*([А-Яа-яЁё]+)", after)
    nxt = m.group(1).lower() if m else ""
    gap = after[:m.start(1)] if m else after[:10]
    if re.search(r"[.!?…\"'»]", gap):
        manual.add(idx)
        continue
    if nxt == "равно" and re.search(r"\b(мы|вы|они)\b", t[max(0, pos - 25):pos], re.I):
        decide[idx] = "vse"
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

out, last = [], 0
for idx, (pos, w) in enumerate(matches):
    if decide.get(idx) == "vyo":
        out.append(t[last:pos])
        out.append("Всё" if w[0] == "В" else "всё")
        last = pos + len(w)
out.append(t[last:])
new_t = "".join(out)

n_vyo = sum(1 for v in decide.values() if v == "vyo")
n_vse = sum(1 for v in decide.values() if v == "vse")
rest = sorted(set(range(len(matches))) - set(decide))
with AMB_OUT.open("w", encoding="utf-8") as f:
    for idx in rest:
        pos, w = matches[idx]
        m = re.match(r"\s*([А-Яа-яЁё]+)", new_t[pos + len(w):])
        nxt = m.group(1).lower() if m else ""
        s0 = new_t.rfind("\n", 0, pos - 500)
        s1 = new_t.find("\n", pos + 200)
        f.write(f"### {idx} | слово={w} | след={nxt}\n{new_t[s0 + 1:s1].replace(chr(10), ' ')}\n\n")

P.write_text(new_t, encoding="utf-8")
print(f"применено: всё={n_vyo}, все(подтверждено)={n_vse}")
print(f"в ручной остаток: {len(rest)} → {AMB_OUT.name}")
