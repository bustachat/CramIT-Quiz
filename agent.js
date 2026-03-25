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

/**
 * Step 1: Ask Claude to scan NESA and find new exam papers.
 * Claude uses web search to discover papers we haven't processed yet.
 */
async function discoverNewPapers(state) {
  console.log('\n🔍 Scanning NESA for new exam papers...');

  const response = await client.messages.create({
    model: 'claude-opus-4-5',
    max_tokens: 2000,
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
    }]
  });

  // Extract text from response (may have tool_use blocks)
  const text = response.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('');

  try {
    const clean = text.replace(/```json|```/g, '').trim();
    // Extract JSON array from the text
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
    model: 'claude-opus-4-5',
    max_tokens: 4000,
    messages: [{ role: 'user', content }]
  });

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
