#!/usr/bin/env python3
"""Все/всё для Gemini: автоклассификация + ручная карта по всем 220 двусмысленным.
Источник — бэкап после ё-пасc (backup/RED-BREAD-gemini-ru.bak-20261002-1229)."""
from pathlib import Path
import glob
import os
import re

PROJ = Path("/home/v/projects/Красный хлеб")
BAKS = sorted(glob.glob(str(PROJ / "backup/RED-BREAD-gemini-ru.bak-*")), key=os.path.getmtime)
SRC = BAKS[-1]
P = PROJ / "gemini/RED-BREAD-gemini-ru.txt"
t = Path(SRC).read_text(encoding="utf-8")

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

# Ручная карта: idx -> 'vyo' | 'vse'. Составлена почиткой контекстов
# vse_gemini_ambig.txt (все 220) с контролем по английскому оригиналу.
VYO_IDX = {
    0, 4, 9, 14, 18, 19, 24, 25, 28, 29, 38, 39, 54, 60, 61, 64, 65, 66, 69,
    73, 74, 84, 120, 121, 124, 125, 128, 129, 131, 138, 145, 155, 157, 159,
    166, 167, 170, 172, 173, 177, 178, 179, 180, 181, 186, 191, 195, 196,
    211, 215, 222, 224, 227, 228, 230, 237, 242, 243, 244, 247, 253, 258,
    263, 265, 268, 277, 279, 280, 281, 286, 287, 288, 291, 294, 295, 304,
    306, 308, 309, 310, 311, 312, 322, 323, 325, 329, 334, 335, 339, 341,
    342, 343, 344, 345, 346, 347, 349, 354, 357, 360, 361, 362, 364, 367,
    369, 370, 374, 375, 380, 382, 387, 404, 412, 418, 427, 428, 429, 430, 434,
}
VSE_IDX = {
    2, 6, 10, 12, 13, 20, 22, 30, 35, 36, 37, 42, 43, 44, 52, 55, 56, 58, 62,
    70, 72, 75, 78, 80, 86, 87, 88, 90, 92, 93, 95, 96, 99, 100, 103, 104,
    107, 108, 110, 111, 112, 113, 114, 116, 117, 132, 133, 134, 140, 142,
    148, 153, 154, 158, 161, 164, 165, 169, 176, 183, 185, 189, 193, 194,
    197, 199, 200, 201, 202, 204, 207, 208, 209, 219, 231, 233, 238, 240,
    255, 270, 296, 301, 317, 327, 328, 336, 337, 355, 363, 372, 383, 384,
    389, 391, 392, 395, 396, 401, 402, 408, 431,
}

matches = [(m.start(), m.group(0)) for m in re.finditer(r"\b[Вв]се\b", t)]
print(f"источник: {Path(SRC).name}; вхождений «все»: {len(matches)}")

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
        ambig.append(idx)

print(f"авто-всё: {len(auto_vyo)}, авто-все: {len(auto_vse)}, двусмысленных: {len(ambig)}")

# сверка ручной карты с двусмысленными
if set(ambig) != VYO_IDX | VSE_IDX:
    miss = sorted(set(ambig) - (VYO_IDX | VSE_IDX))
    extra = sorted((VYO_IDX | VSE_IDX) - set(ambig))
    print(f"РАСХОЖДЕНИЕ КАРТЫ: нет в карте={miss[:20]}, лишнее в карте={extra[:20]}")
    raise SystemExit(1)
if VYO_IDX & VSE_IDX:
    print("КОНФЛИКТ idx в обеих картах:", sorted(VYO_IDX & VSE_IDX))
    raise SystemExit(1)
print("карта покрывает все двусмысленные без конфликтов")

# guardrails как в vse_apply.py (для авто-vyo): граница предложения и т.п. → вручную
decide = {}
guard_manual = set()
for idx in auto_vyo:
    pos, w = matches[idx]
    after = t[pos + len(w):]
    m = re.match(r"\s*([А-Яа-яЁё]+)", after)
    nxt = m.group(1).lower() if m else ""
    gap = after[:m.start(1)] if m else after[:10]
    if re.search(r"[.!?…\"'»]", gap):
        guard_manual.add(idx)
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
            guard_manual.add(idx)
        continue
    decide[idx] = "vyo"
for idx in auto_vse:
    decide[idx] = "vse"

# guardrail-ручные должны быть решены моей картой (или остаются в rest)
for idx in guard_manual:
    if idx in VYO_IDX:
        decide[idx] = "vyo"
    elif idx in VSE_IDX:
        decide[idx] = "vse"

for idx in VYO_IDX:
    decide[idx] = "vyo"
for idx in VSE_IDX:
    decide[idx] = "vse"

rest = sorted(set(range(len(matches))) - set(decide))
if rest:
    print("НЕ РЕШЕНЫ idx:", rest[:30], "... всего", len(rest))
    raise SystemExit(1)

out, last = [], 0
for idx, (pos, w) in enumerate(matches):
    if decide[idx] == "vyo":
        out.append(t[last:pos])
        out.append("Всё" if w[0] == "В" else "всё")
        last = pos + len(w)
out.append(t[last:])
new_t = "".join(out)
P.write_text(new_t, encoding="utf-8")

n_vyo = sum(1 for v in decide.values() if v == "vyo")
n_vse = sum(1 for v in decide.values() if v == "vse")
print(f"OK: всё→{n_vyo}, все→{n_vse}, записан {P.name}")
