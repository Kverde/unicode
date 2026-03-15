# Статья 2. Unicode Character Database (UCD): файлы и структура

## Что такое UCD?

**Unicode Character Database (UCD)** — набор машиночитаемых текстовых файлов, которые определяют свойства каждого символа Unicode. Именно из этих файлов формируются:

- таблицы в стандартных библиотеках (`unicodedata` в Python, `ICU`, `glibc`);
- правила сортировки, нормализации, разбиения на строки/слова;
- регулярные выражения с Unicode-свойствами.

> **Для JS-разработчиков:** движки JavaScript (V8, SpiderMonkey) используют данные UCD под капотом — именно из этих файлов берутся свойства для Unicode property escapes в regex (`/\p{Script=Latin}/u`, `/\p{Lu}/u`) и для API `Intl` (Collator, Segmenter, NumberFormat). Разработчик JS не парсит UCD вручную, но понимание структуры файлов помогает разобраться, откуда берутся свойства символов в этих API.

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
| 6 | Decomposition | `0065 0301` (для é) | Как символ раскладывается на более простые. Пустое поле = символ атомарный. Если нет тега — **каноническая** декомпозиция: `00E9` → `0065 0301` (e + combining acute). Если есть тег — **совместимая**: `00BC` (¼) → `<fraction> 0031 2044 0034`. Подробнее — в [статье 5](../05-normalization/article.md) |
| 7 | Decimal Digit Value | `5` (для символа `5`) | Цифровое значение 0..9, если символ — десятичная цифра (категория `Nd`). Для не-цифр — пусто |
| 8 | Digit Value | (пусто) | Расширенная категория цифр: надстрочные ¹²³ и другие нестандартные цифры, не вошедшие в поле 7. Сейчас почти не используется отдельно от поля 7 |
| 9 | Numeric Value | `1/4` (для ¼) | Рациональное число для любых символов с числовым смыслом: дроби (¼ → `1/4`), римские цифры (Ⅳ → `4`). Для обычных цифр совпадает с полем 7 |
| 10 | Mirrored | `N` | Y = символ зеркалится при RTL-тексте: `(` становится `)`, `<` становится `>` |
| 11 | Unicode 1.0 Name | (пусто) | Устаревшее старое имя из Unicode 1.0 (если отличалось) |
| 12 | ISO Comment | (пусто) | Устаревший комментарий ISO |
| 13 | Uppercase Mapping | (пусто) | Simple Uppercase Mapping — кодовая точка заглавного варианта (если однозначна) |
| 14 | Lowercase Mapping | `0061` | Simple Lowercase Mapping → `a`. Пусто, если символ уже строчной |
| 15 | Titlecase Mapping | (пусто) | Simple Titlecase Mapping. Пусто, если совпадает с Uppercase |

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
- `PropList.txt` — нет особых свойств (не `White_Space`, не `Dash` и т. д.)
- `SpecialCasing.txt` — не упоминается (для é нет особых правил смены регистра)
- `CaseFolding.txt`: `00E9; C; 00E9;` — совпадает сам с собой (уже строчной)

**Итог:** один символ U+00E9 описан в нескольких файлах UCD. `UnicodeData.txt` даёт базовые свойства, остальные файлы дополняют картину.

### Диапазоны

Большинство строк `UnicodeData.txt` описывают ровно один символ. Но для некоторых блоков это было бы неэффективно: CJK-иероглифов десятки тысяч, и перечислять каждый отдельной строкой с одинаковыми свойствами нет смысла. Поэтому для таких блоков используется **запись диапазоном** — два маркера: первая и последняя кодовая точка.

```
4E00;<CJK Ideograph, First>;Lo;0;L;;;;;N;;;;;
9FFF;<CJK Ideograph, Last>;Lo;0;L;;;;;N;;;;;
```

Имена `<..., First>` и `<..., Last>` — это служебные метки, а не реальные имена символов. Они означают: **все кодовые точки от `4E00` до `9FFF` включительно имеют те же свойства**, что указаны в этих строках. В данном случае — категория `Lo` (Letter, Other), Bidi Class `L`, без декомпозиции.

Имена конкретных символов внутри диапазона при этом конструируются **по правилу**: берётся базовое имя группы и добавляется кодовая точка. Например:

- `U+4E00` → `CJK UNIFIED IDEOGRAPH-4E00`
- `U+9FFF` → `CJK UNIFIED IDEOGRAPH-9FFF`
- `U+5B57` (字) → `CJK UNIFIED IDEOGRAPH-5B57`

Это можно проверить прямо в Python:

```python
import unicodedata
print(unicodedata.name('\u4e00'))  # CJK UNIFIED IDEOGRAPH-4E00
print(unicodedata.name('\u5b57'))  # CJK UNIFIED IDEOGRAPH-5B57
print(unicodedata.name('\u9fff'))  # CJK UNIFIED IDEOGRAPH-9FFF
```

**Какие блоки используют диапазоны?**

В `UnicodeData.txt` таких групп несколько:

| Диапазон | Маркер | Что внутри |
|---|---|---|
| `4E00..9FFF` | `CJK Ideograph` | Основной блок CJK-иероглифов (20 992 символа) |
| `3400..4DBF` | `CJK Ideograph Extension A` | Расширение A |
| `20000..2A6DF` | `CJK Ideograph Extension B` | Расширение B (редкие иероглифы) |
| `AC00..D7A3` | `Hangul Syllable` | Слоги хангыля (11 172 символа) |
| `D800..DFFF` | `Surrogate` | Суррогатные пары UTF-16 (не настоящие символы) |
| `E000..F8FF` | `Private Use` | Зона частного использования |

**Важно:** суррогатные кодовые точки (`D800..DFFF`) — это не символы Unicode. Это технические значения, зарезервированные для механизма суррогатных пар UTF-16. Они никогда не должны встречаться в корректно закодированном тексте UTF-8.

**Практическое следствие:** если вы парсите `UnicodeData.txt` вручную, нельзя просто читать строки по одной — нужно обнаруживать пары `<..., First>` / `<..., Last>` и разворачивать диапазон. Иначе в вашей базе окажутся только два символа вместо тысяч.

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
0041..005A    ; Latin    # L&  [26] LATIN CAPITAL LETTER A..Z
0061..007A    ; Latin    # L&  [26] LATIN SMALL LETTER A..Z
0400..0481    ; Cyrillic # L& [130] CYRILLIC CAPITAL LETTER IE..
0030..0039    ; Common   # Nd  [10] DIGIT ZERO..DIGIT NINE
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

В файле **40 свойств**. Ниже полная таблица, сгруппированная по назначению.

**Пробельные символы**

| Свойство | Описание |
|---|---|
| `White_Space` | Пробельные символы: пробел, табуляция, переводы строк. Используется в `str.split()`, токенизаторах. |
| `Pattern_White_Space` | Подмножество для языковых грамматик (Python, JS): только «чистые» пробелы, без NBSP и экзотики. |

**Идентификаторы**

| Свойство | Описание |
|---|---|
| `Other_ID_Start` | Символы, разрешённые в начале идентификатора (дополняют `ID_Start` из DerivedCoreProperties). |
| `Other_ID_Continue` | Символы, разрешённые внутри идентификатора (дополняют `ID_Continue`). |
| `ID_Compat_Math_Start` | Математические символы, допустимые в начале идентификатора для совместимости. |
| `ID_Compat_Math_Continue` | Математические символы, допустимые внутри идентификатора. |

**Пунктуация и разделители**

| Свойство | Описание |
|---|---|
| `Dash` | Все виды тире и дефисов (U+002D, U+2012..U+2015, U+2212 и др.). |
| `Hyphen` | Устаревшее; символы, традиционно считавшиеся дефисами. Superseded by `Dash`. |
| `Quotation_Mark` | Все виды кавычек: `"`, `'`, `«»`, `„"`, `「」` и т. д. |
| `Terminal_Punctuation` | Знаки конца предложения: `.`, `!`, `?`, `。`, `؟` и т. д. |
| `Sentence_Terminal` | Уточнённый список знаков конца предложения (для алгоритма разбиения UAX #29). |
| `Soft_Dotted` | Буквы с точкой (i, j, ї…), у которых точка убирается при добавлении диакритики сверху. |

**Буквы, цифры, письменности**

| Свойство | Описание |
|---|---|
| `Other_Alphabetic` | Дополнительные «буквенные» символы (не Lu/Ll/Lt/Lm/Lo/Nl), включаемые в `Alphabetic`. |
| `Other_Uppercase` | Символы, считающиеся заглавными сверх категории `Lu`. |
| `Other_Lowercase` | Символы, считающиеся строчными сверх категории `Ll`. |
| `Ideographic` | Идеографические символы CJK. |
| `Unified_Ideograph` | Символы, прошедшие процесс унификации CJK в Unicode. |
| `Radical` | Ключи (радикалы) CJK — используются для словарного поиска. |
| `Diacritic` | Диакритические знаки (надстрочные, подстрочные) — влияют на чтение базовых символов. |
| `Extender` | Символы, «растягивающие» слово (U+00B7 MIDDLE DOT, U+30FC KATAKANA-HIRAGANA PROLONGED SOUND MARK). |
| `Modifier_Combining_Mark` | Combining marks с семантикой модификатора (не просто декоративные). |

**Математика и синтаксис**

| Свойство | Описание |
|---|---|
| `Other_Math` | Символы с математическим смыслом, не попавшие в категорию `Sm`. |
| `Pattern_Syntax` | Зарезервированные синтаксические символы для языковых грамматик (например, `@`, `#`, `\`). |

**Эмодзи и визуальные эффекты**

| Свойство | Описание |
|---|---|
| `Regional_Indicator` | 26 символов `🇦`..`🇿` (U+1F1E6..U+1F1FF): два подряд образуют эмодзи-флаг страны. |
| `Variation_Selector` | Невидимые символы, изменяющие отображение предыдущего символа (VS-1..VS-256). |

**Двунаправленный текст (BiDi)**

| Свойство | Описание |
|---|---|
| `Bidi_Control` | Управляющие символы BiDi: LRM, RLM, LRE, RLE, PDF, LRO, RLO (влияют на направление текста). |
| `Join_Control` | ZWJ (U+200D) и ZWNJ (U+200C) — управляют соединением букв (особенно важно для арабского, деванагари). |
| `Logical_Order_Exception` | Символы тайского и кхмерского, хранящиеся не в визуальном порядке. |
| `Prepended_Concatenation_Mark` | Знаки, семантически «прилипающие» к следующему символу (в некоторых арабских письменностях). |

**Технические и служебные**

| Свойство | Описание |
|---|---|
| `Noncharacter_Code_Point` | 66 кодовых точек, зарезервированных навсегда (U+FDD0..U+FDEF, U+FFFE, U+FFFF и т. д.) — не символы. |
| `Deprecated` | Символы, от использования которых Unicode Official отказался (но они остаются для совместимости). |
| `Soft_Hyphen` | U+00AD — мягкий перенос. Невидим, подсказывает браузеру место переноса слова. |
| `Other_Default_Ignorable_Code_Point` | Невидимые символы, которые по умолчанию не отображаются и игнорируются при рендеринге. |
| `Other_Grapheme_Extend` | Символы, которые «продлевают» предыдущий графемный кластер (вносят вклад в `Grapheme_Extend`). |
| `IDS_Binary_Operator` | Операторы описания иероглифов (⿰, ⿱ и т. д.) — используются в системе IDS для описания структуры CJK. |
| `IDS_Trinary_Operator` | Трёхместные операторы описания иероглифов (⿲, ⿳). |
| `IDS_Unary_Operator` | Одноместные операторы описания иероглифов (добавлены в Unicode 15.1). |
| `Hex_Digit` | Шестнадцатеричные цифры: `0–9`, `A–F`, `a–f`, а также их fullwidth-варианты. |
| `ASCII_Hex_Digit` | Только ASCII-варианты шестнадцатеричных цифр: `0–9`, `A–F`, `a–f`. |

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
0130; 0069; 0130; 0130;             # İ (турецкое İ без условия)
0069; 0069; 0049; 0049 0307; tr;    # i → İ (с точкой, турецкий)
```

Эти правила объясняют, почему `"ß".upper() == "SS"` в Python.

---

## 7. CaseFolding.txt — сворачивание регистра (Case Folding)

**Файл:** [`CaseFolding.txt`](https://unicode.org/Public/UCD/latest/ucd/CaseFolding.txt)

Case folding — это нормализация для сравнения без учёта регистра. Отличается от `toLowerCase()`:

```
0041; C; 0061;        # A → a (simple/common)
00DF; F; 0073 0073;   # ß → ss (full, т. е. один символ → два)
0049; T; 0131;        # I → ı (только в турецком, T=Turkic)
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

Таблица весов для Unicode Collation Algorithm (UCA). Подробно разобрана в [статье 6](../06-collation/article.md), но формат такой:

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
