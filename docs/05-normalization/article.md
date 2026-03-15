# Статья 5. Нормализация Unicode: NFD, NFC, NFKD, NFKC

## Проблема: один символ — много представлений

В Unicode один и тот же _воспринимаемый_ символ может быть представлен несколькими разными последовательностями кодовых точек.

Классический пример — «é» (e с акутом):

```
U+00E9          →  é  (одна кодовая точка: LATIN SMALL LETTER E WITH ACUTE)
U+0065 U+0301   →  é  (две кодовые точки: e + COMBINING ACUTE ACCENT)
```

Оба варианта выглядят одинаково, но:
```python
'\u00e9' == '\u0065\u0301'  # False!
'\u00e9' in 'café'          # True или False — зависит от варианта
```

Это не баг — это осознанная часть стандарта. Нормализация — инструмент привести строки к единому виду для корректного сравнения.

---

## 1. Canonical Combining Class (CCC)

**CCC** — числовое свойство (0..254) combining marks. Определяет порядок, в котором они должны стоять после базового символа в нормализованной форме.

```
U+0301  COMBINING ACUTE ACCENT          CCC = 230
U+0308  COMBINING DIAERESIS             CCC = 230
U+0327  COMBINING CEDILLA               CCC = 202
U+0000..большинство букв               CCC = 0  (не combining)
```

Символы с одинаковым CCC могут идти в любом порядке (они независимы). Символы с разными CCC должны идти в возрастающем порядке.

Пример:
```
a + cedilla + acute   =   а\u0327\u0301   (CCC 202, потом 230)
a + acute + cedilla   =   а\u0301\u0327   (РАЗНЫЙ ПОРЯДОК — ненормализовано)
```

После NFD оба будут выглядеть как `а\u0327\u0301`.

---

## 2. Каноническая декомпозиция (NFD)

**NFD** (Normalization Form D — Decomposed) — разложить составные символы на базовый символ + combining marks, расставить combining marks в порядке CCC.

```
é (U+00E9)  →  e (U+0065) + ́ (U+0301)
ö (U+00F6)  →  o (U+006F) + ̈ (U+0308)
ñ (U+00F1)  →  n (U+006E) + ̃ (U+0303)
Ǽ (U+01FC)  →  Æ (U+00C6) + ́ (U+0301)  →  далее не раскладывается (Æ — базовый)
```

Алгоритм декомпозиции рекурсивный: если символ декомпозируется, берём его компоненты и продолжаем раскладывать каждый.

---

## 3. Каноническая композиция (NFC)

**NFC** (Normalization Form C — Composed) — применить NFD, затем _скомпоновать_ обратно там, где это возможно по таблице **Canonical Composition**.

Не всё что разложилось — может сложиться обратно. Если символ есть в списке **Composition Exclusions** (файл `CompositionExclusions.txt`), он не компонуется.

```
e + ́ (U+0301)  →  NFC  →  é (U+00E9)      ✓ есть в таблице
o + ̈ (U+0308)  →  NFC  →  ö (U+00F6)      ✓
U+0041 U+030A   →  NFC  →  Å (U+00C5)       ✓
```

**NFC — рекомендуемая форма** для большинства приложений и хранения данных. NFD удобнее для обработки: combining marks явно отделены от базового символа.

---

## 4. Совместимая декомпозиция (NFKD)

**NFKD** (Normalization Form KD — Compatibility Decomposed) — то же что NFD, но дополнительно раскладывает **compatibility** символы.

Такие символы — это варианты основных символов, добавленные для совместимости со старыми кодировками. В `UnicodeData.txt` их decomposition начинается с тега в `<>`.

Примеры:

| Символ | U+ | NFKD | Тег декомпозиции |
|---|---|---|---|
| ﬁ (fi лигатура) | U+FB01 | f + i | `<compat>` |
| ² (суперскрипт 2) | U+00B2 | 2 | `<super>` |
| ½ (вульгарная дробь) | U+00BD | 1 + ⁄ + 2 | `<fraction>` |
| ｆ (fullwidth f) | U+FF46 | f | `<wide>` |
| ＡＢ (fullwidth ABC) | U+FF21..| ABC | `<wide>` |
| ① (enclosed 1) | U+2460 | 1 | `<circle>` |
| ™ (trademark) | U+2122 | T + M | `<compat>` |

После NFKD строка может стать намного длиннее, а визуально другой.

---

## 5. Совместимая композиция (NFKC)

**NFKC** = NFKD + каноническая композиция. Чаще всего используется для:
- Сравнения строк без учёта визуальных вариантов
- Нормализации идентификаторов (Python SyntaxError при смешении форм)
- Безопасности (предотвращение spoofing через fullwidth символы)

```python
'ｆａｓｔ' == 'fast'   # False
unicodedata.normalize('NFKC', 'ｆａｓｔ') == 'fast'  # True
```

---

## 6. Сводная таблица форм нормализации

| Форма | Декомпозиция | Композиция | Что меняет |
|---|---|---|---|
| NFD  | Каноническая | Нет   | e+combining вместо precomposed |
| NFC  | Каноническая | Да    | Обратно в precomposed (рекомендуется) |
| NFKD | Compat+Canon | Нет   | Ещё раскладывает лигатуры, ширины |
| NFKC | Compat+Canon | Да    | NFKD + обратная композиция |

---

## 7. Где нормализация особенно важна?

### Сравнение строк
```python
# Без нормализации — ошибка!
password_stored = 'café'                    # NFC
password_input  = 'cafe\u0301'              # NFD (разные байты!)
password_stored == password_input           # False — неправильно!

# С нормализацией — правильно
import unicodedata
nfc = lambda s: unicodedata.normalize('NFC', s)
nfc(password_stored) == nfc(password_input) # True
```

### Имена файлов
macOS использует NFD для имён файлов в HFS+. Linux/ext4 хранит байты как есть. Это приводит к проблемам при синхронизации файлов через git:
```bash
# macOS создаёт файл с NFD-именем
# Git на Linux видит его как два разных файла
git status  # нарушения нормализации в именах файлов
```

### Unicode spoofing (атаки через похожие символы)

NFKC не защищает от атак, где используются **визуально похожие символы из разных скриптов**:

```python
real  = "admin"   # все Latin
fake  = "аdmin"   # первая 'а' — Cyrillic U+0430, остальные Latin

real == fake       # False
# NFKC не помогает — оба символа уже в "простой" форме, просто разные скрипты

import unicodedata
unicodedata.normalize('NFKC', fake) == real  # False — разные символы
```

Для таких случаев в Unicode существует отдельный стандарт **UTS #39 — Unicode Security Mechanisms** и файл [`confusables.txt`](https://unicode.org/Public/security/latest/confusables.txt), который перечисляет все пары «confusable»-символов:

```
# confusables.txt (фрагмент):
0430 ;  0061 ;  MA  # а (CYRILLIC SMALL LETTER A) → a (LATIN SMALL LETTER A)
0435 ;  0065 ;  MA  # е (CYRILLIC SMALL LETTER IE) → e (LATIN SMALL LETTER E)
043E ;  006F ;  MA  # о (CYRILLIC SMALL LETTER O) → o (LATIN SMALL LETTER O)
```

**Практика: обнаружение смешанных скриптов**

Надёжная проверка — убедиться, что строка использует только один скрипт:

```python
import unicodedata

def scripts_in_string(s: str) -> set[str]:
    """Возвращает множество скриптов в строке (исключая Common и Inherited)."""
    scripts = set()
    for ch in s:
        # unicodedata не даёт Script напрямую, используем имя символа
        name = unicodedata.name(ch, '')
        if 'CYRILLIC' in name:
            scripts.add('Cyrillic')
        elif 'LATIN' in name:
            scripts.add('Latin')
        # и т. д.
    return scripts

# Лучше — через модуль regex (поддерживает \p{Script=...}):
import regex
def is_mixed_script(s: str) -> bool:
    cyrillic = bool(regex.search(r'\p{Script=Cyrillic}', s))
    latin    = bool(regex.search(r'\p{Script=Latin}', s))
    return cyrillic and latin

print(is_mixed_script("аdmin"))  # True — подозрительно!
print(is_mixed_script("admin"))  # False
print(is_mixed_script("привет")) # False
```

Ссылки: [UTS #39](https://unicode.org/reports/tr39/) · [`confusables.txt`](https://unicode.org/Public/security/latest/confusables.txt)

### Python идентификаторы
Python 3 нормализует идентификаторы через NFKC:
```python
# Это легальный Python (но не рекомендуется):
ｖаr = 42   # fullwidth v + кирилл.а + Latin r
print(ｖаr)  # 42
```

---

## 8. Быстрая проверка нормализации

```python
import unicodedata

def is_normalized(s: str, form: str) -> bool:
    return unicodedata.is_normalized(form, s)  # Python 3.3+
```

`is_normalized` работает быстрее `normalize()` когда строка уже нормализована — не создаёт новый объект.

