#!/usr/bin/env python3
"""все/всё v2: точные правила + двусловный просмотр + tight-контексты. Только проект."""
from pathlib import Path
import re

PROJ = Path("/home/v/projects/Красный хлеб")
P = PROJ / "2015.52429.Red-Bread_djvu.ru.txt"
t = P.read_text(encoding="utf-8")

VY0 = """время временем равно еще ещё же таки больше меньше лучше хуже
чаще реже раньше позже дальше ближе старше младше выше ниже дольше скорее ярче
громче тише сильнее слабее это остальное остальным вокруг дело кончено понятно
готово решено сказано сделано пропало погибло прошло изменилось смешалось
кончилось началось удалось получилось вышло случилось произошло было будет есть
станет стало оказалось кажется ясно видно слышно известно останется остается
осталось лето""".split()

VSE = """люди крестьян крестьяне мужики женщины мужчины дети ребята солдаты
рабочие члены гости девушки парни старики товарищи мальчики девочки мы вы они
эти те остальные разом вместе дружно хором знали знают говорили говорят думали
думают хотели хотят пошли пришли смеялись смеются молчали молчат согласились
разошлись собрались ждали ждут смотрят смотрели стали были будут живут
жили идут сидят стоят поют кричат плачут работают между против кроме перед
среди после""".split()

VSE_POSS = "мои твои свои наши ваши моих твоих своих наших ваших моими твоими своими нашими вашими".split()
VSE_NUM = "два две три четыре пять шесть семь оба обе несколько много мало столько сколько".split()
I_ADV = "впереди позади вдали вблизи внутри внизу вверху сзади".split()  # -и наречия: руками!

PREP2_VYO = {  # предлог -> второе слово ведёт к всё
    "до": {"конца", "копейки", "капли", "основания"},
    "на": {"свете", "свету", "деле"},
    "в": {"дело"},
    "к": {"лучшему"},
}
PREP2_VSE = {  # предлог -> второе слово ведёт к все
    "до": {"одного", "единого", "последнего"},
    "за": {"одного"},
    "без": {"исключения"},
}

def plural_noun_end(w):
    if w == "зря":
        return "vyo"
    if re.fullmatch(r"[а-яё]+(?:ы|а|я|ей|ов|ев|ам|ям|ах|ях|ами|ями)", w):
        return "vse"
    return None

matches = [(m.start(), m.group(0)) for m in re.finditer(r"\b[Вв]се\b", t)]
print(f"осталось вхождений: {len(matches)}")

decide, ambig = {}, []
for idx, (pos, w) in enumerate(matches):
    after = t[pos + len(w):]
    m = re.match(r"\s*([А-Яа-яЁё]+)", after)
    nxt = m.group(1).lower() if m else ""
    gap = after[:m.start(1)] if m else after[:10]
    if re.search(r"[.!?…]", gap):
        ambig.append(idx)  # граница предложения
        continue
    if nxt in VY0:
        if nxt == "равно" and re.search(r"\b(мы|вы|они)\b", t[max(0, pos - 25):pos], re.I):
            decide[idx] = "vse"
        else:
            decide[idx] = "vyo"
        continue
    if nxt in VSE or nxt in VSE_POSS or nxt in VSE_NUM:
        decide[idx] = "vse"
        continue
    if nxt in I_ADV:
        ambig.append(idx)
        continue
    if re.fullmatch(r"[а-яё]+(?:ли|ут|ют|ат|ят)", nxt) and nxt != "тут":
        decide[idx] = "vse"
        continue
    if re.fullmatch(r"[а-яё]+ые", nxt) or re.fullmatch(r"[а-яё]+щие", nxt) or re.fullmatch(r"[а-яё]+(?:их|ых)", nxt):
        decide[idx] = "vse"
        continue
    pe = plural_noun_end(nxt)
    if pe:
        decide[idx] = pe
        continue
    # двусловный просмотр: предлог/связка + второе слово
    m2 = re.match(r"\s*[А-Яа-яЁё]+\s+([А-Яа-яЁё]+)", after)
    nn = m2.group(1).lower() if m2 else ""
    if nxt in ("что", "до", "на", "в", "с", "к", "по", "из", "о", "за", "без"):
        if nxt == "что" and nn in ("угодно", "нибудь"):
            decide[idx] = "vyo"
        elif nn in PREP2_VYO.get(nxt, ()):
            decide[idx] = "vyo"
        elif nn in PREP2_VSE.get(nxt, ()):
            decide[idx] = "vse"
        elif nxt == "с" and re.fullmatch(r"[а-яё]+(?:ами|ями|ьми)", nn):
            decide[idx] = "vse"
        elif nxt == "по" and re.fullmatch(r"[а-яё]+(?:ам|ям)", nn):
            decide[idx] = "vse"
        elif nxt == "из" and nn in ("них", "нас", "вас", "него", "нее", "них"):
            decide[idx] = "vse"
        elif nxt in ("на",) and re.fullmatch(r"[а-яё]+(?:у|ю)", nn):
            decide[idx] = "vse"
        else:
            ambig.append(idx)
        continue
    ambig.append(idx)

out, last = [], 0
for idx, (pos, w) in enumerate(matches):
    if decide.get(idx) == "vyo":
        out.append(t[last:pos])
        out.append("Всё" if w[0] == "В" else "всё")
        last = pos + len(w)
out.append(t[last:])
P.write_text("".join(out), encoding="utf-8")

n_vyo = sum(1 for v in decide.values() if v == "vyo")
n_vse = sum(1 for v in decide.values() if v == "vse")
print(f"применено: всё={n_vyo}, все(подтв.)={n_vse}, в разбор={len(ambig)}")

# tight-контексты: объемлющее предложение, макс 400 символов
with open(PROJ / "vse_ambig_round3.txt", "w", encoding="utf-8") as f:
    for idx in ambig:
        pos, w = matches[idx]
        m = re.match(r"\s*([А-Яа-яЁё]+)", t[pos + len(w):])
        nxt = m.group(1).lower() if m else ""
        s0 = max(t.rfind(".", 0, pos - 250), t.rfind("!", 0, pos - 250),
                 t.rfind("?", 0, pos - 250), t.rfind("\n", 0, pos - 250))
        e1 = t.find(".", pos + 150)
        e2 = t.find("\n", pos + 150)
        if e1 == -1:
            e1 = len(t)
        if e2 == -1:
            e2 = len(t)
        s1 = min(e1, e2)
        ctx = t[s0 + 1:s1 + 1].replace("\n", " ")[:420]
        f.write(f"### {idx} | {w} + {nxt}\n{ctx}\n\n")
print("пул: vse_ambig_round3.txt")

# аудит рискованных уже-применённых (прошлый раунд)
print("== аудит: всё + наречие ==")
for m in re.finditer(r"\b[Вв]сё\s+(давно|скоро|прямо|кругом|что-то|кто-то|куда-то|где-то|когда-то|холодно|тепло|темно|хорошо|плохо|там|тут)\b", t):
    s0 = max(0, m.start() - 90)
    print(f"...{t[s0:m.end()+90].replace(chr(10),' ')}...")
