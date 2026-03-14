# Ресурсы по Unicode

## Спецификации и стандарты

| Ресурс | URL |
|---|---|
| Unicode Standard (последняя версия онлайн) | https://www.unicode.org/versions/latest/ |
| Unicode Standard 15.0 (PDF/HTML) | https://www.unicode.org/versions/Unicode15.0.0/ |
| Unicode Glossary | https://www.unicode.org/glossary/ |
| Unicode FAQ | https://www.unicode.org/faq/ |

## Unicode Character Database (UCD)

| Ресурс | URL |
|---|---|
| Корень UCD (последняя версия) | https://unicode.org/Public/UCD/latest/ucd/ |
| UnicodeData.txt | https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt |
| Blocks.txt | https://unicode.org/Public/UCD/latest/ucd/Blocks.txt |
| Scripts.txt | https://unicode.org/Public/UCD/latest/ucd/Scripts.txt |
| PropList.txt | https://unicode.org/Public/UCD/latest/ucd/PropList.txt |
| DerivedCoreProperties.txt | https://unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt |
| SpecialCasing.txt | https://unicode.org/Public/UCD/latest/ucd/SpecialCasing.txt |
| CaseFolding.txt | https://unicode.org/Public/UCD/latest/ucd/CaseFolding.txt |
| GraphemeBreakProperty.txt | https://unicode.org/Public/UCD/latest/ucd/auxiliary/GraphemeBreakProperty.txt |

## Коллация (Collation)

| Ресурс | URL |
|---|---|
| allkeys.txt — DUCET (весовая таблица) | https://unicode.org/Public/UCA/latest/allkeys.txt |
| Unicode Collation Algorithm (UTS#10) | https://www.unicode.org/reports/tr10/ |
| CLDR (Common Locale Data Repository) | https://cldr.unicode.org/ |
| CLDR данные на GitHub | https://github.com/unicode-org/cldr |

## Нормализация

| Ресурс | URL |
|---|---|
| Unicode Normalization Forms (UAX#15) | https://www.unicode.org/reports/tr15/ |
| Composition Exclusions | https://unicode.org/Public/UCD/latest/ucd/CompositionExclusions.txt |
| NormalizationTest.txt | https://unicode.org/Public/UCD/latest/ucd/NormalizationTest.txt |

## Библиотеки и инструменты

| Ресурс | URL |
|---|---|
| ICU — International Components for Unicode | https://icu.unicode.org/ |
| ICU исходники на GitHub (icu4c + icu4j) | https://github.com/unicode-org/icu |
| Python `unicodedata` (stdlib) | https://docs.python.org/3/library/unicodedata.html |
| PyICU (Python bindings для ICU) | https://pypi.org/project/PyICU/ |
| `regex` модуль (Python, поддержка \p{}) | https://pypi.org/project/regex/ |
| Node.js `Intl` API | https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl |
| `full-icu` npm пакет | https://www.npmjs.com/package/full-icu |

## Скачать UCD-файлы локально

```bash
cd /home/petro/work/unicode-article/02-ucd-files/data
wget https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
wget https://unicode.org/Public/UCD/latest/ucd/Blocks.txt
wget https://unicode.org/Public/UCD/latest/ucd/Scripts.txt
wget https://unicode.org/Public/UCD/latest/ucd/PropList.txt
wget https://unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt
wget https://unicode.org/Public/UCA/latest/allkeys.txt
```

## Зависимости для примеров из статей

```bash
# Python
pip install PyICU regex

# Node.js — встроенный ICU достаточен для большинства примеров
# Для полного набора локалей:
npm install full-icu
# Затем запускать: node --icu-data-dir=node_modules/full-icu script.js

# Linux утилиты
sudo apt install uniutils unicode
```
