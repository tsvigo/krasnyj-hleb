import language_tool_python
from tqdm import tqdm
import os
import sys

def process_book(input_file):
    # Настройки файлов вывода
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_fixed.txt"
    log_file = f"{base_name}_changes_log.txt"

    # 1. Инициализация инструмента
    print("Загрузка языковой модели...")
    tool = language_tool_python.LanguageTool('en-US') 

    # Исключения (пишите в нижнем регистре)
    ignored_words = {'daenerys', 'hogwarts', 'gandalf', 'mordor', 'ussr', 'bolshevik'}

    # 2. Чтение файла
    print(f"Чтение файла {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print("Ошибка: Файл не найден. Проверьте путь.")
        return

    # 3. Разбивка на абзацы
    paragraphs = text.split('\n')
    
    fixed_paragraphs = []
    changes_log = []

    print(f"Найдено {len(paragraphs)} параграфов. Начинаем проверку...")

    # 4. Проход по тексту
    for p in tqdm(paragraphs, unit="par"):
        if not p.strip():
            fixed_paragraphs.append(p)
            continue
        
        try:
            matches = tool.check(p)
            
            filtered_matches = []
            for m in matches:
                # --- ИСПРАВЛЕНИЕ ЗДЕСЬ (error_length вместо errorLength) ---
                bad_word = p[m.offset : m.offset + m.error_length]
                
                if bad_word.lower() in ignored_words:
                    continue
                
                if m.replacements:
                    replacement = m.replacements[0]
                    # Ограничим длину контекста в логе, чтобы не засорять файл
                    ctx_start = max(0, m.offset - 15)
                    ctx_end = min(len(p), m.offset + m.error_length + 15)
                    context_snippet = p[ctx_start:ctx_end].replace('\n', ' ')

                    log_entry = f"Original: '{bad_word}' -> Fixed: '{replacement}' | Context: ...{context_snippet}..."
                    changes_log.append(log_entry)
                    
                    filtered_matches.append(m)

            # Применяем исправления
            corrected_p = language_tool_python.utils.correct(p, filtered_matches)
            fixed_paragraphs.append(corrected_p)

        except Exception as e:
            # Если на конкретном абзаце случилась ошибка, мы не крашим весь скрипт
            # Просто сохраняем оригинал и пишем ошибку в консоль
            print(f"\nОшибка в параграфе: {str(e)}")
            fixed_paragraphs.append(p)

    # 5. Сохранение
    print("Сохранение файлов...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_paragraphs))
        
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Всего исправлений: {len(changes_log)}\n\n")
        f.write('\n'.join(changes_log))

    print(f"Готово!")
    print(f"Исправленный текст: {output_file}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Можно передать файл аргументом или прописать жестко
    # python fix_book.py "имя_файла.txt"
    
    target_file = '/home/v/Desktop/2015.52429.Red-Bread_djvu.txt'
    
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        
    process_book(target_file)
