#!/usr/bin/env node
/**
 * HSC Quiz AI Agent
 * -----------------
 * Monitors NESA for new exam papers, reads them with Claude,
 * generates quiz questions, and drops new subject JSON files
 * into your subjects/ folder automatically.
 *
 * Setup:
 *   npm install @anthropic-ai/sdk node-fetch cheerio
 *   export ANTHROPIC_API_KEY="your-key-here"
 *   node agent.js
 *
 * Run automatically: add to cron or GitHub Actions (see README)
 */

import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import https from 'https';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ── CONFIG ──────────────────────────────────────────────────────────
const SUBJECTS_DIR = './subjects';
const STATE_FILE   = './agent-state.json';
const NESA_BASE    = 'https://educationstandards.nsw.edu.au';

// Subject icons & accent colours - agent picks from these
const SUBJECT_STYLES = {
  'mathematics': { icon: '📐', color: '#7c6af7' },
  'english':     { icon: '📖', color: '#f76a8a' },
  'chemistry':   { icon: '⚗️',  color: '#6af7c8' },
  'biology':     { icon: '🧬', color: '#6af7c8' },
  'physics':     { icon: '⚡', color: '#f7c46a' },
  'history':     { icon: '🏛️',  color: '#f7a06a' },
  'geography':   { icon: '🌏', color: '#6af7a0' },
  'economics':   { icon: '📊', color: '#6aaff7' },
  'legal':       { icon: '⚖️',  color: '#c46af7' },
  'default':     { icon: '📚', color: '#7c6af7' }
};
// ────────────────────────────────────────────────────────────────────

// Load saved state (which papers we've already processed)
function loadState() {
  if (!fs.existsSync(STATE_FILE)) return { processed: [] };
  return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Download a file from a URL as a Buffer
function downloadFile(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    }).on('error', reject);
  });
}

// Get the style for a subject name
function getStyle(subjectName) {
  const lower = subjectName.toLowerCase();
  for (const [key, style] of Object.entries(SUBJECT_STYLES)) {
    if (lower.includes(key)) return style;
  }
  return SUBJECT_STYLES.default;
}

// Generate a safe filename from a subject name + year
function makeFilename(subjectName, year) {
  return subjectName.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') + '-' + year + '.json';
}

// ── CACHED SYSTEM PROMPTS ────────────────────────────────────────────────────
// Prompt caching: static system prompts are sent with cache_control so the
// second+ call within the 5-min TTL pays only 0.1x the input token price.
// Cache write = 1.25x; cache read = 0.1x. Saves ~80% cost on repeat runs.

const SYSTEM_DISCOVER = `You are an agent that monitors the NESA NSW education website for new HSC exam papers.
Return ONLY valid JSON arrays — no prose, no markdown fences. If you cannot find new papers, return [].`;

const SYSTEM_GENERATE = `You are an expert HSC question writer for NSW students.
You generate high-quality multiple-choice quiz questions directly from HSC exam papers.
Follow NESA syllabus terminology precisely. Return ONLY valid JSON arrays — no prose, no markdown fences.`;

// Token usage logger — prints to GitHub Actions log for cost tracking.
function logUsage(label, usage = {}) {
  console.log(
    `[tokens] ${label}: in=${usage.input_tokens || 0} out=${usage.output_tokens || 0} ` +
    `cache_write=${usage.cache_creation_input_tokens || 0} ` +
    `cache_read=${usage.cache_read_input_tokens || 0}`
  );
}

/**
 * Step 1: Ask Claude to scan NESA and find new exam papers.
 * Uses claude-sonnet-4-6 — web search + simple JSON output, no need for Opus.
 */
async function discoverNewPapers(state) {
  console.log('\n🔍 Scanning NESA for new exam papers...');

  const response = await client.messages.create({
    // claude-sonnet-4-6: sufficient for web search + JSON extraction (3x cheaper than Opus)
    model:      'claude-sonnet-4-6',
    max_tokens: 1024,
    // Cache the static system prompt — identical on every nightly run.
    system: [{ type: 'text', text: SYSTEM_DISCOVER, cache_control: { type: 'ephemeral' } }],
    tools: [{ type: 'web_search_20250305', name: 'web_search' }],
    messages: [{
      role: 'user',
      content: `Search the NESA NSW website (educationstandards.nsw.edu.au) for HSC exam papers
      that have been published recently (2023 or 2024).

      Find the direct PDF download URLs for exam papers.
      Already processed papers (skip these): ${JSON.stringify(state.processed)}

      Return a JSON array of objects like:
      [{ "subject": "Mathematics Advanced", "year": "2024", "pdfUrl": "https://..." }]

      Return ONLY the JSON array, nothing else. If no new papers found, return [].`
    }],
    betas: ['prompt-caching-2024-07-31'],
  });

  logUsage('discoverNewPapers', response.usage);

  // Extract text from response (may have tool_use blocks)
  const text = response.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('');

  try {
    const clean = text.replace(/```json|```/g, '').trim();
    const match = clean.match(/\[[\s\S]*\]/);
    if (!match) return [];
    return JSON.parse(match[0]);
  } catch {
    console.log('  Could not parse paper list, skipping this run.');
    return [];
  }
}

/**
 * Step 2: For a given paper, download the PDF and ask Claude to
 * extract questions and generate quiz items with explanations.
 * Uses claude-opus-4-5 — question quality is critical here.
 */
async function generateQuizFromPaper(paper) {
  console.log(`\n📄 Processing: ${paper.subject} ${paper.year}`);

  let pdfBase64 = null;
  if (paper.pdfUrl) {
    try {
      console.log('  Downloading PDF...');
      const buf = await downloadFile(paper.pdfUrl);
      pdfBase64 = buf.toString('base64');
    } catch (e) {
      console.log('  Could not download PDF, using web search fallback...');
    }
  }

  // Build the message content
  const content = [];
  if (pdfBase64) {
    content.push({
      type: 'document',
      source: { type: 'base64', media_type: 'application/pdf', data: pdfBase64 }
    });
  }
  content.push({
    type: 'text',
    text: `${pdfBase64 ? 'From this HSC exam paper PDF' : 'Based on your knowledge of past HSC ' + paper.subject + ' ' + paper.year + ' exams'},
    generate 10 multiple-choice quiz questions for HSC students.

    Rules:
    - Each question must be directly relevant to the HSC ${paper.subject} syllabus
    - 4 options per question (A, B, C, D)
    - Only one correct answer
    - Include a clear explanation of why the correct answer is right
    - Vary difficulty (mix of straightforward and challenging questions)

    Return ONLY a valid JSON array (no markdown, no preamble):
    [
      {
        "year": "HSC ${paper.year}",
        "text": "Question text here?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct": 0,
        "explanation": "Clear explanation of why A is correct..."
      }
    ]`
  });

  const response = await client.messages.create({
    // claude-opus-4-5: keep for question generation — quality matters here.
    model:      'claude-opus-4-5',
    max_tokens: 4000,
    // Cache the static system prompt — identical for every subject/year.
    system: [{ type: 'text', text: SYSTEM_GENERATE, cache_control: { type: 'ephemeral' } }],
    messages: [{ role: 'user', content }],
    betas: ['prompt-caching-2024-07-31'],
  });

  logUsage(`generateQuizFromPaper(${paper.subject} ${paper.year})`, response.usage);

  const text = response.content.filter(b => b.type === 'text').map(b => b.text).join('');

  try {
    const clean = text.replace(/```json|```/g, '').trim();
    const match = clean.match(/\[[\s\S]*\]/);
    if (!match) throw new Error('No JSON array found');
    const questions = JSON.parse(match[0]);
    console.log(`  ✅ Generated ${questions.length} questions`);
    return questions;
  } catch (e) {
    console.log('  ⚠️  Could not parse questions:', e.message);
    return null;
  }
}

/**
 * Step 3: Write the subject JSON file and update the index.
 */
function writeSubjectFile(paper, questions) {
  const style = getStyle(paper.subject);
  const filename = makeFilename(paper.subject, paper.year);

  const subjectData = {
    id: filename.replace('.json', ''),
    name: paper.subject,
    icon: style.icon,
    accentColor: style.color,
    isNew: true,
    year: paper.year,
    questions
  };

  // Write subject file
  const filepath = path.join(SUBJECTS_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(subjectData, null, 2));
  console.log(`  💾 Saved: subjects/${filename}`);

  // Update index.json
  const indexPath = path.join(SUBJECTS_DIR, 'index.json');
  let index = [];
  if (fs.existsSync(indexPath)) {
    index = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
  }

  // Add if not already in index
  if (!index.find(s => s.file === filename)) {
    index.unshift({ file: filename }); // newest first
    fs.writeFileSync(indexPath, JSON.stringify(index, null, 2));
    console.log(`  📋 Updated subjects/index.json`);
  }

  return filename;
}

/**
 * Main agent loop
 */
async function run() {
  console.log('🤖 HSC Quiz Agent starting...');
  console.log('   Time:', new Date().toLocaleString('en-AU', { timeZone: 'Australia/Sydney' }));

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('❌ Missing ANTHROPIC_API_KEY environment variable');
    process.exit(1);
  }

  const state = loadState();
  let newCount = 0;

  // Discover new papers
  const papers = await discoverNewPapers(state);
  console.log(`\n  Found ${papers.length} new paper(s) to process`);

  for (const paper of papers) {
    const key = `${paper.subject}-${paper.year}`;
    if (state.processed.includes(key)) {
      console.log(`  ⏭️  Already processed: ${key}`);
      continue;
    }

    try {
      const questions = await generateQuizFromPaper(paper);
      if (questions && questions.length > 0) {
        writeSubjectFile(paper, questions);
        state.processed.push(key);
        saveState(state);
        newCount++;
      }
    } catch (e) {
      console.error(`  ❌ Error processing ${key}:`, e.message);
    }

    // Polite delay between papers
    await new Promise(r => setTimeout(r, 2000));
  }

  console.log(`\n✅ Done! ${newCount} new subject(s) added.`);

  if (newCount > 0) {
    console.log('\n📱 Next steps:');
    console.log('   1. git add subjects/ && git commit -m "Add new HSC subjects"');
    console.log('   2. git push  →  GitHub Pages auto-deploys the update');
    console.log('   3. Students will see new subjects next time they open the app');
  }
}

run().catch(console.error);
