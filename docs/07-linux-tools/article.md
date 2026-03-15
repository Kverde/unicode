# Статья 7. Unicode на практике: Linux, инструменты, исходники ICU

## 1. Unicode-инструменты в Linux

### uniutils — пакет специализированных утилит

!!! warning "Доступность"
    Пакет `uniutils` есть в репозиториях Ubuntu/Debian, но отсутствует в Parrot OS, Kali и некоторых других дистрибутивах. Если `sudo apt install uniutils` выдаёт `Unable to locate package` — используйте Python-альтернативу ниже.

```bash
# Ubuntu / Debian (если доступен)
sudo apt install uniutils
```

**`uniname`** — вывести Unicode-имена байт/символов файла или stdin:

```bash
echo "Привет" | uniname
# Offset  Name                    Code Point  UTF-8
# 0       CYRILLIC CAPITAL LETTER PE  U+041F  D0 9F
# 2       CYRILLIC SMALL LETTER R     U+0440  D1 80
# ...
```

**`unidesc`** — описание символов (категория, скрипт):

```bash
echo "Hello Привет" | unidesc
```

---

### unicode — интерактивный инструмент поиска

```bash
sudo apt install unicode
```

```bash
# Поиск по имени
unicode acute
unicode "latin small"

# Информация по кодовой точке
unicode U+1F30D
unicode 0x1F30D

# Все символы из блока
unicode --block=Cyrillic | head -30
```

---

### hexdump / xxd — анализ байтов файла

```bash
# Посмотреть байты UTF-8
echo "Мир 🌍" | hexdump -C
# 00000000  d0 9c d0 b8 d1 80 20 f0  9f 8c 8d 0a              |...... ...|

echo "Мир 🌍" | xxd
# 00000000: d09c d0b8 d180 20f0 9f8c 8d0a       ...... .....

# xxd в обратную сторону: hex → binary
echo "48656c6c6f" | xxd -r -p
# Hello
```

---

### iconv — конвертация кодировок

```bash
# Список поддерживаемых кодировок
iconv -l | grep -iE 'utf|koi|cp125|win'

# Конвертация файла
iconv -f windows-1251 -t utf-8 input.txt > output.txt
iconv -f koi8-r -t utf-8 old_file.txt > new_file.txt

# Конвертация с игнорированием ошибок
iconv -f latin1 -t utf-8 -c input.txt > output.txt

# Обнаружение кодировки (через file)
file -i document.txt
# document.txt: text/plain; charset=utf-8
```

---

### Локали и glibc

```bash
# Текущая локаль
locale
# LANG=ru_RU.UTF-8
# LC_COLLATE=ru_RU.UTF-8
# ...

# Все доступные локали
locale -a | grep -i ru

# Где хранятся файлы локалей
ls /usr/share/i18n/locales/ | grep ru
# Файл локали: /usr/share/i18n/locales/ru_RU
# Правила коллации: /usr/share/locale/ru_RU.UTF-8/LC_COLLATE

# Пересборка локалей
sudo locale-gen ru_RU.UTF-8
sudo update-locale LANG=ru_RU.UTF-8

# Сортировка с учётом локали через sort
echo -e "ёж\nЕль\nелка" | LC_ALL=ru_RU.UTF-8 sort
```

---

### Python в командной строке для Unicode-анализа

```bash
# Версия Unicode
python3 -c "import unicodedata; print(unicodedata.unidata_version)"

# Имя символа
python3 -c "import unicodedata; print(unicodedata.name('🌍'))"

# Категория
python3 -c "import unicodedata; print(unicodedata.category('А'))"

# Hex-дамп строки
python3 -c "s='Привет'; print(s.encode('utf-8').hex())"

# Байты → строка
python3 -c "print(bytes.fromhex('d09fd180d0b8d0b2d0b5d182').decode('utf-8'))"
```

---

## 2. Структура исходников ICU

**Репозиторий:** https://github.com/unicode-org/icu

```
icu/
├── icu4c/              # C++ реализация (главная)
│   ├── source/
│   │   ├── common/     # Базовые операции: UTF-8/16, нормализация, свойства
│   │   │   ├── unicode/
│   │   │   │   ├── unistr.h       # UnicodeString класс
│   │   │   │   ├── normalizer2.h  # Нормализация API
│   │   │   │   ├── uchar.h        # Свойства символов (u_charType, u_charName…)
│   │   │   │   └── uscript.h      # Скрипты
│   │   │   ├── normalizer2.cpp    # Реализация NFC/NFD/NFKC/NFKD
│   │   │   ├── uniset.cpp         # UnicodeSet (\p{} паттерны)
│   │   │   └── uchar.cpp          # u_charType и др.
│   │   ├── i18n/       # Locale-sensitive: коллация, форматирование
│   │   │   ├── ucol.cpp           # Collation API (ucol_open, ucol_strcoll…)
│   │   │   ├── collation.h        # Типы весов: CollationData, DUCET
│   │   │   ├── collationiterator.cpp  # Итерация для получения весов
│   │   │   ├── collationkeys.cpp      # Построение sort keys
│   │   │   ├── rulebasedcollator.cpp  # Tailoring
│   │   │   └── regexcmp.cpp       # Unicode regex engine
│   │   ├── data/       # Данные Unicode (скомпилированные из CLDR + UCD)
│   │   │   ├── coll/
│   │   │   │   ├── root.txt    # DUCET (корневые правила)
│   │   │   │   ├── ru.txt      # Русские правила коллации
│   │   │   │   └── de.txt      # Немецкие правила
│   │   │   └── misc/
│   │   │       └── icuver.txt  # Версия ICU и Unicode
│   │   └── test/       # Тесты (полезны как примеры)
│   └── include/
└── icu4j/              # Java реализация
```

### Как читать правила коллации в ICU

Файл `icu4c/source/data/coll/root.txt` — это DUCET в формате ICU resource bundle:

```
root{
    RuleBasedCollator{
        Version{ "56.0" }
        Sequence{
            "[normalization on]"
            "[caseLevel off]"
            "&[before 1] [first regular] < \u0660 = \u06F0"  // Arabic digits
            "& b < c, C"   // b < c, c = C (на одном уровне, разный регистр)
        }
    }
}
```

Русский файл `ru.txt` добавляет правила для ё/е:
```
ru {
    %%CollationElements {
        Sequence {
            "& \u0415 << \u0401"   // Е << Ё (на вторичном уровне)
            "& \u0435 << \u0451"   // е << ё
        }
    }
}
```

### Ключевые функции в ucol.cpp

```cpp
// Открыть коллатор для локали
UCollator* ucol_open(const char* loc, UErrorCode* status);

// Сравнить две строки
UCollationResult ucol_strcoll(const UCollator* coll,
                               const UChar* source, int32_t sourceLength,
                               const UChar* target, int32_t targetLength);

// Получить sort key (для кэширования)
int32_t ucol_getSortKey(const UCollator* coll,
                         const UChar* source, int32_t sourceLength,
                         uint8_t* result, int32_t resultLength);
```

---

## 3. Python `regex` модуль vs стандартный `re`

Стандартный `re` поддерживает только базовые Unicode-классы (`\w`, `\d`). Модуль `regex` (pip install regex) поддерживает полные Unicode-свойства.

### Сравнение возможностей

| Возможность | `re` | `regex` |
|---|---|---|
| `\p{Script=Cyrillic}` | ✗ | ✓ |
| `\p{Letter}` / `\p{L}` | ✗ | ✓ |
| `\p{Block=CJK_Unified_Ideographs}` | ✗ | ✓ |
| `\p{Emoji}` | ✗ | ✓ |
| Grapheme cluster `\X` | ✗ | ✓ |
| Fullcase matching | ✗ | ✓ |
| Atomic groups `(?>...)` | ✗ | ✓ |
| Possessive quantifiers `++` | ✗ | ✓ |

### Синтаксис свойств символов

```python
import regex

# По скрипту
regex.findall(r'\p{Script=Cyrillic}+', text)
regex.findall(r'\p{Cyrillic}+', text)           # сокращённо

# По категории
regex.findall(r'\p{Lu}+', text)                  # uppercase letters
regex.findall(r'\p{Letter}+', text)             # все буквы
regex.findall(r'\p{L}+', text)                  # то же, сокращённо

# По блоку
regex.findall(r'\p{Block=Emoticons}', text)

# По свойству
regex.findall(r'\p{Emoji}+', text)
regex.findall(r'\p{White_Space}+', text)

# Графемные кластеры
regex.findall(r'\X', text)   # каждый кластер = один элемент
```

---

## 4. Анализ Unicode-состава текста на Python

Несколько строк для базовой статистики — категории, скрипты, эмодзи:

```python
import unicodedata
from collections import Counter

text = "Hello Привет مرحبا 🌍🎉 café 中文"

# Подсчёт по категориям General Category
cats = Counter(unicodedata.category(c) for c in text if c != ' ')
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")
```

```
  Ll: 10
  Lo: 5
  Lu: 2
  So: 2
  Mn: 1
  Po: 1
```

```python
import regex  # pip install regex

text = "Hello Привет مرحبا 🌍🎉"
print(regex.findall(r'\p{Script=Latin}+',    text))  # ['Hello']
print(regex.findall(r'\p{Script=Cyrillic}+', text))  # ['Привет']
print(regex.findall(r'\p{Script=Arabic}+',   text))  # ['مرحبا']
print(regex.findall(r'\p{Emoji_Presentation}', text)) # ['🌍', '🎉']
print(regex.findall(r'\X', '👨‍👩‍👧'))             # ['👨\u200d👩\u200d👧'] — 1 кластер
```

---

## 5. Полезные однострочники для отладки Unicode

```bash
# Найти не-ASCII символы в файле
grep -P '[^\x00-\x7F]' file.txt

# Найти файлы с BOM
grep -rl $'\xef\xbb\xbf' .

# Конвертировать NFD-имена файлов в NFC (macOS → Linux)
python3 -c "
import os, unicodedata
for f in os.listdir('.'):
    nfc = unicodedata.normalize('NFC', f)
    if f != nfc:
        os.rename(f, nfc)
        print(f'renamed: {f!r} → {nfc!r}')
"

# Показать hex Unicode для строки
python3 -c "
s = input('Введите строку: ')
for ch in s:
    print(f'U+{ord(ch):04X} = {ch!r}')
"

# Статистика символов файла по категориям
python3 -c "
import sys, unicodedata
from collections import Counter
text = open(sys.argv[1]).read()
cats = Counter(unicodedata.category(c) for c in text)
for cat, n in sorted(cats.items()):
    print(f'{cat}: {n}')
" myfile.txt
```
