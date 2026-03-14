#!/usr/bin/env node
/**
 * Статья 5 — Коллация: Unicode Collation Algorithm и CLDR.
 * Примеры на Node.js через встроенный Intl API.
 *
 * Запуск: node examples.js
 *
 * Для полного набора локалей (CLDR):
 *   npm install full-icu
 *   node --icu-data-dir=node_modules/full-icu examples.js
 */

// ─────────────────────────────────────────────
// 0. Проблема наивной сортировки
// ─────────────────────────────────────────────

console.log('=== Проблема наивной сортировки ===\n');

const ruWords    = ['ёж', 'Ель', 'елка', 'Ёж', 'ель', 'Ежевика', 'Ещё'];
const enWords    = ['apple', 'Banana', 'cherry', 'Apricot', 'banana', 'CHERRY'];
const diaWords   = ['café', 'cafe', 'Café', 'CAFE', 'cáfe'];
const fileNames  = ['file1', 'file10', 'file2', 'file20', 'file3'];

console.log('Русские слова (naive):', [...ruWords].sort());
console.log('Английские слова (naive):', [...enWords].sort());
console.log('С диакритикой (naive):', [...diaWords].sort());
console.log('Файлы с числами (naive):', [...fileNames].sort());
console.log();


// ─────────────────────────────────────────────
// 1. Intl.Collator — стандартный API
// ─────────────────────────────────────────────

console.log('=== Intl.Collator ===\n');

// Базовый collator с локалью
function sortWith(words, locale, options = {}) {
  const col = new Intl.Collator(locale, options);
  return [...words].sort(col.compare);
}

console.log('Русские слова:');
console.log('  ru    (default):', sortWith(ruWords, 'ru'));
console.log('  ru    (primary):', sortWith(ruWords, 'ru', { sensitivity: 'base' }));

console.log('\nАнглийские слова:');
console.log('  en    (default):', sortWith(enWords, 'en'));
console.log('  en    (base):   ', sortWith(enWords, 'en', { sensitivity: 'base' }));

console.log('\nС диакритикой:');
console.log('  en    (variant):', sortWith(diaWords, 'en', { sensitivity: 'variant' }));  // все уровни
console.log('  en    (base):   ', sortWith(diaWords, 'en', { sensitivity: 'base' }));     // только L1

console.log();


// ─────────────────────────────────────────────
// 2. Sensitivity levels
// ─────────────────────────────────────────────

console.log('=== Sensitivity levels ===\n');

// Intl.Collator sensitivity:
//   'base'    — только L1 (primary: разные буквы)
//   'accent'  — L1 + L2 (+ диакритика)
//   'case'    — L1 + L3 (+ регистр, но не диакритика)
//   'variant' — L1+L2+L3+L4 (всё, по умолчанию)

const testPairs = [
  ['a', 'A'],
  ['a', 'á'],
  ['á', 'Á'],
  ['cafe', 'café'],
  ['straße', 'strasse'],
];

for (const sensitivity of ['base', 'accent', 'case', 'variant']) {
  const col = new Intl.Collator('en', { sensitivity });
  console.log(`sensitivity='${sensitivity}':`);
  for (const [a, b] of testPairs) {
    const result = col.compare(a, b);
    const label = result === 0 ? 'EQUAL' : result < 0 ? `'${a}'<'${b}'` : `'${a}'>'${b}'`;
    console.log(`  ${JSON.stringify(a)} vs ${JSON.stringify(b)}: ${label}`);
  }
  console.log();
}


// ─────────────────────────────────────────────
// 3. Locale-специфичные правила
// ─────────────────────────────────────────────

console.log('=== Locale-специфичные правила ===\n');

// Шведский: ä, ö, å идут ПОСЛЕ z
const seWords = ['ärlig', 'zebra', 'öppen', 'apple', 'åska', 'banana'];
console.log('Слова с ä/ö/å:');
console.log('  en (naive):     ', sortWith(seWords, 'en'));
console.log('  sv (шведский):  ', sortWith(seWords, 'sv'));  // ä, ö, å после z
console.log('  de (немецкий):  ', sortWith(seWords, 'de'));  // ä ≈ a

// Немецкий phonebook vs standard
const deWords = ['Müller', 'Mueller', 'Muller', 'müssen', 'muss'];
console.log('\nНемецкие слова с ü:');
console.log('  de (standard):  ', sortWith(deWords, 'de'));
console.log('  de-u-co-phonebk:', sortWith(deWords, 'de-u-co-phonebk'));  // ü=ue

// Финский: v и w эквивалентны
const fiWords = ['vaara', 'waara', 'vesi', 'wesi'];
console.log('\nФинские слова (v/w):');
console.log('  fi (финский):  ', sortWith(fiWords, 'fi'));
console.log('  en (английский):', sortWith(fiWords, 'en'));

console.log();


// ─────────────────────────────────────────────
// 4. Numeric collation (натуральная сортировка)
// ─────────────────────────────────────────────

console.log('=== Numeric collation ===\n');

const numericFiles = ['file1', 'file10', 'file2', 'file20', 'file3', 'file100'];
console.log('  naive sort:    ', [...numericFiles].sort());
console.log('  numeric=false: ', sortWith(numericFiles, 'en', { numeric: false }));
console.log('  numeric=true:  ', sortWith(numericFiles, 'en', { numeric: true }));

const versionStrings = ['v1.0', 'v10.0', 'v2.0', 'v1.10', 'v1.2'];
console.log('\nВерсии (numeric=true):', sortWith(versionStrings, 'en', { numeric: true }));
console.log('Версии (naive):       ', [...versionStrings].sort());
console.log();


// ─────────────────────────────────────────────
// 5. caseFirst — буквы с заглавных или строчных
// ─────────────────────────────────────────────

console.log('=== caseFirst ===\n');

const mixedCase = ['Apple', 'apple', 'APPLE', 'Banana', 'banana'];
console.log('  caseFirst=undefined (по умолчанию):', sortWith(mixedCase, 'en'));
console.log('  caseFirst="upper":                 ', sortWith(mixedCase, 'en', { caseFirst: 'upper' }));
console.log('  caseFirst="lower":                 ', sortWith(mixedCase, 'en', { caseFirst: 'lower' }));
console.log();


// ─────────────────────────────────────────────
// 6. Collator.resolvedOptions() — что реально поддерживается
// ─────────────────────────────────────────────

console.log('=== resolvedOptions ===\n');

const locales = ['ru', 'en', 'de', 'sv', 'zh', 'ja', 'ar'];
for (const loc of locales) {
  try {
    const col = new Intl.Collator(loc);
    const opts = col.resolvedOptions();
    console.log(`  ${loc.padEnd(6)}: locale=${opts.locale}, collation=${opts.collation}`);
  } catch (e) {
    console.log(`  ${loc.padEnd(6)}: недоступен — ${e.message}`);
  }
}
console.log();


// ─────────────────────────────────────────────
// 7. Кэширование Collator (производительность)
// ─────────────────────────────────────────────

console.log('=== Производительность: кэшировать Collator ===\n');

const words = Array.from({ length: 1000 }, (_, i) => `word_${i}`);

// Плохо: создавать Collator на каждое сравнение
console.time('без кэша (1000 слов)');
[...words].sort((a, b) => new Intl.Collator('ru').compare(a, b));
console.timeEnd('без кэша (1000 слов)');

// Хорошо: создать один раз
console.time('с кэшем (1000 слов)');
const cachedCollator = new Intl.Collator('ru');
[...words].sort(cachedCollator.compare);
console.timeEnd('с кэшем (1000 слов)');

// Ещё лучше: localeCompare тоже кэшируется внутренне в V8
console.time('localeCompare (1000 слов)');
[...words].sort((a, b) => a.localeCompare(b, 'ru'));
console.timeEnd('localeCompare (1000 слов)');
console.log();


// ─────────────────────────────────────────────
// 8. Сравнение строк для поиска (без сортировки)
// ─────────────────────────────────────────────

console.log('=== Поиск без учёта регистра/диакритики ===\n');

const texts = [
  'Кафе «Уют»',
  'CAFÉ DE PARIS',
  'cafe central',
  'Café Müller',
  'кофейня',
];

const query = 'cafe';
const baseCollator = new Intl.Collator('und', { sensitivity: 'base', usage: 'search' });

// Простой поиск через localeCompare с sensitivity=base
function fuzzyIncludes(text, query, locale = 'und') {
  const col = new Intl.Collator(locale, { sensitivity: 'base', usage: 'search' });
  // Для поиска подстроки нужно скользящее окно — это упрощение:
  if (text.length < query.length) return false;
  for (let i = 0; i <= text.length - query.length; i++) {
    const sub = text.slice(i, i + query.length);
    if (col.compare(sub, query) === 0) return true;
  }
  return false;
}

console.log(`Поиск '${query}' в текстах (sensitivity=base):`);
for (const text of texts) {
  const found = fuzzyIncludes(text, query);
  console.log(`  ${found ? '✓' : '✗'} ${JSON.stringify(text)}`);
}
