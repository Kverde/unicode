#!/usr/bin/env python3
"""
Статья 4 — Нормализация Unicode: NFD, NFC, NFKD, NFKC.
Практические примеры на Python.
"""
import unicodedata


# ─────────────────────────────────────────────
# 1. Разные представления одного символа
# ─────────────────────────────────────────────

def show_codepoints(s: str, label: str = "") -> None:
    cps = [f"U+{ord(c):04X}({unicodedata.name(c, '?')[:20]})" for c in s]
    print(f"  {label:<12}: len={len(s)}  {'  '.join(cps)}")


print("=== Представления символа 'é' ===\n")
precomposed = '\u00e9'         # LATIN SMALL LETTER E WITH ACUTE
decomposed  = '\u0065\u0301'   # e + COMBINING ACUTE ACCENT

print(f"  precomposed == decomposed: {precomposed == decomposed}")
print(f"  Оба выглядят одинаково:    '{precomposed}' == '{decomposed}'")
print()
show_codepoints(precomposed, "precomposed")
show_codepoints(decomposed,  "decomposed")
print()


# ─────────────────────────────────────────────
# 2. Основные формы нормализации
# ─────────────────────────────────────────────

def normalize_all(s: str) -> dict[str, str]:
    return {form: unicodedata.normalize(form, s) for form in ('NFC', 'NFD', 'NFKC', 'NFKD')}


def show_normalization(s: str, label: str = "") -> None:
    print(f"Исходная строка {label!r}: {s!r}  (len={len(s)})")
    norms = normalize_all(s)
    for form, result in norms.items():
        cps = ' '.join(f'U+{ord(c):04X}' for c in result)
        print(f"  {form:5s}: {result!r:20s} len={len(result):3d}  [{cps}]")
    print()


print("=== Нормализация разных символов ===\n")

test_strings = [
    ('\u00e9',          "é precomposed"),
    ('\u0065\u0301',    "é decomposed"),
    ('\u00f1',          "ñ precomposed"),
    ('\u006e\u0303',    "ñ decomposed"),
    ('\ufb01',          "ﬁ ligature"),    # fi лигатура
    ('\u00b2',          "² superscript"), # суперскрипт 2
    ('\u00bd',          "½ fraction"),    # вульгарная дробь 1/2
    ('\uff46',          "ｆ fullwidth"),   # fullwidth f
    ('\u2460',          "① enclosed"),    # circled 1
    ('\u2122',          "™ trademark"),
    ('caf\u00e9',       "'café' NFC"),
    ('caf\u0065\u0301', "'café' NFD"),
]

for s, label in test_strings:
    show_normalization(s, label)


# ─────────────────────────────────────────────
# 3. Canonical Combining Class
# ─────────────────────────────────────────────

print("=== Canonical Combining Class (CCC) ===\n")

combining_marks = [
    ('\u0301', "COMBINING ACUTE ACCENT"),
    ('\u0300', "COMBINING GRAVE ACCENT"),
    ('\u0308', "COMBINING DIAERESIS"),
    ('\u0327', "COMBINING CEDILLA"),
    ('\u0323', "COMBINING DOT BELOW"),
    ('\u0330', "COMBINING TILDE BELOW"),
    ('\u0315', "COMBINING COMMA ABOVE RIGHT"),
    ('\u035c', "COMBINING DOUBLE BREVE BELOW"),
]

for ch, name in combining_marks:
    cp = ord(ch)
    ccc = unicodedata.combining(ch)
    print(f"  U+{cp:04X}  CCC={ccc:3d}  {name}")

print()
print("Порядок combining marks в NFD:")
# Символ с двумя combining marks в разном порядке
s1 = 'a\u0327\u0301'   # a + cedilla(202) + acute(230) — правильный порядок
s2 = 'a\u0301\u0327'   # a + acute(230) + cedilla(202) — неправильный

nfd1 = unicodedata.normalize('NFD', s1)
nfd2 = unicodedata.normalize('NFD', s2)

print(f"  s1 (cedilla+acute): {' '.join(f'U+{ord(c):04X}(CCC={unicodedata.combining(c)})' for c in s1)}")
print(f"  s2 (acute+cedilla): {' '.join(f'U+{ord(c):04X}(CCC={unicodedata.combining(c)})' for c in s2)}")
print(f"  nfd1 == nfd2: {nfd1 == nfd2}  (NFD канонизирует порядок)")
print()


# ─────────────────────────────────────────────
# 4. Проверка нормализованности
# ─────────────────────────────────────────────

print("=== Проверка нормализованности (is_normalized) ===\n")

samples = [
    'Hello',
    'café',             # скорее всего NFC
    'caf\u0065\u0301',  # NFD (decomposed é)
    '\ufb01',           # fi лигатура — не в NFKC
    'ＡＢＣ',            # fullwidth — не в NFKC
]

for s in samples:
    row = [f"{form}={unicodedata.is_normalized(form, s)}"
           for form in ('NFC', 'NFD', 'NFKC', 'NFKD')]
    print(f"  {s!r:20s}: {', '.join(row)}")
print()


# ─────────────────────────────────────────────
# 5. Практика: сравнение строк с нормализацией
# ─────────────────────────────────────────────

print("=== Сравнение строк через нормализацию ===\n")

def normalize_equal(a: str, b: str, form: str = 'NFC') -> bool:
    return unicodedata.normalize(form, a) == unicodedata.normalize(form, b)


pairs = [
    ('café', 'caf\u0065\u0301', "NFC vs NFD"),
    ('ñoño', 'n\u0303on\u0303o', "NFC vs NFD 2"),
    ('ﬁlm', 'film', "fi-лигатура vs f+i"),
    ('２０２４', '2024', "fullwidth vs ASCII"),
    ('admin', '\u0430dmin', "Latin vs Cyrillic 'a' (spoofing!)"),
]

for a, b, desc in pairs:
    eq_raw  = a == b
    eq_nfc  = normalize_equal(a, b, 'NFC')
    eq_nfkc = normalize_equal(a, b, 'NFKC')
    print(f"  {desc}")
    print(f"    raw=={eq_raw}  NFC=={eq_nfc}  NFKC=={eq_nfkc}")
print()


# ─────────────────────────────────────────────
# 6. Ручная реализация NFC (упрощённая)
# ─────────────────────────────────────────────

print("=== Ручная реализация NFD-декомпозиции ===\n")

def decompose_char_manual(ch: str) -> list[str]:
    """
    Получить каноническую декомпозицию символа (1 уровень).
    Работает через поле Decomposition из unicodedata.
    """
    decomp = unicodedata.decomposition(ch)
    if not decomp or decomp.startswith('<'):
        # Нет канонической декомпозиции (или только compatibility)
        return [ch]
    # decomp = "0065 0301" — кодовые точки через пробел
    return [chr(int(cp_hex, 16)) for cp_hex in decomp.split()]


def manual_nfd(s: str) -> str:
    """
    Очень упрощённая NFD: рекурсивная декомпозиция + сортировка по CCC.
    (Без полного рекурсивного раскрытия — только 1 уровень для демонстрации)
    """
    result = []
    for ch in s:
        parts = decompose_char_manual(ch)
        result.extend(parts)
    # Стабильная сортировка: CCC=0 остаётся на месте, остальные сортируем
    # Это упрощение — реальный алгоритм сложнее
    return ''.join(result)


test_chars = ['é', 'ñ', 'ö', 'ü', 'Ǽ']
print(f"{'Символ':<8} {'manual NFD':<30} {'stdlib NFD'}")
print("-" * 60)
for ch in test_chars:
    manual = manual_nfd(ch)
    stdlib = unicodedata.normalize('NFD', ch)
    manual_cps = ' '.join(f'U+{ord(c):04X}' for c in manual)
    stdlib_cps = ' '.join(f'U+{ord(c):04X}' for c in stdlib)
    match = "✓" if manual == stdlib else "✗"
    print(f"{ch!r:<8} [{manual_cps:<26}]  [{stdlib_cps}]  {match}")
print()


# ─────────────────────────────────────────────
# 7. NFKC и безопасность: fullwidth-атаки
# ─────────────────────────────────────────────

print("=== NFKC и fullwidth символы ===\n")

# Fullwidth ASCII — выглядит как обычный текст, но другие байты
fullwidth_examples = [
    ('Ａ', 'A', "Fullwidth A"),
    ('０', '0', "Fullwidth 0"),
    ('ｆ', 'f', "Fullwidth f"),
    ('！', '!', "Fullwidth !"),
    ('　', ' ', "Ideographic Space"),
]

for fw, normal, desc in fullwidth_examples:
    nfkc_fw = unicodedata.normalize('NFKC', fw)
    print(f"  {desc}: {fw!r} U+{ord(fw):04X}  →NFKC→  {nfkc_fw!r} U+{ord(nfkc_fw):04X}  "
          f"match={nfkc_fw == normal}")

print()
username = 'ａｄｍｉｎ'  # fullwidth admin
print(f"  username = {username!r}")
print(f"  == 'admin': {username == 'admin'}")
print(f"  NFKC == 'admin': {unicodedata.normalize('NFKC', username) == 'admin'}")
print()

# ─────────────────────────────────────────────
# 8. Нормализация в паролях — типичная ловушка
# ─────────────────────────────────────────────

print("=== Нормализация паролей ===\n")

import hashlib

def hash_password(password: str, normalize: bool = False) -> str:
    if normalize:
        password = unicodedata.normalize('NFC', password)
    return hashlib.sha256(password.encode('utf-8')).hexdigest()[:16]

pwd_nfc = 'café secret'
pwd_nfd = 'caf\u0065\u0301 secret'  # то же самое, но NFD

print(f"  NFC пароль: {pwd_nfc!r}")
print(f"  NFD пароль: {pwd_nfd!r}")
print(f"  Хэши без нормализации: nfc={hash_password(pwd_nfc)}  nfd={hash_password(pwd_nfd)}")
print(f"  Совпадают: {hash_password(pwd_nfc) == hash_password(pwd_nfd)}")
print()
print(f"  Хэши с NFC-нормализацией: nfc={hash_password(pwd_nfc, True)}  nfd={hash_password(pwd_nfd, True)}")
print(f"  Совпадают: {hash_password(pwd_nfc, True) == hash_password(pwd_nfd, True)}")
