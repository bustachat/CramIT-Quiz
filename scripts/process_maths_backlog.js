#!/usr/bin/env node
/**
 * CramIT — Maths Standard 2 Image Backlog Processor
 * ==================================================
 * One-off script to process the 6 existing HSC Maths Standard 2 exam papers
 * (2020–2025). For each paper it:
 *
 *   1. Opens the zip-disguised-as-PDF that contains pre-rendered JPEGs + text
 *   2. Reads the manifest.json to understand page structure
 *   3. Sends each page image + its text to Claude Vision to identify which
 *      questions contain diagrams and what crop region covers them
 *   4. Crops each diagram from the full-page JPEG (using sharp)
 *   5. Uploads the cropped diagram to Supabase Storage (bucket: exam-images)
 *   6. Returns a manifest of { year, question, imageUrl } for every diagram found
 *
 * Cost estimate: ~$0.003 per page × 256 pages total ≈ $0.77
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-... SUPABASE_SERVICE_KEY=eyJ... node process_maths_backlog.js
 *
 * Optional env vars:
 *   DRY_RUN=1          — skip uploads, just print what would be uploaded
 *   START_YEAR=2023    — process only papers from this year onwards
 *   PAGES_PER_BATCH=5  — how many pages to send to Claude at once (default 3)
 */

'use strict';

const fs    = require('fs');
const path  = require('path');
const AdmZip = require('adm-zip');
const Anthropic = require('@anthropic-ai/sdk');
const { createClient } = require('@supabase/supabase-js');

// ─── Config ────────────────────────────────────────────────────────────────────
const SUPABASE_URL      = 'https://ohqtefjawaphtsebnaxg.supabase.co';
const SUPABASE_KEY      = process.env.SUPABASE_SERVICE_KEY; // service role key needed for storage writes
const ANTHROPIC_KEY     = process.env.ANTHROPIC_API_KEY;
const DRY_RUN           = !!process.env.DRY_RUN;
const START_YEAR        = parseInt(process.env.START_YEAR || '2020', 10);
const PAGES_PER_BATCH   = parseInt(process.env.PAGES_PER_BATCH || '3', 10);
const STORAGE_BUCKET    = 'exam-images';
const SUBJECT_ID        = 'mathematics-standard-2';

// Papers in order — paths match what's in the GitHub repo
const PAPERS = [
  { year: 2020, file: path.join(__dirname, '2020hscmathematicsstandard2.pdf') },
  { year: 2021, file: path.join(__dirname, '2021hscmathematicsstandard2.pdf') },
  { year: 2022, file: path.join(__dirname, '2022hscmathsstd2.pdf') },
  { year: 2023, file: path.join(__dirname, '2023hscmathsstd2.pdf') },
  { year: 2024, file: path.join(__dirname, '2024hscmathsstd2.pdf') },
  { year: 2025, file: path.join(__dirname, '2025hscmathsstandard2.pdf') },
];

// ─── Helpers ────────────────────────────────────────────────────────────────────

function log(msg, ...args) {
  console.log(`[${new Date().toISOString()}] ${msg}`, ...args);
}

function requireEnv() {
  const missing = [];
  if (!ANTHROPIC_KEY) missing.push('ANTHROPIC_API_KEY');
  if (!SUPABASE_KEY && !DRY_RUN) missing.push('SUPABASE_SERVICE_KEY');
  if (missing.length) {
    console.error(`\nMissing required environment variables: ${missing.join(', ')}\n`);
    process.exit(1);
  }
}

/**
 * Load all files from the zip into memory.
 * Returns { manifest, pages: Map<pageNum, { imageBuffer, text }> }
 */
function loadPaper(filePath) {
  const zip = new AdmZip(filePath);
  const manifestEntry = zip.getEntry('manifest.json');
  if (!manifestEntry) throw new Error(`No manifest.json in ${filePath}`);
  const manifest = JSON.parse(manifestEntry.getData().toString('utf8'));

  const pages = new Map();
  for (const page of manifest.pages) {
    const imgEntry  = zip.getEntry(page.image.path);
    const txtEntry  = zip.getEntry(page.text.path);
    pages.set(page.page_number, {
      imageBuffer: imgEntry ? imgEntry.getData() : null,
      text: txtEntry ? txtEntry.getData().toString('utf8').replace(/\r/g, '') : '',
      meta: page,
    });
  }
  return { manifest, pages };
}

/**
 * Ask Claude Vision to analyse a batch of pages and identify diagram regions.
 *
 * Returns an array of:
 *   { pageNum, questionNum, diagramType, cropHint: { top, left, width, height } | null }
 *
 * cropHint values are *fractions* of the full page (0–1), so they scale to any
 * image resolution. Set to null if Claude thinks the whole page contains one
 * diagram.
 */
async function analysePages(anthropic, pagesBatch) {
  const contentBlocks = [];

  for (const { pageNum, imageBuffer, text } of pagesBatch) {
    // Page header text block
    contentBlocks.push({
      type: 'text',
      text: `\n--- PAGE ${pageNum} ---\nExtracted text:\n${text.substring(0, 800)}\n`,
    });
    // Page image
    contentBlocks.push({
      type: 'image',
      source: {
        type: 'base64',
        media_type: 'image/jpeg',
        data: imageBuffer.toString('base64'),
      },
    });
  }

  contentBlocks.push({
    type: 'text',
    text: `
You are analysing pages from an HSC Mathematics Standard 2 exam paper.

For EACH page above, identify any diagrams, graphs, charts, tables, or figures
that are part of a question (not just text or blank space).

Return a JSON array — one object per diagram found across ALL pages. If a page
has no diagram, do NOT include it. Format:

[
  {
    "pageNum": 6,
    "questionNum": 11,
    "diagramType": "line graph",
    "cropHint": {
      "top": 0.35,
      "left": 0.05,
      "width": 0.90,
      "height": 0.45
    }
  }
]

Rules:
- questionNum: the HSC question number shown on the page (integer)
- diagramType: brief description e.g. "bar chart", "network diagram", "triangle", "scatter plot"
- cropHint: fractional coordinates (0–1) of the JPEG that tightly bounds the diagram.
  top/left are the top-left corner. Exclude surrounding question text — just the visual.
  If the diagram fills the whole page return null.
- If one question has TWO diagrams (e.g. table + graph), return two objects with the same questionNum.
- Ignore "Do NOT write in this area" boxes and answer boxes. Only diagrams, charts, graphs, tables.
- Return ONLY valid JSON. No prose. No markdown code fences.
`,
  });

  const response = await anthropic.messages.create({
    model: 'claude-opus-4-5',
    max_tokens: 1024,
    messages: [{ role: 'user', content: contentBlocks }],
  });

  const raw = response.content.find(b => b.type === 'text')?.text ?? '[]';

  // Strip markdown fences if Claude adds them despite instructions
  const cleaned = raw.replace(/^```[a-z]*\n?/i, '').replace(/\n?```$/i, '').trim();

  try {
    return JSON.parse(cleaned);
  } catch (e) {
    log(`  ⚠ JSON parse error for batch, raw response: ${raw.substring(0, 200)}`);
    return [];
  }
}

/**
 * Crop a JPEG buffer using sharp.
 * cropHint values are fractions (0–1) of the image dimensions.
 */
async function cropImage(imageBuffer, cropHint, pageWidth, pageHeight) {
  const sharp = require('sharp');

  if (!cropHint) {
    // Return the original image resized to a reasonable width
    return sharp(imageBuffer)
      .resize({ width: 800, withoutEnlargement: true })
      .jpeg({ quality: 85 })
      .toBuffer();
  }

  const left   = Math.round(cropHint.left   * pageWidth);
  const top    = Math.round(cropHint.top    * pageHeight);
  const width  = Math.round(cropHint.width  * pageWidth);
  const height = Math.round(cropHint.height * pageHeight);

  // Add a small padding (2% of page width) so we don't clip right at the edge
  const pad = Math.round(0.02 * pageWidth);
  const safeLeft   = Math.max(0, left - pad);
  const safeTop    = Math.max(0, top - pad);
  const safeWidth  = Math.min(pageWidth  - safeLeft, width  + pad * 2);
  const safeHeight = Math.min(pageHeight - safeTop,  height + pad * 2);

  return sharp(imageBuffer)
    .extract({ left: safeLeft, top: safeTop, width: safeWidth, height: safeHeight })
    .resize({ width: 800, withoutEnlargement: true })
    .jpeg({ quality: 88 })
    .toBuffer();
}

/**
 * Upload a buffer to Supabase Storage.
 * Returns the public URL.
 */
async function uploadToSupabase(supabase, year, questionNum, diagramIndex, buffer) {
  const fileName = `${SUBJECT_ID}/${year}/q${questionNum}_d${diagramIndex}.jpg`;

  const { error } = await supabase.storage
    .from(STORAGE_BUCKET)
    .upload(fileName, buffer, {
      contentType: 'image/jpeg',
      upsert: true,          // idempotent — safe to re-run
    });

  if (error) throw new Error(`Storage upload failed: ${error.message}`);

  const { data } = supabase.storage
    .from(STORAGE_BUCKET)
    .getPublicUrl(fileName);

  return data.publicUrl;
}

// ─── Main ──────────────────────────────────────────────────────────────────────

async function processPaper(anthropic, supabase, paper) {
  log(`\n${'='.repeat(60)}`);
  log(`Processing ${paper.year} paper: ${path.basename(paper.file)}`);

  if (!fs.existsSync(paper.file)) {
    log(`  ✗ File not found: ${paper.file}`);
    return [];
  }

  const { manifest, pages } = loadPaper(paper.file);
  log(`  Loaded: ${manifest.num_pages} pages`);

  // Build batches of PAGES_PER_BATCH pages
  const pageNums = [...pages.keys()].sort((a, b) => a - b);
  const batches  = [];
  for (let i = 0; i < pageNums.length; i += PAGES_PER_BATCH) {
    batches.push(pageNums.slice(i, i + PAGES_PER_BATCH));
  }

  log(`  Sending ${batches.length} batches of ≤${PAGES_PER_BATCH} pages to Claude Vision...`);

  const allDiagrams = [];

  for (let bIdx = 0; bIdx < batches.length; bIdx++) {
    const batch = batches[bIdx];
    process.stdout.write(`  Batch ${bIdx + 1}/${batches.length} (pages ${batch[0]}–${batch[batch.length - 1]})...`);

    const pagesBatch = batch.map(pn => ({
      pageNum: pn,
      imageBuffer: pages.get(pn).imageBuffer,
      text: pages.get(pn).text,
    }));

    let diagrams = [];
    try {
      diagrams = await analysePages(anthropic, pagesBatch);
    } catch (e) {
      console.log(` ✗ Claude error: ${e.message}`);
      continue;
    }

    process.stdout.write(` found ${diagrams.length} diagram(s)\n`);
    allDiagrams.push(...diagrams);

    // Brief pause between API calls to stay within rate limits
    if (bIdx < batches.length - 1) {
      await new Promise(r => setTimeout(r, 800));
    }
  }

  log(`  Total diagrams identified: ${allDiagrams.length}`);

  // Deduplicate by (pageNum, questionNum, diagramIndex) in case Claude returns duplicates
  const seen = new Set();
  const unique = allDiagrams.filter(d => {
    const key = `${d.pageNum}-${d.questionNum}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // Crop & upload
  const results = [];
  const diagramCountPerQ = {};

  for (const diagram of unique) {
    const page = pages.get(diagram.pageNum);
    if (!page || !page.imageBuffer) {
      log(`  ⚠ No image data for page ${diagram.pageNum}, skipping`);
      continue;
    }

    const qn = diagram.questionNum;
    diagramCountPerQ[qn] = (diagramCountPerQ[qn] || 0) + 1;
    const dIdx = diagramCountPerQ[qn];

    const { width: pageWidth, height: pageHeight } = page.meta.image.dimensions;

    let croppedBuffer;
    try {
      croppedBuffer = await cropImage(page.imageBuffer, diagram.cropHint, pageWidth, pageHeight);
    } catch (e) {
      log(`  ⚠ Crop failed for Q${qn} page ${diagram.pageNum}: ${e.message}`);
      croppedBuffer = page.imageBuffer; // fallback: use full page
    }

    if (DRY_RUN) {
      const kb = Math.round(croppedBuffer.length / 1024);
      log(`  [DRY RUN] Would upload: ${SUBJECT_ID}/${paper.year}/q${qn}_d${dIdx}.jpg (${kb}KB) — ${diagram.diagramType}`);
      results.push({
        year: paper.year,
        questionNum: qn,
        diagramIndex: dIdx,
        diagramType: diagram.diagramType,
        pageNum: diagram.pageNum,
        imageUrl: `[DRY_RUN] exam-images/${SUBJECT_ID}/${paper.year}/q${qn}_d${dIdx}.jpg`,
      });
    } else {
      try {
        const url = await uploadToSupabase(supabase, paper.year, qn, dIdx, croppedBuffer);
        const kb = Math.round(croppedBuffer.length / 1024);
        log(`  ✓ Q${qn} diagram ${dIdx} (${diagram.diagramType}) → ${url.split('/').pop()} [${kb}KB]`);
        results.push({
          year: paper.year,
          questionNum: qn,
          diagramIndex: dIdx,
          diagramType: diagram.diagramType,
          pageNum: diagram.pageNum,
          imageUrl: url,
        });
      } catch (e) {
        log(`  ✗ Upload failed for Q${qn}: ${e.message}`);
      }
    }
  }

  return results;
}

async function main() {
  requireEnv();

  log('CramIT — Maths Standard 2 Image Backlog Processor');
  log(`DRY_RUN=${DRY_RUN}  START_YEAR=${START_YEAR}  PAGES_PER_BATCH=${PAGES_PER_BATCH}`);

  // Init clients
  const anthropic = new Anthropic({ apiKey: ANTHROPIC_KEY });
  const supabase  = DRY_RUN
    ? null
    : createClient(SUPABASE_URL, SUPABASE_KEY);

  // Ensure storage bucket exists (service role required)
  if (!DRY_RUN) {
    const { error: bucketErr } = await supabase.storage.createBucket(STORAGE_BUCKET, {
      public: true,
      allowedMimeTypes: ['image/jpeg', 'image/png', 'image/webp'],
      fileSizeLimit: 5 * 1024 * 1024, // 5 MB
    });
    if (bucketErr && !bucketErr.message.includes('already exists')) {
      console.error('Failed to create storage bucket:', bucketErr.message);
      process.exit(1);
    }
    log(`Storage bucket "${STORAGE_BUCKET}" ready`);
  }

  const papersToProcess = PAPERS.filter(p => p.year >= START_YEAR);
  log(`Processing ${papersToProcess.length} paper(s): ${papersToProcess.map(p => p.year).join(', ')}\n`);

  const allResults = [];

  for (const paper of papersToProcess) {
    const results = await processPaper(anthropic, supabase, paper);
    allResults.push(...results);
  }

  // Write a summary manifest
  const manifestPath = path.join(__dirname, 'maths_images_manifest.json');
  const manifestData = {
    generated: new Date().toISOString(),
    subjectId: SUBJECT_ID,
    totalDiagrams: allResults.length,
    diagrams: allResults,
  };
  fs.writeFileSync(manifestPath, JSON.stringify(manifestData, null, 2));

  log(`\n${'='.repeat(60)}`);
  log(`DONE. ${allResults.length} diagrams processed.`);
  log(`Manifest written to: ${manifestPath}`);

  if (DRY_RUN) {
    log('\n⚠ This was a DRY RUN. Re-run without DRY_RUN=1 to upload for real.');
  } else {
    log('\nNext steps:');
    log('  1. Review maths_images_manifest.json');
    log('  2. Update index.html to load diagram images from Supabase Storage');
    log('     (replace hardcoded Q16–Q37 image refs with imageUrl from manifest)');
    log('  3. Run the full question migration to move hardcoded JS → Supabase questions table');
  }
}

main().catch(e => {
  console.error('\nFatal error:', e);
  process.exit(1);
});
