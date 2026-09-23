#!/usr/bin/env python3
"""Перевод книги .txt через Ollama (en -> ru)"""

import requests
import sys
import time
from pathlib import Path


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2"  # или llama3, mistral
CHUNK_SIZE = 2000  # символов на chunk — безопасный размер для контекста


def translate_chunk(text: str, attempt=1) -> str:
    prompt = (
        "Translate the following English text into Russian. "
        "Output ONLY the Russian translation, nothing else. "
        "Preserve paragraph breaks.\n\n"
        f"{text}"
    )
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4096,
            }
        }, timeout=300)
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except Exception as e:
        if attempt < 3:
            print(f"  Ошибка: {e}, повтор {attempt}/3...")
            time.sleep(5)
            return translate_chunk(text, attempt + 1)
        raise


def split_into_chunks(text: str, max_size: int) -> list[str]:
    """Разбивает текст по абзацам, не превышая max_size."""
    paragraphs = text.split("\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 > max_size and current:
            chunks.append(current.strip())
            current = ""
        current += para + "\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def main():
    if len(sys.argv) < 2:
        print("Использование: python translate.py input.txt [output.txt]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".ru.txt")

    text = input_file.read_text(encoding="utf-8")
    chunks = split_into_chunks(text, CHUNK_SIZE)

    print(f"Файл: {input_file} ({len(text)} символов)")
    print(f"Модель: {MODEL}")
    print(f"Частей: {len(chunks)}")
    print(f"Вывод: {output_file}")
    print("-" * 40)

    translated_parts = []
    start = time.time()

    for i, chunk in enumerate(chunks, 1):
        elapsed = time.time() - start
        eta = (elapsed / i * (len(chunks) - i)) if i > 1 else 0
        print(f"[{i}/{len(chunks)}] {len(chunk)} симв. | ETA: {eta/60:.0f} мин")

        result = translate_chunk(chunk)
        translated_parts.append(result)

        # сохраняем промежуточный результат после каждого куска
        output_file.write_text("\n\n".join(translated_parts), encoding="utf-8")

    total = time.time() - start
    print("-" * 40)
    print(f"Готово за {total/60:.1f} мин -> {output_file}")


if __name__ == "__main__":
    main()
