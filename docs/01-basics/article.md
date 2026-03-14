# Статья 1. Основы Unicode: кодовые точки, плоскости, блоки

!!! info "О проекте"
    Этот сайт и все статьи на нём сгенерированы нейросетью **Claude Sonnet 4.6** (Anthropic) в диалоге с автором. Материалы прошли редакцию и проверку, но могут содержать неточности — всегда сверяйтесь с [официальной документацией Unicode](https://unicode.org/reports/).

## 1. Зачем вообще понадобился Unicode?

До Unicode каждая страна и компания изобретала собственную кодировку. В мире одновременно существовали сотни несовместимых систем: ASCII (7-бит, только английский), KOI8-R (русский), CP1252 (Windows Western), ISO 8859-1..16, GB2312 (китайский), Shift-JIS (японский) и т.д.

Проблемы были повсюду:

- Письмо, написанное в Windows на русском, открывалось кракозябрами в Unix.
- Один байт `0xE9` — это `é` в Latin-1, `й` в KOI8-R и совсем другое в Big5.
- Смешать русский с греческим в одном тексте было невозможно без специальных хаков.

В 1987 году инженеры Xerox и Apple начали работу над универсальным стандартом. В 1991 году вышла версия Unicode 1.0. Сегодня (Unicode 15.1) стандарт охватывает **149 878 символов**, **161 скрипт** и поддерживает все живые и многие исторические письменности мира.

---

## 2. Кодовые точки (Code Points)

Ключевое понятие Unicode — **кодовая точка** (code point). Это просто целое неотрицательное число, однозначно идентифицирующее символ. Записывается как `U+XXXX` (hex).

```
U+0041  →  A  (LATIN CAPITAL LETTER A)
U+0410  →  А  (CYRILLIC CAPITAL LETTER A)
U+1F30D →  🌍 (EARTH GLOBE EUROPE-AFRICA)
```

Всё кодовое пространство: **U+0000..U+10FFFF** — 1 114 112 позиций.

> **Важно:** кодовая точка — это _абстрактное число_, а не байты в памяти. Как именно хранить эти числа — задача **кодировок** (UTF-8, UTF-16, UTF-32). Это разные вещи! (Подробнее — в статье 3.)

---

## 3. Плоскости (Planes)

Всё кодовое пространство поделено на **17 плоскостей** по 65 536 (0x10000) позиций каждая:

| № | Диапазон | Название | Что там |
|---|---|---|---|
| 0 | U+0000..U+FFFF | Basic Multilingual Plane (BMP) | Почти все современные письменности, CJK, символы |
| 1 | U+10000..U+1FFFF | Supplementary Multilingual Plane (SMP) | Исторические письменности, эмодзи, нотация |
| 2 | U+20000..U+2FFFF | Supplementary Ideographic Plane (SIP) | Редкие CJK-иероглифы |
| 3 | U+30000..U+3FFFF | Tertiary Ideographic Plane (TIP) | Очень редкие CJK (с Unicode 13.0) |
| 14 | U+E0000..U+EFFFF | Supplementary Special-purpose Plane (SSP) | Языковые теги, вариационные селекторы |
| 15 | U+F0000..U+FFFFF | Supplementary Private Use Area-A (SPUA-A) | Приватное использование |
| 16 | U+100000..U+10FFFF | Supplementary Private Use Area-B (SPUA-B) | Приватное использование |
| 4-13 | — | (зарезервированы) | Не используются |

**Плоскость 0 (BMP)** — самая важная. Если символ в BMP, то в UTF-16 он занимает ровно 2 байта. Символы вне BMP называются **supplementary characters** и требуют суррогатных пар в UTF-16.

---

## 4. Блоки (Blocks)

Внутри каждой плоскости символы сгруппированы в **блоки** — непрерывные диапазоны, обычно объединяющие символы одной письменности или тематики.

Примеры:

| Блок | Диапазон | Размер |
|---|---|---|
| Basic Latin | U+0000..U+007F | 128 |
| Latin-1 Supplement | U+0080..U+00FF | 128 |
| Cyrillic | U+0400..U+04FF | 256 |
| Cyrillic Supplement | U+0500..U+052F | 48 |
| Arabic | U+0600..U+06FF | 256 |
| CJK Unified Ideographs | U+4E00..U+9FFF | 20 912 |
| Emoticons | U+1F600..U+1F64F | 80 |
| Mahjong Tiles | U+1F004..U+1F00F | 16 |

Полный список — в файле `Blocks.txt` из Unicode Character Database (UCD).

> **Блок ≠ Скрипт.** Блок — это фиксированный диапазон адресов. Скрипт — это свойство символа (к какой письменности он относится). Например, знаки препинания из блока «Basic Latin» относятся к скрипту «Common», а не «Latin».

---

## 5. Скрипты (Scripts)

Скрипт — это атрибут символа из файла `Scripts.txt`. Символ имеет ровно один скрипт (или значение `Common` / `Inherited` для «разделяемых» символов).

```
U+0041 (A)  →  Script: Latin
U+0410 (А)  →  Script: Cyrillic
U+0660 (٠)  →  Script: Arabic      (арабская цифра 0)
U+0030 (0)  →  Script: Common      (обычная цифра 0 — общая для всех)
U+0301 ( ́)  →  Script: Inherited   (combining accent наследует скрипт базового символа)
```

Скрипты важны для:
- Регулярных выражений: `\p{Script=Cyrillic}`
- Обнаружения спуфинга (IDN homograph attacks)
- Выбора шрифта

---

## 6. Категории символов (General Category)

Каждый символ имеет **General Category** — двухбуквенный код:

| Код | Название | Пример |
|---|---|---|
| Lu | Letter, Uppercase | A, А, Ñ |
| Ll | Letter, Lowercase | a, а, ñ |
| Lt | Letter, Titlecase | Dž |
| Lm | Letter, Modifier | ʰ (modifier letter h) |
| Lo | Letter, Other | 中 (CJK), ء (Arabic) |
| Mn | Mark, Nonspacing | ́ (combining acute) |
| Mc | Mark, Spacing Combining | ा (деванагари гласная) |
| Me | Mark, Enclosing | ⃝ |
| Nd | Number, Decimal Digit | 0..9, ٠..٩ |
| Nl | Number, Letter | Ⅳ (римские цифры) |
| No | Number, Other | ½, ② |
| Pc | Punctuation, Connector | _ (underscore) |
| Pd | Punctuation, Dash | -, –, — |
| Ps | Punctuation, Open | (, [, { |
| Pe | Punctuation, Close | ), ], } |
| Pi | Punctuation, Initial Quote | « |
| Pf | Punctuation, Final Quote | » |
| Po | Punctuation, Other | !, ., , |
| Sm | Symbol, Math | +, =, ∑ |
| Sc | Symbol, Currency | $, €, ₽ |
| Sk | Symbol, Modifier | ^ (spacing circumflex) |
| So | Symbol, Other | ©, ™, 🌍 |
| Zs | Separator, Space | (пробел, неразрывный пробел) |
| Zl | Separator, Line | U+2028 |
| Zp | Separator, Paragraph | U+2029 |
| Cc | Other, Control | U+0000..U+001F (управляющие) |
| Cf | Other, Format | U+200B (zero-width space), BOM |
| Cs | Other, Surrogate | U+D800..U+DFFF |
| Co | Other, Private Use | U+E000..U+F8FF |
| Cn | Other, Not Assigned | нет символа |

---

## 7. Unicode Character Database (UCD)

Все свойства символов хранятся в **Unicode Character Database** — наборе текстовых файлов, публикуемых вместе с каждой версией стандарта.

Главный файл — `UnicodeData.txt`. Каждая строка описывает один символ (или диапазон):

```
0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;
```

15 полей через `;`:
1. Кодовая точка (hex)
2. Имя символа
3. General Category
4. Canonical Combining Class (0 = нет, 1..254 = порядок combining marks)
5. Bidi Class (L=слева-направо, R=справа-налево, AN=арабская цифра…)
6. Декомпозиция (тип + кодовые точки)
7-8. Числовые значения (для цифр)
9. Mirrored (Y/N) — зеркалится ли при RTL
10. Unicode 1.0 имя (устаревшее)
11. ISO Comment (устаревшее)
12. Simple Uppercase Mapping
13. Simple Lowercase Mapping
14. Simple Titlecase Mapping

Подробнее о файлах UCD — в статье 2.

---

## Примеры кода → `examples.py` и `examples.js`

Запустите примеры из соседних файлов, чтобы исследовать свойства символов интерактивно.
