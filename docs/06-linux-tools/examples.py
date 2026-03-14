#!/usr/bin/env python3
"""
Статья 6 — Unicode на практике: Linux, инструменты, исходники ICU.
Главный скрипт: анализ Unicode-состава текстового файла.

Использование:
  python3 examples.py <файл>
  python3 examples.py -               # читать из stdin
  python3 examples.py                 # анализировать встроенный тестовый текст

Зависимости:
  pip install regex      # для расширенных Unicode-свойств
"""
import sys
import unicodedata
from collections import Counter
from pathlib import Path


# ─────────────────────────────────────────────
# 1. Чтение входных данных
# ─────────────────────────────────────────────

SAMPLE_TEXT = """\
Hello, World! Привет, Мир! مرحبا بالعالم こんにちは 你好世界
Unicode содержит: буквы (Aa Яя), цифры (123 ١٢٣), знаки (+-=),
диакритика: café naïve résumé, эмодзи: 🌍🎉🚀👨‍👩‍👧,
символы: © ™ ℝ ∑ ∞, стрелки: ← → ↑ ↓, математика: ²³½⅓,
иврит: שלום, хинди: नमस्ते, греческий: Ελλάδα, корейский: 안녕하세요
"""

if len(sys.argv) > 1:
    src = sys.argv[1]
    if src == '-':
        text = sys.stdin.read()
    else:
        text = Path(src).read_text(encoding='utf-8', errors='replace')
else:
    text = SAMPLE_TEXT
    print("(Используется встроенный тестовый текст. Передайте имя файла как аргумент.)\n")


# ─────────────────────────────────────────────
# 2. Базовая статистика
# ─────────────────────────────────────────────

print("=" * 60)
print("АНАЛИЗ UNICODE-СОСТАВА ТЕКСТА")
print("=" * 60)
print()

total_chars   = len(text)
utf8_bytes    = len(text.encode('utf-8'))
ascii_chars   = sum(1 for c in text if ord(c) < 128)
non_ascii     = total_chars - ascii_chars
unique_chars  = len(set(text))
planes = Counter(ord(c) >> 16 for c in text)

print(f"Символов (code points): {total_chars}")
print(f"Байт в UTF-8:           {utf8_bytes}")
print(f"Уникальных символов:    {unique_chars}")
print(f"ASCII символов:         {ascii_chars} ({ascii_chars/total_chars*100:.1f}%)")
print(f"Non-ASCII символов:     {non_ascii} ({non_ascii/total_chars*100:.1f}%)")
print()
print("По плоскостям:")
PLANE_NAMES = {0: "BMP", 1: "SMP (emoji, исторические)", 2: "SIP (редкие CJK)"}
for plane, count in sorted(planes.items()):
    name = PLANE_NAMES.get(plane, f"Plane {plane}")
    print(f"  Plane {plane} ({name}): {count}")
print()


# ─────────────────────────────────────────────
# 3. Статистика по General Category
# ─────────────────────────────────────────────

CATEGORY_NAMES = {
    'Lu': 'Letter Uppercase', 'Ll': 'Letter Lowercase', 'Lt': 'Letter Titlecase',
    'Lm': 'Letter Modifier',  'Lo': 'Letter Other',
    'Mn': 'Mark Nonspacing',  'Mc': 'Mark Spacing',     'Me': 'Mark Enclosing',
    'Nd': 'Number Decimal',   'Nl': 'Number Letter',    'No': 'Number Other',
    'Pc': 'Punct Connector',  'Pd': 'Punct Dash',       'Ps': 'Punct Open',
    'Pe': 'Punct Close',      'Pi': 'Punct Init Quote', 'Pf': 'Punct Final Quote',
    'Po': 'Punct Other',
    'Sm': 'Symbol Math',      'Sc': 'Symbol Currency',  'Sk': 'Symbol Modifier',
    'So': 'Symbol Other',
    'Zs': 'Separator Space',  'Zl': 'Sep Line',         'Zp': 'Sep Para',
    'Cc': 'Control',          'Cf': 'Format',           'Cs': 'Surrogate',
    'Co': 'Private Use',      'Cn': 'Unassigned',
}

cats = Counter(unicodedata.category(c) for c in text)
print("По категориям General Category:")
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    name = CATEGORY_NAMES.get(cat, cat)
    bar = '█' * min(count, 40)
    print(f"  {cat} ({name:20s}): {count:5d}  {bar}")
print()


# ─────────────────────────────────────────────
# 4. Статистика по скриптам (через UnicodeData / regex)
# ─────────────────────────────────────────────

print("По скриптам:")

# Попробуем через regex (если установлен)
try:
    import regex

    # Получить скрипт символа через regex.regex.cache / unicode properties
    def get_script_regex(char: str) -> str:
        r"""Определить скрипт символа через свойство \p{Script=...}"""
        scripts_to_check = [
            'Latin', 'Cyrillic', 'Arabic', 'Han', 'Hiragana', 'Katakana',
            'Hangul', 'Greek', 'Hebrew', 'Devanagari', 'Bengali', 'Gujarati',
            'Gurmukhi', 'Kannada', 'Malayalam', 'Oriya', 'Tamil', 'Telugu',
            'Thai', 'Tibetan', 'Armenian', 'Georgian', 'Ethiopic',
        ]
        for script in scripts_to_check:
            if regex.match(rf'\p{{Script={script}}}', char):
                return script
        # Проверить Common и Inherited
        cp = ord(char)
        cat = unicodedata.category(char)
        if cat in ('Nd', 'Po', 'Ps', 'Pe', 'Pd', 'Sm', 'Sc', 'Zs'):
            return 'Common'
        if cat.startswith('C'):
            return 'Control/Format'
        return 'Other'

    script_counts: Counter = Counter()
    for ch in text:
        script_counts[get_script_regex(ch)] += 1

    for script, count in sorted(script_counts.items(), key=lambda x: -x[1]):
        pct = count / total_chars * 100
        bar = '█' * min(int(pct), 30)
        print(f"  {script:20s}: {count:5d} ({pct:5.1f}%)  {bar}")

except ImportError:
    print("  (модуль regex не установлен — скрипты не определяются)")
    print("  Установите: pip install regex")

print()


# ─────────────────────────────────────────────
# 5. Найти эмодзи в тексте
# ─────────────────────────────────────────────

print("Эмодзи в тексте:")

try:
    import regex
    emojis = regex.findall(r'\p{Emoji_Presentation}|\p{Extended_Pictographic}', text)
    emoji_counts = Counter(emojis)
    if emoji_counts:
        for emoji, count in sorted(emoji_counts.items(), key=lambda x: -x[1]):
            cp = ord(emoji[0]) if emoji else 0
            print(f"  {emoji}  U+{cp:04X}  ×{count}")
    else:
        print("  (эмодзи не найдены)")
except ImportError:
    # Fallback: категория So + SMP
    emojis = [c for c in text if ord(c) > 0xFFFF or unicodedata.category(c) == 'So']
    print(f"  (приблизительно, без regex): {list(set(emojis))[:20]}")
print()


# ─────────────────────────────────────────────
# 6. Найти не-ASCII символы с их именами
# ─────────────────────────────────────────────

print("Уникальные не-ASCII символы (топ-30 по частоте):")
non_ascii_chars = Counter(c for c in text if ord(c) >= 128)
for ch, count in non_ascii_chars.most_common(30):
    cp = ord(ch)
    name = unicodedata.name(ch, "?")
    cat  = unicodedata.category(ch)
    print(f"  U+{cp:05X}  {ch!r:5s} ×{count:3d}  [{cat}]  {name}")
print()


# ─────────────────────────────────────────────
# 7. Проверка нормализации текста
# ─────────────────────────────────────────────

print("Нормализация:")
for form in ('NFC', 'NFD', 'NFKC', 'NFKD'):
    is_norm = unicodedata.is_normalized(form, text)
    norm_text = unicodedata.normalize(form, text)
    diff = len(norm_text) - len(text)
    print(f"  {form}: already_normalized={is_norm}  "
          f"len_diff={diff:+d}  "
          f"bytes_diff={len(norm_text.encode('utf-8')) - utf8_bytes:+d}")
print()


# ─────────────────────────────────────────────
# 8. Обнаружение потенциальных проблем
# ─────────────────────────────────────────────

print("Потенциальные проблемы:")

# Символы в нескольких скриптах с похожим видом (Confusables)
latin_chars = set(c for c in text if unicodedata.category(c).startswith('L')
                   and 'LATIN' in unicodedata.name(c, ''))
cyrillic_look_like_latin = []
for c in text:
    name = unicodedata.name(c, '')
    if 'CYRILLIC' in name and unicodedata.category(c).startswith('L'):
        # Проверить, есть ли похожий Latin символ
        lower = c.lower()
        if any(l.lower() == lower for l in 'aAbBcCeEHKMmopPrTx'):
            cyrillic_look_like_latin.append(c)

if cyrillic_look_like_latin:
    unique_conf = set(cyrillic_look_like_latin)
    conf_info = [f"U+{ord(c):04X}({unicodedata.name(c, '?')[:20]})" for c in sorted(unique_conf)]
    print(f"  Кириллические символы, похожие на латинские: {conf_info}")
else:
    print("  Подозрительных смешений Latin/Cyrillic не обнаружено")

# Управляющие символы (кроме \n, \r, \t)
control_chars = [c for c in text if unicodedata.category(c) == 'Cc'
                  and c not in '\n\r\t']
if control_chars:
    print(f"  Управляющие символы: {[f'U+{ord(c):04X}' for c in set(control_chars)]}")
else:
    print("  Управляющих символов не обнаружено")

# Нулевые и нулевой-ширины символы
zero_width = [c for c in text if unicodedata.category(c) == 'Cf']
if zero_width:
    zw_info = [f"U+{ord(c):04X}({unicodedata.name(c, '?')})" for c in set(zero_width)]
    print(f"  Format/Zero-width символы: {zw_info}")
else:
    print("  Format/Zero-width символов не обнаружено")

print()


# ─────────────────────────────────────────────
# 9. regex-примеры: поиск по Unicode-свойствам
# ─────────────────────────────────────────────

try:
    import regex

    print("=== Поиск по Unicode-свойствам (regex модуль) ===\n")

    patterns = [
        (r'\p{Script=Latin}+',    "Latin слова"),
        (r'\p{Script=Cyrillic}+', "Cyrillic слова"),
        (r'\p{Script=Arabic}+',   "Arabic слова"),
        (r'\p{Script=Han}+',      "Han (CJK)"),
        (r'\p{Lu}',               "Заглавные буквы"),
        (r'\p{Nd}+',              "Числа (decimal)"),
        (r'\p{Emoji_Presentation}+', "Emoji"),
        (r'\X',                   "Графемные кластеры"),
    ]

    for pattern, description in patterns:
        matches = regex.findall(pattern, text)
        count = len(matches)
        examples = matches[:5]
        print(f"  {description} ({pattern}):")
        print(f"    Найдено: {count}  Примеры: {examples}")
    print()

    # Замена fullwidth символов на ASCII
    fullwidth_text = "Ｈｅｌｌｏ，　Ｗｏｒｌｄ！"
    normalized = regex.sub(r'\p{InFullwidth_Latin_Letters}|[\uFF01-\uFF60\uFFE0-\uFFE6]',
                            lambda m: unicodedata.normalize('NFKC', m.group()),
                            fullwidth_text)
    print(f"  Fullwidth → ASCII:")
    print(f"    Исходная: {fullwidth_text!r}")
    print(f"    NFKC:     {unicodedata.normalize('NFKC', fullwidth_text)!r}")
    print()

except ImportError:
    print("(Секция regex пропущена — установите: pip install regex)\n")
