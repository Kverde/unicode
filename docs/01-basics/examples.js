#!/usr/bin/env node
/**
 * Статья 1 — Основы Unicode: кодовые точки, плоскости, блоки.
 * Примеры на Node.js.
 *
 * Node.js имеет встроенную поддержку Unicode через:
 *   - String методы: codePointAt(), fromCodePoint(), normalize()
 *   - Intl API (locale-sensitive операции)
 *
 * Запуск: node examples.js
 */

// ─────────────────────────────────────────────
// 1. Кодовые точки строки
// ─────────────────────────────────────────────

function codePoints(str) {
  // Spread разбивает строку по code points (не по UTF-16 единицам)
  return [...str].map(ch => ({
    char: ch,
    codePoint: ch.codePointAt(0),
    hex: `U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`,
  }));
}

console.log('=== Кодовые точки строки ===\n');
const testStrings = ['Hello', 'Привет', '🌍🎉', 'A𝄞B'];
for (const s of testStrings) {
  console.log(`"${s}" (length=${s.length}, codePoints=${[...s].length}):`);
  for (const {char, hex} of codePoints(s)) {
    console.log(`  ${hex}  ${JSON.stringify(char)}`);
  }
  console.log();
}


// ─────────────────────────────────────────────
// 2. Ловушка: length строки в JS — это UTF-16 единицы, не code points
// ─────────────────────────────────────────────

console.log('=== Ловушка: длина строки в JS ===\n');
const examples = ['A', 'А', '🌍', '𠀀', 'Hello 🌍'];
for (const s of examples) {
  const utf16Units = s.length;           // UTF-16 code units
  const codePointCount = [...s].length;  // реальные code points
  console.log(`${JSON.stringify(s).padEnd(20)} length=${utf16Units}, codePoints=${codePointCount}`);
}
console.log();


// ─────────────────────────────────────────────
// 3. Создание символа по кодовой точке
// ─────────────────────────────────────────────

console.log('=== String.fromCodePoint ===\n');
const cps = [0x0041, 0x0410, 0x1F30D, 0x1D11E];  // A, А, 🌍, 𝄞
for (const cp of cps) {
  const ch = String.fromCodePoint(cp);
  console.log(`U+${cp.toString(16).toUpperCase().padStart(5, '0')}  ${ch}`);
}
console.log();


// ─────────────────────────────────────────────
// 4. Определение плоскости символа
// ─────────────────────────────────────────────

const PLANE_NAMES = {
  0:  'BMP  (Basic Multilingual Plane)',
  1:  'SMP  (Supplementary Multilingual Plane)',
  2:  'SIP  (Supplementary Ideographic Plane)',
  3:  'TIP  (Tertiary Ideographic Plane)',
  14: 'SSP  (Supplementary Special-purpose Plane)',
  15: 'SPUA-A',
  16: 'SPUA-B',
};

function getPlane(ch) {
  const cp = ch.codePointAt(0);
  const planeNum = cp >> 16;
  return { planeNum, planeName: PLANE_NAMES[planeNum] ?? `Plane ${planeNum}` };
}

console.log('=== Плоскости символов ===\n');
const planeTests = [
  ['A',      'Latin A'],
  ['中',      'CJK иероглиф'],
  ['🌍',     'Emoji'],
  ['\u{10450}', 'Deseret (SMP)'],
  ['\u{20000}', 'CJK Ext-B (SIP)'],
];
for (const [ch, desc] of planeTests) {
  const cp = ch.codePointAt(0);
  const { planeNum, planeName } = getPlane(ch);
  console.log(`U+${cp.toString(16).toUpperCase().padStart(5, '0')}  ${desc.padEnd(25)} → Plane ${planeNum}: ${planeName}`);
}
console.log();


// ─────────────────────────────────────────────
// 5. Проверка суррогатных пар (UTF-16 внутри JS строк)
// ─────────────────────────────────────────────

console.log('=== Суррогатные пары в UTF-16 (внутреннее представление JS) ===\n');
const emoji = '🌍';
const highSurrogate = emoji.charCodeAt(0);  // U+D83C
const lowSurrogate  = emoji.charCodeAt(1);  // U+DF0D
console.log(`'🌍' в UTF-16:`);
console.log(`  High surrogate: 0x${highSurrogate.toString(16).toUpperCase()}  (U+D800..U+DBFF)`);
console.log(`  Low surrogate:  0x${lowSurrogate.toString(16).toUpperCase()}   (U+DC00..U+DFFF)`);

// Вычислить code point из суррогатной пары вручную:
const cp = 0x10000 + (highSurrogate - 0xD800) * 0x400 + (lowSurrogate - 0xDC00);
console.log(`  Кодовая точка: U+${cp.toString(16).toUpperCase()}`);
console.log(`  Проверка: ${String.fromCodePoint(cp)}`);
console.log();


// ─────────────────────────────────────────────
// 6. Intl.getCanonicalLocales и версия ICU
// ─────────────────────────────────────────────

console.log('=== Node.js / ICU info ===\n');
console.log(`Node.js version: ${process.version}`);
// Intl.DateTimeFormat().resolvedOptions() даёт locale info
const dtf = new Intl.DateTimeFormat('ru-RU', { dateStyle: 'full' });
console.log(`Intl locale:     ${dtf.resolvedOptions().locale}`);
// Проверить поддержку расширенного ICU:
try {
  const col = new Intl.Collator('zh-u-co-pinyin');
  console.log(`Chinese pinyin collation: ${col.resolvedOptions().collation}`);
} catch (e) {
  console.log(`Pinyin collation: не поддерживается (нужен full-icu)`);
}
console.log();


// ─────────────────────────────────────────────
// 7. Итерация по графемным кластерам (Node >= 16, Intl.Segmenter)
// ─────────────────────────────────────────────

console.log('=== Графемные кластеры (Intl.Segmenter) ===\n');
if (typeof Intl.Segmenter !== 'undefined') {
  const segmenter = new Intl.Segmenter('und', { granularity: 'grapheme' });
  const testStr = 'e\u0301\u0308';  // e + combining acute + combining diaeresis
  const segments = [...segmenter.segment(testStr)];
  console.log(`Строка: ${JSON.stringify(testStr)}  (length=${testStr.length}, codePoints=${[...testStr].length})`);
  console.log(`Графемные кластеры: ${segments.length}`);
  for (const seg of segments) {
    console.log(`  ${JSON.stringify(seg.segment)}`);
  }

  // Флаг государства (двойной эмодзи)
  const flag = '🇷🇺';
  const flagSegs = [...segmenter.segment(flag)];
  console.log(`\n'${flag}' — length=${flag.length}, codePoints=${[...flag].length}, graphemes=${flagSegs.length}`);
} else {
  console.log('Intl.Segmenter недоступен (нужен Node.js >= 16)');
}
