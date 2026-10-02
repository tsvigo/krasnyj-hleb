#!/usr/bin/env python3
"""Конвейер перевода книги через Gemini (бесплатный тариф Google AI Studio).

Стадии:
  split  — режет английский оригинал на главы и чанки (без API)
  run    — переводит недостающие чанки (resume, rate-limit, retry)
  merge  — собирает полный русский текст из переведённых чанков
  status — что сделано, что осталось

Ключ: переменная окружения GEMINI_API_KEY или файл .env в корне проекта.
Модель: GEMINI_MODEL (по умолчанию gemini-2.5-flash).
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path("/home/v/projects/Красный хлеб")
EN_FILE = ROOT / "2015.52429.Red-Bread_djvu_fixed.txt"
WORK = ROOT / "gemini"
CH_DIR = WORK / "chapters"     # chNN.en.txt — нарезанные главы
PART_DIR = WORK / "parts"      # chNN.pKK.en.txt — чанки под перевод
OUT_DIR = WORK / "out"         # chNN.pKK.ru.txt — переводы
MANIFEST = WORK / "manifest.json"

# Канонический порядок глав в порядке их физического появления в OCR-файле
# (XV стоит между оглавлением и главой I, XVIII помечена как XVI).
FILE_ORDER = ["XV", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX",
              "X", "XI", "XII", "XIII", "XIV", "XVI", "XVII", "XVIII", "XIX"]
ROMAN2NUM = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
             "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
             "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19}

SYSTEM = (
    "Ты — профессиональный литературный переводчик с английского на русский. "
    "Переводишь книгу Мориса Хиндуса «Красный хлеб» (Red Bread, 1931). "
    "Стиль: живой книжный русский, без канцелярита и без дословной кальки. "
    "Сохраняй разбивку на абзацы один в один, прямую речь в кавычках «», "
    "имена собственные и реалии в соответствии с русской традицией. "
    "Не используй markdown-разметку (**, ##), списки и пояснения — только чистый текст перевода."
)
PROMPT_TMPL = "Переведи следующий отрывок книги на русский. Только перевод:\n\n{text}"

CHUNK_WORDS = 3500          # целевой размер чанка в словах
SLEEP_OK = 7.0              # пауза между запросами (~8.5 RPM < лимита 10 RPM)
MAX_RETRIES = 8
MAX_ROUNDS = 6


def _header_hits(lines):
    """Нечёткий поиск шапок CHAPTER (включая OCR-мусор вида 'C }! A P T E R')."""
    hits = []
    for i, l in enumerate(lines):
        letters = re.sub(r"[^A-Za-z]", "", l).upper()
        if letters.startswith("CHAPTER") or letters.startswith("CAPTER"):
            if i > 0 and lines[i - 1].strip().upper() == "CONTENTS":
                continue
            hits.append(i)
    return hits


def cmd_split(_args):
    lines = EN_FILE.read_text(encoding="utf-8").splitlines()
    hits = _header_hits(lines)
    if len(hits) != len(FILE_ORDER):
        sys.exit(f"ОШИБКА: найдено {len(hits)} шапок, ожидалось {len(FILE_ORDER)}: {hits}")
    CH_DIR.mkdir(parents=True, exist_ok=True)
    PART_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"chapters": [], "chunk_words": CHUNK_WORDS}
    for k, start in enumerate(hits):
        end = hits[k + 1] if k + 1 < len(hits) else len(lines)
        roman = FILE_ORDER[k]
        num = ROMAN2NUM[roman]
        body = lines[start + 1:end]
        # заголовок главы — первая непустая строка после шапки
        title = next((s.strip() for s in body if s.strip()), "")
        text = "\n".join(body).strip() + "\n"
        ch_name = f"ch{num:02d}"
        (CH_DIR / f"{ch_name}.en.txt").write_text(text, encoding="utf-8")
        # чанки по абзацам
        paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        parts, cur, words = [], [], 0
        for p in paras:
            w = len(p.split())
            if cur and words + w > CHUNK_WORDS:
                parts.append("\n\n".join(cur))
                cur, words = [], 0
            cur.append(p)
            words += w
        if cur:
            parts.append("\n\n".join(cur))
        for kk, chunk in enumerate(parts, 1):
            (PART_DIR / f"{ch_name}.p{kk:02d}.en.txt").write_text(chunk + "\n", encoding="utf-8")
        manifest["chapters"].append({"num": num, "roman": roman, "title": title, "parts": len(parts)})
        print(f"ch{num:02d} [{roman}] {title[:50]!r}: {len(parts)} чанков, {len(text.split())} слов")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(c["parts"] for c in manifest["chapters"])
    print(f"ИТОГО: {len(manifest['chapters'])} глав, {total} чанков → {WORK}/")


def _load_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_file = ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY"):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not api_key:
        sys.exit("ОШИБКА: нет GEMINI_API_KEY (переменная окружения или .env в корне проекта)")
    from google import genai
    return genai.Client(api_key=api_key)


def cmd_run(args):
    if not MANIFEST.exists():
        sys.exit("ОШИБКА: сначала выполни split")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # Ротация моделей по ретраям: пробуем лучшую, затем гарантированно рабочую
    models = [m.strip() for m in os.environ.get(
        "GEMINI_MODELS",
        "gemini-3.8-flash,gemini-3.1-flash-lite,gemini-3.7-flash,gemini-3.5-flash",
    ).split(",") if m.strip()]
    print(f"Модели по ротации: {', '.join(models)}")
    parts = [f"ch{c['num']:02d}.p{kk:02d}" for c in manifest["chapters"] for kk in range(1, c["parts"] + 1)]
    todo = [p for p in parts if not (OUT_DIR / f"{p}.ru.txt").exists()
            or not (OUT_DIR / f"{p}.ru.txt").read_text(encoding="utf-8").strip()]
    done = len(parts) - len(todo)
    if args.limit:
        todo = todo[:args.limit]
    print(f"Всего {len(parts)}, готово {done}, к работе {len(todo)}")
    if not todo:
        print("Переводить нечего — выполни merge")
        return
    client = _load_client()
    from google.genai import errors

    def try_chunk(stem):
        text = (PART_DIR / f"{stem}.en.txt").read_text(encoding="utf-8")
        prompt = PROMPT_TMPL.format(text=text)
        for attempt in range(1, MAX_RETRIES + 1):
            model = models[(attempt - 1) % len(models)]
            try:
                resp = client.models.generate_content(
                    model=model, contents=prompt,
                    config={"system_instruction": SYSTEM, "temperature": 0.3},
                )
                ru = (resp.text or "").strip()
                if not ru:
                    raise RuntimeError("пустой ответ")
                print(f"  [{stem}] {model} — успех")
                tmp = OUT_DIR / f"{stem}.ru.txt.tmp"
                tmp.write_text(ru + "\n", encoding="utf-8")
                tmp.replace(OUT_DIR / f"{stem}.ru.txt")
                print(f"  [{stem}]: {len(ru.split())} слов")
                return True
            except (errors.APIError, RuntimeError, ConnectionError) as e:
                wait = min(15 * attempt, 120)
                print(f"  [{stem}] {model}, попытка {attempt}/{MAX_RETRIES}: {type(e).__name__}: {str(e)[:100]}; жду {wait}с")
                time.sleep(wait)
        return False

    # Многоходовка: неудачные чанки не убивают процесс, идут в следующий круг
    pending = todo
    for rnd in range(1, MAX_ROUNDS + 1):
        if rnd > 1:
            print(f"=== Раунд {rnd}: догоняю {len(pending)} чанков, пауза 60с ===", flush=True)
            time.sleep(60)
        failed = []
        for stem in pending:
            if not try_chunk(stem):
                failed.append(stem)
            time.sleep(SLEEP_OK)
        pending = failed
        if not pending:
            break
    left = sum(1 for p in parts if not (OUT_DIR / f"{p}.ru.txt").exists())
    if pending:
        sys.exit(f"ОШИБКА: {len(pending)} чанков не переведено за {MAX_ROUNDS} раундов: {pending[:5]}... (повтори run)")
    print(f"Готово. Осталось чанков: {left}" + (" — повтори run" if left else " — выполни merge"))


def cmd_merge(_args):
    if not MANIFEST.exists():
        sys.exit("ОШИБКА: сначала выполни split")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # Канонический порядок чтения I..XIX (в OCR-файле XV физически стоит первой)
    chapters = sorted(manifest["chapters"], key=lambda c: c["num"])
    out = []
    missing = []
    for c in chapters:
        head = f"ГЛАВА {c['roman']}\n\n{c['title']}\n"
        out.append(head)
        for kk in range(1, c["parts"] + 1):
            f = OUT_DIR / f"ch{c['num']:02d}.p{kk:02d}.ru.txt"
            if not f.exists():
                missing.append(f.name)
                continue
            out.append(f.read_text(encoding="utf-8").strip())
    if missing:
        sys.exit(f"ОШИБКА: нет {len(missing)} переводов: {missing[:5]} ...")
    dest = WORK / "RED-BREAD-gemini-ru.txt"
    dest.write_text("\n\n".join(out), encoding="utf-8")
    print(f"Собрано: {dest} ({len(dest.read_text(encoding='utf-8').split())} слов)")


def cmd_status(_args):
    if not MANIFEST.exists():
        print("split ещё не выполнялся")
        return
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    total = done = 0
    for c in manifest["chapters"]:
        d = sum(1 for kk in range(1, c["parts"] + 1)
                if (OUT_DIR / f"ch{c['num']:02d}.p{kk:02d}.ru.txt").exists())
        total += c["parts"]
        done += d
        flag = "✓" if d == c["parts"] else f"{d}/{c['parts']}"
        print(f"ch{c['num']:02d} [{c['roman']}] {c['title'][:45]:45} {flag}")
    print(f"ИТОГО: {done}/{total} чанков")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("split")
    run = sub.add_parser("run")
    run.add_argument("--limit", type=int, default=0, help="перевести не больше N чанков (для пробы)")
    sub.add_parser("merge")
    sub.add_parser("status")
    args = ap.parse_args()
    {"split": cmd_split, "run": cmd_run, "merge": cmd_merge, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    main()
