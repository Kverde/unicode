#!/usr/bin/env node
/**
 * Статья 3 — Кодировки: UTF-8, UTF-16, UTF-32.
 * Практические примеры на Node.js.
 *
 * Запуск: node examples.js
 */

// ─────────────────────────────────────────────
// 1. Кодирование строки в байты (через Buffer)
// ─────────────────────────────────────────────

console.log('=== Кодирование в байты (Buffer) ===\n');

function showEncodings(str) {
  console.log(`Строка: ${JSON.stringify(str)}`);
  for (const enc of ['utf8', 'utf16le', 'latin1', 'ascii']) {
    try {
      const buf = Buffer.from(str, enc);
      const hex = buf.toString('hex').replace(/(.{2})/g, '$1 ').trim();
      console.log(`  ${enc.padEnd(10)}: [${hex}]  (${buf.length} байт)`);
    } catch (e) {
      console.log(`  ${enc.padEnd(10)}: ошибка — ${e.message}`);
    }
  }
  // UTF-8 через TextEncoder (Web API, доступен в Node >= 11)
  const encoded = new TextEncoder().encode(str);
  const hex8 = [...encoded].map(b => b.toString(16).padStart(2, '0')).join(' ');
  console.log(`  TextEncoder: [${hex8}]  (${encoded.length} байт)`);
  console.log();
}

for (const ch of ['A', 'А', 'ñ', '🌍', '中']) {
  showEncodings(ch);
}


// ─────────────────────────────────────────────
// 2. Суррогатные пары: внутреннее представление JS
// ─────────────────────────────────────────────

console.log('=== Суррогатные пары в JS (UTF-16) ===\n');

function analyzeSurrogatePairs(str) {
  console.log(`Строка: ${JSON.stringify(str)}`);
  console.log(`  str.length (UTF-16 units): ${str.length}`);
  console.log(`  [...str].length (code points): ${[...str].length}`);
  for (let i = 0; i < str.length; i++) {
    const unit = str.charCodeAt(i);
    const hex = `0x${unit.toString(16).toUpperCase().padStart(4, '0')}`;
    let kind = '';
    if (unit >= 0xD800 && unit <= 0xDBFF) kind = ' ← high surrogate';
    if (unit >= 0xDC00 && unit <= 0xDFFF) kind = ' ← low surrogate';
    console.log(`  unit[${i}]: ${hex}${kind}`);
  }
  console.log();
}

for (const s of ['AB', '🌍', '𝄞', '🇷🇺']) {
  analyzeSurrogatePairs(s);
}


// ─────────────────────────────────────────────
// 3. Ручное вычисление суррогатной пары
// ─────────────────────────────────────────────

console.log('=== Суррогатные пары: вычисление вручную ===\n');

function toSurrogatePair(cp) {
  if (cp < 0x10000) throw new Error('BMP символ, суррогат не нужен');
  const cpPrime = cp - 0x10000;
  const high = 0xD800 + (cpPrime >> 10);
  const low  = 0xDC00 + (cpPrime & 0x3FF);
  return { high, low };
}

function fromSurrogatePair(high, low) {
  return 0x10000 + ((high - 0xD800) << 10) + (low - 0xDC00);
}

const smpChars = [0x1F30D, 0x1D11E, 0x20000, 0x1F3B5];
for (const cp of smpChars) {
  const { high, low } = toSurrogatePair(cp);
  const restored = fromSurrogatePair(high, low);
  const char = String.fromCodePoint(cp);
  console.log(
    `U+${cp.toString(16).toUpperCase().padStart(5, '0')}  ${char}  →` +
    `  high=U+${high.toString(16).toUpperCase()}` +
    `  low=U+${low.toString(16).toUpperCase()}` +
    `  restore=U+${restored.toString(16).toUpperCase().padStart(5, '0')}`
  );
}
console.log();


// ─────────────────────────────────────────────
// 4. TextEncoder / TextDecoder (Web API)
// ─────────────────────────────────────────────

console.log('=== TextEncoder / TextDecoder ===\n');

const encoder = new TextEncoder();  // всегда UTF-8
const decoder = new TextDecoder('utf-8');

const text = 'Hello, Мир! 🌍';
const bytes = encoder.encode(text);
const decoded = decoder.decode(bytes);

console.log(`Оригинал:    ${text}`);
console.log(`Байты (hex): ${Buffer.from(bytes).toString('hex')}`);
console.log(`Декодировано: ${decoded}`);
console.log(`Совпадает:   ${text === decoded}`);
console.log();

// Декодирование из UTF-16LE (Windows-стиль)
const utf16buf = Buffer.from('Привет', 'utf16le');
const decoded16 = new TextDecoder('utf-16le').decode(utf16buf);
console.log(`UTF-16LE bytes: ${utf16buf.toString('hex')}`);
console.log(`Decoded: ${decoded16}`);
console.log();


// ─────────────────────────────────────────────
// 5. Длина строки: code units vs code points vs graphemes
// ─────────────────────────────────────────────

console.log('=== Длина строки на разных уровнях ===\n');

function stringMetrics(s) {
  const utf8Len = Buffer.from(s, 'utf8').length;
  const utf16Units = s.length;
  const codePoints = [...s].length;
  let graphemes = 0;
  if (typeof Intl.Segmenter !== 'undefined') {
    const seg = new Intl.Segmenter('und', { granularity: 'grapheme' });
    graphemes = [...seg.segment(s)].length;
  } else {
    graphemes = '(Intl.Segmenter unavailable)';
  }
  return { utf8Len, utf16Units, codePoints, graphemes };
}

const tests = ['Hello', 'Привет', '🌍🎉', 'é', 'e\u0301', '👨‍👩‍👧', '🇷🇺'];
console.log(`${'строка'.padEnd(20)} ${'utf8'.padEnd(8)} ${'utf16'.padEnd(8)} ${'cp'.padEnd(8)} graphemes`);
console.log('─'.repeat(60));
for (const s of tests) {
  const { utf8Len, utf16Units, codePoints, graphemes } = stringMetrics(s);
  const repr = JSON.stringify(s).padEnd(20);
  console.log(`${repr} ${String(utf8Len).padEnd(8)} ${String(utf16Units).padEnd(8)} ${String(codePoints).padEnd(8)} ${graphemes}`);
}
console.log();


// ─────────────────────────────────────────────
// 6. Обнаружение BOM
// ─────────────────────────────────────────────

console.log('=== Обнаружение BOM ===\n');

function detectBOM(buf) {
  if (buf[0] === 0xEF && buf[1] === 0xBB && buf[2] === 0xBF) return 'UTF-8 BOM';
  if (buf[0] === 0xFF && buf[1] === 0xFE && buf[2] === 0x00 && buf[3] === 0x00) return 'UTF-32 LE BOM';
  if (buf[0] === 0x00 && buf[1] === 0x00 && buf[2] === 0xFE && buf[3] === 0xFF) return 'UTF-32 BE BOM';
  if (buf[0] === 0xFF && buf[1] === 0xFE) return 'UTF-16 LE BOM';
  if (buf[0] === 0xFE && buf[1] === 0xFF) return 'UTF-16 BE BOM';
  return 'No BOM';
}

const bomTests = [
  ['UTF-8 BOM',   Buffer.from([0xEF, 0xBB, 0xBF, 0x48, 0x65])],
  ['UTF-16 LE',   Buffer.from([0xFF, 0xFE, 0x48, 0x00])],
  ['UTF-16 BE',   Buffer.from([0xFE, 0xFF, 0x00, 0x48])],
  ['No BOM',      Buffer.from([0x48, 0x65, 0x6C, 0x6C])],
];

for (const [desc, buf] of bomTests) {
  console.log(`  ${desc.padEnd(15)}: BOM=${buf.subarray(0, 4).toString('hex').padEnd(10)}  → ${detectBOM(buf)}`);
}
console.log();


// ─────────────────────────────────────────────
// 7. Ловушки при работе с суррогатами
// ─────────────────────────────────────────────

console.log('=== Ловушки и граничные случаи ===\n');

// Нельзя slice по index — можно разрезать суррогатную пару
const emoji = '🌍World';
console.log(`'${emoji}'.slice(0, 2) = ${JSON.stringify(emoji.slice(0, 2))}  (НЕПРАВИЛЬНО — разрезает суррогат)`);
console.log(`[...'${emoji}'].slice(0, 2).join('') = ${[...emoji].slice(0, 2).join('')}  (правильно — через code points)`);
console.log();

// Regex без флага u может неправильно матчить
const emojiStr = '🌍🎉🚀';
console.log(`/${emojiStr}/ без флага u:`);
console.log(`  /./g matches: ${emojiStr.match(/./g)?.length}  (считает UTF-16 units!)`);
console.log(`  /./gu matches: ${emojiStr.match(/./gu)?.length}  (с флагом u — code points)`);
console.log();

// String.prototype.at() vs []  (Node >= 16)
if (emoji.at) {
  console.log(`emoji.at(0) = ${emoji.at(0)}  (правильно)`);
  console.log(`emoji[0] = ${emoji[0]}  (неправильно для суррогатов)`);
}
