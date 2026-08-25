#!/usr/bin/env node
/**
 * CramIT Content Agent (Stage 9, Phase 1 — autonomy Level 1: PR only)
 * -------------------------------------------------------------------
 * Nightly job (GitHub Actions: .github/workflows/content-agent.yml):
 *
 *   1. DISCOVER  — search NESA for newly published HSC exam papers
 *                  (claude-sonnet-5 + web search — cheap).
 *   2. TRIAGE    — read each new paper's PDF and write a structured
 *                  fit-assessment report to docs/paper-reports/
 *                  (claude-sonnet-5 — reading + classification).
 *   3. GENERATE  — ONLY for the subjects the app already supports:
 *                  extract MC questions in the app's exact schema and
 *                  append them to subjects/{id}.json
 *                  (claude-opus-4-8 — question quality is critical).
 *   4. VALIDATE  — run scripts/validate_subjects.cjs; if it fails, the
 *                  subject file is restored and nothing is committed.
 *
 * The agent NEVER pushes to main. The workflow commits its output to an
 * agent/content-* branch and opens a PR for human review.
 *
 * New subjects are NEVER created here — each needs hand-written filter
 * logic and UI in index.html (see CLAUDE.md §10 "Adding a new subject").
 * For roadmap subjects the triage report IS the deliverable: a briefing
 * for the human porting session.
 *
 * Diagram-dependent questions are skipped (the agent cannot crop PDFs —
 * that is the Python tooling in scripts/) and listed in the run summary
 * so a human can follow up.
 *
 * Local usage:
 *   node agent.js --selftest     # offline checks, no API calls
 *   ANTHROPIC_API_KEY=... node agent.js
 */

import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import https from 'https';
import os from 'os';
import { execSync } from 'child_process';

// ── CONFIG ──────────────────────────────────────────────────────────

const SUBJECTS_DIR = './subjects';
const REPORTS_DIR = './docs/paper-reports';
const STATE_FILE = './agent-state.json';
// Workflow points this at a temp file and uses it as the PR body.
const SUMMARY_FILE = process.env.AGENT_SUMMARY_FILE || null;
const MAX_PAPERS_PER_RUN = 3; // keeps the first run (backlog) from ballooning

// Subjects the app supports today. Generation only ever targets these.
// `file` must match subjects/{file}; `searchName` is what NESA calls it.
const SUPPORTED_SUBJECTS = {
  'mathematics-standard-2': { searchName: 'Mathematics Standard 2', file: 'mathematics-standard-2.json' },
  'health-movement-science': { searchName: 'Health and Movement Science', file: 'health-movement-science.json' },
  'multimedia':             { searchName: 'Industrial Technology', file: 'multimedia.json' },
  'vet-construction':       { searchName: 'Construction Examination', file: 'vet-construction.json' },
};

// Roadmap subjects (CLAUDE.md §7) — triage report only, never generation.
const ROADMAP_SUBJECTS = [
  'Mathematics Advanced', 'English Advanced', 'English Standard',
  'Biology', 'Chemistry', 'Physics',
  'Legal Studies', 'Business Studies', 'Economics',
];

// NOTE on prompt caching: deliberately NOT used here. Each prompt below is
// far under the minimum cacheable prefix (4096 tokens on Opus/Haiku tiers),
// so cache_control would silently do nothing — and a nightly run makes each
// call at most a handful of times anyway. Don't "fix" this by adding
// cache_control back; see ~/.claude/CLAUDE.md (minimum-prefix caveat).

const client = process.env.ANTHROPIC_API_KEY
  ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  : null;

// ── SMALL UTILITIES ─────────────────────────────────────────────────

function logUsage(label, usage = {}) {
  console.log(
    `[tokens] ${label}: in=${usage.input_tokens || 0} out=${usage.output_tokens || 0} ` +
    `cache_write=${usage.cache_creation_input_tokens || 0} ` +
    `cache_read=${usage.cache_read_input_tokens || 0}`
  );
}

function slugify(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function loadState() {
  if (!fs.existsSync(STATE_FILE)) return { processedPapers: [] };
  return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2) + '\n');
}

// Pull the first JSON array or object out of a model response —
// tolerates markdown fences and surrounding prose.
function extractJson(text) {
  const clean = text.replace(/```json|```/g, '').trim();
  const start = Math.min(
    ...['[', '{'].map(ch => { const i = clean.indexOf(ch); return i === -1 ? Infinity : i; })
  );
  if (!isFinite(start)) throw new Error('no JSON found in response');
  return JSON.parse(clean.slice(start).replace(/[^\]}]*$/, ''));
}

// Download a URL as a Buffer, following up to 3 redirects.
function downloadFile(url, redirectsLeft = 3) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        if (redirectsLeft <= 0) return reject(new Error('too many redirects'));
        return resolve(downloadFile(new URL(res.headers.location, url).href, redirectsLeft - 1));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode}`));
      }
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    }).on('error', reject);
  });
}

// Years already present in a supported subject's data — used to build the
// discovery skip list so we never re-process a paper we already cover.
function existingYears(subjectId) {
  const filepath = path.join(SUBJECTS_DIR, SUPPORTED_SUBJECTS[subjectId].file);
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  const years = new Set();
  for (const q of [...(data.mcQuestions || []), ...(data.writtenQuestions || [])]) {
    if (q.year) years.add(String(q.year));
  }
  return years;
}

// ── LOCAL QUESTION VALIDATION ───────────────────────────────────────
// Mirrors the invariants scripts/validate_subjects.cjs enforces, applied
// per-question BEFORE merging so one bad question doesn't poison the file.

function validateMC(q, allowed) {
  const errs = [];
  if (typeof q.q !== 'string' || !q.q.trim()) errs.push('missing/empty q');
  if (!Array.isArray(q.options) || q.options.length !== 4) errs.push('options must be array of 4');
  else if (q.options.some(o => typeof o !== 'string')) errs.push('non-string option');
  if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer > 3) errs.push(`answer out of range: ${q.answer}`);
  if (!Number.isInteger(q.year)) errs.push(`year must be an integer: ${q.year}`);
  if (typeof q.solution !== 'string' || !q.solution.trim()) errs.push('missing solution');
  if (q.image || q.optionImages) errs.push('agent questions must not reference images');
  if (allowed.categories.size > 0 && !allowed.categories.has(q.category)) {
    errs.push(`category "${q.category}" not in existing set`);
  }
  if (allowed.topics.size > 0 && !allowed.topics.has(q.topic)) {
    errs.push(`topic "${q.topic}" not in existing set`);
  }
  return errs;
}

// Allowed category/topic values, derived from the subject's existing data —
// the generator must not invent new filter values the UI doesn't know about.
function allowedValues(data) {
  const categories = new Set((data.mcQuestions || []).map(q => q.category).filter(Boolean));
  const topics = new Set((data.mcQuestions || []).map(q => q.topic).filter(Boolean));
  return { categories, topics };
}

// Append new questions to a subject file, deduping against existing question
// text. Returns { added, rejected } and writes the file only if added > 0.
function mergeIntoSubjectFile(filepath, newQuestions) {
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  const allowed = allowedValues(data);
  const seen = new Set((data.mcQuestions || []).map(q => q.q.replace(/\s+/g, ' ').trim().toLowerCase()));

  const added = [];
  const rejected = [];
  for (const q of newQuestions) {
    const errs = validateMC(q, allowed);
    const key = typeof q.q === 'string' ? q.q.replace(/\s+/g, ' ').trim().toLowerCase() : '';
    if (errs.length) { rejected.push({ q: q.q, errs }); continue; }
    if (seen.has(key)) { rejected.push({ q: q.q, errs: ['duplicate of existing question'] }); continue; }
    seen.add(key);
    added.push(q);
  }

  if (added.length > 0) {
    data.mcQuestions = [...(data.mcQuestions || []), ...added];
    fs.writeFileSync(filepath, JSON.stringify(data, null, 2) + '\n');
  }
  return { added, rejected };
}

// ── STEP 1: DISCOVERY (claude-sonnet-5 + web search) ────────────────

async function discoverNewPapers(state) {
  console.log('\n🔍 Scanning NESA for new exam papers...');

  const year = new Date().getFullYear();
  const skip = [...state.processedPapers];
  for (const id of Object.keys(SUPPORTED_SUBJECTS)) {
    for (const y of existingYears(id)) skip.push(`${id}-${y}`);
  }

  const supportedList = Object.entries(SUPPORTED_SUBJECTS)
    .map(([id, s]) => `- "${s.searchName}" → subjectId "${id}"`).join('\n');

  const response = await client.messages.create({
    // claude-sonnet-5: web search + JSON extraction — no need for Opus.
    model: 'claude-sonnet-5',
    max_tokens: 1024,
    system: 'You monitor the NESA NSW website (educationstandards.nsw.edu.au) for newly published HSC exam papers. Return ONLY valid JSON — no prose, no markdown fences. If nothing new is found, return [].',
    tools: [{ type: 'web_search_20250305', name: 'web_search' }],
    messages: [{
      role: 'user',
      content: `Search educationstandards.nsw.edu.au for HSC exam papers published for ${year - 1} or ${year}.

Subjects the app supports (set "subjectId" to the mapped id):
${supportedList}

Roadmap subjects (set "subjectId" to null):
${ROADMAP_SUBJECTS.map(s => `- ${s}`).join('\n')}

Already processed — skip these (key = slug-year): ${JSON.stringify(skip)}

Return a JSON array (max ${MAX_PAPERS_PER_RUN} items, newest first):
[{ "subject": "Mathematics Standard 2", "subjectId": "mathematics-standard-2", "year": 2026, "pdfUrl": "https://..." }]

pdfUrl must be a direct PDF link on educationstandards.nsw.edu.au. Return [] if nothing new.`,
    }],
  });

  logUsage('discover', response.usage);
  const text = response.content.filter(b => b.type === 'text').map(b => b.text).join('');
  try {
    const papers = extractJson(text);
    return Array.isArray(papers) ? papers.slice(0, MAX_PAPERS_PER_RUN) : [];
  } catch (e) {
    console.log('  ⚠️  Could not parse discovery response — skipping this run.', e.message);
    return [];
  }
}

// ── STEP 2: TRIAGE (claude-sonnet-5, reads the PDF) ─────────────────

async function triagePaper(paper, pdfBase64) {
  console.log(`  🔬 Triaging ${paper.subject} ${paper.year}...`);

  const content = [];
  if (pdfBase64) {
    content.push({ type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: pdfBase64 } });
  }
  content.push({
    type: 'text',
    text: `Analyse this HSC ${paper.subject} ${paper.year} exam paper for conversion into a quiz app that supports:
(a) 4-option multiple-choice questions, and
(b) short-answer written questions marked by AI against keywords + a model answer.
The app CANNOT present extended essays, and diagram/stimulus images require separate manual extraction.

Return ONLY this JSON object:
{
  "sections": [{ "name": "Section I", "questionCount": 15, "type": "multiple-choice | short-answer | extended-response" }],
  "mcCount": 0,
  "shortAnswerCount": 0,
  "extendedResponseCount": 0,
  "diagramDependentCount": 0,
  "themes": ["3-6 recurring topics/themes in this paper"],
  "fitSummary": "2-3 sentences: how well this paper maps onto the quiz format and what would be lost",
  "recommendation": "one of: generate-mc | generate-mc-and-written | written-only | poor-fit"
}`,
  });

  const response = await client.messages.create({
    // claude-sonnet-5: reading + classification — no need for Opus.
    model: 'claude-sonnet-5',
    max_tokens: 2048,
    system: 'You are an expert on NSW HSC exam structure. Return ONLY valid JSON — no prose, no markdown fences.',
    messages: [{ role: 'user', content }],
  });

  logUsage(`triage(${paper.subject} ${paper.year})`, response.usage);
  const text = response.content.filter(b => b.type === 'text').map(b => b.text).join('');
  return extractJson(text);
}

function writeTriageReport(paper, report) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
  const slug = slugify(paper.subject);
  const filepath = path.join(REPORTS_DIR, `${slug}-${paper.year}.md`);
  const supported = paper.subjectId && SUPPORTED_SUBJECTS[paper.subjectId];

  const lines = [
    `# Paper triage — ${paper.subject} ${paper.year}`,
    '',
    `> Generated by the Content Agent on ${new Date().toISOString().slice(0, 10)}.`,
    `> Source: ${paper.pdfUrl || 'n/a'}`,
    `> App support: ${supported ? `✅ supported (\`${paper.subjectId}\`)` : '⬜ roadmap subject — this report is the briefing for a future porting session'}`,
    '',
    '## Structure',
    '',
    '| Section | Questions | Type |',
    '|---|---|---|',
    ...(report.sections || []).map(s => `| ${s.name} | ${s.questionCount} | ${s.type} |`),
    '',
    `- Multiple-choice: **${report.mcCount ?? '?'}**`,
    `- Short-answer written: **${report.shortAnswerCount ?? '?'}**`,
    `- Extended response / essay: **${report.extendedResponseCount ?? '?'}**`,
    `- Diagram-dependent (need manual image extraction): **${report.diagramDependentCount ?? '?'}**`,
    '',
    '## Themes',
    '',
    ...(report.themes || []).map(t => `- ${t}`),
    '',
    '## Fit assessment',
    '',
    report.fitSummary || 'n/a',
    '',
    `**Recommendation:** \`${report.recommendation || 'n/a'}\``,
    '',
  ];
  fs.writeFileSync(filepath, lines.join('\n'));
  console.log(`  📋 Report: ${filepath}`);
  return filepath;
}

// ── STEP 3: GENERATION (claude-opus-4-8, supported subjects only) ───

async function generateQuestions(paper, pdfBase64) {
  console.log(`  ✍️  Generating questions for ${paper.subject} ${paper.year}...`);

  const filepath = path.join(SUBJECTS_DIR, SUPPORTED_SUBJECTS[paper.subjectId].file);
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  const allowed = allowedValues(data);

  // A real question from this subject as a few-shot example — keeps the
  // solution HTML and field usage exactly on-pattern.
  const example = (data.mcQuestions || []).find(q => !q.variant && !q.image && !q.optionImages)
    || (data.mcQuestions || [])[0];

  const fieldRules = [
    '- "year": ' + paper.year + ' (integer, not a string)',
    allowed.categories.size > 0
      ? `- "category": one of ${JSON.stringify([...allowed.categories].sort())} — never invent a new value`
      : null,
    allowed.topics.size > 0
      ? `- "topic": one of ${JSON.stringify([...allowed.topics].sort())} — never invent a new value`
      : null,
    '- "q": question text (plain text; simple HTML like <table> allowed if the question needs one)',
    '- "options": exactly 4 strings',
    '- "answer": 0-indexed integer into options',
    '- "solution": step-by-step HTML using <div class="step"><span class="step-number">1.</span> ...</div> blocks, matching the example',
  ].filter(Boolean).join('\n');

  const content = [
    { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: pdfBase64 } },
    {
      type: 'text',
      text: `Extract every multiple-choice question from this HSC ${paper.subject} ${paper.year} paper and convert each into the quiz app's schema.

Field rules:
${fieldRules}

Example of a real question in this subject (match its style and solution format exactly):
${JSON.stringify(example, null, 2)}

CRITICAL — skip any question that depends on a diagram, graph, photo, or visual stimulus. Text-only tables you can reconstruct as <table> HTML are fine. Never describe a diagram in words as a substitute.

Return ONLY this JSON object (no markdown fences):
{
  "questions": [ { ...schema above... } ],
  "skipped": [ { "questionNumber": "Q7", "reason": "requires network diagram" } ]
}`,
    },
  ];

  const response = await client.messages.create({
    // claude-opus-4-8: question quality is critical — keep Opus (CLAUDE.md §13).
    model: 'claude-opus-4-8',
    max_tokens: 8192, // a full year's MC set with HTML solutions is long
    system: 'You are an expert HSC question writer for NSW students. You convert real HSC exam questions into structured quiz JSON with precise NESA syllabus terminology and clear step-by-step solutions. Return ONLY valid JSON.',
    messages: [{ role: 'user', content }],
  });

  logUsage(`generate(${paper.subject} ${paper.year})`, response.usage);
  const text = response.content.filter(b => b.type === 'text').map(b => b.text).join('');
  const result = extractJson(text);
  return { questions: result.questions || [], skipped: result.skipped || [], filepath };
}

// ── STEP 4: VALIDATE (same script CI runs) ──────────────────────────

function runRepoValidator() {
  try {
    execSync('node scripts/validate_subjects.cjs', { stdio: 'pipe' });
    return true;
  } catch (e) {
    console.error('  ❌ validate_subjects.cjs failed:\n' + (e.stdout || '') + (e.stderr || ''));
    return false;
  }
}

// ── MAIN ────────────────────────────────────────────────────────────

async function run() {
  console.log('🤖 CramIT Content Agent starting...');
  console.log('   Time:', new Date().toLocaleString('en-AU', { timeZone: 'Australia/Sydney' }));

  if (!client) {
    console.error('❌ Missing ANTHROPIC_API_KEY environment variable');
    process.exit(1);
  }

  const state = loadState();
  const summary = []; // markdown lines → PR body

  const papers = await discoverNewPapers(state);
  console.log(`\n  Found ${papers.length} new paper(s)`);

  for (const paper of papers) {
    const key = `${slugify(paper.subject)}-${paper.year}`;
    if (state.processedPapers.includes(key)) continue;

    console.log(`\n📄 ${paper.subject} ${paper.year}`);
    let pdfBase64 = null;
    try {
      const buf = await downloadFile(paper.pdfUrl);
      if (buf.length > 25 * 1024 * 1024) throw new Error('PDF too large (>25MB)');
      pdfBase64 = buf.toString('base64');
    } catch (e) {
      console.log(`  ⚠️  PDF download failed (${e.message}) — skipping, will retry next run.`);
      continue; // not marked processed → retried tomorrow
    }

    try {
      // TRIAGE — always, for every paper.
      const report = await triagePaper(paper, pdfBase64);
      writeTriageReport(paper, report);
      summary.push(`### ${paper.subject} ${paper.year}`);
      summary.push(`Triage: ${report.mcCount} MC · ${report.shortAnswerCount} short-answer · ${report.extendedResponseCount} extended · ${report.diagramDependentCount} diagram-dependent → \`${report.recommendation}\``);
      summary.push(`Report: \`docs/paper-reports/${slugify(paper.subject)}-${paper.year}.md\``);

      // GENERATE — only supported subjects, only if triage says MC fits.
      const supported = paper.subjectId && SUPPORTED_SUBJECTS[paper.subjectId];
      const mcFits = ['generate-mc', 'generate-mc-and-written'].includes(report.recommendation);
      if (supported && mcFits) {
        const { questions, skipped, filepath } = await generateQuestions(paper, pdfBase64);
        const original = fs.readFileSync(filepath, 'utf8');
        const { added, rejected } = mergeIntoSubjectFile(filepath, questions);

        if (added.length > 0 && !runRepoValidator()) {
          fs.writeFileSync(filepath, original); // restore — never commit a broken file
          summary.push(`⚠️ **Generation rolled back** — merged file failed validate_subjects.cjs.`);
        } else {
          summary.push(`Added **${added.length}** MC questions to \`${SUPPORTED_SUBJECTS[paper.subjectId].file}\` (${rejected.length} rejected by local validation).`);
          rejected.forEach(r => summary.push(`  - rejected: "${String(r.q).slice(0, 80)}..." — ${r.errs.join('; ')}`));
          skipped.forEach(s => summary.push(`  - ⏭️ skipped ${s.questionNumber}: ${s.reason} *(needs manual diagram extraction — scripts/extract_maths_diagrams.py)*`));
        }
      } else if (supported) {
        summary.push(`No generation — triage recommendation was \`${report.recommendation}\`.`);
      } else {
        summary.push(`Roadmap subject — triage report only, no code changes.`);
      }

      state.processedPapers.push(key);
      saveState(state);
      summary.push('');
    } catch (e) {
      console.error(`  ❌ Error processing ${key}:`, e.message);
      summary.push(`### ${paper.subject} ${paper.year}\n❌ Failed: ${e.message} — will retry next run.\n`);
    }

    await new Promise(r => setTimeout(r, 2000)); // polite delay between papers
  }

  if (SUMMARY_FILE && summary.length > 0) {
    fs.writeFileSync(SUMMARY_FILE, [
      '## Content Agent nightly run',
      '',
      '⚠️ **Review every question before merging** — the Content Agent runs at autonomy Level 1 (PR only, per docs/agents-plan.md).',
      '',
      ...summary,
    ].join('\n'));
  }
  console.log(`\n✅ Done. ${papers.length} paper(s) examined.`);
}

// ── SELFTEST (offline — no API calls) ───────────────────────────────

function selftest() {
  console.log('Running offline selftest...');
  let failures = 0;
  const check = (name, cond) => {
    console.log(`  ${cond ? '✅' : '❌'} ${name}`);
    if (!cond) failures++;
  };

  // JSON extraction tolerates fences and prose
  check('extractJson: fenced array', JSON.stringify(extractJson('```json\n[1,2]\n```')) === '[1,2]');
  check('extractJson: object with prose', extractJson('Here you go: {"a":1}').a === 1);

  // Question validation
  const allowed = { categories: new Set(['F2']), topics: new Set() };
  const good = { year: 2026, category: 'F2', q: 'What is 2+2?', options: ['1', '2', '3', '4'], answer: 3, solution: '<div class="step">...</div>' };
  check('validateMC: accepts valid question', validateMC(good, allowed).length === 0);
  check('validateMC: rejects bad answer index', validateMC({ ...good, answer: 5 }, allowed).length > 0);
  check('validateMC: rejects invented category', validateMC({ ...good, category: 'Z9' }, allowed).length > 0);
  check('validateMC: rejects image refs', validateMC({ ...good, image: '/diagrams/x.jpg' }, allowed).length > 0);
  check('validateMC: rejects string year', validateMC({ ...good, year: '2026' }, allowed).length > 0);

  // Merge: appends valid, dedupes, rejects invalid — on a temp copy
  const tmp = path.join(os.tmpdir(), `cramit-selftest-${Date.now()}.json`);
  fs.writeFileSync(tmp, JSON.stringify({ id: 't', mcQuestions: [{ ...good, q: 'Existing question?' }] }));
  const r = mergeIntoSubjectFile(tmp, [good, good, { ...good, answer: 9 }]);
  check('merge: adds 1, dedupes 1, rejects 1', r.added.length === 1 && r.rejected.length === 2);
  const after = JSON.parse(fs.readFileSync(tmp, 'utf8'));
  check('merge: file now has 2 questions', after.mcQuestions.length === 2);
  fs.unlinkSync(tmp);

  // Repo validator still passes untouched
  check('validate_subjects.cjs passes on current repo', runRepoValidator());

  // Supported subject files all exist, parse, and have questions.
  // (Note: health-movement-science has no year fields — HMS is topic-based — so
  // existingYears() legitimately returns an empty set for it.)
  for (const s of Object.values(SUPPORTED_SUBJECTS)) {
    check(`subjects/${s.file} exists + has mcQuestions`, (() => {
      try {
        const d = JSON.parse(fs.readFileSync(path.join(SUBJECTS_DIR, s.file), 'utf8'));
        return (d.mcQuestions || []).length > 0;
      } catch { return false; }
    })());
  }

  console.log(failures === 0 ? '\nOK — all selftests passed.' : `\nFAILED — ${failures} selftest(s) failed.`);
  process.exit(failures === 0 ? 0 : 1);
}

if (process.argv.includes('--selftest')) {
  selftest();
} else {
  run().catch(e => { console.error('❌ Fatal:', e); process.exit(1); });
}
