/**
 * migrate_index.cjs — one-shot index.html transformation
 * 1. Removes question data blocks (lines 492–9224)
 * 2. Inserts async subject-loading infrastructure
 * Run once: node migrate_index.cjs
 */

const fs   = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, 'index.html');
const lines    = fs.readFileSync(htmlPath, 'utf8').split('\n');

console.log(`Input: ${lines.length} lines`);

// Verify expected content at boundaries before touching anything
const line492  = lines[491]; // 0-indexed
const line9224 = lines[9223];

if (!line492.trim().startsWith('<script>')) {
  console.error(`ERROR: Line 492 expected to be <script>, got: ${JSON.stringify(line492)}`);
  process.exit(1);
}
if (line9224.trim() !== '') {
  // might be ]; or blank — tolerate
  console.warn(`WARN: Line 9224 is: ${JSON.stringify(line9224)} (expected blank)`);
}

// The new code that replaces lines 492-9224
const LOADER_CODE = `<script>
// ════════════════════════════════════════════════════════
//  SUBJECT DATA LOADING
//  All question data lives in subjects/*.json.
//  Loaded on demand when a subject is opened; cached in memory.
// ════════════════════════════════════════════════════════

const SUBJECT_ID_MAP = {
  maths:      'mathematics-standard-2',
  hms:        'pdhpe-hms',
  multimedia: 'multimedia',
  vet:        'vet-construction',
};

const subjectCache = {};

async function loadSubjectData(key) {
  if (subjectCache[key]) return subjectCache[key];
  const id = SUBJECT_ID_MAP[key];
  if (!id) return null;
  const res = await fetch('/subjects/' + id + '.json');
  if (!res.ok) throw new Error('Failed to load ' + id + '.json (HTTP ' + res.status + ')');
  const data = await res.json();
  subjectCache[key] = data;
  // Patch SUBJECTS config with values derived from loaded data
  const s = SUBJECTS[key];
  if (s) {
    if (!s.categories && data.mcQuestions) {
      const cats = [...new Set(data.mcQuestions.map(q => q.category).filter(Boolean))];
      s.categories = ['all', ...cats];
    }
    if (!s.topics && data.mcQuestions) {
      const t = ['all', ...new Set(data.mcQuestions.map(q => q.topic).filter(Boolean))];
      s.topics = t.slice(0, 12);
    }
  }
  return data;
}
`;

// Lines before <script> (0-indexed: 0 to 490 inclusive = first 491 lines)
const before = lines.slice(0, 491);
// Lines after the data block (0-indexed: 9224 onward = line 9225+ in 1-indexed)
const after  = lines.slice(9224);

const newContent = [...before, ...LOADER_CODE.split('\n'), ...after].join('\n');

// Write backup first
fs.writeFileSync(htmlPath + '.bak', lines.join('\n'), 'utf8');
console.log(`Backup written to index.html.bak`);

fs.writeFileSync(htmlPath, newContent, 'utf8');
const newLineCount = newContent.split('\n').length;
console.log(`Done. ${lines.length} → ${newLineCount} lines (removed ${lines.length - newLineCount} lines of question data)`);
