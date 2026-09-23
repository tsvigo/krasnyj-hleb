import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import os

# --- НАСТРОЙКИ ---
# Имя входного файла (должен лежать рядом со скриптом)
INPUT_FILE = "/home/v/Desktop/2015.52429.Red-Bread_djvu_fixed.txt"
# Имя выходного файла
OUTPUT_FILE = "/home/v/Desktop/translated_output_fixed.txt"

# Коды языков FLORES-200 (важно для NLLB!)
# Английский: eng_Latn, Русский: rus_Cyrl, Немецкий: deu_Latn и т.д.
SOURCE_LANG = "eng_Latn" 
TARGET_LANG = "rus_Cyrl"

# Модель. 
# "facebook/nllb-200-distilled-600M" - быстрая, легкая (рекомендуется для ПК)
# "facebook/nllb-200-1.3B" - качественнее, но тяжелее
# "facebook/nllb-200-3.3B" - максимальное качество (требует много RAM/VRAM)
MODEL_NAME = "facebook/nllb-200-3.3B"

def translate_file():
    print(f"Загрузка модели {MODEL_NAME}...")
    
    # Определение устройства (GPU или CPU)
    #   device = 0 if torch.cuda.is_available() else -1
    # Принудительно используем CPU (процессор), чтобы избежать ошибок CUDA
    device = -1 
    device_name = "GPU" if device == 0 else "CPU"
    print(f"Используется устройство: {device_name}")

    try:
        # Инициализация пайплайна перевода
        translator = pipeline(
            "translation", 
            model=MODEL_NAME, 
            device=device, 
            src_lang=SOURCE_LANG, 
            tgt_lang=TARGET_LANG,
            max_length=512 # Максимальная длина одного куска
        )
    except Exception as e:
        print(f"Ошибка загрузки модели: {e}")
        return

    print("Начинаю перевод...")

    if not os.path.exists(INPUT_FILE):
        print(f"Файл {INPUT_FILE} не найден!")
        return

    # Открываем файлы
    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        
        lines = f_in.readlines()
        total_lines = len(lines)
        
        # Буфер для накопления текста (чтобы не гонять нейросеть ради одного слова)
        chunk = []
        chunk_size = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Если строка пустая, просто пишем перенос строки
            if not line:
                f_out.write("\n")
                continue
            
            # Переводим строку (абзац)
            # Примечание: для очень длинных абзацев NLLB может обрезать текст.
            # В идеале нужно использовать splitter, но для обычных .txt построчный перевод работает хорошо.
            try:
                # result возвращает список словарей [{'translation_text': '...'}]
                output = translator(line)
                translated_text = output[0]['translation_text']
                
                f_out.write(translated_text + "\n")
                
                # Простой прогресс-бар в консоли
                if i % 10 == 0:
                    print(f"Переведено строк: {i}/{total_lines}", end="\r")
                    
            except Exception as e:
                print(f"\nОшибка при переводе строки {i}: {e}")
                f_out.write(line + "\n") # Если ошибка, пишем оригинал

    print(f"\n\nГотово! Перевод сохранен в {OUTPUT_FILE}")

if __name__ == "__main__":
    translate_file()
