#!/usr/bin/env python3
"""Проход 2: английские хвосты и остатки. Только папка проекта."""
from pathlib import Path

P = Path("/home/v/projects/Красный хлеб/2015.52429.Red-Bread_djvu.ru.txt")

PAIRS = [
    ("коммунистическому аналогу Сcouts и Girl Guides",
     "коммунистическому аналогу скаутов и девочек-гайдов", 1),
    ("с rattling of death in his lungs, который",
     "с предсмертными хрипами в лёгких, который", 1),
    ("Никакие курицы не strutted вокруг их гостиной",
     "Никакие курицы не расхаживали по их гостиной", 1),
    ("в Комиссариате по Agriculture",
     "в Комиссариате земледелия", 1),
    ("был oportunistом", "был оппортунистом", 1),
    ("в Москве’s feverish haste to achieve industrial self-",
     "в московской лихорадочной спешке добиться промышленной само-", 1),
    ("Достаточности. Сама мощь",
     "достаточности. Сама мощь", 1),
    ("его огромные waiting rooms",
     "его огромные залы ожидания", 1),
    ("программы Комиссара по Agriculture на следующий год",
     "программы наркома земледелия на следующий год", 1),
    ("сотрудник GPU из числа слушателей",
     "сотрудник ГПУ из числа слушателей", 1),
    ("с heatedly спорили о своих местах",
     "горячо спорили о своих местах", 1),
    ("потрясая ее до sophistication и нового направления",
     "встряхивая её, приближая к новому уровню и новому направлению", 1),
    ("Но whatever might have happened in the village, whatever the feelings of the people, the lands that stretched before me were rich in promise. The rye on the land of the kolhoz was gorgeous, tall, clean, heavily eared and in even rows, sowed evidently not by the irregular human hand but by the mathematically controlled grain drill. Only slightly less gorgeous were the spring crops on the other side of the road - potatoes, barley, oats, and large patches of flax, all so high that they hid the earth with their sweep of green.",
     "Но что бы ни случилось в деревне, каковы бы ни были чувства людей, земли, расстилавшиеся передо мной, были полны обещаний. Рожь на колхозной земле была великолепна — высокая, чистая, с тяжёлыми колосьями и ровными рядами, посеянная, очевидно, не неровной человеческой рукой, а математически точной зерновой сеялкой. Лишь чуть менее великолепны были яровые на другой стороне дороги — картофель, ячмень, овёс и большие участки льна, все такие высокие, что скрывали землю сплошной зеленью.", 1),
    ("он сам стал баптистскимconvert, и теперь",
     "он сам обратился в баптизм, и теперь", 1),
    ("от десяти до пятидесяти копеек apiece",
     "от десяти до пятидесяти копеек за штуку", 1),
    ("они стали более worldly и не торопились",
     "они стали более светскими и не торопились", 1),
    ("а со звучным smackом",
     "а со звучным чмоканьем", 1),
    ("и все они становятся такими nowadays, эти молодые женщины",
     "и все они становятся такими в наши дни, эти молодые женщины", 1),
    ("Голосование проводится не по тайному ballotу, а путем поднятия рук",
     "Голосование проводится не тайно, а поднятием рук", 1),
    ("Из них commune является",
     "Из них коммуна является", 1),
    ("В commune исчезают",
     "В коммуне исчезают", 1),
    ("Из всех commune, которые",
     "Из всех коммун, которые", 1),
    ("В commune единственными",
     "В коммуне единственными", 1),
    ("need for themselves the kolhoz is obliged to sell it to the government. It is not supposed to keep an ‘idle’ surplus on hand.",
     "", 1),
    ("The above scheme, however, is intended as a guiding principle rather than as a fixed rule. In a booklet that attempts to explain in popular language the ruling of the kolhozlsenlr and the principle underlying the question of distribution of income in",
     "", 1),
    ("The mass meeting of the kolhoz is the real master of its income, and only this mass meeting can decide how to divide it and how much to apportion to each fund. The kolhozlsentr is merely offering the general suggestions that the income is to be di\\dd",
     "", 1),
    ("Есть вопрос о manufactured goods, всегда",
     "Есть вопрос о промтоварах, всегда", 1),
    ("человек с Chautauqua не может",
     "чатоквский лектор не может", 1),
    ("двадцать семь были heifers",
     "двадцать семь были тёлками", 1),
    ("RED BREAD", "КРАСНЫЙ ХЛЕБ", 1),
    ("Неивльно построенные, товкрccd перед нами",
     "Недавно построенные, высились перед нами", 1),
    ("как иvere конюшни",
     "как и все коровники", 1),
    ("и вместо них ropes прикреплены к бревнам",
     "а верёвки, привязанные к брёвнам, заменяли перегородки", 1),
    ("Но здесь ivere пространство, свет и воздух",
     "Но здесь были простор, свет и воздух", 1),
    ("THE NEW AND THE OLD", "НОВОЕ И СТАРОЕ", 1),
    ("я больше не легко dismiss такой вопрос",
     "я уже не отмахиваюсь легко от такого вопроса", 1),
    ("— earnestly спросил он",
     "— горячо спросил он", 1),
    ("Strange land!", "Странная страна!", 1),
    ("карабкаясь по fences monkey-like",
     "карабкаясь по заборам, как обезьяна", 1),
    ("С грязью и трудом, и filth и невежеством",
     "С грязью, трудом, мерзостью и невежеством", 1),
    ("пренебрегая приказом Комиссара по Agriculture не slaughtering скота, пригодного для разведения",
     "пренебрегая приказом комиссара земледелия не резать скот, пригодный для разведения", 1),
    ("Whenever she found any irregularity, she immediately set about to remove it and searching out the man in charge of the stables, she chided him for his laxity with such vigour and eloquence that he felt ashamed and crushed. There was a woman with a real social spirit, though she was so old and had never learned to read or to write. Was not Ulyana живым доказательством",
     "Заметив малейший непорядок, она тут же принималась его устранять, а разыскав конюха, отвечавшего за конюшню, отчитывала его за нерадивость с такой горячностью и красноречием, что тому становилось стыдно и он чувствовал себя раздавленным. Вот была женщина с настоящим чувством коллективизма, хотя она была так стара и так и не научилась ни читать, ни писать. Разве Ульяна не была живым доказательством", 1),
    ("как это сделал колхоз.Sentiments and calculations that actuate a peasant play no part on the kolhoz-",
     "как это сделал колхоз. Чувства и расчёты, которыми руководствуется крестьянин, не играют в колхозе никакой роли.", 1),
    ("вспоминал о агентах шатаукуа в те дни",
     "вспоминал о чатоквских агентах в те дни", 1),
]

def main():
    t = P.read_text(encoding="utf-8")
    errors = []
    applied = 0
    for old, new, exp in PAIRS:
        c = t.count(old)
        if c != exp:
            errors.append(f"ОЖИДАЛОСЬ {exp}, НАЙДЕНО {c}: {old[:80]!r}")
            continue
        t = t.replace(old, new)
        applied += 1
    if errors:
        print("ОШИБКИ (файл НЕ записан):")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    P.write_text(t, encoding="utf-8")
    print(f"OK: применено {applied} замен")

if __name__ == "__main__":
    main()
