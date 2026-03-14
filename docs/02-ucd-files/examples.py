#!/usr/bin/env python3
"""
Статья 2 — Unicode Character Database (UCD).
Парсинг файлов UCD вручную + сравнение с модулем unicodedata.

Перед запуском скачайте файлы:
  cd data/
  wget https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
  wget https://unicode.org/Public/UCD/latest/ucd/Blocks.txt
  wget https://unicode.org/Public/UCD/latest/ucd/Scripts.txt
  wget https://unicode.org/Public/UCD/latest/ucd/PropList.txt
"""
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


# ─────────────────────────────────────────────
# 1. Парсинг UnicodeData.txt
# ─────────────────────────────────────────────

def parse_unicode_data(path: Path) -> list[dict]:
    """Распарсить UnicodeData.txt в список словарей."""
    FIELDS = [
        "code_point", "name", "general_category", "canonical_combining_class",
        "bidi_class", "decomposition", "decimal_digit", "digit", "numeric",
        "mirrored", "unicode_1_name", "iso_comment",
        "uppercase_mapping", "lowercase_mapping", "titlecase_mapping",
    ]
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            rec = dict(zip(FIELDS, parts))
            rec["code_point"] = int(rec["code_point"], 16)
            records.append(rec)
    return records


def expand_ranges(records: list[dict]) -> list[dict]:
    """Развернуть диапазоны (First/Last) в отдельные записи."""
    result = []
    i = 0
    while i < len(records):
        rec = records[i]
        name = rec["name"]
        if name.endswith(", First>"):
            # Следующая запись — Last
            last_rec = records[i + 1]
            template_name = name[1:-8]  # убрать < и ", First>"
            cat = rec["general_category"]
            for cp in range(rec["code_point"], last_rec["code_point"] + 1):
                new_rec = dict(rec)
                new_rec["code_point"] = cp
                new_rec["name"] = f"{template_name}-{cp:04X}"
                result.append(new_rec)
            i += 2
        else:
            result.append(rec)
            i += 1
    return result


print("=== Парсинг UnicodeData.txt ===\n")
udata_path = DATA_DIR / "UnicodeData.txt"

if not udata_path.exists():
    print(f"Файл не найден: {udata_path}")
    print("Скачайте: wget https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt -P data/")
    print()
else:
    records = parse_unicode_data(udata_path)
    print(f"Всего строк в файле: {len(records)}")

    # Подсчёт по категориям
    cats = Counter(r["general_category"] for r in records)
    print("\nТоп-10 категорий:")
    for cat, count in cats.most_common(10):
        print(f"  {cat}: {count}")

    # Все символы категории Pi (Initial Quote Punctuation)
    pi_chars = [r for r in records if r["general_category"] == "Pi"]
    print(f"\nСимволы категории Pi (Initial Quote): {len(pi_chars)}")
    for r in pi_chars:
        cp = r["code_point"]
        try:
            ch = chr(cp)
            name = unicodedata.name(ch)
        except (ValueError, TypeError):
            name = r["name"]
        print(f"  U+{cp:04X}  {name}")

    # Символы с числовым значением (дроби)
    fractions = [r for r in records if "/" in r["numeric"]]
    print(f"\nДроби (numeric содержит '/'): {len(fractions)}")
    for r in fractions[:10]:
        cp = r["code_point"]
        try:
            ch = chr(cp)
        except ValueError:
            ch = "?"
        print(f"  U+{cp:04X}  {ch}  numeric={r['numeric']}  {r['name']}")

    # Символы с decomposition (для нормализации)
    with_decomp = [r for r in records if r["decomposition"]]
    print(f"\nСимволов с decomposition: {len(with_decomp)}")
    # Первые 5 с compat-decomposition (тип в угловых скобках)
    compat = [r for r in with_decomp if r["decomposition"].startswith("<")]
    print(f"  Из них с compatibility decomposition: {len(compat)}")
    print("  Первые 5:")
    for r in compat[:5]:
        cp = r["code_point"]
        try:
            ch = chr(cp)
        except ValueError:
            ch = "?"
        print(f"    U+{cp:04X}  {ch}  decomp={r['decomposition']!r}  {r['name']}")
    print()


# ─────────────────────────────────────────────
# 2. Парсинг Blocks.txt
# ─────────────────────────────────────────────

def parse_blocks(path: Path) -> list[tuple[int, int, str]]:
    """Вернуть список (start, end, block_name)."""
    blocks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            range_part, name = line.split(";", 1)
            start_s, end_s = range_part.strip().split("..")
            blocks.append((int(start_s, 16), int(end_s, 16), name.strip()))
    return blocks


def find_block(cp: int, blocks: list[tuple[int, int, str]]) -> str:
    for start, end, name in blocks:
        if start <= cp <= end:
            return name
    return "No Block"


print("=== Парсинг Blocks.txt ===\n")
blocks_path = DATA_DIR / "Blocks.txt"

if not blocks_path.exists():
    print(f"Файл не найден: {blocks_path}")
    print("Скачайте: wget https://unicode.org/Public/UCD/latest/ucd/Blocks.txt -P data/")
    print()
else:
    blocks = parse_blocks(blocks_path)
    print(f"Всего блоков: {len(blocks)}")
    print("\nПервые 10 блоков:")
    for start, end, name in blocks[:10]:
        size = end - start + 1
        print(f"  U+{start:04X}..U+{end:04X}  ({size:5d} позиций)  {name}")

    # Найти блок для нескольких символов
    print("\nОпределение блока для символов:")
    test_chars = ['A', 'А', '🌍', '中', '½', '؀']
    for ch in test_chars:
        cp = ord(ch)
        block = find_block(cp, blocks)
        print(f"  U+{cp:05X}  {ch!r:5}  →  {block}")
    print()


# ─────────────────────────────────────────────
# 3. Парсинг Scripts.txt
# ─────────────────────────────────────────────

def parse_scripts(path: Path) -> list[tuple[int, int, str]]:
    """Вернуть список (start, end, script_name)."""
    scripts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Убираем комментарий
            line = line.split("#")[0].strip()
            if not line:
                continue
            range_part, script = line.split(";", 1)
            range_part = range_part.strip()
            script = script.strip()
            if ".." in range_part:
                start_s, end_s = range_part.split("..")
                start, end = int(start_s, 16), int(end_s, 16)
            else:
                start = end = int(range_part, 16)
            scripts.append((start, end, script))
    return scripts


def find_script(cp: int, scripts: list[tuple[int, int, str]]) -> str:
    for start, end, script in scripts:
        if start <= cp <= end:
            return script
    return "Unknown"


print("=== Парсинг Scripts.txt ===\n")
scripts_path = DATA_DIR / "Scripts.txt"

if not scripts_path.exists():
    print(f"Файл не найден: {scripts_path}")
    print("Скачайте: wget https://unicode.org/Public/UCD/latest/ucd/Scripts.txt -P data/")
    print()
else:
    scripts = parse_scripts(scripts_path)

    # Подсчёт символов по скриптам
    script_counts: Counter = Counter()
    for start, end, script in scripts:
        script_counts[script] += end - start + 1

    print(f"Всего диапазонов в Scripts.txt: {len(scripts)}")
    print("\nТоп-15 скриптов по количеству символов:")
    for script, count in script_counts.most_common(15):
        print(f"  {script:30s}: {count}")

    # Определение скрипта для символов
    print("\nОпределение скрипта для символов:")
    test_chars = ['A', 'А', '🌍', '中', '0', '٠', 'ñ', 'ל', 'ম']
    for ch in test_chars:
        cp = ord(ch)
        script = find_script(cp, scripts)
        block = find_block(cp, blocks) if blocks_path.exists() else "?"
        print(f"  U+{cp:05X}  {ch!r:5}  Script={script:15s}  Block={block}")
    print()


# ─────────────────────────────────────────────
# 4. Парсинг PropList.txt — бинарные свойства
# ─────────────────────────────────────────────

def parse_proplist(path: Path) -> dict[str, list[tuple[int, int]]]:
    """Вернуть словарь {property_name: [(start, end), ...]}"""
    props: dict[str, list] = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.split("#")[0].strip()
            if not line:
                continue
            range_part, prop = line.split(";", 1)
            range_part = range_part.strip()
            prop = prop.strip()
            if ".." in range_part:
                start_s, end_s = range_part.split("..")
                start, end = int(start_s, 16), int(end_s, 16)
            else:
                start = end = int(range_part, 16)
            props[prop].append((start, end))
    return dict(props)


def count_prop_chars(ranges: list[tuple[int, int]]) -> int:
    return sum(end - start + 1 for start, end in ranges)


print("=== Парсинг PropList.txt ===\n")
proplist_path = DATA_DIR / "PropList.txt"

if not proplist_path.exists():
    print(f"Файл не найден: {proplist_path}")
    print("Скачайте: wget https://unicode.org/Public/UCD/latest/ucd/PropList.txt -P data/")
    print()
else:
    props = parse_proplist(proplist_path)
    print(f"Всего свойств в PropList.txt: {len(props)}")
    print("\nКоличество символов с каждым свойством:")
    for prop_name in sorted(props.keys()):
        count = count_prop_chars(props[prop_name])
        print(f"  {prop_name:35s}: {count}")
    print()

    # Проверить свойство White_Space
    if "White_Space" in props:
        print("Символы White_Space:")
        for start, end in props["White_Space"]:
            for cp in range(start, end + 1):
                try:
                    ch = chr(cp)
                    name = unicodedata.name(ch, "?")
                except ValueError:
                    name = "?"
                print(f"  U+{cp:04X}  {name!r}")
    print()


# ─────────────────────────────────────────────
# 5. Сравнение с unicodedata (stdlib)
# ─────────────────────────────────────────────

print("=== Сравнение нашего парсера с unicodedata (stdlib) ===\n")
test_chars = ['A', 'a', 'А', 'ñ', '0', '½', '🌍']
print(f"{'Символ':<8} {'unicodedata.name':<45} {'unicodedata.category':<8}")
print("-" * 65)
for ch in test_chars:
    name = unicodedata.name(ch, "N/A")
    cat  = unicodedata.category(ch)
    print(f"{ch!r:<8} {name:<45} {cat}")
print()
print(f"Версия Unicode в unicodedata: {unicodedata.unidata_version}")
