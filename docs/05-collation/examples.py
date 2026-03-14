#!/usr/bin/env python3
"""
Статья 5 — Коллация: Unicode Collation Algorithm и CLDR.
Практические примеры на Python.

Зависимости:
  pip install PyICU        # Python bindings для ICU
  # На Linux:
  # sudo apt install libicu-dev
  # pip install PyICU

Если PyICU не установлен — примеры с ним будут пропущены.
"""
import unicodedata
import locale
from functools import cmp_to_key

# ─────────────────────────────────────────────
# 0. Проблема наивной сортировки
# ─────────────────────────────────────────────

print("=== Проблема наивной сортировки ===\n")

ru_words = ['ёж', 'Ель', 'елка', 'Ёж', 'ель', 'Ежевика', 'Ещё']
en_words = ['apple', 'Banana', 'cherry', 'Apricot', 'banana', 'CHERRY']
mixed    = ['café', 'cafe', 'Café', 'CAFE', 'cáfe']
numbers  = ['file1', 'file10', 'file2', 'file20', 'file3']

print("Русские слова:")
print(f"  Naive:    {sorted(ru_words)}")
print(f"  Expected: ['ежевика', 'ёж', 'Ёж', 'ель', 'Ель', 'елка', 'ещё']  (приблизительно)")

print("\nАнглийские слова:")
print(f"  Naive:    {sorted(en_words)}")
print(f"  Expected: ['apple', 'Apricot', 'Banana', 'banana', 'CHERRY', 'cherry']")

print("\nСловa с диакритикой:")
print(f"  Naive:    {sorted(mixed)}")
print(f"  Expected: ['cafe', 'CAFE', 'café', 'Café', 'cáfe'] (L1 одинаковый)")

print("\nФайлы с числами:")
print(f"  Naive:    {sorted(numbers)}")
print(f"  Natural:  ['file1', 'file2', 'file3', 'file10', 'file20']")
print()


# ─────────────────────────────────────────────
# 1. locale.strcoll — системная коллация (зависит от LANG)
# ─────────────────────────────────────────────

print("=== locale.strcoll (системная локаль) ===\n")

try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    ru_sorted = sorted(ru_words, key=cmp_to_key(locale.strcoll))
    print(f"  ru_RU.UTF-8: {ru_sorted}")
except locale.Error as e:
    print(f"  Локаль ru_RU.UTF-8 недоступна: {e}")

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    en_sorted = sorted(en_words, key=cmp_to_key(locale.strcoll))
    print(f"  en_US.UTF-8: {en_sorted}")
except locale.Error as e:
    print(f"  Локаль en_US.UTF-8 недоступна: {e}")

# Вернуть системную локаль
locale.setlocale(locale.LC_ALL, '')
print()


# ─────────────────────────────────────────────
# 2. Ручная реализация UCA-подобной сортировки (упрощённая)
# ─────────────────────────────────────────────

def simple_sort_key(s: str, case_sensitive: bool = False) -> tuple:
    """
    Упрощённый ключ сортировки:
    - L1: NFKD, убрать combining marks → основные буквы в нижнем регистре
    - L2: combining marks (диакритика)
    - L3: регистр оригинала
    """
    nfkd = unicodedata.normalize('NFKD', s)
    l1 = ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn').lower()
    l2 = ''.join(c for c in nfkd if unicodedata.category(c) == 'Mn')
    l3 = s if case_sensitive else s.lower()
    return (l1, l2, l3)


print("=== Упрощённая UCA-подобная сортировка ===\n")
print("Слова с диакритикой:")
sorted_mixed = sorted(mixed, key=simple_sort_key)
print(f"  {sorted_mixed}")

print("\nАнглийские слова (case-insensitive):")
sorted_en = sorted(en_words, key=simple_sort_key)
print(f"  {sorted_en}")
print()


# ─────────────────────────────────────────────
# 3. PyICU — полная реализация UCA + CLDR
# ─────────────────────────────────────────────

try:
    import icu
    HAS_ICU = True
except ImportError:
    HAS_ICU = False
    print("PyICU не установлен. Установите: pip install PyICU")
    print("(на Linux: sudo apt install libicu-dev && pip install PyICU)")
    print()


if HAS_ICU:
    print("=== PyICU: коллация с разными локалями ===\n")

    def icu_sort(words: list[str], locale_id: str, **kwargs) -> list[str]:
        collator = icu.Collator.createInstance(icu.Locale(locale_id))
        # Strength: PRIMARY, SECONDARY, TERTIARY (по умолчанию TERTIARY)
        if 'strength' in kwargs:
            collator.setStrength(kwargs['strength'])
        return sorted(words, key=collator.getSortKey)

    # Русский
    print("Русские слова:")
    print(f"  ru_RU (default):  {icu_sort(ru_words, 'ru_RU')}")

    # Английский
    print("\nАнглийские слова:")
    print(f"  en_US (tertiary): {icu_sort(en_words, 'en_US')}")
    print(f"  en_US (primary):  {icu_sort(en_words, 'en_US', strength=icu.Collator.PRIMARY)}")

    # Диакритика
    print("\nСлова с диакритикой:")
    print(f"  en_US (tertiary): {icu_sort(mixed, 'en_US')}")
    print(f"  en_US (primary):  {icu_sort(mixed, 'en_US', strength=icu.Collator.PRIMARY)}")

    # Шведский: ä и ö идут ПОСЛЕ z
    se_words = ['ärlig', 'zebra', 'öppen', 'apple', 'åska', 'banana']
    print(f"\nШведский (sv_SE):  {icu_sort(se_words, 'sv_SE')}")
    print(f"Немецкий (de_DE):  {icu_sort(se_words, 'de_DE')}")  # ä ≈ a

    # Немецкий phonebook vs standard
    de_words = ['Müller', 'Mueller', 'Muller', 'müssen', 'muss']
    print(f"\nНемецкий standard  (de):       {icu_sort(de_words, 'de')}")
    print(f"Немецкий phonebook (de@collation=phonebook): {icu_sort(de_words, 'de@collation=phonebook')}")

    print()

    # ─────────────────────────────────────────────
    # 4. Sort Keys — как они выглядят
    # ─────────────────────────────────────────────

    print("=== Sort Keys ===\n")
    collator_en = icu.Collator.createInstance(icu.Locale('en_US'))
    for word in ['apple', 'Apple', 'APPLE', 'ápple', 'áPPle']:
        key = collator_en.getSortKey(word)
        key_hex = key.hex() if isinstance(key, bytes) else key.encode('latin-1').hex()
        print(f"  {word!r:10s}: {key_hex}")
    print()

    # ─────────────────────────────────────────────
    # 5. Кастомные правила tailoring
    # ─────────────────────────────────────────────

    print("=== Кастомные правила (tailoring) ===\n")

    # Пример: поставить цифры после букв
    # В UCA цифры обычно идут перед буквами
    test_words = ['apple', '10', 'banana', '2', 'cherry', '1']
    print(f"Стандартная en_US: {icu_sort(test_words, 'en')}")

    # Tailoring: числа в конце
    rules = "&z < 0 < 1 < 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9"
    custom_collator = icu.RuleBasedCollator(rules)
    custom_sorted = sorted(test_words, key=custom_collator.getSortKey)
    print(f"Кастомные правила (цифры после z): {custom_sorted}")
    print()

    # ─────────────────────────────────────────────
    # 6. Нечёткое сравнение — PRIMARY strength
    # ─────────────────────────────────────────────

    print("=== Сравнение строк без учёта регистра и диакритики ===\n")
    collator_primary = icu.Collator.createInstance(icu.Locale('en'))
    collator_primary.setStrength(icu.Collator.PRIMARY)

    pairs = [
        ('café', 'cafe'),
        ('Ñoño', 'nono'),
        ('apple', 'Apple'),
        ('apple', 'APPLE'),
        ('straße', 'strasse'),
    ]
    for a, b in pairs:
        result = collator_primary.compare(a, b)
        equal = result == 0
        print(f"  {a!r:12s} vs {b!r:12s}: {'EQUAL' if equal else f'diff={result}'}")
    print()


# ─────────────────────────────────────────────
# 7. Натуральная сортировка (без PyICU)
# ─────────────────────────────────────────────

import re

def natural_sort_key(s: str) -> list:
    """Ключ для натуральной сортировки: числа как числа, буквы как строки."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', s)]


print("=== Натуральная сортировка ===\n")
file_names = ['file1', 'file10', 'file2', 'file20', 'file3', 'file100', 'file11']
print(f"  Naive:   {sorted(file_names)}")
print(f"  Natural: {sorted(file_names, key=natural_sort_key)}")
print()

# Смешанные строки
mixed_numbers = ['Chapter 10', 'Chapter 2', 'Chapter 1', 'Chapter 20', 'Intro']
print(f"  Mixed naive:   {sorted(mixed_numbers)}")
print(f"  Mixed natural: {sorted(mixed_numbers, key=natural_sort_key)}")
print()


# ─────────────────────────────────────────────
# 8. Парсинг allkeys.txt (DUCET)
# ─────────────────────────────────────────────

from pathlib import Path

allkeys_path = Path(__file__).parent.parent / "02-ucd-files" / "data" / "allkeys.txt"

if allkeys_path.exists():
    print("=== Парсинг allkeys.txt (DUCET) ===\n")

    def parse_allkeys(path: Path, max_lines: int = 100) -> list[dict]:
        entries = []
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('@'):
                    continue
                # Формат: "0041  ; [.1C47.0020.0008] # COMMENT"
                if ';' not in line:
                    continue
                code_part, weight_part = line.split(';', 1)
                weight_part = weight_part.split('#')[0].strip()
                cps = [int(x, 16) for x in code_part.strip().split()]
                # Парсим все элементы весов [.L1.L2.L3]
                weights = re.findall(r'\[([*.])([0-9A-F]+)\.([0-9A-F]+)\.([0-9A-F]+)\]', weight_part)
                entries.append({'cps': cps, 'weights': weights})
                if len(entries) >= max_lines:
                    break
        return entries

    entries = parse_allkeys(allkeys_path, max_lines=50)
    print(f"Первые 10 записей:")
    for entry in entries[:10]:
        cps_str = ' '.join(f'U+{cp:04X}({chr(cp) if cp < 0x10000 else "?"})'
                           for cp in entry['cps'])
        weights_str = ' '.join(f'[{w[0]}{w[1]}.{w[2]}.{w[3]}]' for w in entry['weights'])
        print(f"  {cps_str:<30}: {weights_str}")
    print()
else:
    print("=== allkeys.txt не найден ===")
    print("Скачайте: wget https://unicode.org/Public/UCA/latest/allkeys.txt "
          "-P ../02-ucd-files/data/")
    print()
