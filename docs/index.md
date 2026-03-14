# Unicode в глубину

Серия технических статей о стандарте Unicode — от основ до внутреннего устройства библиотек.

!!! info "О проекте"
    Этот сайт и все статьи на нём сгенерированы нейросетью **Claude Sonnet 4.6** (Anthropic) в диалоге с автором. Материалы прошли редакцию и проверку, но могут содержать неточности — всегда сверяйтесь с [официальной документацией Unicode](https://unicode.org/reports/).

## О серии

Unicode — это не просто «поддержка разных языков». Это сложный стандарт с базой данных символов, алгоритмами нормализации, сортировки, разбиения текста на кластеры. Эта серия разбирает Unicode изнутри: файлы стандарта, алгоритмы, реализации в Python и Node.js, исходники библиотеки ICU.

Каждая статья сопровождается запускаемыми примерами кода (Python и/или Node.js), которые можно найти в [репозитории](https://github.com).

---

## Статьи

### [1. Основы Unicode: кодовые точки, плоскости, блоки](01-basics/article.md)

История создания Unicode, кодовые точки, 17 плоскостей (BMP и за её пределами), блоки, скрипты и категории символов. Всё что нужно знать перед тем, как идти глубже.

### [2. Unicode Character Database (UCD): файлы и структура](02-ucd-files/article.md)

Где живут данные Unicode и как их читать. Разбираем `UnicodeData.txt`, `Blocks.txt`, `Scripts.txt`, `PropList.txt` и другие файлы UCD вручную — без библиотек.

### [3. Кодировки: UTF-8, UTF-16, UTF-32](03-encodings/article.md)

Чем кодировка отличается от кодового пространства. Алгоритм UTF-8 побайтово, суррогатные пары UTF-16, BOM. Ловушки: почему `len('🌍') == 2` в JavaScript и при чём тут графемные кластеры.

### [4. Нормализация Unicode: NFD, NFC, NFKD, NFKC](04-normalization/article.md)

Почему одна и та же буква может быть разными байтами. Каноническая и совместимая декомпозиция, Canonical Combining Class, обратная композиция. Где это важно: сравнение строк, пароли, безопасность.

### [5. Коллация: Unicode Collation Algorithm и CLDR](05-collation/article.md)

Почему `sort()` врёт для большинства языков. Многоуровневые веса L1/L2/L3, таблица DUCET, локальные правила CLDR. Примеры с PyICU и `Intl.Collator`.

### [6. Unicode на практике: Linux, инструменты, исходники ICU](06-linux-tools/article.md)

Утилиты `uniname`, `iconv`, `hexdump`. Структура репозитория ICU и как читать исходники коллации. Модуль `regex` с поддержкой `\p{Script=Cyrillic}`. Практический скрипт-анализатор Unicode-состава текста.

---

## Примеры кода

Все примеры есть в репозитории рядом с каждой статьёй:

| Статья | Python | Node.js |
|---|---|---|
| 1. Основы | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/01-basics/examples.py) | [examples.js](https://github.com/comtextspace/unicode/blob/main/docs/01-basics/examples.js) |
| 2. UCD файлы | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/02-ucd-files/examples.py) | — |
| 3. Кодировки | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/03-encodings/examples.py) | [examples.js](https://github.com/comtextspace/unicode/blob/main/docs/03-encodings/examples.js) |
| 4. Нормализация | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/04-normalization/examples.py) | [examples.js](https://github.com/comtextspace/unicode/blob/main/docs/04-normalization/examples.js) |
| 5. Коллация | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/05-collation/examples.py) | [examples.js](https://github.com/comtextspace/unicode/blob/main/docs/05-collation/examples.js) |
| 6. Linux/ICU | [examples.py](https://github.com/comtextspace/unicode/blob/main/docs/06-linux-tools/examples.py) | — |

---

## Ресурсы

Ссылки на спецификации, UCD-файлы, документацию библиотек — в разделе [Ресурсы](resources.md).
