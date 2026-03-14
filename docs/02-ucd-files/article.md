# Статья 2. Unicode Character Database (UCD): файлы и структура

## Что такое UCD?

**Unicode Character Database (UCD)** — набор машиночитаемых текстовых файлов, которые определяют свойства каждого символа Unicode. Именно из этих файлов формируются:
- таблицы в стандартных библиотеках (`unicodedata` в Python, `ICU`, `glibc`)
- правила сортировки, нормализации, разбиения на строки/слова
- регулярные выражения с Unicode-свойствами

**Где взять:**
```
https://unicode.org/Public/UCD/latest/ucd/
```

Скачать ключевые файлы локально:
```bash
cd 02-ucd-files/data
wget https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
wget https://unicode.org/Public/UCD/latest/ucd/Blocks.txt
wget https://unicode.org/Public/UCD/latest/ucd/Scripts.txt
wget https://unicode.org/Public/UCD/latest/ucd/PropList.txt
wget https://unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt
wget https://unicode.org/Public/UCD/latest/ucd/SpecialCasing.txt
wget https://unicode.org/Public/UCA/latest/allkeys.txt
```

---

## 1. UnicodeData.txt — главный файл

Самый важный файл UCD. Каждая строка — один символ или начало диапазона. Формат: 15 полей, разделённых `;`.

### Формат строки

```
0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;
```

| № поля | Название | Пример | Пояснение |
|---|---|---|---|
| 1 | Code Point | `0041` | Hex, без префикса U+ |
| 2 | Name | `LATIN CAPITAL LETTER A` | Официальное имя |
| 3 | General Category | `Lu` | Lu=Uppercase Letter |
| 4 | Canonical Combining Class | `0` | 0=не combining mark |
| 5 | Bidi Class | `L` | L=Left-to-Right |
| 6 | Decomposition | (пусто) | Тип и кодовые точки |
| 7 | Decimal Digit Value | (пусто) | Только для цифр Nd |
| 8 | Digit Value | (пусто) | Digit-значение |
| 9 | Numeric Value | (пусто) | Для дробей (½ → 1/2) |
| 10 | Mirrored | `N` | Y=зеркалится в RTL |
| 11 | Unicode 1.0 Name | (пусто) | Устаревшее |
| 12 | ISO Comment | (пусто) | Устаревшее |
| 13 | Uppercase Mapping | (пусто) | Simple uppercase |
| 14 | Lowercase Mapping | `0061` | → 'a' |
| 15 | Titlecase Mapping | (пусто) | Если = uppercase, пусто |

### Диапазоны

Некоторые блоки (CJK, суррогаты) записаны как диапазон — первая и последняя строки с именами `<CJK Ideograph, First>` и `<CJK Ideograph, Last>`:

```
4E00;<CJK Ideograph, First>;Lo;0;L;;;;;N;;;;;
9FFF;<CJK Ideograph, Last>;Lo;0;L;;;;;N;;;;;
```

Это означает, что все кодовые точки 4E00..9FFF имеют категорию `Lo`.

---

## 2. Blocks.txt — блоки Unicode

Простой файл: диапазон и имя блока.

```
# Blocks-15.0.0.txt

0000..007F; Basic Latin
0080..00FF; Latin-1 Supplement
0400..04FF; Cyrillic
1F600..1F64F; Emoticons
```

Используется для функций типа «в каком блоке символ?»

---

## 3. Scripts.txt — скрипты (письменности)

```
# Scripts-15.0.0.txt
0041..005A    ; Latin   # L&  [26] LATIN CAPITAL LETTER A..Z
0061..007A    ; Latin   # L&  [26] LATIN SMALL LETTER A..Z
0400..0481    ; Cyrillic # L& [130] CYRILLIC CAPITAL LETTER IE..
0030..0039    ; Common  # Nd  [10] DIGIT ZERO..DIGIT NINE
```

Заметьте: цифры 0..9 относятся к скрипту `Common` (используются всеми письменностями).

---

## 4. PropList.txt — бинарные свойства

Перечисляет символы, обладающие тем или иным булевым свойством:

```
0009..000D    ; White_Space   # Cc  [5] <control-0009>..<control-000D>
0020          ; White_Space   # Zs       SPACE
00AD          ; Soft_Hyphen   # Cf       SOFT HYPHEN
0021..0023    ; Terminal_Punctuation
```

Важные свойства:
- `White_Space` — пробельные символы (для `str.split()` и т.п.)
- `Alphabetic` — все буквы (включая числа-буквы)
- `ID_Start`, `ID_Continue` — что можно использовать в идентификаторах (Python, JS)
- `Dash` — все виды тире
- `Quotation_Mark` — все кавычки
- `Emoji`, `Emoji_Presentation` — эмодзи

---

## 5. DerivedCoreProperties.txt — производные свойства

Вычисляемые свойства, которые зависят от комбинации других:

```
Alphabetic  = Lu + Ll + Lt + Lm + Lo + Nl + Other_Alphabetic
Uppercase   = Lu + Other_Uppercase
Lowercase   = Ll + Other_Lowercase
```

---

## 6. SpecialCasing.txt — специальные правила регистра

Для случаев, когда `toUpperCase()` не взаимно-однозначна:

```
# код; нижний; заголовочный; верхний; условие (locale)

00DF; 00DF; 0053 0073; 0053 0053;   # ß → SS (заглавная)
FB00; FB00; 0046 0066; 0046 0046;   # ﬀ → FF
0130; 0069; 0130; 0130; # İ (турецкое İ без условия)
0069; 0069; 0049; 0049 0307; tr;    # i → İ (с точкой, турецкий)
```

Эти правила объясняют, почему `"ß".upper() == "SS"` в Python.

---

## 7. CaseFolding.txt — сворачивание регистра (Case Folding)

Case folding — это нормализация для сравнения без учёта регистра. Отличается от `toLowerCase()`:

```
0041; C; 0061;   # A → a (simple/common)
00DF; F; 0073 0073;  # ß → ss (full, т.е. один символ → два)
0049; T; 0131;   # I → ı (только в турецком, T=Turkic)
```

---

## 8. NormalizationTest.txt — тесты нормализации

Файл для проверки реализации алгоритмов NFD/NFC/NFKD/NFKC. Каждая строка — 5 столбцов:

```
# исходная; NFC; NFD; NFKC; NFKD
00C0;00C0;0041 0300;00C0;0041 0300;
```

Удобно использовать при написании своей реализации нормализации.

---

## 9. allkeys.txt — весовая таблица DUCET (для коллации)

Таблица весов для Unicode Collation Algorithm (UCA). Подробно разобрана в статье 5, но формат такой:

```
0041  ; [.1C47.0020.0008] # LATIN CAPITAL LETTER A
006F  ; [.1D30.0020.0002] # LATIN SMALL LETTER O
```

Три уровня весов в `[.L1.L2.L3]`:
- L1 = Primary weight (основное различие: буква-буква)
- L2 = Secondary weight (диакритика)
- L3 = Tertiary weight (регистр)

---

## Примеры кода → `examples.py`

Скрипт демонстрирует парсинг UCD-файлов вручную и строит сводную статистику. Сначала скачайте файлы (см. секцию «Где взять» в начале статьи).
