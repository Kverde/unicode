#!/usr/bin/env python3
"""
Статья 3 — Кодировки: UTF-8, UTF-16, UTF-32.
Практические примеры кодирования/декодирования и байтового анализа.
"""


# ─────────────────────────────────────────────
# 1. Кодирование одного символа в разных UTF
# ─────────────────────────────────────────────

def show_encodings(char: str) -> None:
    """Показать байты символа во всех основных кодировках."""
    cp = ord(char)
    name = __import__('unicodedata').name(char, "?")
    print(f"Символ: {char!r}  U+{cp:05X}  {name}")
    for enc in ['utf-8', 'utf-16-le', 'utf-16-be', 'utf-32-le', 'utf-32-be']:
        try:
            b = char.encode(enc)
            hex_str = ' '.join(f'{byte:02X}' for byte in b)
            print(f"  {enc:15s}: [{hex_str}]  ({len(b)} байт)")
        except Exception as e:
            print(f"  {enc:15s}: ошибка — {e}")
    print()


print("=== Кодирование символов в разных UTF ===\n")
for ch in ['A', 'А', 'ñ', '中', '🌍', '\u0000']:
    show_encodings(ch)


# ─────────────────────────────────────────────
# 2. Ручное кодирование в UTF-8
# ─────────────────────────────────────────────

def encode_utf8_manual(cp: int) -> bytes:
    """Закодировать кодовую точку в UTF-8 вручную (без stdlib)."""
    if cp < 0 or cp > 0x10FFFF:
        raise ValueError(f"Недопустимая кодовая точка: {cp}")
    if cp <= 0x7F:
        return bytes([cp])
    elif cp <= 0x7FF:
        b1 = 0b11000000 | (cp >> 6)
        b2 = 0b10000000 | (cp & 0b00111111)
        return bytes([b1, b2])
    elif cp <= 0xFFFF:
        b1 = 0b11100000 | (cp >> 12)
        b2 = 0b10000000 | ((cp >> 6) & 0b00111111)
        b3 = 0b10000000 | (cp & 0b00111111)
        return bytes([b1, b2, b3])
    else:
        b1 = 0b11110000 | (cp >> 18)
        b2 = 0b10000000 | ((cp >> 12) & 0b00111111)
        b3 = 0b10000000 | ((cp >> 6) & 0b00111111)
        b4 = 0b10000000 | (cp & 0b00111111)
        return bytes([b1, b2, b3, b4])


def decode_utf8_manual(data: bytes) -> list[int]:
    """Декодировать UTF-8 байты в список кодовых точек (вручную)."""
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        if b & 0b10000000 == 0:          # 1 байт
            cp = b
            i += 1
        elif b & 0b11100000 == 0b11000000:  # 2 байта
            cp = (b & 0b00011111) << 6
            cp |= data[i + 1] & 0b00111111
            i += 2
        elif b & 0b11110000 == 0b11100000:  # 3 байта
            cp = (b & 0b00001111) << 12
            cp |= (data[i + 1] & 0b00111111) << 6
            cp |= data[i + 2] & 0b00111111
            i += 3
        else:                               # 4 байта
            cp = (b & 0b00000111) << 18
            cp |= (data[i + 1] & 0b00111111) << 12
            cp |= (data[i + 2] & 0b00111111) << 6
            cp |= data[i + 3] & 0b00111111
            i += 4
        result.append(cp)
    return result


print("=== Ручное кодирование UTF-8 ===\n")
test_cps = [0x41, 0xC3, 0x410, 0x4E2D, 0x1F30D]
for cp in test_cps:
    ch = chr(cp)
    manual = encode_utf8_manual(cp)
    stdlib = ch.encode('utf-8')
    match = "✓" if manual == stdlib else "✗"
    print(f"U+{cp:05X}  {ch}  manual={manual.hex()}  stdlib={stdlib.hex()}  {match}")

print()
print("=== Ручное декодирование UTF-8 ===\n")
test_bytes = "Hello, Мир! 🌍".encode('utf-8')
decoded = decode_utf8_manual(test_bytes)
reconstructed = ''.join(chr(cp) for cp in decoded)
print(f"Исходная строка:  'Hello, Мир! 🌍'")
print(f"Восстановленная:  {reconstructed!r}")
print(f"Совпадает: {reconstructed == 'Hello, Мир! 🌍'}")
print()


# ─────────────────────────────────────────────
# 3. Суррогатные пары в UTF-16
# ─────────────────────────────────────────────

def encode_utf16_surrogate_pair(cp: int) -> tuple[int, int]:
    """Вычислить суррогатную пару для символа вне BMP."""
    assert 0x10000 <= cp <= 0x10FFFF, "Суррогаты только для SMP и выше"
    cp_prime = cp - 0x10000
    high = 0xD800 + (cp_prime >> 10)
    low  = 0xDC00 + (cp_prime & 0x3FF)
    return high, low


def decode_utf16_surrogate_pair(high: int, low: int) -> int:
    """Восстановить кодовую точку из суррогатной пары."""
    assert 0xD800 <= high <= 0xDBFF, "Не high surrogate"
    assert 0xDC00 <= low  <= 0xDFFF, "Не low surrogate"
    return 0x10000 + ((high - 0xD800) << 10) + (low - 0xDC00)


print("=== Суррогатные пары UTF-16 ===\n")
smp_chars = ['🌍', '𝄞', '𠀀', '🎉', '👨‍👩‍👧']
for ch in smp_chars:
    for sub_ch in ch:  # в случае emoji ZWJ, проходим каждый code point
        cp = ord(sub_ch)
        if cp > 0xFFFF:
            high, low = encode_utf16_surrogate_pair(cp)
            restored = decode_utf16_surrogate_pair(high, low)
            stdlib_bytes = sub_ch.encode('utf-16-le')
            print(f"U+{cp:05X}  {sub_ch}  →  high=U+{high:04X}  low=U+{low:04X}  "
                  f"bytes={stdlib_bytes.hex()}  restore=U+{restored:05X}")
print()


# ─────────────────────────────────────────────
# 4. BOM (Byte Order Mark)
# ─────────────────────────────────────────────

print("=== BOM ===\n")
s = "Привет"
for enc in ['utf-8-sig', 'utf-16', 'utf-32']:
    b = s.encode(enc)
    bom_hex = b[:4].hex()
    print(f"{enc:12s}: первые байты={bom_hex}  всего байт={len(b)}")

print("\nU+FEFF (BOM / Zero Width No-Break Space):")
bom = '\uFEFF'
print(f"  UTF-8:    {bom.encode('utf-8').hex()}")
print(f"  UTF-16LE: {bom.encode('utf-16-le').hex()}")
print(f"  UTF-16BE: {bom.encode('utf-16-be').hex()}")
print(f"  UTF-32LE: {bom.encode('utf-32-le').hex()}")
print()


# ─────────────────────────────────────────────
# 5. Длина строки: байты vs code points vs графемы
# ─────────────────────────────────────────────

import unicodedata

def grapheme_clusters(s: str) -> list[str]:
    """
    Простой алгоритм разбивки на графемные кластеры.
    Реальная реализация сложнее (UAX#29), но для ASCII и простых случаев работает.
    Для полной поддержки используйте: pip install grapheme
    """
    clusters = []
    current = ""
    for ch in s:
        ccc = unicodedata.combining(ch)
        if ccc == 0 and current:
            clusters.append(current)
            current = ch
        else:
            current += ch
    if current:
        clusters.append(current)
    return clusters


print("=== Длина строки на разных уровнях ===\n")
test_strings = [
    "Hello",
    "Привет",
    "🌍🎉",
    "é",          # U+00E9 (precomposed)
    "e\u0301",    # e + combining acute (decomposed)
    "👨‍👩‍👧",     # family emoji (ZWJ sequence)
    "🇷🇺",        # флаг России (regional indicator pair)
]

print(f"{'Строка':<20} {'bytes(utf8)':<13} {'code points':<13} {'graphemes':<10}")
print("-" * 60)
for s in test_strings:
    utf8_len = len(s.encode('utf-8'))
    cp_len   = len(s)  # в Python len() считает code points
    gr_len   = len(grapheme_clusters(s))
    repr_s = repr(s) if len(s) <= 5 else repr(s[:5]) + "…"
    print(f"{repr_s:<20} {utf8_len:<13} {cp_len:<13} {gr_len:<10}")
print()


# ─────────────────────────────────────────────
# 6. Ошибки при декодировании и стратегии обработки
# ─────────────────────────────────────────────

print("=== Стратегии обработки ошибок декодирования ===\n")
broken = b"Hello \xff\xfe World"  # невалидный UTF-8

strategies = ['strict', 'ignore', 'replace', 'backslashreplace', 'xmlcharrefreplace']
for strategy in strategies:
    try:
        result = broken.decode('utf-8', errors=strategy)
        print(f"  {strategy:20s}: {result!r}")
    except Exception as e:
        print(f"  {strategy:20s}: {type(e).__name__}: {e}")
print()


# ─────────────────────────────────────────────
# 7. Автоопределение кодировки
# ─────────────────────────────────────────────

print("=== Автоопределение кодировки (встроенные эвристики) ===\n")

samples = {
    "UTF-8 (русский)": "Привет мир".encode('utf-8'),
    "UTF-8 with BOM":  "Привет мир".encode('utf-8-sig'),
    "UTF-16-LE":       "Привет мир".encode('utf-16-le'),
    "UTF-16 with BOM": "Привет мир".encode('utf-16'),
    "ASCII":           b"Hello world",
    "Latin-1":         "Héllo".encode('latin-1'),
}

for name, data in samples.items():
    bom_hex = data[:4].hex()
    # Простая эвристика по BOM
    if data[:3] == b'\xef\xbb\xbf':
        detected = 'utf-8-sig'
    elif data[:2] == b'\xff\xfe':
        detected = 'utf-16-le'
    elif data[:2] == b'\xfe\xff':
        detected = 'utf-16-be'
    elif all(b < 0x80 for b in data):
        detected = 'ascii/utf-8'
    else:
        detected = '???  (нужен chardet/charset-normalizer)'
    print(f"  {name:25s}: BOM={bom_hex[:8]:8s}  →  {detected}")
print()
print("Для реального определения используйте: pip install charset-normalizer")
