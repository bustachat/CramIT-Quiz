/**
 * RENDER AUDIT — drive the real renderer over every question and look at what
 * a student would actually see.
 *
 *     node scripts/render_audit.cjs            all subjects, both modes
 *     node scripts/render_audit.cjs --strict    exit 1 on any finding
 *     node scripts/render_audit.cjs <subject-id>
 *
 * WHY THIS EXISTS. Every other check in this repo is static: it reads
 * subjects/*.json and reasons about it. The worst defects of the last fortnight
 * were invisible to all of them, because they only existed once the page had
 * been drawn:
 *
 *   · 14 Maths Advanced questions asked about a diagram that was in `q`, which
 *     a multi-part question never renders (2026-09-07)
 *   · 57 Standard 2 questions showed the literal word "undefined" as feedback
 *     (2026-09-05)
 *   · every HMS written question rendered with no marks badge (2026-08-27)
 *
 * Each was found by a human happening to look. This looks, every build.
 *
 * ⚠️ AND IT IS THE ANSWER TO A SECOND FAILURE. On 2026-09-07 a static check was
 * added, and blocked CI, on the belief that a bare '>' inside a quoted
 * attribute closes the tag early. It does not — browsers parse it correctly —
 * and the belief survived because nothing asked the renderer. A static check
 * encodes what we already think we know; this one tests it.
 *
 * HOW. index.html is booted in jsdom with its own inline script running, its
 * fetches served off disk, and Supabase absent (the page degrades to logged-out,
 * which is what a trial student sees anyway). The app's OWN globals are then
 * driven — renderQuestion, togglePart — so this exercises the shipped renderer
 * rather than a copy of it, the same discipline scoring.js tests follow.
 *
 * ⚠️ WHAT IT CANNOT SEE. jsdom has no layout engine: every element measures
 * zero. So overflow, image widths, table scrolling and anything else
 * geometric are OUT OF SCOPE here and still need a real browser at a real
 * viewport (CLAUDE.md section 10 — the test is the measurement). This audit
 * covers what is in the DOM and what it says, not how big it is.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REPO = path.dirname(__dirname);
const ARGS = process.argv.slice(2);
const STRICT = ARGS.includes('--strict');
const ONLY = ARGS.find(a => !a.startsWith('--'));
const SUBJECTS = ['mathematics-standard-2', 'mathematics-advanced', 'vet-construction',
                  'multimedia', 'health-movement-science'];

const F = {};
const add = (k, v) => (F[k] = F[k] || []).push(v);

/** Boot index.html far enough to call its renderer. */
function boot() {
  const html = fs.readFileSync(path.join(REPO, 'index.html'), 'utf8');
  const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    url: 'http://localhost/',
    beforeParse(win) {
      // Serve the app's own fetches off disk. No network, no server.
      win.fetch = async (u) => {
        const rel = String(u).replace(/^https?:\/\/[^/]+/, '').replace(/^\//, '').split('?')[0];
        const p = path.join(REPO, rel);
        if (!fs.existsSync(p)) return { ok: false, status: 404, json: async () => ({}) };
        const body = fs.readFileSync(p, 'utf8');
        return { ok: true, status: 200, text: async () => body, json: async () => JSON.parse(body) };
      };
      win.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {},
                                addListener() {}, removeListener() {} });
      win.scrollTo = () => {};
    },
  });
  const win = dom.window;
  // <script src> is not fetched by jsdom, so load the classic scripts by hand,
  // in document order. supabase.min.js is deliberately skipped: the page
  // degrades to logged-out, which is the state a trial student is in.
  win.eval(fs.readFileSync(path.join(REPO, 'scoring.js'), 'utf8'));
  return win;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const win = boot();
  await sleep(600);
  const doc = win.document;
  const $ = sel => doc.querySelector(sel);

  // Park the app on the quiz screen; every other screen stays hidden so
  // innerText below is the question and nothing else.
  for (const id of ['home', 'picker', 'results', 'trial-wall']) {
    const el = doc.getElementById(id); if (el) el.style.display = 'none';
  }
  doc.getElementById('quiz').style.display = 'block';

  let rendered = 0;
  for (const sid of (ONLY ? [ONLY] : SUBJECTS)) {
    const quizKey = Object.keys(win.eval('SUBJECT_ID_MAP') || {})
      .find(k => win.eval('SUBJECT_ID_MAP')[k] === sid);
    if (!quizKey) { add('R0_not_registered', `${sid}: no SUBJECT_ID_MAP entry — cannot render`); continue; }

    await win.loadSubjectData(quizKey);
    const cache = win.eval('subjectCache')[quizKey];
    if (!cache) { add('R0_not_registered', `${sid}: loadSubjectData returned nothing`); continue; }

    for (const mode of ['written', 'mc']) {
      const bank = mode === 'written' ? (cache.writtenQuestions || []) : (cache.mcQuestions || []);
      if (!bank.length) continue;
      // ⚠️ index.html declares activeQuestions/answers with `let` inside its
      // inline script, so `win.activeQuestions = …` creates a DIFFERENT global
      // and the renderer keeps reading its own stale one — which showed up as
      // 1086 identical "cannot read properties of undefined" throws the first
      // time this ran. Hand the value over a real window property, then assign
      // it into the app's scope from inside.
      win.__auditBank = bank;
      win.eval('currentSubjectKey = ' + JSON.stringify(quizKey));
      win.eval('currentMode = ' + JSON.stringify(mode));
      win.eval('activeQuestions = window.__auditBank; answers = activeQuestions.map(() => null); partDrafts = {};');

      for (let i = 0; i < bank.length; i++) {
        const q = bank[i];
        const tag = `${sid} ${q.year !== undefined ? q.year + ' Q' + q.qNum : 'idx' + i}${mode === 'mc' ? ' [MC]' : ''}`;
        win.eval('currentIdx = ' + i + '; answers[currentIdx] = null;');
        try { win.renderQuestion(); } catch (e) { add('R1_render_threw', `${tag}: ${e.message}`); continue; }
        rendered++;

        const area = $('.question-area');
        if (!area) { add('R1_render_threw', `${tag}: no .question-area`); continue; }

        // Multi-part: open every panel, so nothing hides in a collapsed one.
        const nParts = (q.parts || []).length;
        const seen = [];
        for (let p = 0; p < Math.max(1, nParts); p++) {
          if (nParts) { try { win.togglePart(p); } catch (e) { add('R1_render_threw', `${tag}${q.parts[p].label}: ${e.message}`); } }
          const a = $('.question-area');
          seen.push({ text: a.textContent || '', html: a.innerHTML || '',
                      imgs: a.querySelectorAll('img').length,
                      qText: [...a.querySelectorAll('.q-text, .parts-stem, .part-intro')]
                        .map(el => el.textContent || '').join(' ') });
        }
        const text = seen.map(s => s.text).join(' ');
        const html = seen.map(s => s.html).join(' ');
        const imgs = Math.max(...seen.map(s => s.imgs));

        // R2 — the literal word "undefined" on screen.
        if (/\bundefined\b/.test(text)) add('R2_undefined_on_screen', tag);

        // R3 — a written question with no marks badge.
        if (mode === 'written' && !/\d+\s*marks?/i.test(text)) add('R3_no_marks_badge', tag);

        // R4 — an image the data references that never reaches the DOM. This is
        // the 2026-09-07 class, measured by rendering instead of inferred.
        const refs = (q.image ? 1 : 0) +
          ((String(q.q || '') + String(q.stem || '') +
            (q.parts || []).map(p => String(p.q || '') + String(p.intro || '')).join('')
           ).match(/<img\b/g) || []).length;
        if (refs > 0 && imgs === 0) add('R4_image_never_drawn', `${tag}: references ${refs}, draws 0`);

        // R5 — markup that leaked into visible text. An attribute fragment in
        // textContent means a tag closed somewhere it should not have.
        const leak = text.match(/\b(?:src|alt|style|class|href)="/);
        if (leak) add('R5_markup_leak', `${tag}: …${text.slice(Math.max(0, text.indexOf(leak[0]) - 40), text.indexOf(leak[0]) + 40)}…`);

        // R6 — an MC question whose option images do not all appear.
        if (mode === 'mc' && q.optionImages && q.optionImages.filter(Boolean).length) {
          const want = q.optionImages.filter(Boolean).length;
          const got = $('.question-area').querySelectorAll('img.option-img').length;
          if (got < want) add('R6_option_images_missing', `${tag}: ${got} of ${want}`);
        }

        // R7 — the QUESTION TEXT is empty, whatever else is on screen.
        //
        // ⚠️ Measured on the text elements, not the whole area. A first version
        // tested the area's own length and could never fire on a multi-part
        // question: the marks badge, year and topic chips, "FOR ALL PARTS" and
        // the part rows are always there, so blanking every prompt still left
        // well over the threshold. Proving the check by injection is what
        // exposed that.
        const qText = seen.map(s => s.qText).join(' ').replace(/\s+/g, ' ').trim();
        if (qText.length < 15) add('R7_blank_render', `${tag}: question text is ${qText.length} chars`);

        // R8 — the FEEDBACK a student sees after answering. Built by the app's
        // own buildKeywordFeedback (which delegates to buildPartFeedback for a
        // multi-part question), fed the question's own model answer.
        //
        // This is the check that would have caught the 2026-09-05 Standard 2
        // defect: 57 questions whose bandDescriptors were keyed {high,mid,low}
        // or {1,2,3} instead of {full,partial,minimal}, so the engine's lookup
        // returned undefined and the word was rendered verbatim as the
        // student's feedback. Nothing static saw it; the data was well-formed.
        if (mode === 'written') {
          const strip = h => { const d = doc.createElement('div'); d.innerHTML = h || ''; return d.textContent || ''; };
          const ans = nParts
            ? Object.fromEntries(q.parts.map(p => [p.label, strip(p.answer)]))
            : strip(q.answer || q.modelAnswer);
          let fb = '';
          try { fb = win.buildKeywordFeedback(q, ans) || ''; }
          catch (e) { add('R9_feedback_threw', `${tag}: ${e.message}`); }
          const fbText = strip(fb);
          if (/\bundefined\b/.test(fbText)) add('R2_undefined_on_screen', `${tag} [feedback]`);
          // The engine's generic wording means this question's NESA-derived band
          // text never reached the student.
          if (/Excellent — demonstrates detailed knowledge|Developing — key concepts partially/.test(fbText))
            add('R10_generic_band_shown', tag);
        }
      }
    }
  }

  const TITLES = {
    R0_not_registered: 'Subject cannot be rendered by the app at all',
    R1_render_threw: 'renderQuestion() threw',
    R2_undefined_on_screen: 'The literal word "undefined" is shown to the student',
    R3_no_marks_badge: 'Written question renders with no marks badge',
    R4_image_never_drawn: 'The data references an image the renderer never draws',
    R5_markup_leak: 'Markup leaked into visible text (a tag closed early)',
    R6_option_images_missing: 'Not every option image reaches the DOM',
    R7_blank_render: 'Question renders essentially nothing',
    R9_feedback_threw: 'buildKeywordFeedback() threw',
    R10_generic_band_shown: 'Feedback falls back to the engine generic band wording',
  };

  console.log('='.repeat(78));
  console.log(`RENDER AUDIT — ${rendered} question renders through the real renderer (jsdom)`);
  console.log('='.repeat(78));
  let total = 0;
  for (const k of Object.keys(TITLES)) {
    const v = F[k] || [];
    total += v.length;
    console.log(`\n[${k}] ${TITLES[k]} — ${v.length}`);
    v.slice(0, 25).forEach(x => console.log('    ' + x));
    if (v.length > 25) console.log(`    … and ${v.length - 25} more`);
  }
  console.log('');
  console.log('='.repeat(78));
  console.log(`RENDER findings: ${total}`);
  console.log('⚠️ Layout is OUT OF SCOPE — jsdom has no layout engine, so overflow,');
  console.log('   image widths and table scrolling still need a real browser.');
  console.log('='.repeat(78));
  if (STRICT && total > 0) process.exit(1);
  process.exit(0);
})().catch(e => { console.error('render audit failed to run:', e); process.exit(2); });
