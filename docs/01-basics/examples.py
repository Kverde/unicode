#!/usr/bin/env python3
"""
Статья 1 — Основы Unicode: кодовые точки, плоскости, блоки.
Примеры на Python с использованием стандартной библиотеки unicodedata.
"""
import unicodedata
import sys


# ─────────────────────────────────────────────
# 1. Информация о конкретном символе
# ─────────────────────────────────────────────

def char_info(char: str) -> None:
    """Вывести все основные свойства символа."""
    cp = ord(char)
    print(f"Символ:     {char!r}")
    print(f"Code Point: U+{cp:04X}  (десятичное: {cp})")
    print(f"Имя:        {unicodedata.name(char, '(нет имени)')}")
    print(f"Категория:  {unicodedata.category(char)}")
    print(f"Bidi Class: {unicodedata.bidirectional(char)}")
    print(f"CCC:        {unicodedata.combining(char)}")
    print(f"Mirrored:   {unicodedata.mirrored(char)}")
    print(f"Decomp:     {unicodedata.decomposition(char) or '(нет)'}")
    print(f"East Asian: {unicodedata.east_asian_width(char)}")
    print()


print("=== Свойства отдельных символов ===\n")
for ch in ['A', 'А', 'ñ', '🌍', '½', '؀', '\u0301', '0', '٠']:
    char_info(ch)


# ─────────────────────────────────────────────
# 2. Определение плоскости символа
# ─────────────────────────────────────────────

PLANE_NAMES = {
    0: "BMP (Basic Multilingual Plane)",
    1: "SMP (Supplementary Multilingual Plane)",
    2: "SIP (Supplementary Ideographic Plane)",
    3: "TIP (Tertiary Ideographic Plane)",
    14: "SSP (Supplementary Special-purpose Plane)",
    15: "SPUA-A (Supplementary Private Use Area-A)",
    16: "SPUA-B (Supplementary Private Use Area-B)",
}

def get_plane(char: str) -> tuple[int, str]:
    cp = ord(char)
    plane_num = cp >> 16  # старшие биты
    return plane_num, PLANE_NAMES.get(plane_num, f"Plane {plane_num} (зарезервирована)")


print("=== Плоскости символов ===\n")
test_chars = [
    ('A',      "Latin A"),
    ('中',      "CJK иероглиф"),
    ('🌍',     "Emoji (Земля)"),
    ('𐐷',     "Deseret Small Letter Ew (SMP)"),
    ('𠀀',     "CJK Extension B (SIP)"),
    ('\U000E0041', "Language tag A (SSP)"),
]
for char, desc in test_chars:
    plane_num, plane_name = get_plane(char)
    cp = ord(char)
    print(f"U+{cp:05X}  {desc:30s}  → Plane {plane_num}: {plane_name}")
print()


# ─────────────────────────────────────────────
# 3. Обход диапазона кодовых точек и подсчёт по категориям
# ─────────────────────────────────────────────

from collections import Counter

def count_categories(start: int, end: int) -> Counter:
    """Подсчитать категории символов в диапазоне кодовых точек."""
    cats: Counter = Counter()
    for cp in range(start, end + 1):
        try:
            ch = chr(cp)
            cats[unicodedata.category(ch)] += 1
        except ValueError:
            pass
    return cats


print("=== Категории символов в ASCII (U+0000..U+007F) ===\n")
cats = count_categories(0x0000, 0x007F)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
print()

print("=== Категории символов в Cyrillic block (U+0400..U+04FF) ===\n")
cats = count_categories(0x0400, 0x04FF)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
print()


# ─────────────────────────────────────────────
# 4. Поиск всех символов по категории
# ─────────────────────────────────────────────

def find_chars_by_category(category: str, max_count: int = 20) -> list[str]:
    """Найти первые max_count символов заданной категории в BMP."""
    result = []
    for cp in range(0x10000):
        ch = chr(cp)
        if unicodedata.category(ch) == category:
            result.append(ch)
            if len(result) >= max_count:
                break
    return result


print("=== Первые 20 символов категории Sc (Currency Symbol) ===\n")
currency_symbols = find_chars_by_category("Sc")
for ch in currency_symbols:
    cp = ord(ch)
    name = unicodedata.name(ch, "?")
    print(f"  U+{cp:04X}  {ch}  {name}")
print()


# ─────────────────────────────────────────────
# 5. Числовые значения символов (цифры из разных письменностей)
# ─────────────────────────────────────────────

print("=== Цифры из разных письменностей ===\n")
digit_chars = [
    '0', '٠', '۰', '०', '০', '੦', '૦', '୦', '௦', '൦',  # 0 в разных системах
    '٩', '۹', '९', '৯',  # 9 в разных системах
]
for ch in digit_chars:
    cp = ord(ch)
    num = unicodedata.numeric(ch, None)
    name = unicodedata.name(ch, "?")
    print(f"  U+{cp:04X}  {ch}  numeric={num}  {name}")
print()


# ─────────────────────────────────────────────
# 6. Версия Unicode в вашем Python
# ─────────────────────────────────────────────

print(f"=== Версия Unicode в Python {sys.version.split()[0]} ===\n")
print(f"  unicodedata.unidata_version = {unicodedata.unidata_version}")
print(f"  sys.maxunicode              = U+{sys.maxunicode:X}")
print()
