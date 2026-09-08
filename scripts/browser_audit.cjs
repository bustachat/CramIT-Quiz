/**
 * BROWSER AUDIT — the layout half of "verified in a browser", in CI.
 *
 *     node scripts/browser_audit.cjs            all subjects, three viewports
 *     node scripts/browser_audit.cjs --strict    exit 1 on any finding
 *     node scripts/browser_audit.cjs --widths 320,430
 *
 * WHY THIS EXISTS, and how it differs from render_audit.cjs.
 *
 * Browser verification has been this project's standard since early on, and it
 * is what has actually caught the serious defects — 14 stimulus images that
 * reached no student, nine clipped Maths Advanced stems, a table silently
 * losing its right-hand columns. But it was always done BY HAND, in a session,
 * by an assistant driving the browser. Two consequences:
 *
 *   · it never ran again once the session ended, and
 *   · its provenance was assistant-performed, exactly like the review ledger.
 *
 * `render_audit.cjs` made the STRUCTURAL half permanent by booting the page in
 * jsdom — but jsdom has no layout engine, so it declares overflow, image widths
 * and table scrolling out of scope. This closes that half with a real browser
 * at real viewports, so CLAUDE.md section 10's rule — "the test is the
 * MEASUREMENT, not a remembered threshold" — is enforced rather than recalled.
 *
 * ⚠️ 320px is deliberately the narrowest. A sweep on 2026-09-05 found three
 * Maths Advanced questions overflowing at 320 on tables of 6, 5 and 4 columns,
 * after the "7+ columns" rule of thumb had been measured at 430 and had held
 * there. One width is not a sweep.
 *
 * What it still cannot tell you: whether the content is CORRECT. A wrong model
 * answer renders perfectly.
 *
 * PROVED BOTH WAYS — reports zero on clean data, and fires when the real defect
 * shape is put back:
 *   B1  removing the overflow-x wrapper from 2023 Q23's 11-column z-table
 *       -> "714 > 320" at all three widths
 *   B3  removing the `.parts-stem img` cap AND the inline max-width
 *       -> the 2020 Q29 stimulus renders 1114px inside a 320px area
 *   B4  pointing a stimulus at a path that does not resolve -> 9 hits
 *
 * ⚠️ B0 and B2 are NOT independently proved and are guards rather than tested
 * checks. B2 in particular is close to unreachable while `body` keeps
 * `overflow-x: hidden` — which is exactly the rule that has hidden clipped
 * content in this app before, so the guard is worth its keep. Do not read
 * "0" from either as evidence that they work.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');

const REPO = path.dirname(__dirname);
const ARGS = process.argv.slice(2);
const STRICT = ARGS.includes('--strict');
const wi = ARGS.indexOf('--widths');
const WIDTHS = wi !== -1 ? ARGS[wi + 1].split(',').map(Number) : [320, 375, 430];

const MIME = { '.html': 'text/html', '.js': 'application/javascript', '.json': 'application/json',
               '.css': 'text/css', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
               '.svg': 'image/svg+xml', '.webp': 'image/webp' };

/** Serve the repo. The app fetches /subjects/*.json, so file:// will not do. */
function serve() {
  return new Promise(resolve => {
    const server = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\//, '') || 'index.html';
      const p = path.join(REPO, rel);
      if (!p.startsWith(REPO) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) {
        res.writeHead(404); return res.end('not found');
      }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p).toLowerCase()] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(res);
    });
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

const F = {};
const add = (k, v) => (F[k] = F[k] || []).push(v);

(async () => {
  const { server, port } = await serve();
  const browser = await chromium.launch();
  let measured = 0;

  try {
    for (const width of WIDTHS) {
      const page = await browser.newPage({ viewport: { width, height: 820 } });
      page.on('pageerror', e => add('B0_page_error', `${width}px: ${e.message.slice(0, 120)}`));
      await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForFunction(() => typeof window.renderQuestion === 'function', { timeout: 20000 });

      // Park on the quiz screen.
      await page.evaluate(() => {
        for (const id of ['home', 'picker', 'results', 'trial-wall']) {
          const e = document.getElementById(id); if (e) e.style.display = 'none';
        }
        document.getElementById('quiz').style.display = 'block';
      });

      const subjects = await page.evaluate(() => Object.entries(SUBJECT_ID_MAP)
        .map(([quizKey, id]) => ({ quizKey, id })));

      for (const { quizKey, id } of subjects) {
        await page.evaluate(k => loadSubjectData(k), quizKey);

        for (const mode of ['written', 'mc']) {
          // The whole sweep runs INSIDE the page: layout is synchronous there,
          // so one round trip per subject/mode instead of one per question.
          const out = await page.evaluate(async ([quizKey, mode, width]) => {
            const cache = subjectCache[quizKey];
            const bank = mode === 'written' ? (cache.writtenQuestions || []) : (cache.mcQuestions || []);
            if (!bank.length) return { n: 0, hits: [] };
            window.__bank = bank;
            currentSubjectKey = quizKey;
            currentMode = mode;
            activeQuestions = window.__bank;
            answers = activeQuestions.map(() => null);
            partDrafts = {};

            const hits = [];
            const tagOf = (q, i) => `${q.year !== undefined ? q.year + ' Q' + q.qNum : 'idx' + i}` +
                                    (mode === 'mc' ? ' [MC]' : '');
            for (let i = 0; i < bank.length; i++) {
              const q = bank[i];
              currentIdx = i; answers[i] = null;
              renderQuestion();
              const panels = (q.parts || []).length || 1;
              for (let p = 0; p < panels; p++) {
                if (q.parts && q.parts.length) togglePart(p);
                const area = document.querySelector('.question-area');
                if (!area) continue;

                // Force every image to load and settle, so widths are real.
                const imgs = [...area.querySelectorAll('img')];
                imgs.forEach(im => im.setAttribute('loading', 'eager'));
                await Promise.all(imgs.map(im => im.complete ? null : new Promise(r => {
                  im.onload = r; im.onerror = r; setTimeout(r, 3000);
                })));

                const tag = tagOf(q, i) + (q.parts && q.parts.length ? q.parts[p].label : '');
                if (area.scrollWidth > area.clientWidth + 1) {
                  hits.push(['B1_question_overflows', `${tag}: ${area.scrollWidth} > ${area.clientWidth}`]);
                }
                if (document.body.scrollWidth > width + 1) {
                  hits.push(['B2_page_scrolls_sideways', `${tag}: body ${document.body.scrollWidth} > ${width}`]);
                }
                for (const im of imgs) {
                  const r = im.getBoundingClientRect();
                  if (im.naturalWidth === 0) hits.push(['B4_image_failed_to_load', `${tag}: ${im.getAttribute('src')}`]);
                  else if (r.width > area.clientWidth + 1) {
                    hits.push(['B3_image_wider_than_container', `${tag}: ${Math.round(r.width)} > ${area.clientWidth}`]);
                  }
                }
                // ⚠️ There is deliberately NO separate unwrapped-table check.
                //
                // Two versions were written and both were wrong. The first
                // compared a table's own scrollWidth to its clientWidth — but a
                // <table> never scrolls itself; it lays out as wide as it likes
                // and an ancestor clips it, so the comparison is false almost
                // always (it reported 0 across 41 real tables). The second
                // measured the table against the area and walked up looking for
                // a scroller — but `.question-area` is ITSELF `overflow-x:auto`,
                // so the walk always finds one and the check could never fire.
                //
                // B1 above is the correct and sufficient signal: when a table is
                // not wrapped in its own scroller, the QUESTION AREA is what
                // ends up overflowing, and B1 measures exactly that. Proved by
                // injection — removing the wrapper from 2023 Q23's 11-column
                // z-table makes B1 report 714 > 320/375/430 at all three widths.
              }
            }
            return { n: bank.length, hits };
          }, [quizKey, mode, width]);

          measured += out.n;
          for (const [k, v] of out.hits) add(k, `${id} ${v} @${width}px`);
        }
      }
      await page.close();
    }
  } finally {
    await browser.close();
    server.close();
  }

  const TITLES = {
    B0_page_error: 'The page threw a JavaScript error',
    B1_question_overflows: 'The question area overflows horizontally',
    B2_page_scrolls_sideways: 'The page itself scrolls sideways',
    B3_image_wider_than_container: 'An image renders wider than its container',
    B4_image_failed_to_load: 'An image referenced by a question does not load',
  };

  console.log('='.repeat(78));
  console.log(`BROWSER AUDIT — ${measured} question renders in Chromium at ${WIDTHS.join('/')}px`);
  console.log('='.repeat(78));
  let total = 0;
  for (const k of Object.keys(TITLES)) {
    const v = [...new Set(F[k] || [])];
    total += v.length;
    console.log(`\n[${k}] ${TITLES[k]} — ${v.length}`);
    v.slice(0, 25).forEach(x => console.log('    ' + x));
    if (v.length > 25) console.log(`    … and ${v.length - 25} more`);
  }
  console.log('');
  console.log('='.repeat(78));
  console.log(`BROWSER findings: ${total}`);
  console.log('⚠️ This proves PRESENTATION, not correctness. A wrong model answer');
  console.log('   renders perfectly.');
  console.log('='.repeat(78));
  if (STRICT && total > 0) process.exit(1);
  process.exit(0);
})().catch(e => { console.error('browser audit failed to run:', e); process.exit(2); });
