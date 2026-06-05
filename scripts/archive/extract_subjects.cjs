/**
 * extract_subjects.js — one-shot migration script
 * Extracts question arrays from index.html and writes subjects/*.json
 * Run once: node extract_subjects.js
 */

const fs   = require('fs');
const path = require('path');
const vm   = require('vm');

const htmlPath  = path.join(__dirname, 'index.html');
const subjDir   = path.join(__dirname, 'subjects');
const allLines  = fs.readFileSync(htmlPath, 'utf8').split('\n');

function getLines(from1, to1) {
  // 1-indexed inclusive
  return allLines.slice(from1 - 1, to1).join('\n');
}

function stripDecl(code, varName) {
  // Remove  "const varName = "  prefix and trailing  ";"  or  ";\n"
  return code
    .replace(new RegExp(`^const ${varName}\\s*=\\s*`), '')
    .replace(/;\s*$/, '')
    .trim();
}

function evalBlock(code) {
  const ctx = { result: null };
  vm.runInNewContext(`result = (${code});`, ctx);
  return ctx.result;
}

// ── Extract each block ────────────────────────────────────────────────────────

console.log('Extracting mathsQuestions (lines 497–4199)…');
const mathsMC = evalBlock(stripDecl(getLines(497, 4199), 'mathsQuestions'));
console.log(`  → ${mathsMC.length} questions`);

console.log('Extracting mathsQuestionTips (lines 4206–4645)…');
const mathsTips = evalBlock(stripDecl(getLines(4206, 4645), 'mathsQuestionTips'));
console.log(`  → ${Object.keys(mathsTips).length} tips`);

console.log('Extracting mathsWrittenQuestions (lines 4650–6530)…');
const mathsWritten = evalBlock(stripDecl(getLines(4650, 6530), 'mathsWrittenQuestions'));
console.log(`  → ${mathsWritten.length} written questions`);

console.log('Extracting hmsMcQuestions (lines 6532–7116)…');
const hmsMC = evalBlock(stripDecl(getLines(6532, 7116), 'hmsMcQuestions'));
console.log(`  → ${hmsMC.length} questions`);

console.log('Extracting hmsWrittenQuestions (lines 7118–7357)…');
const hmsWritten = evalBlock(stripDecl(getLines(7118, 7357), 'hmsWrittenQuestions'));
console.log(`  → ${hmsWritten.length} written questions`);

console.log('Extracting vetMcQuestions (lines 7363–8046)…');
const vetMC = evalBlock(stripDecl(getLines(7363, 8046), 'vetMcQuestions'));
console.log(`  → ${vetMC.length} questions`);

console.log('Extracting vetWrittenQuestions (lines 8048–8266)…');
const vetWritten = evalBlock(stripDecl(getLines(8048, 8266), 'vetWrittenQuestions'));
console.log(`  → ${vetWritten.length} written questions`);

console.log('Extracting multimediaMcQuestions (lines 8268–8816)…');
const multimediaMC = evalBlock(stripDecl(getLines(8268, 8816), 'multimediaMcQuestions')
);
console.log(`  → ${multimediaMC.length} questions`);

console.log('Extracting multimediaWrittenQuestions (lines 8818–9223)…');
const multimediaWritten = evalBlock(stripDecl(getLines(8818, 9223), 'multimediaWrittenQuestions'));
console.log(`  → ${multimediaWritten.length} written questions`);

// ── Build JSON files ──────────────────────────────────────────────────────────

const subjects = [
  {
    filename: 'mathematics-standard-2.json',
    data: {
      id:              'mathematics-standard-2',
      name:            'Mathematics Standard 2',
      icon:            '📐',
      accentColor:     '#C17D3C',
      mcQuestions:     mathsMC,
      tips:            mathsTips,
      writtenQuestions: mathsWritten,
    },
  },
  {
    filename: 'pdhpe-hms.json',
    data: {
      id:              'pdhpe-hms',
      name:            'HMS — PDHPE Depth Study',
      icon:            '🏃',
      accentColor:     '#7B9E6B',
      mcQuestions:     hmsMC,
      writtenQuestions: hmsWritten,
    },
  },
  {
    filename: 'multimedia.json',
    data: {
      id:              'multimedia',
      name:            'Industrial Technology — Multimedia',
      icon:            '🎬',
      accentColor:     '#5B7FA6',
      mcQuestions:     multimediaMC,
      writtenQuestions: multimediaWritten,
    },
  },
  {
    filename: 'vet-construction.json',
    data: {
      id:              'vet-construction',
      name:            'VET Construction',
      icon:            '🔨',
      accentColor:     '#f7c46a',
      mcQuestions:     vetMC,
      writtenQuestions: vetWritten,
    },
  },
];

for (const { filename, data } of subjects) {
  const outPath = path.join(subjDir, filename);
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2), 'utf8');
  const mcCount  = data.mcQuestions?.length  ?? 0;
  const wrCount  = data.writtenQuestions?.length ?? 0;
  const fileSize = (fs.statSync(outPath).size / 1024).toFixed(1);
  console.log(`✓ Written ${filename}  (${mcCount} MC, ${wrCount} written, ${fileSize} KB)`);
}

// ── Update subjects/index.json ────────────────────────────────────────────────

const indexPath = path.join(subjDir, 'index.json');
const indexData = [
  { file: 'mathematics-standard-2.json', id: 'mathematics-standard-2', name: 'Mathematics Standard 2' },
  { file: 'pdhpe-hms.json',              id: 'pdhpe-hms',              name: 'HMS — PDHPE Depth Study' },
  { file: 'multimedia.json',             id: 'multimedia',             name: 'Industrial Technology — Multimedia' },
  { file: 'vet-construction.json',       id: 'vet-construction',       name: 'VET Construction' },
  { file: 'mathematics-advanced-2024.json', id: 'mathematics-advanced-2024', name: 'Mathematics Advanced' },
];
fs.writeFileSync(indexPath, JSON.stringify(indexData, null, 2), 'utf8');
console.log(`✓ Updated subjects/index.json`);

console.log('\nExtraction complete. Now update index.html to async-load from subjects/.');
