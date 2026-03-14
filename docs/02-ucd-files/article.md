# Статья 2. Unicode Character Database (UCD): файлы и структура

## Что такое UCD?

**Unicode Character Database (UCD)** — набор машиночитаемых текстовых файлов, которые определяют свойства каждого символа Unicode. Именно из этих файлов формируются:

- таблицы в стандартных библиотеках (`unicodedata` в Python, `ICU`, `glibc`);
- правила сортировки, нормализации, разбиения на строки/слова;
- регулярные выражения с Unicode-свойствами.

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

**Файл:** [`UnicodeData.txt`](https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt)

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

### Разбор строки по шагам

Возьмём реальный символ — `U+00E9`, é (LATIN SMALL LETTER E WITH ACUTE). Найдём его в `UnicodeData.txt`:

```
00E9;LATIN SMALL LETTER E WITH ACUTE;Ll;0;L;0065 0301;;;;N;;;00C9;;00C9
```

Разберём каждое непустое поле:

| № | Значение | Что означает |
|---|---|---|
| 1 | `00E9` | Кодовая точка — U+00E9 |
| 2 | `LATIN SMALL LETTER E WITH ACUTE` | Официальное имя |
| 3 | `Ll` | General Category = Letter, Lowercase |
| 4 | `0` | Combining Class = 0 (базовый символ, не combining mark) |
| 5 | `L` | Bidi Class = Left-to-Right |
| 6 | `0065 0301` | **Каноническая декомпозиция**: é = `e` (U+0065) + ◌́  (U+0301, combining acute accent). Нет тега — значит каноническая, не совместимая |
| 10 | `N` | Не зеркалится в RTL-тексте |
| 13 | `00C9` | Simple Uppercase Mapping → U+00C9 = É |
| 14 | (пусто) | Lowercase mapping пуст — символ уже строчной |
| 15 | `00C9` | Simple Titlecase Mapping = то же, что Uppercase |

Поля 7–9 (числовые значения) пусты — символ не является цифрой. Поля 11–12 устарели.

**Перекрёстные ссылки с другими файлами UCD** для того же символа U+00E9:

- `DerivedCoreProperties.txt` — здесь U+00E9 входит в свойство `Alphabetic` (потому что категория `Ll`), `Lowercase`, `ID_Start`, `ID_Continue`
- `PropList.txt` — нет особых свойств (не `White_Space`, не `Dash` и т.д.)
- `SpecialCasing.txt` — не упоминается (для é нет особых правил смены регистра)
- `CaseFolding.txt`: `00E9; C; 00E9;` — совпадает сам с собой (уже строчной)

**Итог:** один символ U+00E9 описан в нескольких файлах UCD. `UnicodeData.txt` даёт базовые свойства, остальные файлы дополняют картину.

### Диапазоны

Некоторые блоки (CJK, суррогаты) записаны как диапазон — первая и последняя строки с именами `<CJK Ideograph, First>` и `<CJK Ideograph, Last>`:

```
4E00;<CJK Ideograph, First>;Lo;0;L;;;;;N;;;;;
9FFF;<CJK Ideograph, Last>;Lo;0;L;;;;;N;;;;;
```

Это означает, что все кодовые точки 4E00..9FFF имеют категорию `Lo`.

---

## 2. Blocks.txt — блоки Unicode

**Файл:** [`Blocks.txt`](https://unicode.org/Public/UCD/latest/ucd/Blocks.txt)

Простой файл: диапазон и имя блока.

```
# Blocks-17.0.0.txt

0000..007F; Basic Latin
0080..00FF; Latin-1 Supplement
0400..04FF; Cyrillic
1F600..1F64F; Emoticons
```

Используется для функций типа «в каком блоке символ?»

---

## 3. Scripts.txt — скрипты (письменности)

**Файл:** [`Scripts.txt`](https://unicode.org/Public/UCD/latest/ucd/Scripts.txt)

```
# Scripts-17.0.0.txt
0041..005A    ; Latin   # L&  [26] LATIN CAPITAL LETTER A..Z
0061..007A    ; Latin   # L&  [26] LATIN SMALL LETTER A..Z
0400..0481    ; Cyrillic # L& [130] CYRILLIC CAPITAL LETTER IE..
0030..0039    ; Common  # Nd  [10] DIGIT ZERO..DIGIT NINE
```

Заметьте: цифры 0..9 относятся к скрипту `Common` (используются всеми письменностями).

---

## 4. PropList.txt — бинарные свойства

**Файл:** [`PropList.txt`](https://unicode.org/Public/UCD/latest/ucd/PropList.txt)

Перечисляет символы, обладающие тем или иным булевым свойством:

```
0009..000D    ; White_Space   # Cc  [5] <control-0009>..<control-000D>
0020          ; White_Space   # Zs       SPACE
00AD          ; Soft_Hyphen   # Cf       SOFT HYPHEN
0021..0023    ; Terminal_Punctuation
```

Важные свойства:

- `White_Space` — пробельные символы (для `str.split()` и т.п.);
- `Alphabetic` — все буквы (включая числа-буквы);
- `ID_Start`, `ID_Continue` — что можно использовать в идентификаторах (Python, JS);
- `Dash` — все виды тире;
- `Quotation_Mark` — все кавычки;
- `Emoji`, `Emoji_Presentation` — эмодзи.

---

## 5. DerivedCoreProperties.txt — производные свойства

**Файл:** [`DerivedCoreProperties.txt`](https://unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt)

Вычисляемые свойства, которые зависят от комбинации других:

```
Alphabetic  = Lu + Ll + Lt + Lm + Lo + Nl + Other_Alphabetic
Uppercase   = Lu + Other_Uppercase
Lowercase   = Ll + Other_Lowercase
```

---

## 6. SpecialCasing.txt — специальные правила регистра

**Файл:** [`SpecialCasing.txt`](https://unicode.org/Public/UCD/latest/ucd/SpecialCasing.txt)

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

**Файл:** [`CaseFolding.txt`](https://unicode.org/Public/UCD/latest/ucd/CaseFolding.txt)

Case folding — это нормализация для сравнения без учёта регистра. Отличается от `toLowerCase()`:

```
0041; C; 0061;   # A → a (simple/common)
00DF; F; 0073 0073;  # ß → ss (full, т.е. один символ → два)
0049; T; 0131;   # I → ı (только в турецком, T=Turkic)
```

---

## 8. NormalizationTest.txt — тесты нормализации

**Файл:** [`NormalizationTest.txt`](https://unicode.org/Public/UCD/latest/ucd/NormalizationTest.txt)

Файл для проверки реализации алгоритмов NFD/NFC/NFKD/NFKC. Каждая строка — 5 столбцов:

```
# исходная; NFC; NFD; NFKC; NFKD
00C0;00C0;0041 0300;00C0;0041 0300;
```

Удобно использовать при написании своей реализации нормализации.

---

## 9. allkeys.txt — весовая таблица DUCET (для коллации)

**Файл:** [`allkeys.txt`](https://unicode.org/Public/UCA/latest/allkeys.txt)

Таблица весов для Unicode Collation Algorithm (UCA). Подробно разобрана в статье 5, но формат такой:

```
0041  ; [.1C47.0020.0008] # LATIN CAPITAL LETTER A
006F  ; [.1D30.0020.0002] # LATIN SMALL LETTER O
```

Три уровня весов в `[.L1.L2.L3]`:

- L1 = Primary weight (основное различие: буква-буква);
- L2 = Secondary weight (диакритика);
- L3 = Tertiary weight (регистр).

---

## 10. EastAsianWidth.txt — ширина символов в терминале

Файл [`EastAsianWidth.txt`](https://unicode.org/Public/UCD/latest/ucd/EastAsianWidth.txt) определяет, сколько **колонок** символ занимает при выводе в терминале или моноширинном шрифте.

```
# EastAsianWidth.txt (фрагмент)
0000..001F;N   # Narrow — узкие (1 колонка)
1100..115F;W   # Wide — широкие (2 колонки, хангыль)
2E80..2EFF;W   # Wide — CJK радикалы
FF01..FF60;F   # Fullwidth — полноширинные символы
FF61..FFBE;H   # Halfwidth — полуширинные
```

| Код | Значение | Ширина | Примеры |
|---|---|---|---|
| `N` | Narrow | 1 | Latin, Cyrillic, большинство символов |
| `Na` | Narrow (ASCII) | 1 | ASCII: 0x21..0x7E |
| `W` | Wide | **2** | CJK иероглифы, хангыль, хираганa |
| `F` | Fullwidth | **2** | ！Ａ（ — fullwidth варианты ASCII |
| `H` | Halfwidth | 1 | ｶﾅ — halfwidth катакана |
| `A` | Ambiguous | 1 или 2 | Зависит от контекста/терминала |

### Почему это важно на практике

```python
s = "中文"
print(len(s))   # 2 — две кодовые точки

# Но в терминале каждый иероглиф занимает 2 колонки:
import unicodedata

def display_width(s: str) -> int:
    """Ширина строки в терминале (в колонках)."""
    width = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        width += 2 if eaw in ('W', 'F') else 1
    return width

print(display_width("中文"))    # 4, а не 2
print(display_width("Hello"))  # 5
print(display_width("Мир"))    # 3
print(display_width("ａｂｃ")) # 6 — fullwidth латиница
```

Без учёта `EastAsianWidth` таблицы в консоли и progress bar'ы будут «съезжать» при наличии CJK-символов. Стандартная библиотека Python предоставляет `unicodedata.east_asian_width()`, а модуль `wcwidth` (`pip install wcwidth`) реализует полный алгоритм ширины, включая combining marks (которые имеют ширину 0).

---

## Примеры кода

Скрипт демонстрирует парсинг UCD-файлов вручную и строит сводную статистику. Сначала скачайте файлы (см. секцию «Где взять» в начале статьи).

[examples.py](https://github.com/comtextspace/unicode/blob/main/docs/02-ucd-files/examples.py)