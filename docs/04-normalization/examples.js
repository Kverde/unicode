#!/usr/bin/env node
/**
 * Статья 4 — Нормализация Unicode: NFD, NFC, NFKD, NFKC.
 * Примеры на Node.js.
 *
 * Запуск: node examples.js
 */

// ─────────────────────────────────────────────
// 1. Разные представления одного символа
// ─────────────────────────────────────────────

console.log('=== Представления символа "é" ===\n');

const precomposed = '\u00e9';          // LATIN SMALL LETTER E WITH ACUTE
const decomposed  = '\u0065\u0301';    // e + COMBINING ACUTE ACCENT

console.log(`precomposed: ${JSON.stringify(precomposed)}  length=${precomposed.length}`);
console.log(`decomposed:  ${JSON.stringify(decomposed)}   length=${decomposed.length}`);
console.log(`=== (raw):   ${precomposed === decomposed}`);
console.log(`NFC ===:     ${precomposed.normalize('NFC') === decomposed.normalize('NFC')}`);
console.log(`NFD ===:     ${precomposed.normalize('NFD') === decomposed.normalize('NFD')}`);
console.log();


// ─────────────────────────────────────────────
// 2. Все формы нормализации
// ─────────────────────────────────────────────

function showNormalization(s, label = '') {
  console.log(`Исходная ${label}: ${JSON.stringify(s)} (length=${s.length})`);
  for (const form of ['NFC', 'NFD', 'NFKC', 'NFKD']) {
    const result = s.normalize(form);
    const cps = [...result].map(c => `U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`);
    console.log(`  ${form}: ${JSON.stringify(result).padEnd(20)} len=${result.length}  [${cps.join(' ')}]`);
  }
  console.log();
}

console.log('=== Нормализация разных символов ===\n');
const testCases = [
  ['\u00e9',        'é precomposed'],
  ['\u0065\u0301',  'é decomposed'],
  ['\ufb01',        'ﬁ ligature'],
  ['\u00b2',        '² superscript'],
  ['\u00bd',        '½ fraction'],
  ['\uff46',        'ｆ fullwidth'],
  ['\u2460',        '① enclosed'],
  ['\u2122',        '™ trademark'],
];

for (const [s, label] of testCases) {
  showNormalization(s, label);
}


// ─────────────────────────────────────────────
// 3. Практика: сравнение строк через нормализацию
// ─────────────────────────────────────────────

console.log('=== Сравнение строк через нормализацию ===\n');

function normalizeEqual(a, b, form = 'NFC') {
  return a.normalize(form) === b.normalize(form);
}

const pairs = [
  ['café', 'caf\u0065\u0301', 'NFC vs NFD'],
  ['\ufb01lm', 'film', 'fi-лигатура vs f+i'],
  ['２０２４', '2024', 'fullwidth vs ASCII'],
  ['admin', '\u0430dmin', "Latin vs Cyrillic 'a'"],  // spoofing!
];

for (const [a, b, desc] of pairs) {
  console.log(`  ${desc}`);
  console.log(`    raw===: ${a === b},  NFC===: ${normalizeEqual(a, b, 'NFC')},  NFKC===: ${normalizeEqual(a, b, 'NFKC')}`);
}
console.log();


// ─────────────────────────────────────────────
// 4. NFKC и fullwidth символы
// ─────────────────────────────────────────────

console.log('=== NFKC и fullwidth символы ===\n');

const fullwidthExamples = [
  ['\uFF21', 'A', 'Fullwidth A'],
  ['\uFF10', '0', 'Fullwidth 0'],
  ['\uFF46', 'f', 'Fullwidth f'],
  ['\u3000', ' ', 'Ideographic Space'],
];

for (const [fw, normal, desc] of fullwidthExamples) {
  const nfkc = fw.normalize('NFKC');
  console.log(`  ${desc}: ${JSON.stringify(fw)} U+${fw.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')}  →NFKC→  ${JSON.stringify(nfkc)}  match=${nfkc === normal}`);
}

const username = '\uFF41\uFF44\uFF4D\uFF49\uFF4E';  // ａｄｍｉｎ
console.log(`\n  username = ${JSON.stringify(username)}`);
console.log(`  === 'admin': ${username === 'admin'}`);
console.log(`  NFKC === 'admin': ${username.normalize('NFKC') === 'admin'}`);
console.log();


// ─────────────────────────────────────────────
// 5. Нормализация в реальном сценарии: поиск
// ─────────────────────────────────────────────

console.log('=== Поиск с нормализацией ===\n');

const corpus = [
  'café au lait',
  'résumé',
  'naïve',
  'Ångström',
  'El Niño',
];

function normalizedSearch(query, texts, form = 'NFC') {
  const normalizedQuery = query.normalize(form).toLowerCase();
  return texts.filter(t => t.normalize(form).toLowerCase().includes(normalizedQuery));
}

// Запрос в NFD (decomposed), данные в NFC
const query1 = 'cafe\u0301';  // café в NFD
console.log(`Запрос: ${JSON.stringify(query1)} (NFD café)`);
console.log(`  Без нормализации:   ${JSON.stringify(normalizedSearch(query1, corpus.map(s => s.normalize('NFC')), null))}`);
// null — просто toLowerCase без normalize
const rawSearch = (q, texts) => texts.filter(t => t.toLowerCase().includes(q.toLowerCase()));
console.log(`  Без нормализации:   ${JSON.stringify(rawSearch(query1, corpus))}`);
console.log(`  С NFC-нормализацией: ${JSON.stringify(normalizedSearch(query1, corpus, 'NFC'))}`);
console.log();


// ─────────────────────────────────────────────
// 6. Combining marks: CCC и порядок
// ─────────────────────────────────────────────

console.log('=== Порядок combining marks в NFD ===\n');

// a + cedilla (CCC=202) + acute (CCC=230) — правильный порядок по CCC
const s1 = 'a\u0327\u0301';   // a + cedilla + acute
const s2 = 'a\u0301\u0327';   // a + acute + cedilla  (неправильный порядок)

console.log(`s1 (cedilla+acute): ${JSON.stringify(s1)}`);
console.log(`s2 (acute+cedilla): ${JSON.stringify(s2)}`);
console.log(`s1 === s2 (raw): ${s1 === s2}`);
console.log(`NFD: s1=${JSON.stringify(s1.normalize('NFD'))}  s2=${JSON.stringify(s2.normalize('NFD'))}`);
console.log(`NFD ===: ${s1.normalize('NFD') === s2.normalize('NFD')}`);
console.log();


// ─────────────────────────────────────────────
// 7. Emoji и нормализация
// ─────────────────────────────────────────────

console.log('=== Emoji и нормализация ===\n');

const emojiTests = [
  '🌍',        // простой emoji
  '👨‍👩‍👧',  // ZWJ sequence (family)
  '🇷🇺',       // региональные индикаторы (флаг)
  '👍🏾',       // emoji + modifier цвета кожи
];

for (const e of emojiTests) {
  const cps = [...e].map(c => `U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')}`);
  const nfc  = e.normalize('NFC');
  const nfkc = e.normalize('NFKC');
  console.log(`${e}  [${cps.join(' ')}]`);
  console.log(`  NFC===orig: ${nfc === e},  NFKC===orig: ${nfkc === e}`);
}
console.log();

console.log('Вывод: emoji не меняются при NFC/NFD/NFKC/NFKD (кроме вариационных селекторов)');
