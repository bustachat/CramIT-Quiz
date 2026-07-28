// One-off script: reorders subjects/mathematics-standard-2.json's
// studyNotes array alphabetically by syllabus code (A1, A2, A4, F1, F4,
// F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5), per owner's request once
// all 16 topics were built. Sorts on the code parsed from each topic's
// title (e.g. "A1 — Formulae & Equations" -> letter "A", number 1).
// Run once: node scripts/archive/reorder_maths_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes) || data.studyNotes.length !== 16) {
  console.log('Expected exactly 16 studyNotes topics, found ' + (data.studyNotes || []).length + ' — aborting.');
  process.exit(1);
}

function parseCode(title) {
  const m = title.match(/^([A-Z]+)(\d+)/);
  if (!m) throw new Error('Could not parse a syllabus code from title: ' + title);
  return { letter: m[1], number: parseInt(m[2], 10) };
}

const before = data.studyNotes.map(t => t.title);

data.studyNotes.sort((a, b) => {
  const ca = parseCode(a.title), cb = parseCode(b.title);
  if (ca.letter !== cb.letter) return ca.letter.localeCompare(cb.letter);
  return ca.number - cb.number;
});

const after = data.studyNotes.map(t => t.title);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('Before:\n  ' + before.join('\n  '));
console.log('After:\n  ' + after.join('\n  '));
