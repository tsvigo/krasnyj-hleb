#!/usr/bin/env python3
"""Разбор все/всё: автоклассификация + выгрузка двусмысленных. Только проект."""
from pathlib import Path
import re

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")
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
print(f"всего вхождений: {len(matches)}")

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
        auto_vse.append(idx)  # глаголы мн.ч.: говорили, знают (кроме наречия тут)
    elif re.fullmatch(r"[а-яё]+ые", nxt):
        auto_vse.append(idx)  # прил. мн.ч.: большие (ср.р. на -ые не бывает)
    elif re.fullmatch(r"[а-яё]+щие", nxt):
        auto_vse.append(idx)  # причастия мн.ч.: присутствующие
    elif re.fullmatch(r"[а-яё]+(?:их|ых)", nxt):
        auto_vse.append(idx)  # род. мн.ч.: молодых
    elif re.fullmatch(r"(?:мои|твои|свои|наши|ваши|моих|твоих|своих|наших|ваших|моими|твоими|своими|нашими|вашими)", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"(?:два|две|три|четыре|пять|шесть|семь|оба|обе|несколько|много|мало|столько|сколько)", nxt):
        auto_vse.append(idx)
    elif re.fullmatch(r"[а-яё]+(?:ло|лось|но|то)", nxt) and nxt not in ("село", "тепло", "дело", "лицо", "пятно", "окно", "поле", "море", "горе", "тело"):
        auto_vyo.append(idx)  # ср.р.: было, сказано (кроме существительных)
    else:
        s0 = t.rfind("\n", 0, pos - 600)
        s1 = t.find("\n", pos + 200)
        ctx = t[s0 + 1:s1].replace("\n", " ")
        ambig.append((idx, pos, w, nxt, ctx))

print(f"авто-всё: {len(auto_vyo)}, авто-все: {len(auto_vse)}, двусмысленных: {len(ambig)}")

with open("/tmp/opencode/vse_auto.txt", "w", encoding="utf-8") as f:
    f.write("VY0:" + ",".join(map(str, auto_vyo)) + "\n")
    f.write("VSE:" + ",".join(map(str, auto_vse)) + "\n")

with open("/tmp/opencode/vse_ambig.txt", "w", encoding="utf-8") as f:
    for idx, pos, w, nxt, ctx in ambig:
        f.write(f"### {idx} | слово={w} | след={nxt}\n{ctx}\n\n")
print("записано: /tmp/opencode/vse_ambig.txt")
