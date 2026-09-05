#!/usr/bin/env node
// scripts/validate_subjects.cjs
// Structural validation for subjects/*.json — checks the invariants
// index.html relies on. Run locally with `node scripts/validate_subjects.cjs`;
// also runs in CI on every push/PR (.github/workflows/validate.yml).
// Exits non-zero on any structural issue so CI fails loudly.

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SUBJECTS_DIR = path.join(ROOT, 'subjects');
const DIAGRAMS_DIR = path.join(ROOT, 'diagrams');

const issues = [];
const warn = (f, msg) => issues.push(`[${f}] ${msg}`);

const diagramFiles = new Set(fs.readdirSync(DIAGRAMS_DIR).filter(f => !f.startsWith('.')));

const indexPath = path.join(SUBJECTS_DIR, 'index.json');
if (fs.existsSync(indexPath)) {
  try {
    JSON.parse(fs.readFileSync(indexPath, 'utf8'));
  } catch (e) {
    warn('index.json', `invalid JSON: ${e.message}`);
  }
}

const files = fs.readdirSync(SUBJECTS_DIR).filter(f => f.endsWith('.json') && f !== 'index.json');
let totalMC = 0, totalWritten = 0, imgRefs = 0, missingImgs = 0;

for (const file of files) {
  let data;
  try {
    data = JSON.parse(fs.readFileSync(path.join(SUBJECTS_DIR, file), 'utf8'));
  } catch (e) {
    warn(file, `invalid JSON: ${e.message}`);
    continue;
  }

  const mc = data.mcQuestions || [];
  const written = data.writtenQuestions || [];
  totalMC += mc.length;
  totalWritten += written.length;

  const checkImg = (p, ctx) => {
    if (!p) return;
    imgRefs++;
    if (!p.startsWith('/diagrams/')) { warn(file, `${ctx}: image path not under /diagrams/: ${p}`); return; }
    const name = p.replace('/diagrams/', '');
    if (!diagramFiles.has(name)) { missingImgs++; warn(file, `${ctx}: missing image file ${name}`); }
  };

  mc.forEach((q, i) => {
    const ctx = `MC[${i}] (${q.year || '?'} ${q.category || q.topic || ''})`;
    if (typeof q.q !== 'string' || !q.q.trim()) warn(file, `${ctx}: missing/empty q`);
    if (!Array.isArray(q.options) || q.options.length !== 4) warn(file, `${ctx}: options not array of 4 (got ${q.options && q.options.length})`);
    if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer > 3) warn(file, `${ctx}: answer out of range: ${q.answer}`);
    if (q.options && q.options.some(o => typeof o !== 'string')) warn(file, `${ctx}: non-string option`);
    checkImg(q.image, ctx + ' image');
    if (q.optionImages) {
      if (!Array.isArray(q.optionImages) || q.optionImages.length !== 4) warn(file, `${ctx}: optionImages not array of 4`);
      else q.optionImages.forEach((p, j) => checkImg(p, `${ctx} optionImages[${j}]`));
    }
    if (q.q && (q.q.match(/<table/g) || []).length !== (q.q.match(/<\/table>/g) || []).length) {
      warn(file, `${ctx}: unbalanced <table> in q`);
    }
  });

  written.forEach((q, i) => {
    const ctx = `WR[${i}] (${q.year || '?'} ${q.category || q.topic || ''})`;
    if (typeof q.q !== 'string' || !q.q.trim()) warn(file, `${ctx}: missing/empty q`);
    if (!q.keywords?.length && !q.acceptableAnswers?.length) warn(file, `${ctx}: no scoring mechanism (keywords or acceptableAnswers)`);
    if (!q.answer && !q.modelAnswer && !q.sampleAnswer) warn(file, `${ctx}: no model answer (answer/modelAnswer/sampleAnswer)`);
    checkImg(q.image, ctx + ' image');
    if (q.q) {
      if ((q.q.match(/<table/g) || []).length !== (q.q.match(/<\/table>/g) || []).length) {
        warn(file, `${ctx}: unbalanced <table> in q`);
      }
      const imgs = q.q.match(/<img[^>]+src="([^"]+)"/g) || [];
      imgs.forEach(tag => { const m = tag.match(/src="([^"]+)"/); if (m) checkImg(m[1], ctx + ' inline img'); });
    }

    // ── Multi-part written questions (CLAUDE.md §10 rule 9) ──
    // A question carrying parts[] is answered and marked part by part. The
    // per-part marks are the only ones the student ever sees on such a
    // question, so they must total the question's own mark — which
    // check_written_key.cjs verifies against NESA. Without this assertion the
    // two could drift and nothing would report it.
    if (q.parts !== undefined) {
      if (!Array.isArray(q.parts) || q.parts.length < 2) {
        warn(file, `${ctx}: parts must be an array of 2 or more (got ${Array.isArray(q.parts) ? q.parts.length : typeof q.parts})`);
      } else {
        const seen = new Set();
        let sum = 0;
        q.parts.forEach((p, j) => {
          const pctx = `${ctx} parts[${j}]`;
          if (typeof p.label !== 'string' || !p.label.trim()) warn(file, `${pctx}: missing/empty label`);
          else if (seen.has(p.label)) warn(file, `${pctx}: duplicate label ${p.label}`);
          else seen.add(p.label);
          if (!Number.isInteger(p.marks) || p.marks < 1) warn(file, `${pctx}: marks must be a positive integer (got ${p.marks})`);
          else sum += p.marks;
          if (typeof p.q !== 'string' || !p.q.trim()) warn(file, `${pctx}: missing/empty q`);
          if (!p.keywords?.length && !p.acceptableAnswers?.length) warn(file, `${pctx}: no scoring mechanism (keywords or acceptableAnswers)`);
          if (!p.answer) warn(file, `${pctx}: no model answer`);
          [p.q, p.intro].forEach(html => {
            if (!html) return;
            const imgs = html.match(/<img[^>]+src="([^"]+)"/g) || [];
            imgs.forEach(tag => { const m = tag.match(/src="([^"]+)"/); if (m) checkImg(m[1], `${pctx} inline img`); });
          });
        });
        const qMarks = q.marks || q.maxMark || q.totalMarks || 0;
        if (sum !== qMarks) warn(file, `${ctx}: parts marks total ${sum} but question is ${qMarks}`);
      }
    }
    if (q.stem !== undefined && !q.parts) warn(file, `${ctx}: has stem but no parts[]`);
  });
}

console.log(`Subjects: ${files.join(', ')}`);
console.log(`Totals: MC=${totalMC} Written=${totalWritten} imageRefs=${imgRefs} missingImages=${missingImgs}`);
console.log(`Issues: ${issues.length}`);
issues.forEach(i => console.log('  ' + i));

if (issues.length > 0) {
  console.error(`\nFAILED — ${issues.length} structural issue(s) found.`);
  process.exit(1);
}
console.log('\nOK — all subject JSON files pass structural validation.');
