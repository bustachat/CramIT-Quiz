# CramIT — Session History

Not auto-loaded into every session — read this only when investigating *how* or
*why* something was built a certain way. Current instructions live in
`CLAUDE.md`. This file is an append-only log of completed work; git history is
the byte-accurate record, this is the human-readable narrative alongside it.

---

## Completed stages / features (chronological)

- Supabase schema deployed (tables, RLS, functions)
- Google OAuth configured (testing mode — approved test users only)
- Stripe products created (sandbox/test mode)
- GitHub repo set up (`bustachat/CramIT-Quiz`)
- Cloudflare Pages deployed at `https://cramit-quiz.pages.dev`
- Supabase Edge Function `clever-action` deployed
- Stripe webhook registered pointing to Edge Function
- All secrets added to Cloudflare and Supabase
- Billing UI wired into `index.html`
- Google login working after redirect URL fix
- `SUPABASE_ANON` and `APP_URL` filled in `index.html`
- **Stage 1 complete** — progress bar glow, year/topic badges on questions, reset confirmation modal, touch targets 52px, safe-area-inset for notched phones
- **Stage 2 complete** — diagram extractor v3, 76 images in `/diagrams/`, calibration mode, stimulus/options split
- **Stage 3 complete** — images wired into quiz renderer (`image` + `optionImages`), `MATHS_IMG` retired, category filter with live counts, HSC 90/Extended 318 toggle
- **Stage 4 complete** — Multimedia + HMS ported into `index.html` with full MC + written question sets
- **Stage 5 complete** — keyword scoring + bandDescriptors on all 42 written questions, upgraded written UI (keyword grid, score heading, colour pills), AI marking via `/mark-written` (Cloudflare Pages Function) with monthly quota by plan (Free=0, Base=50, Unlimited/Flex=100), student answer display, stem keyword matching, try-again fix, `ANTHROPIC_API_KEY` added to Cloudflare, SQL migration run in Supabase
- **Stage 6 complete** — 10-question trial per subject replaces permanent free tier; trial counter in localStorage; mid-quiz trial wall with score + CTA; picker locks year/category/Extended 318/Test Mode/Written Response during trial; stats only tracked for logged-in users; upgrade prompt handles both logged-in and logged-out states
- **Stage 7A complete** — Per-question progress tracking via localStorage JSON map `{questionIdx: 0|1}` keyed by stable position in master array. Last-attempt-wins (re-answering overwrites, never inflates total). `getMasterArray()` returns unfiltered master array so `indexOf()` is shuffle/filter-safe. `getSubjectStats()` derives seen/correct/pct. Card badges show "X seen · Y%". Aggregate totals on home screen. Data structure ready for Phase B Supabase sync.
- **Stage 7B complete** — Cross-device progress sync via Supabase `user_progress` table. `syncAnswerToSupabase()` fire-and-forget UPSERT after every answer (quiz never waits on network). `loadProgressFromSupabase()` called on login — fetches all rows, merges into localStorage (server wins on conflict). Offline answers preserved until next sync. Table has UNIQUE(user_id, subject_key, question_idx, mode) — re-answers update one row, never duplicate. RLS enabled.
- **Stage 8 complete** — Maths Section II written questions fully added. 101 written questions covering 2020–2025 HSC papers. Stage 8A: 68 text-only questions with keywords, band descriptors, model answers. Stage 8B: 33 additional questions with diagram images (`image:` field), 47 JPG images extracted from exam PDFs via PyMuPDF and committed to `/diagrams/`. Images audited and re-cropped (15 fixed: wrong page numbers, text bleeding, edge clipping). Key Concepts grid hidden for Maths (numerical keywords are scoring markers, not display concepts). Known limitation: some images have minor text label clipping ("NOT TO SCALE" etc.) — root cause is `auto_bbox` detecting vectors only, not text. Fix: rebuild extractor with Claude Vision `--detect` mode + full-width crop (x0=30, x1=565) before automation goes live.
- **Stage 8.9 complete** — Formula Hint widget for Maths MC questions in Practice mode. Green lightbulb "Hint" button appears in the question header for formula-based questions. Pressing it reveals a tip card: a prompt asking which formula applies, 3 radio button choices (1 correct, 2 plausible wrong), per-choice explanations, correct/wrong colour feedback, Try Again resets, "Got it →" closes the card. Does NOT appear in Test mode. Does NOT count against the trial limit. Covers 73 of 90 HSC questions (non-formula/image-only questions skipped). Full Extended 318 coverage: F1/F2/M1 variants use exact index range lookup (`mathsQuestionTips` keys 1–89, variant indices 90–206 mapped via range table); S1S2/T2/A2/N1/P1 variants use keyword matching on question text (returns null on no match — never shows a wrong hint). Key implementation: `getTipForQuestion(q)` is the single lookup function used by `openTip()`, `checkTipAnswer()`, and `renderQuestion()` — all three must call this function, not `mathsQuestionTips[masterIdx]` directly.
- **Stage 8.5 complete** — Written question diagram extractor rebuilt as `extract_written_diagrams.py`. Replaces 4 one-off fix scripts. CROP mode bootstraps 15 hard-coded entries (2020–2025) using PyMuPDF clip at x0=30, x1=565 (full-width). DETECT mode (`--detect`) uses Claude Vision (`claude-sonnet-4-6`) to scan Section II pages. PyMuPDF-based coordinate detection finds y_start (topmost vector drawing filtered for borders) and y_end (first `(a)` text or instruction verb near left margin). Registry stored in `written_diagram_registry.json` (version 1).
- **API cost optimisation complete** — Prompt caching + token logging added to all API-calling files. `mark-written.js`: model → `claude-haiku-4-5`, system prompt cached, token usage logged to Cloudflare dashboard. `agent.js`: `SYSTEM_DISCOVER` + `SYSTEM_GENERATE` constants extracted, `logUsage()` helper added, `discoverNewPapers` model → `claude-sonnet-4-6`. `extract_maths_diagrams.py` + `extract_written_diagrams.py`: vision model → `claude-sonnet-4-6`. Patterns saved to global `~/.claude/CLAUDE.md`.
- **Question text accuracy pass complete (partial)** — 25 of 90 HSC Section I MC question texts updated to exact NESA wording using `verify_question_text.py` (PyMuPDF extraction) + `apply_question_text_fixes.py` (quality-filtered apply). 39 questions skipped — PDF extraction returned garbled text (image-based questions). Those need manual review pre-launch. `question_text_diff.txt` in repo root has the full list.
- **Bug fixes (Session 5)** — `mark-written.js`: subscription-not-found now returns `sub_not_found` reason instead of misleading "upgrade" message. `index.html` 2024 Q15 histogram: added `hideQ:true` (NESA embedded question text inside stimulus image). 2022 Q13 normal distribution: restored exact NESA question wording.
- **UX — Sliding segmented filter controls (Session 6, 2026-06-08)** — Replaced `.filter-chip` pill buttons with animated sliding segmented controls. Amber pill slides smoothly to selected option via `transform: translateX()` (GPU-accelerated, no layout reflow). Mobile: full-width, horizontal scroll, `flex: 0 0 auto` buttons. Desktop: `inline-flex fit-content` — never sprawls across wide screens. `applyFilter()` updates only the tapped control — no full DOM rebuild, no cross-slider flash. Year change resets category to All and rebuilds only the category control via `rebuildCategoryControl()`. `updateModeCounts()` patches mc-count and written-count spans after every filter tap. Categories and topics set to `null` when no questions have those fields (prevents solo "All" rendering for VET/Multimedia/Maths). All controls scroll horizontally on mobile.
- **UX — Profile avatar + bottom sheet (Session 6, 2026-06-08)** — Replaced full-width user bar with compact amber avatar circle (user initial) in top-right of home header. Tapping opens a bottom sheet with email, plan summary, Billing and Sign out actions. Sheet slides up with backdrop dismiss. Logo reduced 200px → 120px. Header top padding uses `env(safe-area-inset-top)` — respects notch on iPhone, minimal on Android. Auth state: logged-out shows compact Google Sign in button in header row.
- **HMS FA2 — Training for Improved Performance questions (Session 7, 2026-06-09)** — 58 MC + 10 written questions added to `subjects/pdhpe-hms.json`. Covers full NESA FA2 syllabus (HM12-04, HM12-05, HM12-08): exercise assessment (PAR-Q, VO₂ max, fitness testing), training methods (anaerobic: HIIT/SIT/plyometrics/resistance; aerobic: continuous/fartlek/aerobic interval/circuit; flexibility: static/dynamic/ballistic/PNF; strength; skill/tactical), principles of training (progressive overload, specificity, reversibility, variety, thresholds, warm-up/cool-down), physiological adaptations (HR, stroke volume, cardiac output, VO₂ max, haemoglobin, hypertrophy, fast/slow twitch fibres), periodisation (pre/in/off-season, tapering, peaking, psychological strategies), nutrition (pre/during/post performance, fluid intake). 10 written: 4×3-mark, 4×5-mark, 2×12-mark with Band 6 scaffold. Soccer/football examples throughout.
- **HMS picker — FA1/FA2 Assessment toggle (Session 7, 2026-06-09)** — New `Assessment` segmented control (All / FA1 — Injury / FA2 — Training) above Topic filter in HMS picker. Selecting FA2 collapses Topic to the 6 training topics; FA1 shows the 6 injury topics. Topic filter rebuilt via `rebuildTopicControl()` on assessment change (mirrors `rebuildCategoryControl()` pattern). `fa2_` prefix stripped from topic labels; `returnplay` → "Return to Play". `positionAllSliders` updated to include `seg-assess`. `applyFilter` idMap includes `assessment: 'seg-assess'`. HMS `getMC`/`getWritten` filter by `filters.assessment` group before `filters.topic`.
- **Bug fixes (Session 7, 2026-06-09)** — Results breakdown now shows in Practice mode (was Test mode only — condition was `!isPracticeMode`). Written results screen: shows "Session complete 📝" instead of "Excellent" (pct was hardcoded to 100 for written mode). AI marking quota fix: if `sub.status === 'active'` or `'trialing'` but `plan` maps to quota=0 (Stripe webhook sync delay), silently use base quota (50 marks) — prevents subscribed users seeing "upgrade" message. `no_plan` fallback message improved. Filter-row `overflow-x: auto` on all screen sizes — pill scroller contained to filter bar on desktop, not page.
- **HMS FA2 content expansion (Session 8, 2026-06-10)** — 3 new topic groups added to `subjects/pdhpe-hms.json`: `fa2_psychology` (12 MC + 2 written: arousal, inverted U hypothesis, trait/state anxiety, mental rehearsal, relaxation, SMART goals), `fa2_individual_group` (12 MC + 2 written: H-O-W-S-C-S-E session design, macrocycle/mesocycle/microcycle, individual vs group tapering, small-sided games, 12-mark periodisation scaffold), `fa2_sleep` (8 MC + 1 written: sleep/growth hormone/cortisol, dehydration, hydration guidelines). Existing topics deepened: `fa2_nutrition` 4→12 questions (carb loading, GI, electrolytes, iron, RED-S), `fa2_periodisation` +2 (step taper, exponential decay types). Added 8 linking MC questions (principle→adaptation→performance chain) and 3 new written questions (dietary requirements for different sports, factors influencing strategies/tactics, principles→adaptations→performance). 12-topic slice limit removed from `loadSubjectData()`. FA2 topic arrays updated in all 4 locations in `index.html`. `fa2_assessment` label renamed to "Exercise Assessment" to prevent duplicate with FA1 "Assessment" topic.
- **Workbook alignment analysis (Session 8, 2026-06-10)** — Reviewed student workbook (`Olivier Khoury - CQ3...docx`) against assessment notification PDF. Confirmed assessment covers 4 syllabus sections: exercise assessment, training methods/principles/adaptations, individual vs group sports, dietary requirements. "How do individuals train for sustained movement and performance?" is NOT on this assessment (HSC scope only). All assessment dot points now covered in quiz.
- **Maths Section II written questions complete (Session 10, 2026-06-16)** — All missing Section II written questions added for 2022 (6 questions), 2023 (10 questions), 2024 (12 questions), and 2025 (6 questions). Total writtenQuestions in `subjects/mathematics-standard-2.json`: 151 (covers 2020–2025 complete). Stimulus images rendered at 2x from NESA exam PDFs via PyMuPDF and committed to `/diagrams/`. Questions built from MG answers: answers, keywords, bandDescriptors all populated. 2025 questions added: Q22 (N2, network flow/max flow 5m), Q26 (M4, trapezoidal rule+SA+% error 6m), Q35 (M6, sine rule obtuse triangle 3m), Q36 (F1, declining-balance depreciation 4m), Q37 (M7, cosine rule+area equilateral triangles 4m), Q39 (A4, exponential decay model 3m).
- **Stimulus image overhaul complete (Session 11, 2026-06-17)** — All 34 full-page placeholder stimulus JPGs replaced: 13 geometric/network diagrams converted to crisp SVGs (`fix_stimulus_images.py` auto-crop + hand-authored SVG for networks, bearings, triangles, critical paths, box plots, pentagon, compass survey); 15 data-heavy graphs re-cropped to tight bounds at 2x resolution via `fix_stimulus_images.py`; 5 table questions (2022 Q20, 2023 Q17/Q29/Q37, 2024 Q41) had `image` set to null with full table data embedded in `q` field. 18 old full-page JPGs deleted. Companion `_Q22b_stimulus.svg` created for 2025 Q22 flow network part b. *(This SVG was superseded and deleted in the 2026-07-04 housekeeping pass — see below.)*
- **2025 written question PDF audit complete (Session 12, 2026-06-17)** — All 2025 written questions verified against NESA PDF. Fixed: Q18 (embed FV table, fix compounding type), Q21 (merge incorrectly split (a)+(b) entries), Q25 (replace partial 3m entry with full 6m question + scatterplot image), Q31 (image null → embed income tax table), Q34 (embed FV factors table), Q38 (add entirely missing 3m fuel efficiency question), Q40 (add entirely missing 5m normal distribution question). Re-cropped Q20/Q25/Q32 stimulus JPGs at correct tight bounds. Total writtenQuestions: 151. Crop methodology: hardcoded (y0,y1) bounds per question derived from PDF text block positions — same approach as MC `diagram_registry.json`. Script: `fix_2025_written_questions.py`.
- **2022–2024 written question PDF audit complete (Session 12, 2026-06-17)** — All 2022/2023/2024 written questions verified against NESA PDFs (text extracted via PyMuPDF). 21 issues fixed across all three years. 2022 (8 fixes): Q16/Q22 split entries merged, Q19/Q24/Q25/Q27/Q30/Q36 truncated entries expanded with missing sub-parts and FV tables. 2023 (8 fixes): Q21 partial (c,d) only → full 5m question, Q24/Q26 duplicate sub-part entries removed, Q25 split entries merged with full FV table, Q29 wrong content corrected (had depreciation instead of monthly repayment table), Q30/Q32/Q36 entirely missing questions added. 2024 (5 fixes): Q20/Q24 split entries expanded with full FV table and missing sub-parts, Q31/Q33/Q37 entirely missing questions added. Total writtenQuestions: 151 (unchanged — merges and additions balanced). Script: `audit_written_2022_2024.py`.
- **NESA category audit + multi-select filter (Session 9, 2026-06-16)** — All 318 Maths Standard 2 MC questions re-categorised to correct NESA codes (19 codes: A1–S5). Previous categories were mis-labelled — S4, N2, N3 etc. were buried under wrong codes. Script `fix_mc_categories.cjs` used 35-char exact-match map for 90 HSC originals + keyword regex for 228 variants. Final distribution confirmed (A1=16, A2=19, A4=30, F1=28, F2=15, F4=25, F5=4, M1=41, M2=4, M4=12, M5=13, M7=20, N1=7, N2=5, N3=1, S1=22, S2=17, S4=15, S5=24). Multi-select category filter built: `pickerFilters.categories[]` array (empty=All), `toggleCategory(c)` toggling, amber active state via `#seg-cat .seg-btn.active` CSS rule (no slider div — each button self-highlights). Categories sorted alphabetically. `NESA_CAT_LABELS` constant maps codes to full names. `getMC`/`getWritten` filter on `filters.categories?.length`.
- **Variant category audit complete (2026-06-21)** — 33 variant MC questions had wrong category codes inherited from the keyword-regex pass in Session 9. All 4 incorrect codes fixed: F2→F4 (12 compound wage/investment variants), M4→M7 (9 distance/speed/BAC variants), M5→M6 (9 true bearing variants), N1→N2 (3 network degree-sum variants). Source questions confirmed against MG PDFs. Final distribution: 16 category codes (A1–S5), zero orphaned codes. All 318 MC categories now verified correct against NESA MGs.
- **Written question table audit complete (2026-06-21)** — All 151 written questions audited for structured data rendered as plain text. 14 markdown pipe-table blocks converted to HTML `<table>` tags via `fix_pipe_tables.cjs`. 3 tax bracket questions (2021 Q22, 2020 Q20, 2023 Q37) converted from bullet-point lists to 2-column `<table>`. 2 month-data questions converted from prose sentences to tables. All 28 tables across `subjects/mathematics-standard-2.json` wrapped in `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;">` and set to `font-size:0.68em` — confirmed correct size on mobile. Zero tables missing overflow wrapper or font-size.
- **Tool auto-approval configured (2026-06-21)** — `.claude/settings.local.json` (project) and `~/.claude/settings.json` (global) updated with `Bash(*)`, `PowerShell(*)`, `Read(*)`, `Write(*)`, `Edit(*)`, `Glob(*)`, `Grep(*)` wildcards plus all Chrome MCP and visualize MCP tools. Eliminates per-tool approval prompts for standard development operations.
- **Test Mode MC re-selection bug fixed (2026-06-21)** — In Test Mode, clicking an answer immediately called `renderQuestion()` which disabled all option buttons, preventing the user from changing their answer. Fix: `selectAnswer()` in test mode now only highlights the chosen option (adds `selected-test` class) and shows the Next button — it does NOT set `answered=true` or call `renderQuestion()`. Scoring (score++, streak, `recordAnswer`) moved to `nextQuestion()` where it runs when the user confirms by clicking Next. Users can now re-click any option to change selection before advancing.
- **Quiz footer nav buttons redesigned (2026-06-21)** — Prev button redesigned as compact 52×52px icon-only square (`←`), `2px solid var(--muted)` border. Next/Show button fills remaining width via `flex: 1`. Removed `margin: 14px 20px 28px` from `.next-btn` (was inflating row height and misaligning buttons). Footer uses `align-items: center`. Footer padding handles all outer spacing.
- **MC image-question text audit complete (2026-06-21)** — All 33 image-based MC questions (those with `image` or `optionImages` fields) visually verified against NESA PDFs by rendering exam pages at 2x PNG via PyMuPDF and comparing using Read tool. 4 fixes applied to `subjects/mathematics-standard-2.json`: 2020 Q8 (add "the subjects and"), 2020 Q15 (add missing die-rolling rule sentence), 2022 Q13 (add "for some positive values of z", shaded area diagram sentence, full final question wording), 2023 Q8 (add "The table of scores below is partially completed."). All 90 HSC MC questions now verified against NESA PDFs (text-only questions via PyMuPDF extraction pass + this image pass).
- **Written question stimulus image audit complete (2026-06-22)** — All 75 written question stimulus images visually verified by reading each JPG directly. Results recorded in `diagram_audit.json` (permanent reference — do not re-scan PDFs). Findings: 44 clean, 13 minor text bleed (cosmetic), 7 drawing grids (intentional — kept for haptic feature), 1 answer lines (minor), 1 right-edge clip (minor), 1 REAL issue. Real issue fixed: `2022_Q23_stimulus.jpg` re-cropped by user to include x-axis label "Average hours of phone use per day". Zero real issues remaining. 2 orphaned unreferenced images deleted (`2022_Q19_stimulus.jpg`, `2022_Q24_stimulus.jpg` — content already embedded as HTML tables).
- **Lightbox transparent PNG fix (2026-06-22)** — `#img-lightbox img` now has `background:#fff; padding:12px`. Transparent PNGs were invisible when tapped to enlarge (black lines on transparent = invisible on dark lightbox). White background restores visibility. One CSS line change in `index.html`.
- **Written test mode overhaul (2026-06-22)** — Test mode written questions now behave like a real exam: textarea always editable, Next saves silently (blank = skipped), Prev saves before going back, last question shows "Submit test →" with confirm modal (answered count + skip count), results screen shows per-question breakdown (student answer vs model answer side by side). No AI marking, no keyword scoring, no band feedback in test mode. `showSubmitTestModal()` reuses existing reset modal DOM with temporary event listeners. Practice mode unchanged.
- **MC table audit complete (2026-06-22)** — All 33 image-based MC questions audited. Only 2020 Q8 violated the HTML table rule (stimulus was Subject/John's score/Mean/SD table image; options A/B/C/D were Strongest/Weakest 2-column table images). Fixed: stimulus table and 4 option tables converted to inline HTML `<table>` tags in `q` and `options` fields. 5 PNG files deleted (`_2020_Q8_stimulus/A/B/C/D.png`). `hideQ:true` removed. All other image-based questions use graphs, histograms, geometric shapes, or petrol pump illustrations — all appropriate as images.

## Question JSON Migration — complete (2026-06-05)

All question data previously hardcoded in `index.html` was extracted to individual JSON files in `subjects/`. `index.html` reduced from 11,195 → 2,502 lines (−78%).

One JSON file per subject, all years combined (not split per year — the year filter already works client-side from the `year:` field, and the agent can append new years to the existing file). Files created at the time: `mathematics-standard-2.json` (318 MC incl. variants + 73 tips, 101 written, 608 KB), `pdhpe-hms.json` (57 MC, 17 written, 118 KB — later grew to 165 MC / 35 written), `multimedia.json` (60 MC, 29 written, 118 KB), `vet-construction.json` (75 MC, 23 written, 103 KB). JSON format: `{ id, name, icon, accentColor, mcQuestions[], writtenQuestions[], tips{} }` — same field names as the old JS objects.

Extraction scripts committed to repo at the time: `extract_subjects.cjs`, `migrate_index.cjs` (later moved to `scripts/archive/`).

## Full code review + 3 critical fixes (2026-07-02)

Whole-app review (index.html, all 5 Cloudflare functions, agent.js, scripted validation of all subject JSON). Three critical bugs fixed:

1. **Submit-test crash** — `showSubmitTestModal()` referenced element IDs (`reset-modal-title/body/confirm/cancel`) that never existed, so tapping "Submit test →" threw a TypeError and written tests could not be submitted. IDs added to the reset modal markup; function rewritten to toggle `.modal-visible` (the modal's real show mechanism, not `style.display`) and to temporarily swap the buttons' `onclick` properties (prevents the inline reset handlers double-firing), restoring them on cleanup. Verified in browser: submit modal opens with counts, Cancel restores reset-modal state, Submit shows results, normal reset modal unaffected.
2. **Model answers missing from written test results** — breakdown only read `q.modelAnswer`, but all 238 written questions across all subjects store it in `answer`. Now uses the same `q.answer || q.modelAnswer || q.sampleAnswer` chain as practice mode, with `\n→<br>` for plain-text answers. Also: student answer now HTML-escaped in the breakdown (was raw innerHTML), marks label reads `marks || maxMark || totalMarks` (HMS uses `maxMark`), question text runs through `formatQuestionText()`.
3. **PWA icons didn't exist** — manifest referenced `icons/icon-192.png`/`icon-512.png` but no `icons/` folder was in the repo (404s broke Chrome installability and the iOS home-screen icon). Generated both from `CramIT_Logo_Transparent.png` on a #FAF8F5 background (maskable-safe, no alpha). Manifest `theme_color`/`background_color` updated from stale dark `#0a0a0f` → `#FAF8F5`.

## Security pass — function auth + entitlement (2026-07-02, verified 2026-07-04)

All Cloudflare Pages Functions now require a verified Supabase JWT; identity is derived server-side, never from the request body.

- New shared module `functions/_lib/auth.js` (underscore prefix = not routed): `requireUser()` verifies the `Authorization: Bearer` token against `/auth/v1/user`; `corsHeaders()` replaces CORS `*` with an allowlist (`cramit-quiz.pages.dev` + `*.cramit-quiz.pages.dev` previews — add `cramit.com.au` there at domain launch); `getSubscriptionRow()`/`countSubjectSelections()` do service-role lookups.
- `create-checkout.js`: user_id/email from verified token; `plan_type` derived server-side from `subject_count` (client-sent plan_type ignored — can't buy base price for 7 subjects); subject_count bounded 2–20.
- `customer-portal.js`: Stripe customer looked up from the caller's own subscription row; body `customer_id` removed; `return_url` validated against app origins (open-redirect guard).
- `update-subscription.js`: subscription ID **and** subject count read from DB (`subject_selections` count is source of truth); body fully ignored. Still cancels when count ≤ 1.
- `mark-written.js`: quota charged to the verified user; body `userId` ignored.
- `upgrade-flex.js` **deleted** (dead since handleUpgradeFlex → customer portal; was an unauthenticated Stripe mutation).
- `index.html`: new `authHeaders()` helper; all 5 call sites send the bearer token; bodies no longer carry user_id/customer_id/subscription_id/plan_type; `x-user-email` header removed. `authHeaders()` races `getSession()` against a 4s timeout — Supabase's cross-tab auth lock (navigator.locks) can hang indefinitely in a profile with a stale lock, which froze the AI-marking spinner in owner testing; on timeout the call degrades to 401 + visible keyword-grid fallback instead of hanging.
- ✅ Entitlement migration run (2026-07-04) — `migrations/2026-07-02_subject_entitlement.sql` executed in Supabase SQL Editor. BEFORE INSERT trigger on `subject_selections` + unique (user_id, subject_id) index are live. Entitlement is now DB-enforced.
- ✅ Deployed auth verified (2026-07-04) — AI marking confirmed working end-to-end on the live site with a verified JWT (200, real feedback). Initial spinner-hang report traced to Supabase getSession() stale cross-tab lock, fixed with 4s timeout race (commit 30d463f). Still to test when convenient: full Stripe sandbox checkout (subscribe 2 subjects with `4242…` → unlock; billing portal opens) — timing note: `handlePaymentReturn` inserts selections after polling the webhook (~20s max); with the trigger live, a slower webhook means inserts fail once and the user re-taps the subject.

## iOS install banner (2026-07-02)

iOS never fires `beforeinstallprompt` (Apple allows no programmatic PWA install prompt), so the install banner never appeared on iPhones. New `maybeShowIOSInstallHint()` in `index.html`: on iOS + not standalone + not previously dismissed, reuses `#install-banner` with manual instructions — Safari gets "Tap [share icon] Share, then Add to Home Screen"; Chrome/Firefox/Edge/in-app browsers (CriOS/FxiOS/EdgiOS/Instagram/FB/TikTok UA match) get "Open this page in Safari" first. Install button hidden on iOS; dismiss persists via `cramit_ios_install_dismissed` in localStorage; running standalone suppresses the banner. Android/desktop `beforeinstallprompt` flow unchanged.

## Bug batch — review findings (c)(d)(e) (2026-07-04)

Three student-facing bugs from the code review fixed in `index.html`, all browser-verified:

1. **Trial double-count** — `nextQuestion()` charged the trial every time it advanced past a question, so Prev/Next over answered questions burned extra trial questions. New session-scoped `trialCounted` Set (reset in `startQuiz()`): each question index is charged at most once per session. Verified: answer Q1 → Next → Prev → Next leaves the counter at 1 (was 2).
2. **Stale AI feedback across sessions** — `aiResults`/`aiMarkingPending` were never reset, so feedback from a previous quiz could surface on the same index of a new one. `startQuiz()` now clears both; a `quizSession` counter also invalidates in-flight `/mark-written` responses that land after a new quiz starts (`tryAiMarking` captures the session and drops mismatched results).
3. **Payment return while logged out** — `handlePaymentReturn()` dereferenced `currentUser.id` with no guard and cleared the pending-subject keys before doing anything, so a student whose session didn't survive the Stripe redirect crashed the unlock flow and lost the record of what they paid for. Restructured: unlock logic extracted to `completePendingUnlock()`; when logged out, pending keys are KEPT, a "sign in to unlock" banner shows (new `showHomeBanner()` helper), and the auth listener calls `completePendingUnlock()` on the next sign-in (clears keys first, so double-fires no-op).

## Housekeeping pass (2026-07-04)

Repo cleaned and docs trued up:
- Deleted 27 orphaned diagram files (superseded crops, verified unreferenced by any subject JSON or index.html; checked 2025 Q22b first — the referenced `.png` exists, only the draft `.svg` was orphaned).
- Deleted `subjects/mathematics-advanced-2024.json` + its `index.json` entry (old agent schema — `questions/text/correct` — unloadable by the app).
- Deleted root scratch (one-off category-audit scripts + inputs, `_png_test/`, `_verify_mc/`, stray temp file) — all from completed audits already recorded here.
- `db/schema.sql` (which EXISTS — the old §6 tree wrongly said root `schema.sql`) extended with the Stage 7B `user_progress` table (reconstructed — verify against a `supabase db dump` when convenient) and a verbatim copy of the entitlement trigger.
- §6 file tree rewritten to match the actual repo (db/, scripts/, icons/, migrations/, _lib/; removed phantom sw.js/billing.js/subject-selector.html entries); pre-launch tasks #2–#4 marked done.
- Pricing decision: 6 subjects stays `base_plus` at $19.95 — forcing Unlimited would charge more ($19.99) than advertised; Unlimited begins at 7 subjects.

## CLAUDE.md restructure (2026-07-04)

Project CLAUDE.md had grown to ~84KB (~21,000 tokens), loaded in full on every session start. ~70% of it was session narrative rather than active instructions. Split three ways:
- **CLAUDE.md** — trimmed to current instructions, reference tables, and code patterns only (~6-7k tokens).
- **docs/HISTORY.md** (this file) — every dated session-log entry, verbatim.
- **docs/agents-plan.md** — the Blueprint V4 agent roster, staging/release strategy, and agent build order (§20/23/24 of the old file) — none of it is needed until Stage 9 starts.

Also added: `scripts/validate_subjects.cjs` (structural validation for all subject JSON — options count, answer index range, image references resolve) and a GitHub Action (`.github/workflows/validate.yml`) that runs it plus a syntax check on all Cloudflare functions on every push/PR — the project's first automated CI check.

## Content Agent rebuild (2026-07-04, Stage 9 Phase 1)

Full rewrite of `agent.js` — the old version wrote a schema the app couldn't load (`questions/text/correct` vs `mcQuestions/q/answer`), created a new subject file per paper (wrong: the app hardcodes subjects), and used retired models + the obsolete prompt-caching beta header. Design decisions:

- **Two-phase: triage then generation.** Owner's call — most papers share a structure (MC + written + diagrams) but some (English) are all-written and fit differently. Every discovered paper first gets a Sonnet-5 triage report (`docs/paper-reports/{subject}-{year}.md`): section breakdown, MC/short-answer/essay/diagram counts, fit assessment, recommendation. Opus-4-8 generation only runs when triage says MC fits AND the subject is one of the 4 the app supports.
- **Never creates new subjects.** Each new subject needs hand-written `getMC`/`getWritten` filter logic + a card in `index.html` — inherently a human job. For roadmap subjects (Maths Adv, English, sciences, Legal, Business, Economics) the triage report is the deliverable: a briefing for the future porting session.
- **Autonomy Level 1 from day one** (per `docs/agents-plan.md` risk table): new workflow `.github/workflows/content-agent.yml` (nightly 11pm Sydney + workflow_dispatch) commits to `agent/content-*` and opens a PR — never touches main.
- **Guardrails:** per-question local validation mirroring `validate_subjects.cjs` (bad questions rejected individually, listed in PR body); category/topic values must come from the subject's existing set — the generator can't invent filter values the UI doesn't know; dedupe against existing question text; diagram-dependent questions always skipped and listed for the manual crop pass; after merge the real `validate_subjects.cjs` runs and the file is rolled back on failure; `MAX_PAPERS_PER_RUN = 3` so the first-run backlog spreads over nights; failed PDF downloads aren't marked processed (auto-retry next night).
- **Models:** `claude-sonnet-5` discovery + triage, `claude-opus-4-8` generation. No `cache_control` — prompts are under the minimum cacheable prefix (see agent.js comment).
- **Known limitation:** PRs opened with the default `GITHUB_TOKEN` don't trigger `validate.yml`, so the workflow runs the validator itself as an explicit step. Swap in a PAT later if real CI on agent PRs is wanted.

Verified: `node agent.js --selftest` (14 offline checks: JSON extraction, question validation accept/reject, merge/dedupe/rollback on a temp file, repo validator green, all 4 subject files parse) — all pass; `node --check agent.js` clean; workflow YAML parses (js-yaml). Caught during selftest: `pdhpe-hms.json` has no `year` fields (HMS is topic-based) — `existingYears()` legitimately returns an empty set for it; state-file dedupe covers HMS instead. **Not yet run against the live API** — blocked on the `ANTHROPIC_API_KEY` GitHub Secret; first run should be manual (workflow_dispatch) with careful PR review.

## Question Expansion Strategy (Stage 3 decision, still partially pending)

Background: the Maths Standard 2 standalone file (v5.4) was expanded from 90 to 318 questions using a **variant** strategy — 3 variants per non-image question, each with different numbers and a different correct answer position (A/B/C/D rotated), totalling 4 questions per concept. The `variant: true` flag marks expanded questions; the HSC 90/Extended 318 toggle controls which set students see.

Decision by subject at the time:
| Subject | Variant approach | Reasoning |
|---|---|---|
| Maths Standard 2 | ✅ Done — 318 questions | Calculation questions = easy to variant. Rotate A/B/C/D as correct answer. |
| Multimedia | ⬜ Still pending — generate additional questions from NESA reference docs | Mostly conceptual definitions — can't just "change the numbers". |
| HMS | ⬜ Partially done via FA2 content expansion (Session 7-8) — not flagged `variant: true`, just new original topics | Protocol-based (RICER, TOTAPS); different injury scenarios/sports/body parts. |
| VET Construction | ❌ Skip entirely | Mostly visual (tool identification from images). Not worth generating variants without images. |

Variant rules for Maths (for reference, if ever extended to other subjects): skip any question with a diagram/image; write 3 variants per skippable question with different numbers and a different correct-answer position; each variant needs a full step-by-step `solution`; mark with `variant: true`; Python-verify all calculations before committing.

## Stage 11 — Cloudflare Migration (complete, May 2026)

Netlify is gone. CramIT now runs entirely on Cloudflare Pages. What was migrated: hosting + static files (Netlify → Cloudflare Pages `cramit-quiz.pages.dev`), serverless functions (`netlify/functions/` CommonJS → `functions/` ESM Cloudflare Pages Functions), function URLs (`/.netlify/functions/{name}` → `/{name}`), env vars (Netlify Dashboard → Cloudflare Pages Settings → Secrets). The lessons learned from this migration (no `wrangler.toml`, ESM only, `env.VAR` not `process.env.VAR`, UTF-8 PowerShell gotcha) are still load-bearing and live in `CLAUDE.md` §9, not here.

Still to do (optional, only if `diagrams/` outgrows git): R2 image storage — create bucket `cramit-assets`, upload `diagrams/`, add `IMAGE_BASE_URL` constant, prefix image paths in `renderQuestion()`.

## Side project — Olivier full-course HMS exam tool (2026-07-22)

Built `olivier-hms-exam-prep.html`, a second standalone study tool for one student (Olivier), covering the **entire Year 12 HSC Health and Movement Science course** — both Focus Areas, all 9 topics — as opposed to the earlier `olivier-hms-prep.html` which only covered a Focus Area 2 in-class assessment. Same 4-tab shape (Study / Practice MC / Written Help / Mock Exam) and reuses that file's CSS/JS engine wholesale, re-pointed at a new 9-topic question pool and 9 topic-colour CSS vars.

Source: the local ATAR Notes "HSC Health and Movement Science — Summary Sheets" book (photographed scan, not committed — copyright). Study notes were written in original wording from it; 11 genuine diagrams were cropped directly from the scan via `scripts/crop_olivier_hms_exam.py` (PyMuPDF, fraction-of-page clip crops, 160 DPI / q82 JPEG → `olivier-hms-exam-diagrams/`); publisher tables were rebuilt as clean HTML `<table>`s (CramIT "tables are HTML generated" rule). All **90 MC + 10 written** questions are original, written for this tool (not reused from `pdhpe-hms.json`).

Verified in the Browser pane: all 4 tabs switch; accordion opens all 9 topics; all 11 cropped images load (naturalWidth>0, none broken); practice scoring + explanation reveal works; mock exam renders 10 MC + 3 written (3/5/12-mark), timer + progress label update, submit produces MC review and written keyword-marking feedback with chips. Data validated via Node (90 MC across 9 topics, answer indices in range; 10 written = 4×3 / 4×5 / 2×12). Not part of the CramIT app — no auth/billing/Supabase, never integrated into `index.html`.

**Follow-up (2026-07-23):** Community Health topic — added an "SDGs in action" box with the four real-world "how" examples (outback-Australia telehealth = SDG 3, South-East Asia education = SDG 4, Sweden social services = SDG 10, Copenhagen green cities = SDG 11), spelled out "United Nations (UN)" in the SDG heading + a 2015/17-goals caption (accurate general knowledge, not in the ATAR Notes book — kept at owner's request), and added 3 matching Practice-MC (community pool 9→12, bank 90→93).

## Side project — Olivier HMS exam-format recalibration + content enrichment (2026-07-24)

Executed `docs/olivier-hms-exam-plan.md` in full (Parts A + B). The plan was written in a prior research session after reading NESA's own sample HSC paper and finding the tool's Mock Exam didn't resemble the real exam. Scope stayed inside `olivier-hms-exam-prep.html` only — no CramIT app/billing/auth/Supabase touched (same "do NOT integrate" rule as the file itself).

**Part A — recalibrated the Mock Exam to the real NESA HMS paper structure (100 marks, 3 sections):**
- Replaced the flat `WRITTEN_Q` array with `SECTION2_SLOTS` (7 slots Q21–27 matching the sample paper's exact 3/6/7/8/10/12/10 mark pattern, multi-part where the real paper is; **2 candidate versions per slot**, mock draws one each so the total is always exactly 56) and `SECTION3_BANK` (2 FA1 + 2 FA2 stimulus-based 12-mark extended responses; mock always draws one FA1 + one FA2 = 24). All prompts original wording, NESA style only (guardrail — never copied the sample paper's text).
- Section III stimulus is **original inline HTML** (a fictional-town health-stats table, an ageing-population table, two injury/training scenarios) — no copyrighted images, consistent with the project's redraw-don't-screenshot diagram policy.
- Rewrote `startMock`/`renderMockQuestions`/`selectMockOpt`/`submitMock`/`resetMock`: Section I now draws **20** MC (was 10); three visually distinct section banners; `markPart()` keyword-estimates marks per written part (fraction of keyword coverage → awarded/marks) and sums to a **/100** total (MC /20 + SII ~/56 + SIII ~/24). Timer is a **3-hour** H:MM:SS countdown (was 50 min). Written marks clearly labelled as an estimate.
- A.4 — relabelled the 3 Written-Help scaffold tabs to the real bands: **Short Answer (2–4)**, **Extended Answer (6–10, multi-part a/b)**, **Extended Response (12, Section III stimulus)** — each rewritten (verb→depth guidance, judgement requirement for Discuss/Analyse, stimulus-first structure) with new worked model answers, including a full 12-mark model on the Riverton SDG stimulus.

**Part B — content enrichment (curated, original wording; sources in the plan):**
- **Injury (thinnest topic, biggest win):** read the 43-slide `DLSR 12 HMS Depth Study` deck (`.pptx.pdf` — had a text layer, extracted with PyMuPDF, no vision render needed). Added **16 original MC** (sprain vs strain, indirect-injury causes, acute/chronic, stress fracture, simple/compound fracture, subluxation, rehab-stage order, active/passive mobilisation, mobilisation timing, conditioning/atrophy, cold-vs-heat, readiness indicators, sport-specific testing, painkiller ethics, psychological readiness) → injury pool **12→28**. Plus a Study-card note-grid (rehab stages in order; return-to-play & ethics).
- **Other FA2 topics:** curated **15 original MC** from `subjects/pdhpe-hms.json` idea material (HIIT, cardiac output, anaerobic threshold, reversibility, specificity, PAR-Q, beep test, mesocycle, inverted-U, strategy vs tactics, warm-up phase 1, pre-match meal, in-event carbs, fluid rate, cortisol/sleep) — kept the file's existing `{topic,q,options,answer,explanation}` shape (did **not** adopt CramIT's `optionExplanations` engine change — deferred to contain scope/risk). training 11→16, assess 9→11, groups 10→14, fuel 10→14.
- **FA1 Topic 1:** cross-checked against the YR11 `HMS_Short_Answer_All`/`HMS_Extended_Answer_All` flashcard decks (native PowerPoint text via zipfile/`<a:t>` regex). Found the card was missing the "what is health" foundations, so added **7 original MC** (WHO vs AIHW definitions, five dimensions, why definitions differ, dynamic nature, epidemiology, infant mortality) → health pool 10→17, and a Study-card "Defining health" + "Dynamic nature & epidemiology" note-grid.

MC bank overall **93 → 131**. Verified: Node data check (all 131 options length 4, answer indices in range, all have explanations, all topics map to a pill; `SECTION2_SLOTS` candidates sum to exactly 56; `SECTION3_BANK` has ≥1 FA1 + ≥1 FA2; paper = 20+56+24 = 100). Browser pane (no console errors): practice renders per topic with correct counts (injury 28, health 17, training 16, fuel 14); full Mock start→submit cycle assembles 20 MC + 7 Section II parts (56) + 2 Section III stimulus (24), full-keyword answers score **100/100**, empty submission scores **0/100**, 14 written-feedback cards render; Section III stat-table stimulus and the new Study note-boxes display correctly.

**Follow-up same day — ported the FA2 depth that was lost when the older FA2-only tool (`olivier-hms-prep.html`, 9 FA2 topics) was collapsed into the full-course tool's 5.** Owner flagged FA2 content still felt thin; gap analysis against the old tool found 5 missing study areas, all now added to the new tool with diagrams: (1) **Principles of training** — the 6 principles as a set + thresholds/warm-up/cool-down + SIT-vs-HIIT → training card; (2) **Tapering types** — step/linear/exponential-slow/exponential-fast volume-reduction bar diagram (ported `.taper-*`/`.tbar` CSS) + "why tapering works — metabolic adaptation" note → groups card; (3) **Psychology depth** — the **Inverted-U hypothesis SVG** (A/B/C points, recoloured to `--groups`), fine-vs-gross-motor arousal, trait-vs-state anxiety, strategies → groups card; (4) **Session structure** — **H-O-W-S-C-S-E** component grid (ported `.howscse-*` CSS) + the 4 warm-up phases in order → groups card; (5) **Nutrition depth** — nutrient timing & glycemic index (low-GI before / high-GI during), carbohydrate loading (>90-min events, 7–12 g/kg, needs a taper), key nutrients (electrolytes, iron), **RED-S** → fuel card. Minor gaps closed too: common fitness tests (VO₂ max, beep test, 1RM, skinfolds, Cooper run) → assess card; sleep growth-hormone/cortisol mechanism + basketball-shooting +9% stat, and synovial-fluid joint lubrication → fuel card. Added **19 matching Practice MC** (variety, individuality, overtraining/recovery, aerobic threshold %, SIT, cool-down, step-taper, taper metabolic reasoning, taper intensity-vs-volume, fine-motor arousal, trait/state anxiety, process concentration, inverted-U point C, HOWSCSE 'H', GI timing, carb-loading who/needs-taper, RED-S, iron). MC bank **131 → 150** (training 16→22, groups 14→22, fuel 14→19). Verified: Node data check green (all 150 options length-4, indices in range, Section II still 56); Browser pane no console errors, all new diagrams render (4 taper types / 21 bars, 7 HOWSCSE cells, 1 inverted-U SVG path), all new note-boxes present, practice renders for the enlarged topics.

**Content-accuracy audit (same day, owner-requested after spotting the pre-season figure).** Did a full pass over every numeric/factual claim in the study content, cross-checking the old FA2 tool and web sources. Two real errors found, both traced to figures copied verbatim from the ATAR Notes summary book during the original 2026-07-22 build (not introduced by the FA2 port — the port added *new* sections but didn't reconcile the pre-existing overlapping bullets, which is how these survived):
- **Pre-season "lasts 6–12 months"** — an ATAR Notes months-for-weeks typo. Standard HSC/S&C sources (pdhpe.net, teachPE, NSCA, Human Kinetics) all give **6–12 weeks** (8–12 weeks); it also can't coexist with a 6-month in-season + off-season inside a 12-month macrocycle. Corrected to ~6–12 weeks (up to 2–4 months in some sports). Fixed also: sub-phase durations restored to mesocycle 4–8 wk / microcycle 7–10 day, and tapering % (step ~33%+33%, exp-slow ~40–50% endurance, exp-fast ~20–30%) restored to the taper-type diagram.
- **"By 2026, ~22% of Australians over 65"** — wrong; AIHW/ABS put it at **~16% (1 in 6)** today, with ~22% only a ~2060s projection. Corrected in all three places it appeared (study card, an MC, and the Section III ageing stimulus).
Everything else verified accurate or defensibly sourced (life expectancy ≈83 / F85 / M81; First Nations gap ~8 yr; CVD ~45k deaths; cancer ~17% total burden; sleep 8–10 h; basketball +9% = Mah 2011; carb loading 7–12 g/kg / >90 min / needs taper; hydration 150–250 mL per 15–20 min; RICER ice 20 min / 2 h; Privacy Act 1988 / My Health Records Act 2012; SDGs adopted 2015). One minor wording note left as-is: "aerobic threshold 55–85% max HR" is really the aerobic training *zone* (a common HSC simplification, carried from the old tool). Verified: Node data check green (150 questions, Section II 56); web sources cited in-session.

**Same day, follow-up — Part C plan + Phase 1 execution (Y12 FA2 gap-fill).** Owner asked for a systematic plan to scale this up against the real syllabus reference site (hms.pdhpe.net) and cross-check the YR11 PPTX decks + CramIT's live app. Research found the tool only covers **Year 12** — Year 11 (Preliminary, FA1 "Health for Individuals and Communities" + FA2 "The Body and Mind in Motion", 33 subtopics) is entirely absent, and confirmed the YR11 Prelim flashcard PPTX (previously flagged as maybe off-topic) is in fact a direct Year 11 FA2 source. Also found 3 Year 12 FA2 subtopics with no clear home: Biomechanics, Role of Technology, Supplements & Micronutrients. Full plan written as Part C of `docs/olivier-hms-exam-plan.md`. Verified against the actual NESA sample HSC exam PDF (39 pages, full-text searched) that the HSC exam is **Year 12 content only** — zero Year 11 references anywhere in the sample paper — so Mock Exam stays Year-12-only; Year 11 will populate Study/Practice modes only. Owner also caught that Year 11 and Year 12 syllabi share some topics (flagged RICER) — checking this assumption against pdhpe.net found Year 11's "Role of First Aid" dot point is actually about general movement-related conditions (dehydration, stress fractures), not the RICER/TOTAPS/DRSABCD framework (that's Year 12-only) — a reminder to verify each suspected overlap individually rather than pattern-match by topic name.

Executed **Phase 1 (Y12 FA2 gap-fill)**: Biomechanics already adequately covered, no change. Added a **Role of Technology** note-box to the groups card (training innovations / equipment advances / recording & monitoring, per the syllabus's 3-category dot point) and a **Supplements & Micronutrients** note-box to the fuel card (protein, creatine/ATP-PCR, caffeine/CNS, micronutrient supplementation — framed with both benefit and limitation per NESA's "Discuss" command verb). +7 Practice MC (150 → 157). Verified: Node data check green, browser pane confirms both render with no console errors. Next: Y12 FA1 dot-point audit, then Y11 FA1 build, then Y11 FA2 build (per Part C's phased order).

**2026-07-24, follow-up — Part C Phase 2 (Y12 FA1 dot-point audit).** Read all 19 Y12 FA1 subpages on hms.pdhpe.net (`get_page_text` on each — dot points/captions were enough to diff against the existing note-boxes; no carousel screenshots needed) and diffed against the 4 existing cards (`health`/`system`/`tech`/`community`). Tech (4/4 subtopics) and most of health/system were already adequately covered — no change, matching Phase 1's pattern of not every flagged topic being a real gap. Confirmed real gaps, each traced to a specific NESA content point rather than a general "could add more" feeling:
- **Health card:** the "ATSI **+ one other group**" inequity content point had no second group at all — added a rural & remote case study (data/determinants/causes/actions) since pdhpe.net names it as its own worked example. The "CVD, cancer **+ one other condition**" content point only had 2 of the required 3 — extended the existing two-column disease table to a third column, Injury (pdhpe.net's own worked example for the third condition), rather than bolting on a separate box, per the "diff, don't just add" rule. Added a short note on the specifically **sociological** (not just behavioural) causes of risky health behaviour — masculinity norms and beauty-standard pressure — since the syllabus names "sociological causes" as its own sub-point.
- **System card:** added the "future opportunities" content point (rural/remote, ATSI, disability — all three named directly in the syllabus) and a "current & emerging challenges" note (rising GP/ED wait times, workforce shortages, the privatisation debate, ageing/chronic-disease pressure), both of which had zero prior coverage. Extended the funding note with the "healthcare vs prevention" spending trade-off and added My Aged Care as a named Commonwealth-funded program row in the existing schemes table.
- **Community card:** added Healthy Cities Illawarra — the syllabus's own named local example — to the existing SDGs-in-action box.

Every new numeric/factual claim was independently verified via websearch against AIHW before being typed in (per §C.6, the rule written after the pre-season/over-65 errors): life expectancy by remoteness (regional ~1–2 yrs lower, remote up to ~7 yrs lower than major cities), youth injury mortality (73% of 15–24 deaths, 2017–19; unintentional injury deaths fell 18→12 per 100,000 2007–2019), and Healthy Cities Illawarra's history (one of Australia's original 1987 WHO Healthy Cities pilot sites, still active across the Illawarra). +10 Practice MC (157 → 167: health 17→22, system 9→13, community 12→13). Verified: Node data check green (167 MC, all options length 4, all answer indices in range, all have explanations; Section II candidates still sum to exactly 56; Section III still has 2 FA1 + 2 FA2 candidates); browser pane — Health/System/Community cards all expand and render the new note-boxes/table columns correctly, Practice MC topic counts confirmed on-screen (22/13/13), no console errors.

**Same day, immediate follow-up — writing-quality fix.** Owner flagged that several of the new note-boxes/an MC question explained *why* content was added ("NESA requires...", "the syllabus specifically asks...", "named directly in the syllabus...") instead of reading as plain study content — meta-commentary bleeding into a student-facing tool. Rewrote 4 note-box bullets to drop the self-referential framing and swapped one MC question that tested syllabus trivia ("what does NESA require you to know") for one that tests actual content (rural/remote access barriers). No data-shape or count changes (still 167 MC). Verified: Node check green, browser pane loads with no console errors.

**2026-07-24, same day — Y12 FA2 full dot-point audit (owner-requested, not in the original phased order).** Owner asked "is EVERY topic covered for Y12 FA1 & FA2" — the honest answer was no: Phase 1 had only individually checked 3 of FA2's 17 subtopics (the ones flagged as having no obvious topic-card home); the other 14 had only been matched to a card by name/similarity, never actually read against pdhpe.net's dot points — precisely the risk §C.6 exists to prevent. Owner asked for the same full audit FA1 just got. Read all 14 remaining FA2 subpages individually and diffed against the 5 existing cards (`assess`/`training`/`groups`/`fuel`/`injury`). 10 of 14 were already well covered (Pre-Exercise Questionnaire, Types of Training, Relationships of Training Principles, Applied Strategies in Sports, Dietary Requirements, Sleep/Nutrition/Hydration, Recovery Strategies, Sporting Injury Prevention — near-exact matches to existing note-boxes/tables). Confirmed real gaps:
- **Assess card:** the syllabus's own named fitness tests, **Yo-yo test** and **Wingate test**, weren't listed among the "common tests" (only VO₂ max/beep test/1RM/skinfolds/Cooper run were there) — added both with a one-line description each.
- **Training card:** "Application of Training Principles" wants the 6 principles evaluated as applied to **both** aerobic **and** strength training specifically — the card listed the principles but never contrasted the two contexts. Added a 6-row table (progressive overload/thresholds/reversibility/specificity/variety/warm-up-cool-down × aerobic vs strength).
- **Groups card:** "Factors of Strategy Application" — nature of the sport, skill level/experience, environmental/game conditions, opposition strengths/weaknesses, psychological readiness/team cohesion, communication, physical conditioning/fatigue — was an **entire content point with zero prior coverage**. Added a full note-box.
- **Injury card:** "Drug Use and Injury Management" only had one existing line about painkiller ethics; the syllabus's health-implications/ethics/**drug-testing** sub-points (WADA, Therapeutic Use Exemptions) were completely absent. Added two note-boxes — verified WADA's Prohibited List and TUE approval criteria via websearch before writing them up.

+8 Practice MC (167 → 175: assess 11→13, training 22→24, groups 26→28, injury 28→30). Verified: Node data check green (175 MC, Section II still sums to exactly 56, Section III still 2 FA1 + 2 FA2); browser pane — Assessment/Training/Individual vs Group/Injury cards all expand and render the new content correctly, Practice MC counts confirmed on-screen (Assessment 13, Injury 30), no console errors.

**Same day, immediate follow-up — a real miss caught by the owner.** Owner pasted a screenshot of the actual "Benefits to health, participation and performance" carousel slide on the Performance/Fitness Testing page — content that `get_page_text` had only returned as a bare heading during the audit, with no bullet text (the exact text-extraction blind spot §C.1 already documented: slide prose is only visible in the images, not the extracted text). The audit had wrongly assumed the app's pre-existing "Why fitness testing differs by athlete" table already covered this slide without checking. It didn't: the syllabus's actual 3-vs-3 category framework is Health Monitoring / Motivation & Goal Setting / Program Design (recreational) vs Performance Optimisation / Talent Identification / Injury Prevention & Recovery (elite) — the app's table was only a loose paraphrase missing Health Monitoring and Talent Identification entirely. Rewrote the table to the correct 3-category structure (original wording, not copied), renamed "Yo-yo test" to its precise syllabus name **Yo-Yo Intermittent Recovery Test** in both the note-box and its MC question, and added 2 more Practice MC covering Health Monitoring and Talent Identification specifically. MC bank 175 → 177 (assess 13→15). Verified: Node check green, browser pane confirms the corrected table renders with no console errors, Practice MC count confirmed on-screen (Assessment 15). **Lesson for future phases:** when a page's `get_page_text` heading has no bullet content underneath it, that's a signal the real content is only in the slide images — screenshot it rather than assuming existing app content already covers it.

**Y12 (both focus areas) is now fully dot-point-audited against the real syllabus** (with the one correction above). Next: Y11 FA1 build, then Y11 FA2 build (per Part C's phased order).

**Same day, follow-up — table redesign for mobile + aesthetics.** Owner flagged that `.dtable`'s formatting was poor: a hard `min-width:520px` plus `overflow-x:auto` meant wide tables (the new 4-column chronic-conditions table especially) silently cut off content on phone screens with no visible scroll affordance, and the flat `#1A1A2E` header colour didn't match each topic card's own accent colour used everywhere else in the design. Owner also asked for a visual (screenshot-based) MCP review of `hms.pdhpe.net/year-12-health-and-movement-science` for comparison/reference — confirmed it's just the FA1/FA2 hub page (teal/navy banners linking out to the 36 subtopic pages), no tables of its own to reference there.

Fixed with a CSS-only responsive redesign, no JS: (1) added `--accent:var(--health)` (etc, one per topic) as an inline custom property on each of the 9 `.topic-card` wrapper divs; (2) `.dtable th` now uses `background:var(--accent,#1A1A2E)`, so every table's header colour automatically matches its own topic card instead of a flat unrelated navy; (3) above ~640px, tables render as a normal grid (unchanged from before, still horizontally scrollable as a fallback for genuinely wide ones); (4) below ~640px, added the standard CSS-only "stacked card" responsive-table pattern — `display:block` on all table elements including `<caption>` (missing that caused captions to shrink-wrap to ~80px and wrap one word per line — caught and fixed during verification), each `<tr>` becomes its own bordered rounded card, the first `<td>` becomes a coloured header bar (topic accent), and every other `<td>` gets a small uppercase label (from a new `data-label="..."` attribute) showing which column it belongs to. Added `data-label` to all 80 non-first `<td>` cells across the 8 `.dtable` tables in the file. No content or MC changes — data-shape unaffected (still 177 MC). Verified: browser pane at 375px mobile width — the 4-column chronic-conditions table now renders as fully readable stacked cards with no cut-off content, header colours confirmed to match each topic (blue for health, green for assess, etc); at desktop width, tables render as normal grids with topic-coloured headers instead of flat navy; no console errors.

**2026-07-25 — full accordion-based re-review of all 36 Y12 pages, root-cause fix for the audit method itself.** Owner clarified "review using MCP" meant systematically re-checking the actual pdhpe.net content pages, not a styling comparison — prompting a proper look at *why* the fitness-testing slide had been missed. Root cause: every hms.pdhpe.net subpage renders its real content inside a Bootstrap accordion (`.accordion-title`/`.accordion-collapse`/`.accordion-body`), collapsed by default. `get_page_text` only reads rendered/visible text, so every prior pass on this project (Phase 2, the Y12 FA2 audit) had been reading nothing but repeated collapsed-state boilerplate (the content-point statement, "Example(s)", NESA glossary) — not the actual explanatory paragraphs underneath each item. This was a much bigger miss than the single image-only slide caught the session before. Fixed by running `document.querySelectorAll('.accordion-title').forEach(t => t.click())` via `javascript_exec` before every `get_page_text` call, expanding all accordion items at once.

Re-read all 19 FA1 + 17 FA2 pages this way (per owner's instruction: "fa1 the review then fa2"). Confirmed corrections, primary source wins:
- **Ageing population projection**: "1 in 4 (25%) by 2050" replaces the "~22% by the 2060s" figure (itself a Phase-1 correction of an earlier ATAR Notes error) — ABS's own published series vary 25–28% across 2051–2071 depending on base year, so pdhpe.net's specific stated figure was adopted.
- **Hydration protocol**: rewritten to the mL/kg-based framework pdhpe.net states (5–10 mL/kg 2–4 hrs before, 400–800 mL/hr during, 125–150% of fluid lost after) replacing vague fixed volumes (500 mL/300 mL).
- One suspected conflict — carb-loading threshold ">60 min" on pdhpe.net vs the app's existing ">90 min" — was checked against sports-science literature (ScienceDirect, Gatorade Sports Science Institute) and found to be a **false alarm**: the app's existing two-box structure (in-event fuelling at >60 min, separate from true carbohydrate-loading at >90 min) was already more precise than pdhpe.net's single blended threshold. No change made — logged here per the "flag discrepancies rather than silently picking one" rule.

Confirmed real content gaps, all filled:
- **Health card**: sex-specific leading causes of death (coronary heart disease → males, dementia → females, AIHW); a full "healthy ageing" section — WHO's functional-ability definition, opportunities, and named strategies (Find Your 30, My Aged Care, Home Care Packages, Men's Sheds) that the content point had never actually had content for, only a thin "moderate gap" flag from Phase 2.
- **System card**: the equity-vs-equality distinction (a foundational PDHPE concept, entirely absent); Primary Health Networks + an ACCHO funding example; complementary healthcare expanded from one line to actual products/services lists plus a regulation-caution note; a critical-health-consumer "red flags" checklist (miracle-cure claims, unsupported buzzwords, no regulatory info); climate/environmental health as a named emerging system challenge.
- **Community card**: the "Closing the Gap" campaign (a major named Indigenous-health policy, absent from the community card despite being one of pdhpe.net's own two named "Australian Examples" for SDGs 3 and 10); Healthy Cities Illawarra rewritten with its actual SDG-by-SDG program breakdown instead of a generic description.
- **Groups card**: a new "Yearly training program — individual vs group, by phase" table — the syllabus's own "Compare a yearly training program" content point had only ever been answered by a single exam-tip line about competition frequency, never an actual phase-by-phase comparison.
- **Injury card**: the **HARM** acronym (Heat/Alcohol/Running/Massage — what to avoid during the RICER window), missing entirely despite being the standard companion acronym to RICER; **strict liability** and Sport Integrity Australia added to the drug-testing content.
- **Assess/fuel cards**: named pre-exercise screening tools (APEST, PAR-Q+) and the term "contraindications"; protein dosage figures (0.8 g/kg baseline, 1.2–1.8 g/kg for hypertrophy).

+13 Practice MC (177 → 190: health 22→24, system 13→17, community 13→14, assess 15→17, groups 28→29, injury 30→32). Verified: Node data check green (190 MC, all options length 4, all answer indices in range, Section II candidates still sum to exactly 56, Section III still 2 FA1 + 2 FA2, all 9 `.dtable` tables have matching `data-label` counts); browser pane — all 9 topic cards expanded and checked via `javascript_exec`/`getBoundingClientRect` (confirmed the new yearly-program table renders at the correct size/position with the groups card's indigo accent), Practice MC counts spot-checked on-screen match Node exactly (Health 24, Injury 32), no console errors throughout.

Folded the accordion-expand method into `docs/olivier-hms-exam-plan.md` §C.6 and the `feedback_pdhpe_visual_review` memory as the mandatory first step for any future pdhpe.net page read — this applies directly to the still-unstarted Year 11 build (Phases 3–4), which will lean on pdhpe.net even more heavily as the primary source. Next: Y11 FA1 build.

**2026-07-26 — Role of Technology refresh, falls stat highlighted, local pdhpe.net cache.** Owner asked for three small fixes plus a bigger workflow change. Fixes: (1) the groups card's "Training innovations" bullet now names **AR** alongside VR and **VBT (velocity-based training)** alongside smart resistance machines, matching pdhpe.net's own wording; (2) split the single yearly-program exam-tip into two, adding a dedicated "role & impact of technology" tip (benefit vs cost/equity/over-reliance framing) so the technology content gets its own exam-strategy note instead of sharing the yearly-program one; (3) the ageing card's falls stat ("leading cause of injury-related death for older Australians") is now visually flagged with a new `.stat-flag` CSS class (amber highlight, bold) instead of sitting as a plain bullet.

Owner also asked whether pdhpe.net's own per-page Revision Questions are covered anywhere in Practice MC or Written Help — checked one sample page (Impact of Ageing): its questions are all open-ended (Define/Explain/Justify/Propose), Practice MC is multiple-choice only, and Written Help is 3 generic scaffolds, not organised per-topic. Answer: no, they aren't explicitly mapped anywhere yet — flagged as a real feature-scope decision (a per-topic revision-question bank with original model answers) rather than assumed and built.

**Local pdhpe.net cache set up** (`pdhpe-net-cache/`, gitignored — never committed) to stop re-fetching the same pages every session. Contains 9 markdown files mirroring the app's own topic-card structure (`y12-fa1-health.md` through `y12-fa2-injury.md`) plus a README explaining the copyright rationale (hms.pdhpe.net is a commercial tutoring product, not NESA's own material — the existing "never copy verbatim into the app" rule was extended to this cache too: condensed original-wording notes, not raw scrapes, except revision-question prompts which are kept close to verbatim since they're short functional text needed for coverage-checking). Backfilled all 36 Y12 pages' notes from this session's accordion-expand extraction so the 2026-07-25 re-review's work isn't lost. Verified: `git status`/`git check-ignore` confirm the folder is excluded and untracked.

**2026-07-26 — Revision Questions feature built (the previously-flagged undecided item).** Owner confirmed both open design questions: placement = a new "Revision Questions — test yourself" block inside each existing Study topic-card accordion (not a new tab), and scope = all 9 Y12 topic cards in one pass rather than one cluster first. Curated 2–3 highest-value revision-question prompts per pdhpe.net content point (from the `pdhpe-net-cache/` files' `Revision Qs:` lines, picking the most distinct command-verb/content combinations rather than porting every listed prompt) and wrote an original model answer for each — grounded only in facts already verified and present in the app/cache (no new unverified numeric claims introduced), consistent with the "curate, don't bulk copy" and "primary source wins" rules in `docs/olivier-hms-exam-plan.md` §C.6. 74 revision questions total across the 9 cards (health 13, system 12, tech 7, community 5, assess 6, training 7, groups 8, fuel 6, injury 10). Engine: new `.revision-block`/`.revision-item` CSS (click-to-reveal answer via `max-height` transition, chevron rotates) and a `toggleRevision(el)` JS function, reusing the existing accordion visual language. Inserted as the last element inside each topic-card's `.topic-body`, after the existing exam-tip/eg-box. Verified: Node check confirms 9 `.revision-block` elements, 74 matched `.revision-item`/`.revision-q`/`.revision-a`/`toggleRevision(this)` counts, and balanced `<div>` tags (614/614); browser pane confirmed click-to-reveal opens and closes correctly (tested first and last-card items), no console errors, longest answer (459 chars) renders well under the `max-height:400px` cap so nothing is clipped, checked at both desktop and mobile (375px) viewport widths.

**2026-07-26 — "Study & Writing Help" prototype ported into the real CramIT app (index.html), HMS only.** Owner asked whether `olivier-hms-exam-prep.html`'s Study tab and Written Help tab could be brought into the actual live app (not the side-project file itself — CLAUDE.md's "never integrate" rule stays intact; only the already-original wording those tabs contain was reused as a content source). Planned first (Explore → Plan → Code, per the workflow): research confirmed `subjects/*.json` tolerates unknown top-level keys (`scripts/validate_subjects.cjs` only ever reads `mcQuestions`/`writtenQuestions`), the quiz engine's `currentMode`/`renderQuestion()` is built around one-question-at-a-time flow and a poor fit for prose, and access gating happens once in `renderPicker()`'s `inTrial` check — so the safest design was a new sibling view, not a third quiz mode.

Built: (1) `subjects/pdhpe-hms.json` gained two new top-level keys, `studyNotes` (9 topics, each with `noteBoxes`/`examTips`, programmatically extracted from the olivier file's 9 `.topic-card` blocks via a one-off Python regex script rather than hand-transcribed, to avoid transcription errors across ~50 note-boxes) and `writingScaffolds` (the 3 generic mark-band scaffolds — Short/Extended/Extended-Response — with steps and one model answer each). Purely additive: `git diff --stat` showed 409 insertions, 0 deletions. (2) `index.html` gained a new `#study-view` sibling to `#picker`/`#quiz` (not a new `currentMode` branch), a new "Study & Writing Help" `.mode-card` in `renderPicker()` reusing the exact same `inTrial` flag that already gates Written Response (no new access-control logic), and `openStudyView()`/`showStudySection()`/`renderStudyNotesHtml()`/`renderWritingHelpHtml()` JS functions plus new CSS (`.study-card`, `.study-toggle`, `.scaffold-step`, `.wh-anchor`) built entirely from existing design tokens, reusing the existing `.model-answer` reveal-box pattern for scaffold model answers.

Scope deliberately narrow (v1): HMS only, text-only (no diagrams, no revision-Q&A accordion — those need image re-hosting and a bigger content job, logged as follow-ups), gated identically to existing premium modes (no free-content loophole introduced).

Verified: `node scripts/validate_subjects.cjs` green (618 MC/238 written across all 4 subjects, unchanged from before this change — confirming the new keys didn't disturb existing data); browser preview (`npx serve` via `.claude/launch.json`) driven through `javascript_exec` since the Browser pane wasn't visually displayed this session — confirmed via DOM inspection: the new mode-card renders correctly locked (🔒, `opacity:0.45`, `cursor:not-allowed`) for a logged-out/non-subscribed user, identical treatment to the existing Written Response card right above it (gating parity); all 9 Study topic cards render and expand, first card's 10 note-boxes + exam-tip text confirmed present; Writing Help's 3 scaffold cards render with correct badges, model-answer reveal toggles correctly; regression check confirmed existing MC (165) and Written (35) quiz modes for HMS still render unchanged; mobile viewport (375px) confirmed no horizontal overflow and toggle/card-header touch targets both ≥52px per the project's touch-target rule.

**Same day, corrected — owner rejected the first prototype twice, both times for good reason.** First correction: "Study & Exam Mode" was not meant to be a third mode-card living inside the existing picker — it's meant to be the **front page** of the HMS subject itself. Reworked `renderPicker()`: for subjects with `hasStudy`, it now renders a Study Mode/Exam Mode toggle first, where **Exam Mode is exactly today's picker** (`renderExamModeHtml()`, a pure extraction of the old `renderPicker()` body, byte-for-byte the same UI) and **Study Mode** is the new content with its own nested Notes/Writing Help toggle. `#study-view` (the separate full-screen div from the first attempt) was deleted entirely — everything now lives inside `#picker`. Gating reworked to a free-preview model instead of the original all-or-nothing lock: `STUDY_FREE_TOPIC_COUNT` (1) topic is always free so non-subscribers get a real taste; the rest show locked (🔒, no body HTML rendered into the DOM) and tapping opens the subscribe modal; Writing Help is fully gated behind its own panel. Diagrams (14 images) were also ported into `/diagrams/` at this point, since the owner asked for parity with the standalone tool's pictures.

Second correction, worse: comparing the CramIT rendering side-by-side against `olivier-hms-exam-prep.html`, the owner found the content didn't actually match — because the first extraction script (regex-based) had flattened the standalone's structure into flat `noteBoxes`/`images`/`examTips` arrays, discarding two things the source actually does: pairing note-boxes into a 2-column `.note-grid`, and interleaving note-grids/diagrams/comparison tables in a specific sequence. It also silently dropped every `.dtable` comparison table and never ported the `.stat-flag` CSS (so a highlighted sentence rendered as plain unstyled text) — both real, silent content losses, not just cosmetic. Root-cause fixed by rewriting the extraction with BeautifulSoup instead of regex, walking the actual DOM tree so each topic's content is captured as an **ordered `blocks[]` array** (`noteGrid` with 1–2 boxes, `image`/`imageGrid`, `table`, `examTip`, `linkIt`) that preserves both order and pairing exactly; `renderStudyBlock()` in `index.html` switches on `block.type`. Ported the missing `.study-dtable` (the proven responsive mobile-stacked-card table CSS, adapted from the standalone's `.dtable`) and `.stat-flag` CSS. The owner also separately flagged that the Notes/Writing Help toggle buttons were an ad hoc bordered-pill design ("amateur hour") — replaced with the app's own existing `.seg-control`/`.seg-slider` segmented control (the same component already used for Year/Category/Assessment filters), first at full width (still "huge" per feedback) then corrected to the default compact fit-content sizing that Assessment itself uses.

Third round of corrections, from a direct visual diff against a standalone screenshot: the app was still missing the 74 click-to-reveal **Revision Questions** entirely (never ported — flagged as deferred in the first pass, but the owner wants them included), the single "🔗 Link it" callout (same oversight), `.study-note-box` had no background/padding at all (the standalone's `.note-box{background:#F8F9FA;border-radius:10px;padding:12px}` was never ported, so note-boxes rendered as bare text with only grid-gap between them), and the paired stretching images (dynamic-vs-static / PNF) weren't uniform height because the extraction never captured the original `<img style="max-height:165px;width:auto">` inline style the owner's own prior session had already solved. Fixed all four: `revisionQuestions:[{q,a}]` added per topic (replacing the old flat `examTips` array — exam-tip and link-it are now just more `blocks[]` entries, `examTip`/`linkIt`, so ordering is unified with everything else), `.study-note-box` given `background:var(--surface2);border-radius:10px;padding:12px` (adapted to CramIT's own token instead of copying the standalone's hardcoded grey), and `image_obj()` in the extraction script now captures and passes through the original `style` attribute verbatim instead of re-deriving new sizing math.

Verified this round: `node scripts/validate_subjects.cjs` green throughout every JSON rebuild; `javascript_exec` confirms per-topic `blocks[]` kind-sequences now match the source exactly (spot-checked all 9 topics); revision toggle opens/closes with the correct `max-height` transition; both stretching images measured at exactly 165px height; note-box background confirmed via `getComputedStyle` as `--surface2`; screenshots (once the Browser pane cooperated — it repeatedly stopped compositing frames mid-session, a recurring friction point this session) confirm the 2-column pairing, topic-accent-colored headings, the amber `.stat-flag` highlight, and the blue-accented chronic-conditions table all render correctly and match the standalone. **Lesson for future ports of this kind:** don't build a bespoke flat schema for "porting content" — walk the source DOM with a real parser and preserve its structure (order, grouping, inline styles) directly; a schema invented ahead of actually looking at the full structure will silently drop things a flat regex pass can't see.

- **Automated billing test harness added (2026-07-27)** — 48 tests across 5 files in new `tests/` directory, run via Node's built-in test runner (`node --test tests/*.test.js`, `npm test`) — no new dependency added deliberately, since the project has no other test tooling yet. Covers: (1) pricing-tier math in `create-checkout.js`/`update-subscription.js` — `getPlanType`/`buildLineItems`/`buildUpdatedItems` exported (additive `export` keyword only, no behavior change) so tier boundaries (2/6/7/8+ subjects) and Stripe line-item tier-transition diffs (e.g. `base_plus → unlimited` deletes base+extra, adds cap) are pinned without hitting real Stripe; (2) `_lib/auth.js` — `corsHeaders` origin allowlist (incl. a lookalike-domain rejection case), `requireUser` token verification paths, `getSubscriptionRow`/`countSubjectSelections`, all via a temporary `global.fetch` override, restored in `afterEach`; (3) auth-gate test across all 4 billing/AI functions — POST with no `Authorization` header returns 401 before any Stripe/Supabase/Claude call is reached (confirms the CLAUDE.md invariant that identity never comes from the request body); (4) `mark-written.js` quota logic (sub-not-found, no-plan, quota-reached, 30-day reset, active-status-but-plan-not-synced-yet webhook-delay fallback) via mocked Supabase responses, stopping before the real Claude call. Also added a `Run billing function tests` + `Install dependencies` step to `.github/workflows/validate.yml` so this runs on every push/PR alongside the existing subject-JSON and function-syntax checks. **Explicit scope boundary**: none of this touches the real Stripe API, real Supabase Auth API, or real Claude API — it verifies this codebase's own logic and request-shaping, not that Stripe/Supabase/Anthropic still behave the way the code assumes. The manual Stripe-sandbox checklist in CLAUDE.md §12 (full payment flow, webhook, customer portal) is still required before any billing change ships. Verified: `npm test` → 48/48 pass; `node scripts/validate_subjects.cjs` and per-file `node --check` on all `functions/*.js` still green after the `export` additions.

- **"Manage subjects" — remove-a-subject feature added (2026-07-27)** — While manually running through the billing test cases above, the owner found there was no way to reduce their subject count anywhere: not via the Stripe Customer Portal (which by design in this app only exposes payment method/invoices/cancel — plan-switching there would bypass the subject-count-driven pricing entirely) and not via the app itself. Code search confirmed: `addSubject()` in `index.html` inserts into `subject_selections`, but no corresponding remove/delete existed anywhere — clicking an already-subscribed subject card only opens the quiz, and the profile sheet had just "Billing & subscription" and "Sign out". Notably, the existing swap-prompt banner (shown at the 7-subject cap) already told users to *"Deselect a subject to swap it"* — a feature that didn't exist. Backend support (`update-subscription.js`'s `buildUpdatedItems` downgrade transitions) was already fully built and unit-tested from the harness above; it was simply unreachable. Chose a dedicated "Manage subjects" bottom sheet (opened from the profile sheet) over an inline X on subject cards — the cards are already whole-card-tappable on a touch device, so a small delete icon in that same tap target risked accidental billing changes; a separate management surface with an explicit confirm step matches how Netflix/Spotify-style "manage add-ons" screens handle this. Implementation: `manage-subjects-btn` in the profile sheet (visible only when subscribed with ≥1 subject), a new `manage-subjects-sheet` listing each subject with a Remove button, `confirmRemoveSubject()` reusing the existing `reset-modal` (same swap-handlers-then-restore pattern as `showSubmitTestModal`, so no new confirm-dialog styling was introduced), and `removeSubject()` which deletes the `subject_selections` row, calls `/update-subscription` if on a paid plan, then calls `loadUserState()` for authoritative state (a removal can cancel the whole subscription if it was the last subject — Stripe/Supabase are the source of truth, not optimistic local state). `subject_selections` RLS already granted `delete` for `auth.uid() = user_id` (`db/schema.sql`) and the entitlement trigger is INSERT-only, so no DB changes were needed. Verified: syntax-checked the modified inline `<script>` blocks; drove the actual page with Playwright against a static file server (`chromium-1194` from `/opt/pw-browsers`) with `currentUser`/`userSub`/`userSubjects` set directly via `page.evaluate()` to simulate a logged-in Unlimited subscriber with 3 subjects (no real Supabase/Stripe session available in this sandbox) — confirmed the Manage Subjects button appears, the sheet lists all 3 subjects with working Remove buttons, the confirm modal shows the correct "Remove {name}?" text and prorate/cancel warning copy, Cancel closes it and fully restores the reset-modal's original reset-quiz text/handlers (no state leakage), and the only console errors were the sandbox's blocked Google Fonts CDN request (pre-existing, unrelated to this change — confirmed by reproducing it on a plain page load with none of the new code triggered). Did NOT click "Yes, remove" in this sandbox, since that hits real `/update-subscription` + Supabase, which aren't reachable here — **the actual removal flow (delete + Stripe proration + possible cancellation) still needs a live run through the Stripe-sandbox checklist in CLAUDE.md §12/pre-launch checklist #1** before this ships to students.

- **Manage Subjects merged, live-tested, then reworked for deferred downgrades (2026-07-27)** — PR #1 (test harness + Manage Subjects) was merged straight to `main` at the owner's explicit request, skipping the usual preview-first step, so it could be tested against the real production Cloudflare deployment. Live test (removing Multimedia from a 3-subject Unlimited-tier plan) surfaced two things: (1) the price dropped and Multimedia access was revoked *immediately*, with an implicit Stripe proration credit — the owner wants downgrades to defer to the end of the paid billing period instead ("I don't want to refund money prorated... common practice and better for revenue continuity" — i.e. upgrade-now/downgrade-at-renewal, not immediate-refund); (2) the removed subject's card fell back to showing fresh "10 free trial questions" copy despite having real answer history — investigation confirmed no data was actually lost (`user_progress` only cascades on account deletion, `updateStats()` sums across all subjects regardless of subscription) but the card-badge logic only displayed subscribed-stats when `canAccessViaSubscription()` was true, so it silently fell through to the trial branch. Also requested: verify the case of removing one subject and adding a different one where the net subject count is unchanged (a same-tier swap) — should trigger zero billing changes.
  - **Deferred downgrades**: the natural place to apply this — the Stripe webhook handler `clever-action` — turned out to be a Supabase Edge Function with no source in this repo, so a DIY "apply at renewal via webhook" approach wasn't viable from here. Used Stripe's native **Subscription Schedules** instead, entirely self-contained in `update-subscription.js`: on a downgrade, a 2-phase schedule is created/updated (phase 1 = current items until `current_period_end`, phase 2 = the new lower items, `iterations:1` + `end_behavior:'release'` so it hands back to a plain subscription afterward) — no proration, no webhook needed, Stripe applies phase 2 automatically at the real renewal boundary. Two new nullable columns were required (owner ran the SQL manually in Supabase SQL Editor, confirmed before the code was pushed): `subscriptions.stripe_schedule_id` (tracks an in-flight schedule across requests, so repeat calls update/release it instead of creating duplicates) and `subject_selections.pending_removal_at` (stamped by the server, with the service-role key, to the authoritative Stripe `current_period_end` — access is checked client-side as "active if this is null or still in the future," with lazy self-cleanup of expired rows on the next `loadUserState()`, so no cron is needed for either the access side or the pricing side).
  - **Reconciliation is fully stateless/idempotent**: every `/update-subscription` call recomputes the *target* tier from scratch — subject rows with `pending_removal_at` set are excluded from the target count regardless of which action triggered the call — then reverse-derives the *currently billed* tier from live Stripe subscription items (`getCurrentTierInfo`) and compares (`compareTiers`): target tier higher → apply immediately (releasing any pending-downgrade schedule first, exactly as before this change); lower → create/update the deferred schedule; identical → release any schedule with zero Stripe calls. This is what makes the **same-tier swap case correct without any special-casing**: removing Multimedia (3→2, a real downgrade, schedule created) followed by adding VET (target recomputed as 3 again, matching current billing) resolves to "same" and releases the schedule — while Multimedia's own `pending_removal_at` is untouched and still lapses on its original schedule, since each row's grace period is independent of what else gets added later. Covered by new unit tests including the exact swap sequence (`tests/update-subscription.test.js`, "End-to-end tier reconciliation" block).
  - **Client changes**: `removeSubject()` no longer deletes the `subject_selections` row directly (needed the server's service-role key to stamp the real period end, avoiding a new RLS grant) — it just posts `{action:'remove', subject_id}` to `/update-subscription`. `addSubject()` still inserts client-side for the common case, but now also posts `{action:'add', subject_id}` so the server can clear a stale `pending_removal_at` if the same subject is re-added before its grace period ends (undo). `loadUserState()` now filters `userSubjects` by `pending_removal_at` (access continues until that timestamp) and tracks a parallel `userSubjectsPending` map for UI display. Manage Subjects sheet shows "Ends {date}" instead of a Remove button for subjects already pending, and the confirm dialog copy was updated to describe the deferred behavior instead of immediate proration.
  - **Card-badge fix (point 2)**: gated on `subStats.seen > TRIAL_LIMIT` — answering more questions than the trial ever allows is only possible via real subscribed access, so this cleanly distinguishes "was subscribed, now expired" (shows real grayed-out stats + "not currently subscribed") from a genuine trial-only user (unchanged trial-progress copy), without needing to track which mode each historical answer was given under.
  - **Explicit scope boundary**: the Subscription Schedule Stripe API calls (`createDowngradeSchedule`/`updateDowngradeSchedule`/`safeReleaseSchedule`/`safeCancelSchedule`) are new, nontrivial Stripe surface this codebase hasn't used before, and could not be verified against live Stripe from this sandbox — only the pure decision logic around them (`getCurrentTierInfo`, `compareTiers`, `buildPhaseItems`, `getExtraQty`, and the full reconciliation sequence for the swap case) is unit-tested (19 new tests, 67/67 total passing). **A live Stripe Sandbox run through the full add/remove/swap/cancel sequence is required before this ships** — flagged explicitly to the owner, who was told to run it against the next deployment.
  - Verified: `npm test` → 67/67 pass; `node scripts/validate_subjects.cjs` and `node --check` on both modified `functions/*.js` files green; drove the actual page with Playwright simulating a subscriber with one subject mid-grace-period (`pending_removal_at` 2 days out) — Manage Subjects correctly showed "Ends {date}" instead of Remove for that subject and "2 subjects on your plan · 1 ending soon" in the summary; separately verified the card-badge fix against both a truly-expired-with-history subject (showed "15 seen · 67% · not currently subscribed") and a genuine mid-trial user (unchanged "3/10 trial used · 7 left" — confirms the fix didn't regress the common trial case).

- **INCIDENT — deferred-downgrade schedule feature broke subject removal live, rolled back (2026-07-27)** — Within minutes of the merge above going live, the owner tried removing a subject on a real 4-subject plan and got "Could not remove subject — please try again" every time. This session has no Cloudflare Pages Function log access, so the exact Stripe error from `subscriptionSchedules.create`/`.update()` couldn't be captured before acting — given every live removal was failing, the priority was restoring working functionality first, diagnose the Stripe Subscription Schedule bug later without production pressure. Rolled `functions/update-subscription.js` and `functions/_lib/auth.js` back byte-for-byte to their state immediately after PR #1 (commit `05fe4e5`, the last known-good deploy — immediate proration on downgrade, no schedules), reverted the two test files that referenced the now-removed schedule functions, and reverted `index.html`'s `addSubject`/`removeSubject`/`loadUserState`/Manage-Subjects-sheet code to match (client no longer sends `{action, subject_id}` or expects deferred/pending state, since the server no longer understands it). **Kept** the card-badge fix (Point 2 above) — it's independent of the billing/schedule logic and still correct — reapplied by hand on top of the reverted file. The two new DB columns (`subscriptions.stripe_schedule_id`, `subject_selections.pending_removal_at`) were left in place (harmless, unused, nullable — no data was written to them since nothing ever succeeded) rather than dropped, since nothing currently reads or writes them and reverting a schema addition carries more risk than benefit here.
  - Net effect: subject removal is back to the pre-incident behavior — immediate Stripe proration/credit, immediate access change — exactly as it worked right after PR #1, before the deferred-downgrade attempt.
  - Verified: `npm test` → 48/48 pass (back to the pre-schedule-feature count); `node --check` on both functions clean; `node scripts/validate_subjects.cjs` clean; confirmed via `git diff 05fe4e5` that `functions/update-subscription.js`, `functions/_lib/auth.js`, and `index.html` (except the deliberately-kept card-badge fix) are byte-identical to the last known-good commit.
  - **Lesson for next time a Stripe API surface this codebase has never used before (Subscription Schedules, in this case) gets built**: ship it behind a manual test on a real Stripe Sandbox subscription BEFORE merging to the live branch, not after — unit tests on the surrounding decision logic (which is all that could be verified here, see the scope-boundary note above) do not substitute for actually calling the new API once. If Cloudflare Function log access becomes available in a future session, use it immediately when a live billing action starts failing, before reaching for a rollback — this session had to choose speed over precise diagnosis because no log access was available.
  - **Still open**: the actual bug in the Subscription Schedule calls was never identified (no log access) — deferred-downgrade billing is NOT implemented right now, back to immediate proration. If this is revisited, test the exact `subscriptionSchedules.create({from_subscription})` → `.update()` sequence against a real Stripe Sandbox subscription first, in isolation, before wiring it into `update-subscription.js` again.

- **Deferred-downgrade feature restored for a properly-diagnosable retry (2026-07-27)** — Owner asked why the feature couldn't just be tested again, correctly pointing out the real blocker wasn't "can't test," it was "can't see why it fails" (no Cloudflare log access this session). Checked whether an MCP connector could provide that: the official "Cloudflare Developer Platform" connector (searched the full registry, no other Cloudflare option exists) covers D1/R2/KV/Hyperdrive/Workers resource management only — no log/observability tool at all, and confirmed via `workers_list` that Pages Functions projects aren't even visible through it (it's scoped to standalone Workers). Real-time log tailing (`wrangler pages deployment tail` / the dashboard's live logs) also wouldn't work through this session's proxy regardless, since it's WebSocket-based and the proxy doesn't support upgrades. So: restored `functions/update-subscription.js`, `functions/_lib/auth.js`, `index.html`, and both test files byte-for-byte from commit `992d685` (the pre-rollback schedule-feature state — confirmed via empty `git diff 992d685`), then added **temporary diagnostic error surfacing** on top before redeploying: the server's catch block now returns Stripe's `err.type`/`err.code`/`err.param` alongside `err.message` (Stripe SDK errors carry these, plain `err.message` alone often isn't enough to pinpoint a schedule-API misuse), and both `addSubject()`/`removeSubject()` now `alert()` that full detail directly to whoever is testing, instead of a generic "please try again." This makes the next failure (if any) immediately readable on-screen without needing log access at all. Marked `TEMPORARY` in both files — meant to be removed once the schedule path is confirmed working, not left as permanent UX.
  - Verified: `npm test` → 67/67 pass; `node --check` on both functions clean; syntax-checked `index.html`'s script blocks; `node scripts/validate_subjects.cjs` clean.
  - **Still open**: same as before — the Subscription Schedule calls themselves have not been proven against live Stripe. This restore is specifically to get a second attempt with real diagnostics, not a claim that the bug is fixed.

- **Deferred-downgrade CONFIRMED WORKING live; "Keep" button added; a pre-existing auth bug surfaced (2026-07-27)** — With Cloudflare's real-time log JSON now viewable (owner pasted an actual invocation log — turned out the log itself was just showing a 401, since the Supabase cross-tab session lock had gone stale again, the same class of issue `authHeaders()` already works around with a timeout) and, separately, the Supabase MCP connector connected this session, both blockers from earlier in the day were resolved at once. Queried the live DB directly (`execute_sql` on the `ohqtefjawaphtsebnaxg` project): Multimedia's `subject_selections` row showed `pending_removal_at: 2026-08-27 23:28:07+00` (matching the real Stripe billing period) and the `subscriptions` row had a populated `stripe_schedule_id` — **the Subscription Schedule deferred-downgrade feature is confirmed working end-to-end against Stripe Sandbox.** Cross-checked Supabase's auth logs (`get_logs`, service `auth`) and found a `token_revoked`/refresh-token-rotation event at 23:26:29, ~90 seconds before the successful stamp — this is almost certainly why the owner then saw Manage Subjects fail to reflect the change and briefly appear logged out when trying to interact further: the client-side session handling didn't survive the mid-session token rotation cleanly. This is the same pre-existing `navigator.locks` fragility already called out in `authHeaders()`'s code comment, not a bug in anything built today — logged as a real, separate issue worth hardening in a future session, not fixed here.
  - **Product gap found and fixed**: the owner pointed out there was no way to cancel a pending removal from Manage Subjects — a subject showing "Ends {date}" had no action at all, so the only way back was waiting out the full grace period. Added a **"Keep" button** next to the date on any pending row, wired to a new `undoRemoveSubject()` — deliberately NOT reusing `addSubject()` directly (which also opens the quiz picker and hides the upgrade prompt, wrong UX from this screen) but calling the same server contract (`{action:'add', subject_id}`) that already clears `pending_removal_at` and re-syncs the Stripe schedule/items, since that path already existed and was already covered by the reconciliation logic.
  - Verified: `npm test` → 67/67 pass; `node --check` clean; syntax-checked `index.html`; drove the Manage Subjects sheet with Playwright (subject mid-grace-period) — confirmed the pending row now shows both "Ends {date}" and a working "Keep" button, other subjects still show a normal "Remove" button, only the pre-existing sandbox network errors present.
  - **Net status of the deferred-downgrade feature after this session**: billing logic confirmed working live; access-continuation confirmed working (Multimedia stayed accessible through its grace period); "Keep"/undo now available. Outstanding: the pre-existing auth-session-rotation bug (separate issue, not blocking this feature, but responsible for the confusing display symptoms during testing) and removing the `TEMPORARY` diagnostic error-surfacing once confidence is higher.

- **"Keep" button confirmed live; session closed out (2026-07-27)** — Owner clicked "Keep" on the Multimedia row (pending removal from earlier testing) and checked Supabase's Table Editor directly: both `subject_selections.pending_removal_at` and `subscriptions.stripe_schedule_id` came back `null`, confirming the undo path works end-to-end (schedule released, pending flag cleared, price/access restored to the original tier) — the last open item from this session's billing work. Full status of the deferred-downgrade feature after this session: remove → defer confirmed, access-continuation confirmed, keep/undo confirmed, add (upgrade) unaffected. Still open: the exact "remove one + add a different one, net same subject count" swap (schedule *update* rather than *release*) is unit-tested only, not yet proven against live Stripe; and the pre-existing Supabase auth-session-rotation fragility (separate bug, noted above) is unfixed.
- **Next session's focus, per owner** (also reflected in CLAUDE.md §11 roadmap): (1) extend the Study Mode/Exam Mode framework (currently HMS-only prototype) to the other three subjects in phases — **P1 = Mathematics Standard 2, P2 = VET Construction**, then Multimedia; each phase needs the standalone-reference-file extraction pass described in §7/§10 before porting into `studyNotes`/`writingScaffolds`. (2) A dedicated design/aesthetics review across the app — the warm earth-tone tokens are locked (§15) but overall visual polish hasn't had a focused pass since the early build stages.

**2026-07-28 — Study Mode extended to Mathematics Standard 2 (pilot topic: F1 Money Matters).** Owner asked to extend Study Mode past HMS, picking up P1 from the phased plan above. Unlike HMS, there was no existing standalone prose file to port from, so this is original content authoring — confirmed with the owner up front (write-from-scratch, syllabus-grounded, one pilot topic before doing all 16 Maths categories). Scope-checked against the official MS-F1 Money Matters syllabus structure (three subtopics — F1.1 Interest & depreciation, F1.2 Earning & managing money, F1.3 Budgeting — confirmed via websearch of NESA/curriculum.nsw.edu.au, not copied, used only to check nothing was missed) and cross-checked against the app's own already-verified F1 content (30 MC, 10 written, 13 Formula Hint tips) so the new notes don't contradict anything already live.

Confirmed the Study Mode engine (`renderStudyBlock()`, `renderStudyNotesHtml()`, `hasStudy` flag) built for HMS is fully subject-agnostic — no HMS-specific field is read anywhere, `focusArea` is unused by the renderer. So enabling it for Maths was: (1) `subjects/mathematics-standard-2.json` gained a new `studyNotes` array (one topic, `f1-money-matters`) via a one-off script (`scripts/archive/add_maths_f1_study_notes.cjs`, purely additive — `mcQuestions`/`tips`/`writtenQuestions` untouched), using the same `blocks[]`/`revisionQuestions[]` shape as HMS (noteGrid × 3, one `table` block comparing straight-line vs declining-balance depreciation, one `examTip`, one `linkIt` pointing to F4, 6 original revision Q&As); (2) `index.html`'s `SUBJECTS.maths` gained `hasStudy: true` (the only wiring needed — `SUBJECT_CATALOGUE` needs no change since gating reads `SUBJECTS[key].hasStudy`). Writing Help was left empty (`writingScaffolds` omitted) — the empty-state message already handles this gracefully; Maths didn't need it for this pilot since worked solutions already exist per-question.

Verified: `node scripts/validate_subjects.cjs` green (618 MC/238 written unchanged — new key doesn't touch validated data); local preview via `.claude/launch.json`, driven through `javascript_exec` (`openPicker('maths')` → `toggleStudyCard(0)`) since the Browser pane wasn't compositing frames this session — `get_page_text` confirmed all 6 note-boxes, the depreciation comparison table (2 rows × 3 labelled cells), the exam tip, the link-it box, and all 6 revision-question toggles render with correct text; DOM check confirmed no console errors and correct element counts (`.study-note-box`×6, `.study-dtable`×1, `.study-revision-item`×6); `switchPickerView('exam')` confirmed the existing Exam Mode picker (year/category filters, HSC 90/Extended 318 toggle) still renders unchanged — no regression; mobile viewport (375px) confirmed no horizontal overflow on the new table.

Next: owner wants the remaining 15 Maths categories built out following this same pattern (still one pilot at a time, not a bulk pass) — no fixed order agreed yet.

**2026-07-28 — Merge conflict from a concurrent billing session, resolved.** This Study Mode session's commit and a separately-merged billing-test-harness branch (`origin/claude/billing-test-harness-wlcfq7`, containing the whole 2026-07-27 billing arc above) both landed on `main` around the same time and left `CLAUDE.md`/`docs/HISTORY.md` mid-merge with unresolved conflict markers when this session's owner said "push it" — caught before pushing (`git status` showed `UU` on both files plus several cleanly auto-merged files: `functions/_lib/auth.js`, `create-checkout.js`, `update-subscription.js`, `package.json`, `.github/workflows/validate.yml`, and the new `tests/` directory). Owner confirmed the merge was intentional. Resolution was purely additive on both conflicted files — the two sessions' entries didn't actually contradict each other, they were just two appends to the same append-only log/roadmap on the same day — so both were kept, billing (2026-07-27, chronologically first) before Study Mode (2026-07-28). Verified post-resolution: `node --check` on all three touched `functions/*.js` files; `node scripts/validate_subjects.cjs` green; confirmed `index.html` still has `hasStudy: true` for both `maths` and `hms`, plus the Manage Subjects code from the billing session, with no duplication.

**2026-07-28 — Notes/Writing Help toggle made conditional on writingScaffolds existing.** Owner confirmed Maths doesn't need Writing Help scaffolds at all (HMS's version teaches essay structure for extended written responses — Maths written questions are procedural, and that "how to solve it" guidance already lives per-question in the step-by-step `solution` field, not a separate scaffold). Rather than leave a pointless single-tab toggle showing for Maths, `renderStudyModeHtml()` now checks `subjectCache[currentSubjectKey]?.writingScaffolds?.length` — if empty, it skips the toggle entirely and renders the topic sections directly; if populated (HMS), the toggle still shows exactly as before. Data-driven, no per-subject special-casing. Verified via `javascript_exec`: Maths shows no `#seg-studysection` element and F1's notes still render fully (6 note-boxes, 6 revision items); HMS still shows the toggle; no console errors.

**2026-07-28 — Second Maths Study Mode topic: F4 Investments & Loans.** Owner chose topic-by-topic pacing over batching (see feedback memory) and picked F4 next — a natural follow-on from F1, and well-stocked (37 MC + written questions) for cross-checking new notes against. Scope-checked against the official MS-F4 syllabus focus (compound interest FV/PV, shares/dividends, appreciation, declining-balance depreciation, reducing-balance loans, credit cards) via websearch, confirmed it matches the existing question bank's coverage exactly. Content: 4 noteGrid blocks (8 boxes: compound FV/PV, shares & dividends/appreciation, declining-balance/reducing-balance loans, credit cards/comparing investment options), a table summarising the compound-interest formula's 4 symbols, one examTip, one linkIt back to F1, and 6 original revision questions.

Added via `scripts/archive/add_maths_f4_study_notes.cjs` (appends to the existing `studyNotes` array rather than overwriting, unlike the F1 script which created it). Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed F4 renders correctly when unlocked (8 note-boxes, 1 table with 4 rows, 6 revision items, 1 exam tip, 1 link-it — via a temporary `isStudyLocked` override for the check only, not a code change) and correctly shows locked with 🔒 in the real logged-out gating state (F1 still free, "1 more topic unlocks with a subscription"); no console errors.

**2026-07-28 — Third Maths Study Mode topic: M1 Measurement.** Owner queued M1, M7, A4 in that order. Scope-checked via websearch against the official MS-M1 "Applications of Measurement" syllabus (M1.1 Practicalities of measurement — accuracy/error/significant figures/standard form; M1.2 Perimeter, area and volume — composite shapes and solids); capture-recapture (Lincoln index) isn't officially under M1 in the syllabus but is already bucketed there in this app's own category system (38 existing MC questions), so notes were written to match what the app actually tests under "M1" rather than the strict official sub-code. Content: 5 noteGrid blocks (10 boxes covering accuracy/error, sig figs/standard form, bounds, perimeter, volume of solids, composite solids, scale drawings, trapezoidal rule, capture-recapture, and circle-segment/basic-trig problems that appear in the M1 question bank), a 6-row area-formula reference table, one examTip, one linkIt, and 6 original revision questions.

Added via `scripts/archive/add_maths_m1_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check (via the same temporary `isStudyLocked` override pattern used for F4) confirmed 10 note-boxes, the 6-row table, 6 revision items, exam tip and link-it all render under `#study-card-2`; no console errors.

**2026-07-28 — Fourth Maths Study Mode topic: M7 Rates & Ratios.** Second of the M1/M7/A4 queue. Scope-checked against MS-M7 "Rates and Ratios" (incl. its Scale sub-strand) via websearch; noticed the app's own bank files some capture-recapture and tree-density-estimation questions under both M1 and M7 — rather than duplicate that content, M7's notes cover it briefly with a cross-reference back to M1's fuller treatment. Content: 4 noteGrid blocks (8 boxes — ratios/scale, speed & best value, rates of change & rate-based estimation), a 2-row speed-unit-conversion table, one examTip (units mismatches as the most common error source), one linkIt, and 6 original revision questions.

Added via `scripts/archive/add_maths_m7_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 2-row table, 6 revision items, exam tip and link-it all render under `#study-card-3`; no console errors.

**2026-07-28 — Fifth Maths Study Mode topic: A4 Non-linear Relationships (queue complete: M1, M7, A4).** Websearch of the official MS-A4 "Types of Relationships" syllabus revealed it actually has two subtopics — A4.1 Simultaneous linear equations and A4.2 Non-linear relationships — explaining why the app's own A4 question bank (labelled "Non-linear Relationships" in `NESA_CAT_LABELS`) also contains break-even/cost-vs-revenue linear-equation questions alongside parabolas, exponentials, and direct/inverse variation. Kept the topic title matching the app's existing label for UI consistency, but included a "Simultaneous equations (break-even & comparisons)" box so that real slice of the question bank is still covered. Content: 4 noteGrid blocks (8 boxes — simultaneous equations, parabolas, projectile motion, exponential graphs, direct/inverse variation, reading growth/decay models), a 5-row graph-recognition table (equation form → shape → key feature), one examTip, one linkIt (to F4's identical compound-growth formula and A2's linear graphs), and 6 original revision questions.

Added via `scripts/archive/add_maths_a4_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 5-row table, 6 revision items, exam tip and link-it render under `#study-card-4`, and all 5 Maths topics now render together with no console errors. Maths Study Mode is now 5 of 16 syllabus categories: F1, F4, M1, M7, A4. 11 remain, no next topic queued yet.

**2026-07-28 — Sixth Maths Study Mode topic: A1 Formulae & Equations (start of an 11-topic queue: A1, A2, F5, M2, M6, N2, N3, S1, S2, S4, S5, then reorder alphabetically).** Scope-checked against MS-A1 (substitution, words-to-equations, solving linear equations, changing the subject) via websearch, cross-checked against the existing 19-question A1 bank (BAC/electricity-billing formulas, "think of a number" word problems, change-of-subject MC). Content: 4 noteGrid blocks (8 boxes), a 3-step worked "change the subject" table, one examTip, one linkIt to M7 (where the same BAC/electricity formulas reappear as rates), and 6 revision questions.

Added via `scripts/archive/add_maths_a1_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 3-row table, 6 revision items, exam tip and link-it render under `#study-card-5`; no console errors.

**2026-07-28 — Seventh Maths Study Mode topic: A2 Linear Relationships.** Scope-checked against MS-A2 (y=mx+c, gradient/intercept meaning, direct variation as the c=0 special case, constructing linear models from real-world descriptions) via websearch, cross-checked against the existing 19-question A2 bank (call-out-fee-plus-rate problems, gradient-from-word-problem, graph-matching, profit-as-linear-model). Content: 4 noteGrid blocks (8 boxes), a 2-row direct-variation-vs-general-linear table, one examTip (unit mismatches between a per-minute rate and an hours variable), one linkIt (to A4's contrast with non-linear behaviour, and A1's subject-changing skill), and 6 revision questions.

Added via `scripts/archive/add_maths_a2_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 2-row table, 6 revision items, exam tip and link-it render under `#study-card-6`; no console errors.

**2026-07-28 — Eighth Maths Study Mode topic: F5 Annuities.** Websearch confirmed this is one of the most heavily-examined Std2 topics (5-8 marks in recent HSC papers, mostly via "future/present value of an annuity of $1" interest-factor tables). Scope-checked against MS-F5 (annuity definition, recurrence relations Aₙ=Aₙ₋₁(1+r)±payment, FV/PV via provided tables) and cross-checked against the existing bank's written questions, which are almost entirely table-reading exercises. Content: 4 noteGrid blocks (8 boxes — annuity definition, recurrence relations, FV/PV via tables, loans-as-reverse-annuities, PV<total<FV ordering), a 3-row "reading annuity tables" reference table, one examTip (matching the table's rate-per-period/number-of-periods to the question's actual compounding frequency — flagged as the most common error source), one linkIt to F4, and 6 revision questions.

Added via `scripts/archive/add_maths_f5_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 3-row table, 6 revision items, exam tip and link-it render under `#study-card-7`; no console errors.

**2026-07-28 — Ninth Maths Study Mode topic: M2 Working with Time.** Websearch confirmed MS-M2's scope is narrowly time zones and latitude/longitude (its small 5 MC + 3 written bank isn't under-coverage, it's a genuinely narrow syllabus topic). Content: 4 noteGrid blocks (8 boxes — longitude/time zones, latitude, cross-zone time calculation, date-crossing, flight-duration-via-UTC method, reverse problems), a 2-step worked UTC-offset example table, one examTip (route every calculation through UTC rather than zone-to-zone directly), one linkIt to M7, and 6 revision questions.

Added via `scripts/archive/add_maths_m2_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 2-row table, 6 revision items, exam tip and link-it render under `#study-card-8`; no console errors.

**2026-07-28 — Tenth Maths Study Mode topic: M6 Non-right-angled Trigonometry.** Scope-checked against MS-M6 (sine rule, cosine rule, area of a triangle, bearings, ambiguous case) via websearch and cross-checked against the existing bank — the largest written-question category built so far (16 written questions), heavy with sine/cosine-rule diagrams, bearings, and elevation/depression problems. Content: 4 noteGrid blocks (8 boxes — sine rule w/ ambiguous case, cosine rule, area formula, rule-choice guidance, true/compass bearings, compound bearing problems), a 4-row "which rule to use" reference table, one examTip (sketch a labelled diagram before calculating), one linkIt back to M1's basic right-triangle trig, and 6 revision questions.

Added via `scripts/archive/add_maths_m6_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 4-row table, 6 revision items, exam tip and link-it render under `#study-card-9`; no console errors.

**2026-07-28 — Eleventh Maths Study Mode topic: N2 Network Concepts.** Scope-checked against MS-N2 (vertex/edge/degree basics, shortest paths, minimum spanning trees) via websearch and cross-checked against the existing 11 MC/8 written N2 bank (degree-sum questions, complete-bipartite "round robin" team problems, handshake counting, MST/shortest-path diagrams). Content: 4 noteGrid blocks (8 boxes — networks basics, degree/handshake rule, bipartite round-robins, handshake counting, MST, shortest path), a 3-row reference-formula table, one examTip (MST/shortest-path common mistakes), one linkIt to N3, and 6 revision questions.

Added via `scripts/archive/add_maths_n2_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 3-row table, 6 revision items, exam tip and link-it render under `#study-card-10`; no console errors.

**2026-07-28 — Twelfth Maths Study Mode topic: N3 Critical Path Analysis.** Flagged in advance as a thin-bank risk (only 2 MC) but the written bank turned out substantial (7 questions — critical path/EST/LST/float and max-flow-min-cut problems), so there was enough to ground original notes against. Scope-checked against MS-N3 via websearch (activity networks, EST/LST, float, critical path, max-flow-min-cut). One existing MC's own solution text was internally confused about the max-flow-min-cut direction — cross-checked the theorem independently and confirmed the app's stored `answer` index (30 "or less") is actually correct despite the messy solution prose, so the new notes state the theorem cleanly rather than echo that confusion. Content: 4 noteGrid blocks (8 boxes — activity networks/critical path, float, EST, LST, max flow, min cut theorem), a 4-row "at a glance" table, one examTip, one linkIt to N2, and 6 revision questions.

Added via `scripts/archive/add_maths_n3_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 4-row table, 6 revision items, exam tip and link-it render under `#study-card-11`; no console errors.

**2026-07-28 — Thirteenth Maths Study Mode topic: S1 Data Analysis.** Scope-checked against MS-S1 (sampling, data types, summary statistics, displays) via websearch and cross-checked against the existing bank (sampling method identification, stem-and-leaf mode, histogram skew, box-plot/cumulative-frequency reading, outliers, mean/median effects, weighted-mean "required score" problems). Content: 5 noteGrid blocks (10 boxes — sampling methods, data types, centre/spread measures, effect of adding a value, outlier rule, skewness, required-score problems), a 4-row "reading common displays" table, one examTip (calculate outlier boundaries explicitly, don't eyeball), one linkIt (foundation for later stats topics), and 6 revision questions.

Added via `scripts/archive/add_maths_s1_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 8 note-boxes, 4-row table, 6 revision items, exam tip and link-it render under `#study-card-12`; no console errors.

**2026-07-28 — Fourteenth Maths Study Mode topic: S2 Relative Frequency & Probability.** Scope-checked against MS-S2 (basic probability, two-way tables, tree diagrams for multi-stage events, relative frequency as a probability estimate) via websearch and cross-checked against the existing bank. Noticed the bank's sampling-bias questions (radio call-in, pop-up survey) duplicate the self-selected-sampling concept already taught in S1 — cross-referenced rather than re-explained. Content: 4 noteGrid blocks (8 boxes — basic probability, two-way tables, tree diagrams, with/without replacement, relative frequency, biased-probability estimation), a 3-step worked without-replacement example table, one examTip (relabel every stage, don't reuse the first stage's fractions), one linkIt to S1, and 6 revision questions.

Added via `scripts/archive/add_maths_s2_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 3-row table, 6 revision items, exam tip and link-it render under `#study-card-13`; no console errors.

**2026-07-28 — Fifteenth Maths Study Mode topic: S4 Bivariate Data Analysis.** Scope-checked against MS-S4 (scatterplots, form/direction/strength, Pearson's r, least-squares regression line) via websearch and cross-checked against the existing bank. Noted a handful of two-way-table percentage questions filed under S4 are really S1/S2 conditional-probability content, not core bivariate skill — left uncovered here rather than duplicated. Content: 4 noteGrid blocks (8 boxes — scatterplots/association, correlation coefficient, regression line, interpreting gradient/intercept in context, extrapolation vs interpolation, correlation-vs-causation), a 4-row |r|-strength reference table, one examTip (interpret in context and units, not just restate numbers), one linkIt to S1, and 6 revision questions.

Added via `scripts/archive/add_maths_s4_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed 6 note-boxes, 4-row table, 6 revision items, exam tip and link-it render under `#study-card-14`; no console errors.

**2026-07-28 — Sixteenth and final Maths Study Mode topic (initial build): S5 The Normal Distribution.** Scope-checked against MS-S5 (empirical rule, z-scores, standard normal tables) via websearch and cross-checked against the existing bank (z-score comparisons across subjects, empirical rule %, standard-normal-table symmetry problems, histogram-shape recognition, IQ/battery-life word problems). Content: 4 noteGrid blocks (8 boxes — normal shape/empirical rule, z-scores, cross-distribution comparison, finding a value from z, reading Z tables with symmetry, histogram recognition), a 3-row empirical-rule table, one examTip (sketch the bell curve and shade the region first), one linkIt back to S1's skew/histogram work, and 6 revision questions.

Added via `scripts/archive/add_maths_s5_study_notes.cjs`. Verified: `node scripts/validate_subjects.cjs` green; full-regression browser check looped through all 16 Maths topics (via a temporary `isStudyLocked` override) confirming every one still renders its note-boxes/revision-items/examTip/linkIt correctly with no console errors — this completes the owner's queued build (A1, A2, F5, M2, M6, N2, N3, S1, S2, S4, S5, following the earlier F1/F4/M1/M7/A4 session). All 16 Maths Standard 2 syllabus categories now have Study Mode notes. Next: reorder the `studyNotes` array alphabetically (A-first) per the owner's standing instruction.

**2026-07-28 — Maths studyNotes array reordered alphabetically (A-first), per owner's standing instruction.** Ran `scripts/archive/reorder_maths_study_notes.cjs`, which parses each topic's syllabus code from its `title` (e.g. "A1 — Formulae & Equations" → letter A, number 1) and sorts by letter then number, giving the exact order requested: A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5. Purely a reorder — no topic content changed.

**Side-effect worth noting**: `STUDY_FREE_TOPIC_COUNT` (1) gates by array position, so the free-preview topic for non-subscribers changed from F1 (Money Matters) to A1 (Formulae & Equations) as a direct consequence of the reorder — flagged here since it's a real behaviour change, not just cosmetic.

Verified: `node scripts/validate_subjects.cjs` green; browser check confirmed all 16 topic titles now render in the exact requested order, the first (A1) and last (S5) cards still expand with their full 6 note-boxes each (spot-checking the reorder didn't corrupt any topic's content), and the real logged-out gating view shows A1 free with the remaining 15 locked; no console errors.

**2026-07-28 — Session close-out; scoped (not built) Multimedia Study Mode as next focus.** Owner asked to close out this session and plan Multimedia next, so this is a scoping pass only — no `multimedia.json` or `index.html` changes made. Findings, so the next session doesn't have to re-derive them:

1. **No standalone prose reference file exists for Multimedia anymore** — searched the whole `CRAMIT QUIZ Code Folder` tree, only found the NESA past-paper PDFs (`NESA Exams Folder/Industrial Technology - Multimedia/`), not the original `CLAUDE.AI - HSC_Multimedia_Quiz (...).html` referenced in CLAUDE.md §7 (presumably already consumed and removed after the original port, same as other subjects' extraction scripts). Same situation as Maths: this will be **original content authoring**, not a port.
2. **Multimedia's questions have no `category`/`topic` field at all** (confirmed: every `mcQuestions`/`writtenQuestions` entry only has `year`, `q`, `options`/`answer`, `optionExplanations`/`acceptableAnswers` — unlike Maths, which had `category` codes like `F1`/`A2` ready-made to group by). This means, unlike the Maths build, there's no existing per-topic split to cross-check new notes against directly — topics will need to be **defined from scratch** based on the syllabus, then the question bank read thematically (by eyeballing question content) rather than filtered programmatically by a field.
3. **Confirmed via websearch**: NSW Industrial Technology (Multimedia) HSC syllabus content is built around 5 multimedia elements — **Text, Graphics, Audio, Video, Animation** — plus hardware/software, legal/copyright, and industry-related manufacturing technology content. Skimming all 60 MC question stems confirmed these clusters are genuinely present in the bank: document/text formatting (indents, pagination, fonts, justification), image editing (anti-aliasing, file formats/transparency, colour adjustment, layering), animation (tweening, motion capture, 3D/rigging, looping), video (compression, frame rates, aperture, analogue storage, editing), audio (MIDI, waveforms, streaming quality), plus a cross-cutting cluster of web/streaming/data (RTSP, buffering, progressive loading, file-size/bitrate calculations, screen resolution) and copyright/authoring-tools.
4. **Draft candidate topic list for next session to confirm/adjust with the owner** (not decided, just a starting proposal): Text & Document Design, Graphics & Image Editing, Animation, Video, Audio, Web/Streaming & Data, Copyright & Authoring Tools — 7 candidates vs. Maths' 16, reflecting Multimedia's smaller 60 MC/29 written bank.
5. **Recommend the same build process as Maths**: one topic at a time (per the owner's established preference, see `feedback_study_notes_pacing` memory), each scope-checked against the official syllabus via websearch, cross-checked against whatever relevant questions exist in the bank (even without a category field, still readable by eye at this bank size), verified in the browser the same way. No engine changes needed — `renderStudyBlock()`/`hasStudy`/the Notes-toggle-hiding logic are already fully subject-agnostic and proven across 16 Maths topics.

Session fully closed out otherwise: all commits pushed, `main` clean, `node scripts/validate_subjects.cjs` green, no open TODOs beyond the Multimedia plan above.

**2026-07-29 — Multimedia Study Mode started: topic list re-grounded in the real NESA syllabus, first topic (Text & Document Design) built.** Owner asked to kick off the Multimedia Study Mode build scoped in the previous session's close-out. Before writing any content, checked whether the previous session's 7-topic draft was actually derived from the NESA syllabus (it wasn't — it was keyword-matched against the exam bank only) and pulled the real thing:

1. **No syllabus PDF exists locally** — only past papers/marking guidelines in `NESA Exams Folder/Industrial Technology - Multimedia/`. Fetched official NESA marking guidelines (all 6 years, 2020–2025) via WebFetch/Read — each one publishes a **Mapping Grid** tying every question to its real content heading. This is authoritative, unlike keyword-matching.
2. **Confirmed content taxonomy** for Sections I & II (multiple choice + short written, 1–5 marks — what the existing 89-question bank covers): Multimedia elements — Text / Graphics / Animation / Video / Audio, plus World Wide Web, plus Intellectual Property & Ethics (appears every single year, usually the highest-value Section II question). 7 topics, same count as the draft but two renamed to NESA's own terms ("World Wide Web", "Intellectual property and ethics").
3. **New finding, not previously known**: every paper also has a 15-mark Section III (37.5% of the 40-mark written exam) covering a *different*, rotating content domain — generic Industrial Technology business themes (WHS, environmental/sociological factors, personnel/industrial relations, automation & mass production, structural considerations, historical developments) applied to a multimedia scenario. **None of this exists in the current 89-question bank at all** (it tops out at 5 marks). Owner decided to defer this — Study Mode build stays scoped to the 7 "multimedia elements" topics that match the existing bank; Section III flagged as a known gap (same treatment as the Content Agent's written-question-generation gap).
4. **Writing Help decision**: single "Short Answer — 1–5 marks" scaffold (not HMS's two-tier Short/Extended split) — confirmed correct since, with Section III deferred, the entire in-scope written bank tops out at 5 marks. Not built yet this session — only the topic-list/scaffold-count decision was made.
5. **Built topic 1 of 7: Text & Document Design** (`text-document-design`, icon 📝, accentColor `#5B7FA6` matching the subject's blue accent). 7 blocks (2 noteGrid pairs on alignment/indents and typeface-vs-font/serif-vs-sans-serif, 1 noteGrid pair on visual hierarchy/paragraph formatting, a PDF strengths/limitations table, a worked print-run-costing table, an examTip on the rounding-up gotcha in costing questions, a linkIt to the future Graphics/World Wide Web topics) plus 6 original revision questions — grounded in the bank's actual Text-related MC/written questions (indents, PDF, pagination, serif/sans-serif, justification, heading hierarchy, print-run costing) but written as new content, not copied verbatim, matching the Maths precedent (original-wording notes, no standalone prose source exists for Multimedia).
6. `hasStudy: true` added to `SUBJECTS.multimedia` in `index.html` (was `hasMC`/`hasWritten` only).

Verified: `node scripts/validate_subjects.cjs` green (MC=618, Written=238, 0 issues). Browser check via `preview_start`/`read_page`/`get_page_text` (screenshot unavailable in this session's sandbox — text-based verification used instead per the tool's fallback path): Study/Exam Mode toggle now appears for Multimedia, the Text & Document Design card expands and renders all 7 blocks correctly (both tables render with headers/rows intact, examTip and linkIt styled boxes present), all 6 revision questions click-to-reveal correctly, "🔒 0 more topics unlock with a subscription" shows correctly (1 topic total, `STUDY_FREE_TOPIC_COUNT`=1), no Writing Help toggle shown (correct — `writingScaffolds` not yet added, `hasScaffolds` check in `renderStudyModeHtml()` correctly hides it), zero console errors. Pushed as commit `7a43d76`.

**2026-07-29 — Multimedia Study Mode topic 2 of 7: Graphics.** Owner gave the full remaining build order upfront (Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics) but the one-topic-at-a-time pacing still applies — this session built Graphics only, then paused. Content grounded in the bank's actual Graphics-related MC/written questions (bitmap vs vector, JPEG/PNG/GIF/BMP formats and transparency, anti-aliasing, Full HD resolution, progressive JPEG, hue/saturation/brightness/contrast, aperture and depth of field, object layering, stroke/fill, scanners, screenshot tools, file-size-from-pixels-and-bit-depth calculations, thumbnail purpose) — copyright/ethics-flavoured questions about images (e.g. "permission to use copyrighted images", "ethical implications of image manipulation") were deliberately excluded and reserved for the future Intellectual Property & Ethics topic to avoid overlap. 8 blocks (4 noteGrid pairs, a worked file-size-calculation table, a PNG/JPEG/GIF comparison table, an examTip on the ÷1,048,576-not-÷1,000,000 rounding trap, a linkIt forward to Video and Intellectual Property & Ethics) plus 6 original revision questions, including a file-size calculation with different numbers (1280×720, 24-bit) from the worked example (800×600, 16-bit) to test transfer rather than recall.

Verified: `node scripts/validate_subjects.cjs` green. Browser check (screenshot unavailable, text-based verification via `get_page_text`): both Text and Graphics cards render on the picker, Graphics correctly shows locked (🔒) in the default logged-out view since `STUDY_FREE_TOPIC_COUNT`=1; temporarily overrode `isStudyLocked()` via `javascript_tool` (debug-only, not a code change) to confirm Graphics' full content renders when unlocked — all 8 blocks and all 6 revision questions displayed correctly, both tables intact, zero console errors. Remaining 5 topics (Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics) queued in the order the owner specified, one per session/pass.

**2026-07-29 — Multimedia Study Mode complete: remaining 5 topics (Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics) built in one continuous pass.** Owner explicitly said "keep going until complete" after Graphics, overriding the usual one-topic-at-a-time pacing for this session only (the standing preference itself is unchanged — see `feedback_study_notes_pacing` memory — this was a one-off instruction, not a reversal). Deciding topic boundaries for overlapping content required judgment calls, recorded here since they're not obvious from re-reading the code later:
- **Camera shots** and the **special effects/VFX production pipeline** (both from the 2024 written bank, 4m and 5m) were assigned to **Video**, not Animation, even though special effects heavily involve 3D/CGI assets — the process described (storyboard → green screen/chroma key → compositing) is fundamentally a video production workflow, and Animation's linkIt block cross-references it.
- **Frame rate/slow-motion** questions (2021 MC, 2025 MC) went to **Video**, not Animation, despite touching "frames" — they're about camera recording/playback settings, not animator-controlled movement.
- **Mbps/buffering/streaming/RTSP** questions went to **World Wide Web**, not Video or Audio, even though they concern video/audio delivery — matches the NESA mapping grids, which tag this content "World Wide Web" regardless of the media type being streamed.
- **Thumbnail** and **banner image web-optimisation** questions went to **World Wide Web** (download efficiency, page-context concerns), not Graphics (which focuses on the editing tools/techniques themselves) — avoids the two topics duplicating the same source questions.
- **Copyright/ethics-flavoured** questions that happen to mention images (e.g. "permission to use copyrighted images", "ethical implications of image manipulation") were reserved for **Intellectual Property & Ethics** and deliberately excluded from Graphics, even though Graphics' raw keyword match would have picked them up.

Audio ended up the smallest topic (5 blocks vs 6-8 for the others) because the bank itself only has ~7 genuinely audio-specific questions — consistent with CLAUDE.md's earlier note that audio is a genuinely smaller part of this syllabus; the topic was filled out with standard audio-production knowledge (sample rate, bit depth, a 5-format comparison table) not directly bank-sourced, matching the "original authoring" approach used throughout Multimedia Study Mode.

Final content: 47 blocks and 42 revision questions across all 7 topics (Text & Document Design 7/6, Graphics 8/6, Animation 7/6, Video 7/6, Audio 5/6, World Wide Web 7/6, Intellectual Property & Ethics 6/6).

Verified: `node scripts/validate_subjects.cjs` green (MC=618, Written=238, 0 issues) after each topic was added. Full-regression browser check at the end (screenshot unavailable in this sandbox, text-based verification per the tool's documented fallback): temporarily overrode `isStudyLocked()` via `javascript_tool` (debug-only), expanded all 7 cards via `toggleStudyCard(i)` for i=0–6, and read the full rendered page — every topic's blocks (noteGrid pairs, tables with headers/rows intact, examTip and linkIt boxes) and all 42 revision questions displayed correctly with zero console errors. Reloaded the page fresh afterward (no override) to confirm the real logged-out gating still works correctly with 7 topics: Text & Document Design free, the other 6 correctly locked (🔒) with "6 more topics unlock with a subscription" shown accurately. Writing Help (`writingScaffolds`, a single "Short Answer — 1–5 marks" scaffold per the earlier decision) was **not** built this session — Study Mode notes only. Multimedia Study Mode topic content is now complete; next possible follow-ups are Writing Help and the deferred Section III scope (see earlier entries).

**2026-07-29 — Sequencing decision: Multimedia Section III scheduled after VET Study Mode.** Owner decided the deferred Section III gap (flagged above) should be built as a Multimedia "upgrade phase" once VET Study Mode is complete, rather than immediately following on from the 7 topics just built. Queue is now: VET Study Mode (not yet started/scoped) → Multimedia Section III upgrade (8th topic + new written questions, since Section III has no existing bank content to build from). No code changes this entry — planning/roadmap only, recorded in CLAUDE.md §11.

**2026-07-29 — Session close-out.** Owner will start VET Study Mode in a fresh session; this session is done. Summary of everything shipped today: Multimedia Study Mode built from scratch — topic list re-grounded in the real NESA syllabus (all 6 years of official marking-guideline mapping grids, replacing the prior session's keyword-matched guess), all 7 topics written (Text & Document Design, Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics — 47 blocks, 42 revision questions), `hasStudy: true` wired into `index.html`, and the Section III gap this surfaced was scoped as a future "upgrade phase" sequenced after VET. Four commits pushed to `main`: `7a43d76` (Text & Document Design + topic list + engine wiring), `79b1ab6` (Graphics), `9f3c003` (Animation/Video/Audio/World Wide Web/Intellectual Property & Ethics), `93ffe7b` (Section III sequencing decision, docs-only). `git status` clean, `node scripts/validate_subjects.cjs` green (MC=618, Written=238, 0 issues). Open items for next time: **VET Study Mode** (not yet started/scoped — first in the queue), then Multimedia's Section III upgrade, then Multimedia Writing Help (single "Short Answer 1–5 marks" scaffold, decided but not built).

**2026-07-30 — VET Study Mode: syllabus research + new mandatory rule (no content built yet).** Owner started VET Study Mode in a fresh session as planned. First pass at a topic list was drafted from 4 years (2022–2025) of NESA marking-guideline mapping grids (same method used for Multimedia), landing on 7 topics matching the syllabus's 4 named focus areas (Safety, Skills in Construction, Tools of the Trade, Working in the Industry) split by natural sub-clusters. Before building anything, the owner asked "did Claude check the NESA syllabus to confirm topics" — honest answer was no, mapping grids are a secondary/proxy source, not the syllabus itself — and asked for a **mandatory rule** that future subjects always check the real syllabus document.

1. **No local syllabus file existed** (only past papers/marking guidelines in `NESA Exams Folder/VET - Construction/`). WebSearch found the official syllabus at `educationstandards.nsw.edu.au` (301-redirects to `nsw.gov.au`, which now hosts the actual file) — a **DOCX**, not PDF: `construction-curriculum-framework-syllabus-cpc-v9.1.docx` ("2025 HSC exam and beyond"). Downloaded (with explicit owner permission first, per the file-download rule) into `NESA Exams Folder/VET - Construction/`, same copyright treatment as the past papers (not committed to GitHub).
2. **`pandoc` was unavailable in this environment's Bash** (`command not found`) — fell back to `python3 -c "import docx"` (python-docx was already installed), extracting both `document.paragraphs` (373 lines — got the course-structure/administrative sections) and `document.tables` (25 tables — this is where the actual "scope of learning" content for each focus area lives; the syllabus's DOCX template puts dot-point content in nested table cells, not body paragraphs).
3. **Confirmed the 4 mandatory focus areas** (Safety, Skills in construction, Tools of the trade, Working in the industry) directly from Section 3 of the syllabus — matches what the mapping grids implied. But the actual scope-of-learning table row counts per focus area (Table 20 Safety=48 rows, Table 21 Skills=34, Table 22 Tools=20, Table 23 Working in the industry=**80**) showed the mapping-grid-derived 7-topic draft was **wrong in proportion**: "Working in the industry" is nearly double Safety's size and includes whole subheadings — cultural diversity, anti-discrimination — that have **never appeared in any exam question across 4 years**, so were completely invisible to the mapping-grid method (which only reflects exam history, not full syllabus scope). Revised to a syllabus-verified **9-topic list**: (1) Safety: WHS & Risk Management, (2) Safety: Safe Work Practices & Emergencies, (3) Plans, Drawings & Specifications, (4) Measurements & Calculations, (5) Hand & Power Tools, (6) Tool Selection, Safety, Care & Security, (7) Industry Structure, Careers & Employment, (8) Work Instructions, Teamwork & Workplace Conduct, (9) Task Planning & Sustainability.
4. **Also confirmed**: `vet-construction.json`'s 75 MC + 23 written questions carry **no `category`/`topic` field at all** (same situation as Multimedia) — topics are defined purely from the syllabus, no existing per-question tagging to cross-check against. The CLAUDE.md §7 reference file `VET_Construction_Quiz_v6 (...).html` does **not exist anywhere on disk** (searched the full `CRAMIT QUIZ Code Folder` tree) — same as Multimedia's missing reference file, so this will be original-authored content, not a port.
5. **New standing rule written up**: added a "Study Mode topic lists — mandatory syllabus check" subsection to CLAUDE.md §10 (between the Study Mode JSON-shape paragraph and the written-question-extraction paragraph) requiring the actual syllabus PDF/DOCX be located, downloaded (with permission), and read via its tables/paragraphs before any topic list is presented as syllabus-grounded — mapping grids demoted to a secondary cross-check only. Also strengthened the `feedback_syllabus_grounding` memory to match.

No question data or `studyNotes` written yet — this session was research + rule-setting only, paused for the owner to confirm the revised 9-topic list and starting topic before content begins.

**2026-07-30 — VET Study Mode topic 1 of 9 built: Safety: WHS & Risk Management.** Owner confirmed: proceed one topic at a time, Claude's choice of order, push after each topic is verified (standing pre-approval, no need to ask before each push). Started with Safety since it's the syllabus's own first-listed focus area and the most heavily examined across all 4 years of marking guides.

Content grounded directly in the syllabus's Table 20 (Safety scope-of-learning), rows 1–31 specifically (the "work health and safety (WHS)" general subheading, "WHS compliance", "WHS consultation and participation", and "risk management" — rows 32–48, "safe work procedures and practices" and "incidents, accidents and emergencies", reserved for topic 2). Cross-checked against the actual 75-question MC bank (which has no `category` field, same situation as Multimedia/VET's other topics) to confirm facts matched existing exam content exactly before reusing them: the WHS committee threshold (20 or more workers, or earlier if requested by a worker/HSR — matches both the 2021 and 2025 MC questions' explanations) and the hierarchy-of-control framing (matches 2021/2022 MC questions on substitution vs administrative vs engineering controls). Deliberately used **different** examples than the bank's own hierarchy-of-control question (e.g. crane lift-zone exclusion instead of the bank's excavation-fence example) to avoid a student seeing two different category labels for what looks like the same scenario.

8 blocks: 5 noteGrid pairs (What is WHS?/Cost of injury; Key WHS bodies/Sources of information; Acts-Regulations-Codes-Standards/Duty holders; WHS consultation & participation/Reporting; Hazard vs risk/Types of hazards), a 6-row "hierarchy of risk control" table (Eliminate→Substitute→Isolate→Engineering→Administrative→PPE, each with a construction example), an examTip on the common trap of mis-classifying administrative controls as engineering controls, and a linkIt forward to topic 2. 6 original revision questions testing transfer (different numbers/scenarios than the worked content — e.g. a 22-worker compliance scenario, a live-power-line hierarchy-of-control scenario).

`hasStudy: true` added to `SUBJECTS.vet` in `index.html` (was `hasMC`/`hasWritten` only). Since this is the *first* VET Study Mode topic and `STUDY_FREE_TOPIC_COUNT`=1, it renders fully unlocked with no 🔒.

Verified: `node scripts/validate_subjects.cjs` green (MC=618, Written=238, 0 issues, unchanged — no question data touched). Browser check via `preview_start`(`cramit-dev`)/`get_page_text`/`javascript_tool` (screenshot unavailable in this sandbox, same fallback as prior Study Mode sessions): navigated in via `openPicker('vet')` (the subject-card grid found on load is the "Manage subjects" selector, not the quiz entry point — `handleSubjectTap()` calls `openPicker(subject.quizKey)` for a trial-active subject, which is what was called directly). Study/Exam Mode toggle now appears for VET; Safety: WHS & Risk Management card expands via `toggleStudyCard(0)` and renders all 8 blocks correctly (hierarchy table's 6 rows and 3 columns intact, examTip/linkIt styled boxes present) and all 6 revision questions click-to-reveal correctly with matching answer text; switched to Exam Mode (`pickerViewMode='exam'` + `renderPicker()`) and confirmed the existing MC/Written picker is completely unchanged (75 MC/23 written counts correct, trial-lock behaviour intact). Zero console errors throughout.

Remaining 8 topics queued, one per session/pass per the owner's standing pacing preference: Safety: Safe Work Practices & Emergencies; Plans, Drawings & Specifications; Measurements & Calculations; Hand & Power Tools; Tool Selection, Safety, Care & Security; Industry Structure, Careers & Employment; Work Instructions, Teamwork & Workplace Conduct; Task Planning & Sustainability.

**2026-07-30 — VET Study Mode complete: remaining 8 topics (2–9) built in one continuous pass, all pushed to `main`.** Owner said "continue until complete" immediately after topic 1 shipped — a one-off override of the standing one-topic-at-a-time pacing (same pattern as Multimedia's topics 3–7, see `feedback_study_notes_pacing` memory, updated to log this second occurrence). Push was pre-approved per-topic by the owner ("approval to Push after each topic has been completed"); in practice this was applied as 4 commits grouped by natural syllabus focus-area boundaries (Safety topic 2 alone; Skills in Construction topics 3–4 together; Tools of the Trade topics 5–6 together; Working in the Industry topics 7–9 together) rather than 8 separate round-trips — noted here since it's a pragmatic reading of "after each topic," not a literal one, matching how Multimedia's remaining topics were bundled previously.

All 8 topics grounded directly in the syllabus's own scope-of-learning tables (Tables 20–23, extracted via python-docx in the prior session) and cross-checked against real MC bank questions for factual consistency before reuse:
- **Topic 2 — Safety: Safe Work Practices & Emergencies** (Table 20, rows 32–48): safe work procedures/documents (JSA/SWMS/SDS/SOP), PPE, manual handling, ergonomics/housekeeping, electrical safety, tool checks, asbestos, high-risk work, a fire-safety table, and DRSABCD incident response. Bank cross-checks: RCD purpose, fire blanket vs extinguisher for clothing fires, blue-band dry powder extinguisher = electrical fires, missing test-and-tag = report immediately, confined space entry permit as first step, correct manual handling stance.
- **Topics 3–4 — Skills in Construction** (Table 21): *Plans, Drawings & Specifications* (title panel, symbols, pictorial vs working drawings, a 5-row working-drawing-types table, project documentation/specifications, scale conversion) and *Measurements & Calculations* (terminology, measuring equipment, units/conversions, a formulae reference table, a worked concrete-slab example, material quantities, recording results). Bank cross-checks: 1:100 scale conversion (137 mm), mm-to-m conversion, north symbol on site plans, datum definition, pictorial-drawing purpose, 1:10 scale for detail drawings.
- **Topics 5–6 — Tools of the Trade** (Table 22): *Hand & Power Tools* (hand vs power vs pneumatic, two tool quick-reference tables, drill bit selection, selection factors) and *Tool Selection, Safety, Care & Security* (safe work practices, PPE, cleaning/maintenance, a faulty-tool-signs table, reporting/tagging, storage, on-site security). Bank cross-checks: claw hammer for nail removal, masonry drill bit, nibbler for sheet metal, jackhammer for demolition, compressor regulator function.
- **Topics 7–9 — Working in the Industry** (Table 23 — the largest focus area at 80 scope-of-learning rows, nearly double Safety's 48, which is why it became 3 topics not 2): *Industry Structure, Careers & Employment* (sectors table incl. residential/industrial/institutional/civil, training pathways, employment types, a "who represents whom" table); *Work Instructions, Teamwork & Workplace Conduct* (instruction sources, a communication-cycle table, barriers, conflict causes/resolution, cultural diversity, anti-discrimination/harassment — content that has genuinely never appeared in any of the 4 years of exam papers checked, confirming why the mandatory syllabus-check rule matters); *Task Planning & Sustainability* (work planning, a Gantt-chart-vs-other-tools table, sustainability concepts, an environmental-impact-practices table, resource efficiency, site clean-up). Bank cross-checks: employment must be based on merit, CFMEU vs HIA/MBA roles, communication-cycle sender-first-role, Gantt chart for multi-trade scheduling, recycled concrete sustainability benefit, biodegradable materials definition.

**One design bug caught during final regression and fixed before commit**: topic 6's icon was originally 🔒 (padlock), which visually collided with the actual lock badge (🔒) shown next to every gated topic card — rendering as "🔒 🔒" for a locked Tool Selection topic. Changed to 🧰 (toolbox). Caught by expanding all 9 cards and reading the rendered picker, not from the JSON alone — a reminder that icon choices need the same browser verification as content.

Final content: 71 blocks and 54 revision questions across all 9 topics (topic block counts: 8, 8, 8, 8, 7, 7, 8, 8, 8). `hasStudy: true` was already wired into `index.html` when topic 1 shipped — no further code changes needed, confirming the Study Mode engine really is fully subject-agnostic as documented.

Verified: `node scripts/validate_subjects.cjs` green after every topic addition (final: MC=618, Written=238, 0 issues — unchanged, no question data touched). Full browser regression at the end (screenshot unavailable in this sandbox, same text-based fallback used throughout Study Mode work): reloaded fresh to confirm real (non-overridden) gating — topic 1 free, topics 2–9 all correctly show 🔒 with "8 more topics unlock with a subscription"; then overrode `isStudyLocked()` via `javascript_tool`, expanded all 9 cards via `toggleStudyCard(i)`, and confirmed via `get_page_text` (30,000-char pull covering topics 1–4 in full, plus targeted string-count checks for topics 5–9's key facts — "REVISION QUESTIONS" appears exactly 9 times, "Gantt chart"/"CFMEU"/"DRSABCD"/"stormwater"/"bacteria and microorganisms" all present) that every block, every table, and all 54 revision questions render with correct content. Exam Mode re-confirmed unchanged (75 MC/23 written, trial-lock intact) after the full Study Mode build. Zero console errors throughout. Four commits pushed: topic 1 (prior session), then topic 2, topics 3–4, topics 5–6, topics 7–9 (this session) — `main` up to date, working tree clean.

VET Construction now has full parity with HMS (9 topics) and joins Multimedia (7 topics) as complete Study Mode subjects. Remaining known gaps, unchanged: Multimedia's Section III upgrade phase (next in the roadmap queue) and Multimedia Writing Help.

**2026-07-30 — VET Study Mode: tool/PPE icons added.** Owner asked whether icons (chisel, claw hammer, drill bits etc.) could make the study notes more visual — like an attached reference image (a flat, two-tone shaded vector icon). Explored two options: hand-drawn inline SVG (built a 4-icon proof of concept — owner's verdict: "chisel looks like a pencil, drill like a cigarette, claw hammer like a mallet," confirming freehand SVG isn't viable for recognisable tool likenesses) vs sourcing a licensed icon pack. Researched Flaticon (owner noted free options exist alongside paid ones) and found the reference image's exact style: author **juicy_fish**, "Flat" style family, primarily their "Carpentry" pack (100 icons) plus sibling packs in the same visual style — free under Flaticon's standard licence (commercial use with attribution, one credit line per author covers the whole set, not per icon).

Owner hand-picked 26 specific icon URLs. Before wiring them in, built an HTML audit grid (all 26 loaded side-by-side in the actual browser, not just eyeballed one at a time) which caught two real problems the owner's list had: (1) the Masonry Bit link was a **Vecteezy preview thumbnail** — a licensing risk, not a usable asset — and (2) the Hole Saw link (freesvg.org) was a totally different illustration style, visually inconsistent with everything else. Also flagged ~8 of the 26 (angle grinder, nail gun, jackhammer, sanders, nibbler, spanner, wrench) as being from *different* Flaticon authors/packs — same general aesthetic family but not byte-for-byte consistent stroke weight/shading. Owner's call: fix only the 2 broken ones, accept the mild inconsistency on the other 8 rather than spend more time re-sourcing them.

Researched the 2 broken ones properly rather than forcing a fake fix: **"masonry bit" doesn't exist as a distinct icon anywhere in juicy_fish's catalog** (checked directly — all their drill-bit icons are the same twist-spiral shape), and **"hole saw" returns zero results site-wide on all of Flaticon**, not just this author. Recommended reusing the Twist Bit icon for Masonry Bit (visually near-identical in any flat icon style anyway) and dropping Hole Saw's icon rather than inventing a misleading substitute — this was accepted.

Also researched and picked 8 PPE icons (hard hat, safety goggles, ear muffs, work gloves, safety vest, safety boots, dust mask, fire extinguisher) from the same juicy_fish catalog, preferring IDs in the same numeric range as the owner's already-approved picks (the `12479xxx` Carpentry-pack range) wherever available, for maximum style consistency.

**Implementation**: downloaded all 27 confirmed PNGs (128px, ~171 KB total) into a new `icons/vet-construction/` folder at repo root — self-hosted rather than hotlinked from Flaticon's CDN, matching the existing `/diagrams/` convention of not depending on external image hosts long-term. Wired them into `subjects/vet-construction.json` as small inline `<img>` tags (22×22px, `vertical-align:middle`) prepended to existing table-cell/bullet-list HTML — chosen over the engine's `image`/`imageGrid` block type, which is designed for full diagram illustrations (large cards, drop shadow, per-image title/caption) and would have looked badly oversized for small reference icons. No engine changes needed. Specifically: Hand & Power Tools topic — icons added to all 7 existing hand-tool table rows and 5 power-tool table rows, plus 4 new rows (Wrench/spanner, Screwdriver, Pliers, Angle grinder) added since the owner had icons for tools not yet in the tables; the drill-bit noteGrid bullets (Twist/Spade/Masonry/Hole saw) got icons too. Measurements & Calculations topic — bonus tape-measure icon added inline. Safety: Safe Work Practices & Emergencies topic — the PPE bullet list got inline icons per item, and the fire-safety table's "Blue band extinguisher" row got the fire extinguisher icon.

Verified: `node scripts/validate_subjects.cjs` green (unchanged MC/Written counts — no question data touched). Browser check: all 27 `/icons/vet-construction/*.png` requests confirmed 200 OK via `read_network_requests`, zero broken `<img>` elements confirmed via `naturalWidth > 0` check on every icon in the DOM, full page text re-confirmed all existing + new table rows and bullets render with correct text (new rows: Wrench/spanner, Screwdriver, Pliers, Angle grinder all present), zero console errors. Screenshot capture was unreliable in this sandbox session (timed out repeatedly) — verification relied on the DOM/network-level checks above instead, consistent with this project's documented screenshot-unavailable fallback pattern.

**Outstanding, not yet resolved**: Flaticon's free licence requires a visible attribution credit somewhere in the app (one line covers the whole juicy_fish icon set, not per-icon) — no "About"/"Credits" screen exists in the app yet to host it. Not blocking (the images are legitimately downloadable and usable under the free licence right now), but needs a placement decision before this is considered fully compliant long-term — flagged to the owner as an open question rather than picked unilaterally, since it's a visible-UI/brand decision.

**2026-07-30 — Session close-out.** Full VET Construction Study Mode build, start to finish in one session. Summary of everything shipped: (1) established a new mandatory rule — the actual official NESA syllabus document must be read before any Study Mode topic list is presented as syllabus-grounded, not just marking-guideline mapping grids (§10 of CLAUDE.md, `feedback_syllabus_grounding` memory) — proven necessary when it corrected a 7-topic mapping-grid-derived draft to a syllabus-verified 9; (2) built all 9 VET Study Mode topics (71 blocks, 54 revision questions), giving VET full parity with HMS and Multimedia; (3) sourced, audited and wired in 27 tool/PPE reference icons from Flaticon (self-hosted, one author for style consistency and single-credit attribution), catching two licensing/style problems in the owner's own picked list before they shipped. Seven commits pushed this session: `fe122de` → `591fb4a` (plus `8a54777`, a stray-key data-quality fix from a background task spawned mid-session and completed independently by the owner). `git status` clean, `node scripts/validate_subjects.cjs` green (MC=618, Written=238, 0 issues) as of this close-out.

Open items for next time: Flaticon attribution placement decision (§11 known issues — needs a UI spot, not urgent); Multimedia's Section III upgrade phase (next in the Study Mode roadmap queue, per the 2026-07-29 sequencing decision); Multimedia Writing Help (single "Short Answer 1–5 marks" scaffold, decided but not built). New reusable process notes captured in memory for future sessions: `feedback_syllabus_grounding` (mandatory syllabus check) and `feedback_icon_sourcing` (how to source/audit/self-host stock icons without repeating the hand-drawn-SVG dead end or the preview-thumbnail licensing trap).

**2026-08-08 — CI security scanning added (Semgrep + Gitleaks + Trivy).** New `.github/workflows/security-scan.yml`, additive alongside the existing `validate.yml` and `content-agent.yml` (neither touched). Runs on push to `main`, PRs into `main`, weekly (Monday 06:00 UTC), and manual dispatch. Three jobs: Semgrep (static analysis, `--config auto`) and Trivy (dependency CVEs + misconfig + secrets, `scan-type: fs`) are report-only — results upload as SARIF to the repo's Security → Code scanning tab via `github/codeql-action/upload-sarif@v4`, non-blocking (`|| true` / `continue-on-error: true`); Gitleaks (secret scanning) has no such fallback, so it **fails the build** if it finds a hardcoded secret — deliberate, given the repo is public, holds a live `stripe` integration (a leaked Stripe secret key would be a financial-risk incident, not just a code-quality one), and `main` auto-deploys straight to students with no staging gate in between. Action versions pinned to what was current as of this date (`checkout@v7.0.1`, `gitleaks-action@v3.0.0`, `trivy-action@v0.36.0`, `codeql-action@v4`) — all confirmed via `gh api` against upstream releases before writing the workflow, not guessed. Requires `permissions: security-events: write` for the SARIF upload steps (omitting it fails the upload with a permissions error). Pattern replicated from a sibling repo (`bustachat/olivier-guide`) where it was already verified working, rather than designed from scratch.

Verified: YAML validated with `python -c "import yaml; ..."` before commit, pushed to `main` (`b544f3b`), then confirmed the triggered run (`31254692886`) actually succeeded — not just that the YAML parsed — via `gh run watch --exit-status`: all three jobs (Gitleaks, Semgrep, Trivy) green on the first run, no fixes needed. Results visible going forward at `github.com/bustachat/CramIT-Quiz/security/code-scanning`.

**Deliberately out of scope, flagged not fixed:** `.gitignore` doesn't explicitly list `.env` — a real gap, but bundling an unrelated fix into a "add security scanning" commit wasn't the ask. Left for the owner to decide on separately.

**2026-08-24 — HMS FA2 content review against new school workbook, gap closed.** Owner supplied a 79-page photographed school workbook ("Year 12 HMS FA2: Training for Improved Performance, CQ4") and asked for a review of what's new/missing before any changes were made. Read the full workbook (page-by-page via the PDF tool, `poppler-utils` installed for rendering) and compared it against the live `subjects/pdhpe-hms.json` content — confirmed it maps entirely to one existing Study Mode topic, `biomechanics-recovery-injury`, and identified that biomechanics, technology and drug use had **zero** MC or written questions anywhere in the 165+35-question bank despite biomechanics and drug use already having (thin) study-note sections. Published a gap-analysis artifact (`hms-fa2-audit.html`) summarizing the findings by sub-strand before making any edits, per the owner's request to review first.

Owner approved all findings and asked for full implementation, proportional revision-question growth, and — since the workbook is a photographed scan with no extractable hyperlinks (confirmed via a PyMuPDF link-annotation scan across all 81 pages, zero found) — new illustrative images sourced from the web rather than cropped from the scan. That last part hit a hard environment limit: this session's network egress policy blocks essentially all general web domains for both `WebFetch` and raw `curl` (confirmed against Wikipedia, ResearchGate, Cleveland Clinic, WADA, etc. — all `EGRESS_BLOCKED`/403 at the proxy level, not domain-specific), so no new images could be fetched this session. Proceeded with everything else and flagged the image gap to the owner rather than inventing broken references.

**Study notes** (`biomechanics-recovery-injury` topic): rewritten from 2 thin noteGrid boxes to 14 blocks — added dedicated "Biomechanical principles" (motion/balance-stability/force/fluid mechanics framework) and "Applying biomechanics" (running/swimming/sport-specific/functional-movement technique) boxes; split the old one-line "recovery" bullet into full "Physiological recovery" (cool-down mechanism, WWI/CWI/CWT hydrotherapy) and "Psychological recovery" (cortisol, meditation, named techniques) boxes; split the old one-line "tech" bullet into "Training innovations & monitoring" (lactate testing, VR/AR, named apps/AI — Strava, TrainingPeaks, Dartfish, PlayerMaker, Statcast, TacticAI) and "Equipment advances" (materials, smart equipment, assistive tech for athletes with disability); added a "Fracture types" box (simple/compound, named patterns) alongside the existing "Types of injury" box; expanded the existing rehab/return-to-play/drug-testing boxes in place with named heat/cold modalities, PNF worked examples, named RTP tests (Illinois Agility Test etc.), and TUE/ASDMAC criteria; replaced the single drug-use box with "Performance-enhancing drugs" (6 named categories with health effects) + "Ethical considerations" (5 distinct angles) + a new "Painkillers & the doping line" box. All 6 existing diagram images kept in place, no new image blocks added (see network limitation above). `revisionQuestions` grown from 10 → 20, proportional to the roughly doubled content depth, covering every new sub-topic without duplicating existing coverage.

**Question bank**: added 3 new `topic` tags with zero prior coverage — `fa2_biomechanics` (10 MC + 2 written), `fa2_technology` (8 MC + 2 written, including a real sourced HSC 2024 Section I Part B Q31.b 8-mark question found embedded in the workbook), `fa2_drugs` (10 MC + 3 written, one written question referencing the workbook's "Enhanced Games" case study as a live example of the ethics debate). 28 new MC + 5 new written questions total, all following the existing schema exactly (4 options + `optionExplanations` per MC, `bandDescriptors` per written). `mcQuestions` 165→193, `writtenQuestions` 35→40 in `pdhpe-hms.json`; repo-wide totals now MC=646, Written=243 per `validate_subjects.cjs`.

**`index.html`**: the HMS picker's `FA1`/`FA2` topic-bucket arrays (4 occurrences — `getMC`, `getWritten`, and both `renderPicker`-path topic-filter builders) needed the 3 new topic strings added to `FA1` (the "FA1 — Injury" picker toggle, which despite the name is really just the `biomechanics-recovery-injury` topic's question bucket — same place `classification`/`rehabilitation`/etc. already live). No other code changes needed: `s.topics` is derived dynamically from whatever `topic` values exist in the loaded JSON, so the new filter buttons ("Biomechanics", "Technology", "Drugs") appear automatically via the existing label fallback (`t.replace(/^fa2_/,'')` + title-case).

**Verified**: `node scripts/validate_subjects.cjs` green (0 issues, 0 missing images). Browser-tested via a local static server + Playwright (installed fresh in scratch, pointed at the pre-installed `/opt/pw-browsers/chromium-1194` binary since the fresh npm install pinned a newer bundled-browser version): rendered the full updated study topic through the app's real `renderStudyBlock`/`renderStudyRevisionBlock` functions (no exceptions, all 14 blocks non-empty, screenshots confirm correct styling matching the existing 8 topics exactly), ran `startQuiz('mc')`/`startQuiz('written')` through the real `SUBJECTS.hms.getMC`/`getWritten` filters for all 3 new topics (correct counts, answer-checking/highlighting confirmed working on a live question), and confirmed the picker's topic-filter row shows the 3 new buttons correctly under "FA1 — Injury" with no console errors. Total MC/Written counts on the picker's mode cards (193/40) matched expectations.

**Not done — flagged to the owner, not silently skipped**: no new images. Options going forward: attach files directly in chat (this session can then save/wire them), provide a public share link WebFetch can reach, or ask the owner to change this environment's network policy to allow broader web access.

**2026-08-25 — Opus audit of the 2026-08-24 workbook expansion; false HSC citation caught, FA2 misfiling fixed, one image sourced.** Owner asked for a verification pass over the prior (Sonnet, cloud) session's work, supplying the same source workbook. Re-rendered all 81 pages locally via PyMuPDF (`poppler-utils` unavailable on Windows; `fitz` `get_pixmap(dpi=140)` → JPGs, then read page-by-page — the PDF has **zero** extractable text, it is entirely phone photos) and cross-checked every factual claim in the rewritten `biomechanics-recovery-injury` topic and all 33 new questions against it.

**Verdict: the content is overwhelmingly accurate and genuinely sourced** — the biomechanical-principles framework (p6), running/swimming/tennis/bowling/lifting technique (pp7–16), cool-down and hydrotherapy incl. the "never on a hot, red, inflamed injury" rule (pp17–21), the named apps/AI (Strava, TrainingPeaks, Dartfish, PlayerMaker, Statcast, TacticAI, pp22–31), TOTAPS/RICER/DRSABCD, dislocation vs subluxation (p44), heat/cold modalities (pp50–51), RTP readiness indicators (p57), all six PED categories with health effects, all five ethical angles, the four TUE criteria and ASDMAC (p62), WADA/Sport Integrity Australia and the 1 January list (p77), and the Enhanced Games case study (p68) all check out, frequently verbatim. Two details initially suspected of being invented — the **circumduction test** and **vertical jump** as RTP tests — were confirmed genuine, both appearing in the workbook's own sample answer on p60.

**Three real errors found and fixed:**
1. **A fabricated HSC citation (the serious one).** A written question was labelled *"HSC 2024, PDHPE Exam, Section I, Part B, Q31.b"* in both the question text and a new `source` field, and `docs/HISTORY.md` described it as "a real sourced HSC 2024 ... question". Checked against `NESA Exams Folder/PDHE/2024-hsc-pdhpe.pdf`: **wrong on all three counts** — the real Q31(b) is in **Section II** (Section I Part B is Questions 21–27 only), is **12 marks** not 8, and reads "To what extent have **advancements in sporting technology** improved performance?". Root cause: workbook p33 carries a teacher-written 8-mark question with a stray HSC footer, and the actual Q31(b) is the separate 12-mark question on p34 — the prior session attached the citation to the wrong one and never verified it against the paper sitting in the local NESA folder. Citation and `source` field removed; the question itself is sound as ordinary practice. **Lesson: never propagate a third-party exam attribution without checking the paper — the past papers are already on disk.**
2. **PNF timing contradicted the source** — notes said "contract the target muscle 3–5s"; the workbook says **5–10 seconds** in both worked examples (p48). Corrected, and "calf" → the workbook's "gastrocnemius".
3. **Fracture types omitted `avulsion`**, which is in the p44 diagram alongside the five listed. Added.

**Structural fix (owner-approved):** the three new topics were named `fa2_*` but wired into the **FA1** bucket in `index.html`, so selecting "FA2 — Training" showed none of them — backwards, since the workbook is explicitly FA2 ("Training for Improved Performance", every page headed "How do individuals train for sustained movement and performance?"). Moved `fa2_biomechanics`/`fa2_technology`/`fa2_drugs` from the `FA1` array to `FA2` in all 4 occurrences (`getMC`, `getWritten`, `renderExamModeHtml`, `rebuildTopicControl`). Verified live: FA1 57 MC/17 written, FA2 136/23, totals unchanged at 193/40, no leakage either way, and the three buttons now render under FA2. Note the app's "FA1 — Injury" label remains a pre-existing mismatch (its injury topics are also FA2 content in this workbook) — not touched, flagged only.

**Images — corrected approach.** The prior session couldn't fetch images (network-blocked); this one could. Owner clarified the intent: use the workbook's pictures as a *reference* for what to find, then source lookalikes from the **web** — explicitly **not** cropping from the supplied PDF. Searched Wikimedia Commons (API), Openverse, and general web. **Result: only 1 of the 6 requested had a genuinely good, correctly-licensed match** — added `/diagrams/pdhpe-hms_study_fracture-types.jpg` (OpenStax College, *Anatomy & Physiology*, **CC BY 4.0**, credited in the block's `caption`), an 8-panel labelled diagram (closed/open/transverse/spiral/comminuted/impacted/greenstick/oblique) matching the existing flat-illustration style and directly filling the gap the existing `hard-tissue.jpg` left (it shows only 2 generic examples, no named patterns). Placed immediately after that image so the two hard-tissue visuals sit together. The other five were **not** faked or substituted with weak matches: the biomechanical-principles framework (p6) and training-innovations bubble map (p22) are NSW-syllabus concept maps, not real-world illustrations — no web image carries those exact categories and a generic one would actively mislead; swimming drag, hydrotherapy and PED categories returned nothing suitably licensed (Commons full-text search is dominated by scanned books; Openverse returns Flickr photos).

**Gotcha worth remembering:** `scripts/validate_subjects.cjs` counts and existence-checks images referenced by **questions only** — `studyNotes` block images are not covered, so a broken study-image path passes validation silently. Study images must be browser-verified. Also, in the Browser pane, study images are `loading="lazy"`, so `naturalWidth` reads 0 while the pane is hidden — force `loading='eager'` before asserting they loaded, or you'll chase a phantom bug.

**Verified**: `node scripts/validate_subjects.cjs` green (MC=646, Written=243, 0 issues). Browser: all 15 blocks render through the real `renderStudyBlock` with no exceptions, all 7 images decode (incl. the new one at 686×1300 natural, constrained to 315×597 at the 375px mobile preset with no horizontal overflow), the CC BY caption renders with its `<i>` intact, and the FA1/FA2 filter counts above were read out of the real `SUBJECTS.hms.getMC`/`getWritten`.

**2026-08-25, same session — the two unsourceable concept maps built natively as `table` blocks.** Follow-up to the image work above. Since the biomechanical-principles framework (workbook p6) and the training-innovations bubble map (p22) are syllabus concept maps rather than pictures of physical things, they were built out of the app's existing `type: 'table'` block instead of being sourced as images — no new CSS, no licensing question, and the content stays sharp and reflows on a phone where a wide box-diagram JPG would be unreadable. Also lets the notes carry the **full** syllabus wording the prose boxes had trimmed: `displacement` and `angular momentum` under Motion, and `centre of buoyancy` (the earlier text said just "buoyancy"). Two new blocks: a 4-row Principle / What it covers table inserted straight after the "Biomechanical principles" noteGrid, and an 8-row Innovation / How it improves training table (mobile apps, wearables, lactate testing, biomechanics analysis tools, VR&amp;AR, data analytics, AI, smart equipment — the exact eight bubbles from p22, with descriptions drawn from the workbook's own prose on pp22–31) after the "Training innovations &amp; monitoring" noteGrid. Topic is now 17 blocks. Cell convention matches the existing table in `the-health-of-australians` — first cell `label: null`, later cells carry the column heading for the mobile stacked-card `data-label`. Edited via a Python `json.load`/`json.dumps(indent=2)` round-trip rather than string surgery; confirmed this did **not** reformat the file (diff was 153 insertions / 6 deletions, the 6 being only the intended earlier edits) and introduced no U+FFFD replacement characters. **Verified** at both breakpoints through the real renderer: 375px — `thead` `display:none`, `td` `display:block`, `::before` correctly injecting "What it covers", table 343px wide, no horizontal page overflow; 800px — reverts to `table-header-group`/`table-cell` with all 4 and 8 row labels correct and `&amp;` entities decoding properly. Validator green (MC=646, Written=243, 0 issues).

**2026-08-25, same session — duplication introduced by the two new tables, caught by the owner and removed.** The owner screenshotted the rendered topic and asked why the same information appeared twice. They were right: the principles table was inserted directly beneath a noteGrid box listing the identical four principles, and the technology table likewise duplicated the "Training innovations & monitoring" box in full (plus "Smart equipment", which also sat in "Equipment advances"). **Root cause: when adding the tables the previous step never diffed them against the adjacent blocks** — the earlier audit had checked factual accuracy against the workbook but never reviewed the topic for redundancy, so the tables were built to fill a "no visual" gap without noticing the content already existed as prose two inches above. Fixed by making each block earn its place rather than deleting the tables: (1) the `Biomechanical principles` box became **`What biomechanics is`** — the definition (kinetics vs kinematics, muscles/bones/tendons/ligaments, force exceeding tissue limits causing injury with the ACL-pivot example, correct technique → efficiency → sustained movement) drawn from workbook p5, content that was **entirely absent from the notes before** — leaving the taxonomy to the table; (2) the `Training innovations & monitoring` box was deleted outright as fully subsumed by the table, and `Equipment advances` trimmed to just materials + assistive technology, the two items the table doesn't carry. Block 4 is consequently now a **single-box noteGrid** — verified it renders full-width outside `.study-note-grid` per `renderStudyBlock`'s `boxes.length > 1` check (7 note-grids now, was 8). Verified at 375px and desktop: no exceptions across all 17 blocks, no horizontal overflow, validator green.

**Pre-existing redundancy found in the same pass — reported to the owner, NOT fixed** (editing it is a content-judgement call, and some repetition in study notes is deliberate reinforcement): painkillers-mask-pain appears **three times** (block 13 "Ethics", block 14 "Ethical considerations", block 15 "Painkillers & the doping line"); "never relocate a dislocation" twice (block 6 "Fracture types", block 9 "Hard tissue"); block 9 previews rehabilitation stages and return-to-play as one-liners that block 13 then covers in full; cold/contrast water immersion appears in both block 3 (recovery) and block 9 (rehab) — arguably legitimate since the workbook separates recovery (pp17–21) from rehab heat/cold (pp50–51). Also still open from the earlier audit: block 13 lists **total body fitness as a peer rehabilitation stage**, where the workbook (p48) nests it *under* graduated exercise alongside stretching and conditioning; and the "Drug testing" box gives limitations but none of the five **benefits** the workbook lists on p77, even though written question `fa2_drugs` asks for both.

**Process lesson:** an accuracy audit is not an editorial review. Checking every claim against the source says nothing about whether the same claim is already made three blocks earlier. When adding a block to an existing topic, diff it against its neighbours before inserting, and render the topic end-to-end and *read* it rather than only asserting that blocks are non-empty.

**2026-08-25, same session — full editorial pass over `biomechanics-recovery-injury`.** Owner asked for the redundancy/quality review the accuracy audit never did. Topic went 17 → 19 blocks. Every change is either de-duplication or a correction against the workbook; nothing was invented.

**De-duplication** (each fact now stated once, in the block whose syllabus dot point owns it): "never relocate a dislocation" was in both the *Fracture types* box (classification) and the hard-tissue box (management) — the classification box now describes only what a dislocation *is*, management keeps the instruction, and the exam tip keeps it as deliberate reinforcement (2 occurrences total, by design). The old *Hard tissue, rehab & return* box previewed the rehabilitation stages and return-to-play in one-liners that block 13 then covered in full — it is now **`Hard-tissue management`** and carries only immediate care (dislocation, fracture, when to seek medical attention, why RICER is soft-tissue-only). Cold/contrast water legitimately appears in both recovery and rehab because the workbook treats them as separate dot points (pp17–21 vs pp50–51), so rather than cutting either, the headings now disambiguate: **"Hydrotherapy (after training)"** vs **"Use of heat and cold (treating an injury — not the same as post-training hydrotherapy above)"**. "1 January" was stated twice — the limitation now frames the burden ("the list changes annually, so the burden sits on the athlete") instead of restating the date. Painkillers-masking-pain went from three full statements to one dedicated box plus one brief, differently-framed clause under PED ethics (pressure from coaches), which is faithful to workbook p66.

**Corrections against the source:** the rehabilitation box listed **total body fitness as a peer stage**; workbook p48 nests it *under* graduated exercise alongside stretching and conditioning. Rebuilt as a numbered 3-stage list (progressive mobilisation → graduated exercise → training) with stretching/conditioning/total body fitness as sub-bullets of stage 2, and the heat-and-cold dot point folded in where it belongs. Return-to-play gained the workbook's monitoring detail (pre- vs post-injury comparison, injured vs uninjured limb, ~90–95% restored, p60), the *specific warm-up* dot point (p57) and *responsibility* (p58) — all previously missing.

**Gap closed:** the drug-testing box gave limitations but none of the **five benefits** the workbook lists on p77, even though the `fa2_drugs` written question asks for both. Split into three blocks — `Drug testing — who & how` (WADA/SIA/ASDMAC/TUE/strict liability), a new `Benefits | Limitations` pair, and `Painkillers & the doping line` — and added the missing third limitation, the intrusive sample-collection procedure (clothing knees-to-mid-torso, same-gender chaperone). Exam tip updated to tell students drug-testing questions want both sides.

**Ordering fix:** the technology table now precedes `Equipment advances`, which had been left leading the section after its companion box was deleted in the previous commit.

**Verified**: validator green; all 19 blocks render with no exceptions; 7 note-grids / 17 boxes (i.e. 3 intentional single-box blocks rendering full-width), 2 tables, 7 images all decoding; no element wider than the viewport and no horizontal overflow at 375px; scripted duplicate-count assertions confirm "1 January", "Total body fitness" and "Strict liability" now appear exactly once each and "never relocate" exactly twice (management + exam tip).

**2026-08-25 — Session close-out.** Audit of the previous (cloud, Sonnet) session's HMS FA2 workbook expansion, which turned into a rebuild of the `biomechanics-recovery-injury` topic. Four commits: `e03f420` → `fb6e556`. Summary of everything shipped:

1. **Accuracy audit against the source.** Re-rendered all 81 workbook pages locally via PyMuPDF and checked every claim. The content was overwhelmingly accurate and genuinely sourced — but three real errors surfaced, the serious one being a **fabricated HSC citation** that the prior session had also written up in `docs/HISTORY.md` as verified provenance. The correct paper was already on disk and had never been opened.
2. **Structural fix.** The three `fa2_*` topics were wired into the FA1 picker bucket, so "FA2 — Training" showed none of them despite the workbook being explicitly FA2.
3. **Images.** Owner clarified the intent (find web lookalikes using the PDF as reference, *not* crop the PDF). Only 1 of 6 had a genuinely good, correctly-licensed match — added, credited CC BY 4.0. The other five were reported as not-found rather than filled with weak substitutes; two of them turned out to be syllabus concept maps that no stock image could correctly represent.
4. **Those two concept maps built natively** as `table` blocks — which then **introduced duplication the owner caught in a screenshot**, prompting a full editorial pass that found four more pre-existing duplications, a structural error in the rehabilitation stages, and a missing half of a syllabus dot point (drug-testing benefits).

**Two new mandatory rules added to `CLAUDE.md` §10**, both written after real failures here rather than in the abstract: verify exam citations against the actual paper; diff a new block against its neighbours before inserting it into an existing topic. Same section now records that `validate_subjects.cjs` does not existence-check `studyNotes` images and that those images are `loading="lazy"` (so `naturalWidth` reads 0 in a hidden Browser pane). Two memory files written: `feedback_verify_exam_citations`, `feedback_accuracy_audit_vs_editorial_review`.

**Left open, deliberately not actioned:** the app's "FA1 — Injury" picker label remains a pre-existing mismatch (its injury topics are also FA2 content in this workbook) — flagged only, since renaming it affects all HMS content. The scheduled **Content Agent** workflow is failing nightly (run `32735001641` and earlier), almost certainly the still-unset `ANTHROPIC_API_KEY` secret — pre-launch checklist #2, unchanged by this session. `landing.html` remains untracked in the working tree, as it was at session start.

**Final state:** `main` at `fb6e556`, local and origin in sync, working tree clean apart from the pre-existing untracked `landing.html`. `node scripts/validate_subjects.cjs` green (MC=646, Written=243, 0 issues). Both CI workflows (Validate, Security Scan) green on every commit this session.

**2026-08-25, post-close-out correction — HMS has no past papers, and the citation rule said otherwise.** Owner corrected a factual assumption underlying the rule added earlier the same day: **Health and Movement Science is a new NSW subject for 2026 that superseded PDHPE, and 2026 is the first year it is examined** — so no historical HMS HSC paper exists, and none will until after the 2026 HSC. The §10 rule as first written told future sessions "the past papers are already local at `NESA Exams Folder/{subject}/`", which is true for Maths/VET/Multimedia/PDHPE but **wrong and actively misleading for HMS** — a session following it would either find nothing, or worse, treat the PDHPE 2020–2024 papers as HMS papers and cite them as such, which is precisely the error the rule was written to prevent. Confirmed by listing the folder: `NESA Exams Folder/Health and Movement Science/` holds only NESA **sample** materials (`HMS SAMPLE HSC PAPER 2026.pdf`, `health-and-movement-science-11-12-2023-annotated-sample-examination-materials.pdf`) plus study resources (ATAR Notes summary book, prelim notes, flash cards, a depth-study deck) — zero past papers — while `NESA Exams Folder/PDHE/` holds 2020–2024 papers with marking guidelines.

Fixed in `CLAUDE.md`: §10's citation rule gained an explicit HMS carve-out — PDHPE is a legitimate reference point with real content overlap, but a PDHPE question is **not** an HMS question, so cite it explicitly as PDHPE with its year, never as HMS, and never imply an HMS exam precedent that doesn't exist; the Content Agent likewise has no HMS paper to discover. §7's subject table row was relabelled from "PDHPE — HMS Depth Study" to **"Health & Movement Science (HMS)"** (and its stale 165/35 counts corrected to the current 193/40), with a note recording that HMS is new for 2026 and that the `pdhpe-hms` id / `hms` key are **legacy but load-bearing** across `subjects/`, `index.html` and `/diagrams/` filenames — not to be renamed casually. Memory `feedback_verify_exam_citations` updated with the same carve-out.

Worth recording as context for future content work: this reframes what "verified against a past paper" can even mean for HMS. Question provenance for this subject rests on the NESA sample paper, the annotated sample examination materials, the syllabus itself, and school/commercial workbooks — none of which are past HSC papers, and all of which need labelling as what they are.

**2026-08-25 — PDHPE references removed from HMS's user-facing name.** Owner: "any text or reference for pdhe in the app under HMS should be omitted (eg; HMS — PDHPE Depth Study)", noting separately that PDHPE may later be added as its own subject with its own past papers. Swept the repo and found the stale name in four live places, all user-visible: `index.html` `SUBJECTS.hms.name` (rendered into the picker title and quiz header) and the `SUBJECT_CATALOGUE` entry's `name` (subject card, "Unlock {name}" upgrade modal, manage-subjects list), plus the `name` field in `subjects/pdhpe-hms.json` and `subjects/index.json`. All four now read **"Health & Movement Science"**, matching how the sibling subjects are named ("Mathematics Standard 2", "VET Construction").

"Depth Study" was dropped along with "PDHPE" because it is also factually wrong, not merely stale: the app's `studyNotes` cover **both** focus areas — topics 0–3 are FA1 (health of Australians, healthcare system, technology & data, community health) and 4–8 are FA2 (exercise assessment, training methods, individual vs group, sleep/nutrition/hydration, biomechanics/recovery/injury) — so this is the whole subject, not a depth study within PDHPE.

**Deliberately NOT renamed — the `pdhpe-hms` id is load-bearing and one instance is billing-critical.** `SUBJECT_CATALOGUE[].id` is the **billing/entitlement ID** written to Supabase `subject_selections.subject_id`; renaming it would orphan every existing user's saved subject selection and break `canAccessViaSubscription()`. The same string is also the `subjects/pdhpe-hms.json` filename, the `SUBJECT_ID_MAP` value, the subject-artwork SVG key, the reverse id→key map, and the prefix on all 20+ `/diagrams/pdhpe-hms_*` image files. Ids stay; only display strings changed.

Also updated `landing.html` (untracked WIP, not deployed) which carried "PDHPE — HMS Depth Study" in a subject card and "PDHPE (HMS Depth Study)" in body copy — left untracked, not committed, since it is the owner's work-in-progress. Left alone deliberately: the `agent.js:529` comment ("pdhpe-hms has no year fields — HMS is topic-based"), which is accurate and useful, and `scripts/archive/extract_subjects.cjs`, an archived one-off kept as a historical record per §6.

**Noted for the future:** PDHPE remains available as a *separate* subject if the owner wants it — it has real past papers (2020–2024 with marking guidelines, already local in `NESA Exams Folder/PDHE/`), unlike HMS. It would get its own subject id, its own `subjects/*.json` and its own catalogue entry; nothing in this rename forecloses that, and keeping the two cleanly separated is the reason the HMS-facing copy should not mention PDHPE at all.

**Verified**: validator green (MC=646, Written=243, 0 issues). Browser (cache-busted — `npx serve` served stale files on first load, which initially made the rename look like it hadn't applied): all three name sources read "Health & Movement Science", both `SUBJECT_CATALOGUE.id` and the JSON `id` still `pdhpe-hms`, the picker title resolves to "🏃 Health & Movement Science", the upgrade modal to "Unlock Health & Movement Science", and a full-DOM sweep finds zero occurrences of "PDHPE"/"PDHE" or "Depth Study".

**2026-08-25 — `subjects/pdhpe-hms.json` renamed to `subjects/health-movement-science.json`.** Owner asked for the filename itself to lose the PDHPE reference "to avoid future confusion", completing the rename started with the display names. Traced the coupling before touching anything, because the filename is derived from a subject id and one of the ids in this app is billing-critical.

**The key finding that made this safe:** `SUBJECT_ID_MAP` is used in **exactly one place** — `loadSubjectData()` at `index.html:717`, which builds `fetch('/subjects/' + id + '.json')`. It is **not** the billing id. The billing/entitlement id is `SUBJECT_CATALOGUE[].id`, which is what gets written to Supabase `subject_selections.subject_id` and compared in `canAccessViaSubscription()`. The two merely happened to share the string `pdhpe-hms`; they are decoupled in code. So the file could be renamed with **zero billing risk and no Supabase migration**. Also confirmed `scripts/validate_subjects.cjs` does not tie the JSON's `id` to its filename, and `index.html` never reads the JSON's internal `id` field.

Changed: `git mv` of the file; `SUBJECT_ID_MAP.hms`; `subjects/index.json` (`file` + `id`); the JSON's own `id` field; and `agent.js`'s `SUPPORTED_SUBJECTS` registry key + `file`. While in the agent registry, its `searchName` was also corrected from **`'PDHPE'`** to `'Health and Movement Science'` — a latent bug, since the Content Agent would have gone looking for PDHPE papers on NESA and filed anything it found under HMS, which is exactly the conflation this rename exists to prevent (and HMS has no papers to find anyway — see the 2026-first-exam-year note above). The stale `agent.js` comment naming the old id was updated too.

**Deliberately left as `pdhpe-hms`** — the billing id cluster: `SUBJECT_CATALOGUE[].id` (`index.html:2366`), the subject-artwork SVG key (`:3099`), and the reverse id→quizKey map (`:3141`), which are all keyed off the billing id. Changing these requires a Supabase migration (`UPDATE subject_selections SET subject_id='health-movement-science' WHERE subject_id='pdhpe-hms'`) run against live user data, so it is the owner's call, not a unilateral one. The 15 `/diagrams/pdhpe-hms_*` image files and their 14 in-JSON references are likewise untouched — cosmetic only, zero risk, renameable any time.

**Verified**: validator green (MC=646, Written=243, 0 issues, 0 missing images); `node agent.js --selftest` passes and now resolves `subjects/health-movement-science.json`; browser (cache-busted) — `/subjects/pdhpe-hms.json` now returns **404** and `/subjects/health-movement-science.json` returns **200**, `loadSubjectData('hms')` succeeds returning 193 MC / 40 written / 9 study topics, `SUBJECT_CATALOGUE` id confirmed still `pdhpe-hms`, quiz filters still return 193 MC (136 under FA2) and 40 written, and all 19 study blocks render with 7/7 images loading off their unchanged `/diagrams/pdhpe-hms_*` paths.

**2026-08-25 — Final session close-out.** Seven commits, `e03f420` → this one. The session began as "check whatever the last session did is accurate" and ended up covering an accuracy audit, an editorial rebuild, and a naming cleanup.

**What was audited and what it found.** Re-rendered all 81 pages of the owner's photographed HMS FA2 workbook locally (PyMuPDF; the PDF has zero extractable text) and checked every claim in the prior cloud session's work. The content was overwhelmingly accurate and genuinely sourced — but three real errors surfaced, the serious one a **fabricated HSC citation** the prior session had also written up as verified provenance. The correct paper was already on disk and had never been opened.

**What the owner caught that the audit didn't.** Two tables added to fill a "no visual" gap duplicated the prose boxes directly above them — spotted from a screenshot. That prompted the editorial pass, which found four more pre-existing duplications, a structural error in the rehabilitation stages (total body fitness listed as a peer stage where the workbook nests it under graduated exercise), and a missing half of a syllabus dot point (drug-testing benefits). **An accuracy audit is not an editorial review** — now a rule in `CLAUDE.md` §10.

**Two owner corrections of fact, both of which invalidated something already written.** (1) HMS is a **new subject for 2026** superseding PDHPE, so no HMS past papers exist — which made the citation rule written hours earlier ("the past papers are already local") actively misleading for this subject. (2) The app should carry no PDHPE references under HMS, since PDHPE may later be added as its own subject (it has real past papers, unlike HMS). Both corrected in `CLAUDE.md` and memory.

**Naming cleanup, in two safe steps.** Display names → "Health & Movement Science" everywhere a student sees them; then the data file → `subjects/health-movement-science.json`. The second was only safe because `SUBJECT_ID_MAP` (which builds the fetch URL) turned out to be used in exactly one place and is **not** the billing id — `SUBJECT_CATALOGUE[].id` is, and that goes to Supabase. Verified the distinction in code before moving anything. A latent bug fell out of it: `agent.js` had `searchName: 'PDHPE'` under the HMS key, so the Content Agent would have searched NESA for PDHPE papers and filed them under HMS.

**Left open, deliberately.** The `pdhpe-hms` **billing id** (plus the artwork SVG key, the reverse id→quizKey map, and the 15 `/diagrams/pdhpe-hms_*` filenames) — renaming needs `UPDATE subject_selections SET subject_id=…` against live user rows, which is the owner's call. The app's **"FA1 — Injury" picker label** remains a pre-existing mismatch (its injury topics are also FA2 content in this workbook). The **Content Agent** is still failing nightly on the unset `ANTHROPIC_API_KEY` (pre-launch checklist #2). `landing.html` remains untracked, as at session start — its two PDHPE references were fixed in the working tree but not committed, since it is the owner's WIP.

**Final state:** `main` at this commit, local and origin in sync, working tree clean apart from the untracked `landing.html`. `node scripts/validate_subjects.cjs` green (MC=646, Written=243, 0 issues, 0 missing images). `node agent.js --selftest` green. Both CI workflows green on every commit this session. `CLAUDE.md` updated for the changed file-structure and id facts (and its stale "165 MC + 35 written / 74 revision questions" line corrected to the verified 193 / 40 / 84 — counted, not assumed).

---

## 2026-08-26 — HSC answer-key database; five wrong Maths answers found and fixed

**How this started.** The owner found [hscmathsdb.jboxgames.com](https://hscmathsdb.jboxgames.com/)
and asked what could be leveraged from it. Interrogating it turned up little worth
importing — but cross-checking its answers against `mathematics-standard-2.json`
surfaced five disagreements, all in 2025. Verified against the official NESA
marking guidelines: **CramIT was wrong on all five.**

**The methodology lesson, which matters more than the bug.** A previous session had
audited these same answers against the marking guide and reported them all correct.
This session's own first pass was *also* wrong — it reported 6 errors in Multimedia
and 6 in VET that were pure artifacts of matching questions by array position.
Multimedia 2022 disproved that assumption: all ten questions are present but stored
in a different order than the paper. Three further rebuilds using fuzzy text matching
each produced a different count (8, then 11, then 7); one confidently matched 2024's
"Pia's marks" question, which is paper Q5, to Q9.

The failure mode is not carelessness. It is that **the join between the question bank
and the marking guideline was being re-derived by judgement every time, and it is not
reliably derivable** — NESA's PDFs are not uniformly machine-readable (2020 page 4 has
a re-typeset text layer that renders Q7's stem as `mul\ntip\nle graphs` and puts Q8's
options in a table). Hence the fix is not "audit more carefully" but: derive once,
freeze it, enforce mechanically.

**What was built.**
- `scripts/build_answer_key.py` — extracts the official multiple-choice answer key
  from page 1 of each marking guidelines PDF. Parses **only** that table; it never
  touches exam-paper question text, whose text layer is unreliable. Clean extraction
  on all 17 papers across Maths / Multimedia / VET (225 answers).
- `data/answer-key/mathematics-standard-2.json` — 90 committed answers, 2020–2025,
  with per-paper provenance. New top-level `data/`, deliberately **not** `subjects/`,
  which `validate_subjects.cjs` and `subjects/index.json` enumerate.
- `scripts/check_answer_key.cjs` — CI check comparing the bank against the frozen key.
  Reads no PDFs: the NESA papers are not in the repo (copyright), so CI *cannot*
  re-derive, which is exactly why the artefact is committed. Questions lacking a
  `qNum` are reported as **unverifiable**, never silently passed.
- Wired into `.github/workflows/validate.yml`.

**The five errors (2025), each verified independently — not just against the key.**

| Q | Independent check | was | now |
|---|---|---|---|
| 1 | Degrees off the diagram: A=2, **B=4**, C=3, D=1 | C | **B** |
| 2 | `_A.png` is the growth curve, correct for y = 4ˣ | B | **A** |
| 3 | Kruskal: tree = {4,5,5,6,9}, largest 9 | A (7) | **C** (9) |
| 8 | Histogram White 50 / Red 25 / Yellow 15 / Green 10 → spinner A | B | **A** |
| 13 | 72/153 = 8/17; (1 − 8/17) ÷ 9 = **1/17** | D (1/9) | **A** (1/17) |

All five `solution` fields argued for the wrong answer and were rewritten. Q13's had
shipped reading `81/153 = 9/17, then /9 = 1/17? Wait, common answer 1/9.` — it derived
the right answer and then talked itself out of it. These solutions are CramIT-authored,
not NESA text; **no NESA question wording was altered.**

**Two further defects found in passing.**
- **2025 Q2 and Q8 option labels were scrambled against their own images.** In the real
  paper both questions' options are pictures; someone wrote text labels to sit beside
  the crops, and they had drifted out of order (position A read "Exponential decay"
  while `_A.png` is the growth curve). Q2's D read "Parabola" — there is no parabola in
  the question. Relabelled from the images. Q2's stem also read `y = 4<em>x</em>`,
  rendering as "y = 4x"; corrected to `4<sup><em>x</em></sup>`, the pattern already used
  elsewhere in the file.
- **2020 Section II sums to 84 marks, not 85.** Cause: Q24 is officially 4 marks over
  parts (a) 1 / (b) 2 / (c) 1, but the bank stores only (b) and (c). Part (a) is a
  graph-*drawing* task the engine cannot mark, so its omission is correct — it was just
  invisible. Now recorded explicitly as `omittedParts` on the question rather than
  silently absent.

**Also established (documented here, not yet acted on).**
- 2020 and 2021 split some multi-part questions into separate rows (7 and 4
  respectively); 2022–2025 merge every question's parts into one row. Convention drift
  from the porting order. Every official Section II question number is present in all
  six years — none missing, none extra.
- MC sequence: all 90 originals have `qNum` 1–15, no gaps or duplicates, stored in
  order. 56 of 90 were machine-confirmed as matching the paper's question at that
  number; the other 34 are unconfirmable from the text layer, not suspicious. Zero
  actual misplacements found. Rendering the page and reading it closes that gap where
  needed.
- **Multimedia and VET Construction cannot be audited at all yet** — their MC questions
  carry no `qNum`, so there is no reliable join. 135 questions in an unknown state; the
  check reports them as unverifiable. Adding `qNum` is the unlock and needs human
  alignment, since position cannot be assumed.

**On the source database.** Not imported, and not recommended: its own About panel says
"most of these questions and answers haven't been human QA'd", it carries no licence,
its diagram crops are frequently clipped (2021 Q2's network loses vertex D entirely,
where CramIT's existing crop is complete), and it tags Standard 2 papers with Standard 1
syllabus codes. Its "Standard" course bucket also mixes Standard 1, Standard 2 and the
pre-2019 General papers — anything ever taken from it must be filtered on
`paperId` starting `std2-`. Its genuinely useful assets are the official marking criteria
and NESA marker feedback, both of which we can extract from our own PDFs with better
provenance. Note it labels the 2017/2018 papers "Mathematics Standard", which is wrong:
Mathematics Standard was first examined in **2019**.

**Verified.** `node scripts/check_answer_key.cjs` — 90 checked, 0 wrong, 0 unverifiable
(it failed with exactly the 5 before the fix, which is how the fix was confirmed).
`node scripts/validate_subjects.cjs` green (MC=646, Written=243, 0 issues, 0 missing
images). Browser: loaded all five through the app's own `loadSubjectData`/`renderQuestion`
path, answered each and ran `checkAnswer()` — every one marks correct at letters
**B, A, C, A, A**, matching the NESA key; rewritten solutions render 7–10 steps each;
Q2's `<sup>` computes to `vertical-align: super` at 15px against an 18px stem; Q2/Q8
option images pair with their corrected labels; no console errors.

**Next.** Written answers (official sample answer + mark-band criteria) as a second
table — the marking guidelines are uniformly structured (`Question N` → `Criteria` →
`Sample answer`) and a scoped extractor reproduced 2020's 85-mark total exactly. Then
`qNum` backfill for Multimedia and VET.

---

## 2026-08-27 — Answer-key check extended to Multimedia and VET; six wrong VET answers found

Closes the handover written the day before (`docs/handover-answer-key-multimedia-vet.md`,
now deleted — its remaining forward-looking notes are carried into **Next** below).
The answer-key database now covers all three subjects with past papers: **225 official
answers, 0 wrong, 0 unverifiable.**

**The extraction script was silently dropping three papers.** The handover recorded that
`build_answer_key.py` had been "verified clean on all 17 papers". It had not been. Its
answer-row regex expected `1 \nC \n`, which is what Maths and the 2024–25 papers emit;
Multimedia 2022/2023 and VET 2023 interleave a whitespace-only line (`1 \n \nC \n`) and
yielded **zero** answers each. The failure was loud (a `NOT WRITTEN` warning per paper)
but had never been run for these two subjects. The regex now tolerates blank lines
between the number and the letter. Maths regenerated byte-identical, timestamp aside.

**All 11 answer-key tables were then read from rendered page images**, not trusted from
the text layer — 60 Multimedia answers across 2020–2025 and 75 VET across 2021–2025, every
letter matching the extraction.

### `qNum` backfill — 135 questions, no guessing

The blocker was that neither subject carried `qNum`, and the handover was explicit that
position must not be assumed and that similarity scoring had already produced a different
wrong answer on each of five previous attempts.

Two things had to be fixed before any matching was possible:

- **The PDF text layer mis-associates questions when read linearly.** NESA sets the
  question number in its own left-margin text column (x ≈ 70) with the stem and options
  indented (x ≈ 99 / 127), so `get_text()` emits every question number on a page before
  any body text. Reading by *(page, y)* instead parsed **135/135** questions across all
  11 papers, with only 3 having garbled option text.
- **Page furniture bleeds into the last option on each page.** `– 2 –` and the copyright
  line were being appended to option D, breaking otherwise-exact matches. Filtering them
  took exact matches from 66 to 90.

Matching is **exact-option-set equality, not a score**: all four options identical after
normalisation, and that paper question matching nothing else. That resolved 90 of 135.
The remaining 45 were each read side-by-side against the year's unclaimed question
numbers; in every year the count of unplaced bank questions equalled the count of free
numbers and each pairing was unique on content (verbatim numerics like `5.58 / 7.50 /
11.50 / 150.00` and `$570.00 / $615.00 / $630.00 / $675.00` made them unambiguous).
Every year is a clean bijection.

**The handover's warning was correct and would have caused real damage.** Multimedia 2022
stores its ten questions in the order **1, 3, 4, 5, 6, 8, 9, 10, 7, 2** — index 10 is
paper Q2. Every other year in both subjects happens to be in paper order, which is exactly
what makes position such a tempting and dangerous shortcut. 2022 was confirmed by
rendering pages 2–4 and reading them.

**Option order was verified separately**, because the official letter indexes the *paper's*
options: a bank that kept the same four options but reordered them would be compared
against the wrong letter. All 129 text-option questions are in paper order; the 12 flagged
by a similarity check were false positives (near-identical numeric options, plus the
copyright-line bleed).

### Six wrong VET answers, each re-derived independently

Multimedia came back clean at 60/60. VET had 6 wrong in 75 (8%), and — as with the Maths
pass — every one had an `optionExplanations` entry arguing for the wrong answer. Each was
confirmed from the source, not merely against the key:

| Paper | Bank said | Official | How it was confirmed |
|---|---|---|---|
| 2021 Q1 | D Smoothing | **C Electric** | The diagram is plainly a powered planer — motor housing with cooling vents, front depth knob, rear trigger handle |
| 2022 Q13 | C (Y) | **B (X)** | X carries a hardened carbide tip brazed across the shaft; W is an auger, Y a spade bit, Z a brad point |
| 2022 Q15 | B 7.50 m³ | **A 5.58 m³** | 15 × 10 − 7 × 5.5 = 111.5 m²; × 0.05 m = 5.575. The 7.50 distractor is the full rectangle with the notch left in |
| 2023 Q11 | B String lines and profiles | **D Painted pegs and ground spray** | The question says *surveyor* and *initial*: profiles and string lines are the builder's later set-out |
| 2024 Q11 | B 2900 | **D 4600** | North points up, so east is right; of the two eastern dimensions (5200, 4600) the setback is to the nearest wall. 2900 is a *southern* dimension |
| 2025 Q1 | D Electrical equipment | **C Flammable liquid** | AS 2444: a blue band is foam (AFFF) — Class A/B. Foam is water-based and conducts, so it must never go on live electrical equipment |

### Three questions whose option *text* did not match the paper's images

Found while checking option order — the trap the handover flagged for VET's 19 image
questions. The answers were already right, so the check would never have caught these; a
student would have been marked correct against a description of the wrong picture.

- **VET 2021 Q15** options read `Flat / Slope up / Slope down / Valley`, but the four
  cross-sections are a north→south rise, a fall, a rise-dip-rise and a rise-then-drop, and
  the committed crop shows only the site plan. Rewritten to describe the actual curves.
- **VET 2022 Q7 and Q13** invented descriptors for the W/X/Y/Z image options and got them
  wrong (`Y - masonry bit` for a spade bit; `Y - high corner` for a low position). Both
  reduced to plain `W / X / Y / Z`, exactly as the paper prints them — the committed crops
  already carry the labels.
- **Multimedia 2021 Q1** listed `Helvetica` and `Calibri`; the paper's options are
  `Comic Sans` and `Century Gothic`. Answer (D, Times New Roman) unaffected.

`vet-construction_2025_Q6` is fine: NESA redacted the images for copyright, and CramIT
carries its own drawn substitute where A is the cross-cut saw.

### New tooling

`scripts/backfill_qnum.py` — the positional Section I reader plus the exact-match join.
Deliberately preserved where the previous attempt's scratch script was discarded: that one
scored similarity, this one does not. It reports what it cannot resolve rather than
guessing, and `--write` refuses unless every question in the subject is resolved.

**Verified.** `node scripts/check_answer_key.cjs` → 225 checked, 0 wrong, 0 unverifiable
(it failed with exactly the 6 before the fix). `node scripts/validate_subjects.cjs` green
(MC=646, Written=243, 0 issues, 0 missing images). Re-running the exact-match join against
the written file reproduced all 90 machine matches with **0 contradictions**. Browser:
served the app, loaded VET through `openPicker`/`startQuiz`, rendered 2022 Q13 and answered
it — X marks correct, the drill-bit diagram loads at 800×646 (forced `loading="eager"`, as
stimulus images read `naturalWidth` 0 while the pane is hidden), all four rewritten
explanations render; 2025 Q1, 2021 Q15 and 2024 Q11 each mark correct at C, A and D
respectively against the shuffled option list. No console errors.

**Next.** Written answers as a second table, unchanged from the previous handover: the
marking guidelines are uniformly structured (`Question N` → `Criteria` → `Sample answer`)
and hold official sample answers plus mark-band criteria for ~340 written questions across
the three subjects. A scoped extractor reproduced 2020 Maths' 85-mark Section II total
exactly, so the approach works — but scope the extraction to the criteria table, *before*
`Sample answer`, since a naive digit regex over the whole block over-counts to 117 on
stray digits in the sample working. Note `qNum` alone will not be a sufficient join key
there: **2020 and 2021 Maths split some multi-part questions into separate rows (7 and 4
respectively) where 2022–2025 merge them.**

---

## 2026-08-27 (later) — VET 2021 Q15 option images cropped; the sweep found a second, worse case

Closes the `VET 2021 Q15` known issue in CLAUDE.md §11, including the sweep it asked
for. The sweep is the part that mattered: it turned up a Multimedia question that was
not merely missing pictures but **actively contradicted its own answer**.

### VET 2021 Q15 — the four cross-sections

Only the site-plan stimulus had ever been cropped; the four answer diagrams on page 7
of `2021-hsc-vet-construction.pdf` had not, so the question ran on text descriptions of
the curves. All four are now cropped and wired as `optionImages`.

The page defeats the usual extraction routes: there are **no embedded raster images**
(the diagrams are vector), and the option letters and the `North` / `South` /
`Ground level` labels are **outline paths, not text** — `get_text()` returns none of
them and `get_drawings()` reports only the chart boxes. The crop boxes are therefore
derived from an **ink profile** of the rendered page, which is the only reading that
sees every mark actually printed. Each option is two ink bands (chart + `Ground level`,
then a strip holding `North` / `South`); both are kept.

The paper's own `A.`/`B.`/… glyph is deliberately **excluded** from each crop, unlike
the 56 existing Maths option crops: `index.html` renders its own `<span class="option-label">`
beside the image, so a baked-in letter prints twice. (Option order is safe to rely on —
`shuffle()` shuffles the question list, never the options.)

Each crop was then read back and checked against the paper one by one — the §10 rule 6
trap. All four match their existing descriptions, and the contours (10.500 at the north
end rising to 12.500 at the south) confirm `answer: 0`. **No answer or option text
changed on this question.**

`scripts/crop_vet_2021_q15_options.py` is the script of record.

### A layout problem the crops created, found by measuring rather than assuming

These cross-sections are ~4.6:1 — twice as wide as any existing option image (Maths'
are ~2.2:1). In the `.options-grid-2x2` layout they render **160×35 px** at a 430 px
viewport (iPhone Pro Max), where a gentle dip in C is indistinguishable from a sharp
drop in D. The existing `@media (max-width: 380px)` single-column fallback does not
catch this, since 430 px is well above it.

Added an opt-in `"optionImagesWide": true` on the question plus an `.options-list-wide`
rule that keeps such options one-per-row at every width: **360×78 px**, more than double
the height. Maths' 14 image-option questions were re-checked and still render
`options-grid-2x2` at 2 columns — unchanged.

### The sweep — and Multimedia 2022 Q2

Two passes, because the obvious one would have missed Q15 itself:

1. **Bare-letter options** (`A/B/C/D`, `W/X/Y/Z`) — 7 questions. Four already carried
   `optionImages`; the other three (VET 2022 Q7 and Q13, VET 2025 Q6, plus Maths 2025 Q1)
   are *self-contained*: their single stimulus carries all four labels — wall positions
   W–Z, four drill bits W–Z, four saws A–D, network vertices A–F. Each was opened and
   confirmed, answers included. **None has Q15's gap.**
2. **Stem-based** — questions promising the options are pictures ("which of the following
   best represents/shows…"). This is the pass that finds Q15-shaped gaps, since Q15's
   options were *prose descriptions*, not letters. Six hits were CramIT-authored
   `variant: true` Maths questions (no paper exists, nothing to crop); two VET hits
   (2022 Q11, 2023 Q15) answer with the *name* of a drawing type, so text options are
   correct.

That left **Multimedia 2022 Q2**, which was worse than Q15. The paper shows three star
shapes labelled 1, 2, 3; the port carried no image and appended descriptions to the stem
instead — and **all three were wrong**:

| | paper | port said |
|---|---|---|
| image 1 | filled star, **no** outline | "outline star" |
| image 2 | **unfilled** star **with** outline | "filled circle" |
| image 3 | filled star **with** outline | "filled star" |

The keyed answer D (`2 and 3`) is right for the real pictures, but a student reasoning
correctly from the port's text answers A (`Only 1`) and is **marked wrong**. All four
`optionExplanations` argued from the same wrong descriptions. This is precisely what §10
rule 6 warns about — the answer-key check compares the official letter only and never
sees stem or option text, so it passed this question at 60/60 both before and after.

Fixed: stimulus cropped (`scripts/crop_multimedia_2022_q2_stimulus.py`), the stem
restored to the paper's exact wording ("Which of the following images uses stroke
colour?"), and all four explanations rewritten against the real pictures. **The answer
did not change.**

⚠️ **Process note.** The first edit to `multimedia.json` was written with
`json.dumps(indent=2)` and reformatted the whole file — 461 insertions for a 6-line
change, because it expanded the compact inline arrays in `studyNotes`. Reverted and
redone as a targeted text replacement (6 insertions, 5 deletions). **Do not round-trip a
subject JSON through `json.dumps` to make a small edit** — `vet-construction.json`
happened to survive it only because it has no compact inline formatting.

**Verified.** `node scripts/validate_subjects.cjs` green (MC=646, Written=243,
imageRefs 183→188, 0 missing images, 0 issues); `node scripts/check_answer_key.cjs`
225 checked, 0 wrong, 0 unverifiable. Browser (served locally, `loading='eager'` forced
since lazy images read `naturalWidth` 0 while the pane is hidden): VET 2021 Q15 renders
one-per-row at 430 px with all four crops at 360×78, A marks correct (score 1) and D
marks wrong with A shown correct, all four explanations rendering; Multimedia 2022 Q2
renders the new stimulus (755×271 natural) with the corrected stem, D marks correct;
three Maths option-image questions still render `options-grid-2x2` at 2 columns. All
five new images serve 200 OK; no console errors.

**Still open.** The bare-letter sweep covered MC and written questions in all four
subject files, but "options are prose descriptions of an uncropped picture" can only be
caught by reading stems — the regex used here is a good net, not a proof. The six
`variant: true` Maths graph questions describe graph shapes in text rather than showing
them; that is a content-quality choice for authored variants, not a gap against a paper,
and was left alone.

---

## 2026-08-27 (later still) — Written-answer key built and enforced in CI

The second answer-key table, carried forward from the previous handover. **203 written
questions across three subjects now check against the official marks on every push,
0 wrong, 0 unverifiable.** HMS is excluded and always will be until after the 2026 HSC —
it has no past papers.

### What is enforced, and what deliberately is not

The guidelines lay every part out as `Question N (a)` → a `Criteria`/`Marks` table →
`Sample answer:`. Both the **maximum mark** and the official **sample answer** are
extracted and committed; only the **mark** is enforced. Prose cannot be compared for
equality, so the sample answer is stored as the source a reviewer needs when a bank
answer looks wrong — not as an assertion. (Maths sample answers extract as mangled
equation text, e.g. `x2 102 82 = + 2 = 164`, since the layout is mathematical. Fine for
reference, useless for matching — another reason not to enforce it.)

### The join — aggregate to the question, don't match part-for-part

The handover's warning (`qNum` alone is not a sufficient key, because 2020 and 2021 Maths
split multi-part questions that 2022–2025 merge) is real, and the fix is to stop trying to
pair rows. The bank stores parts three different ways, sometimes in one subject:

    "qNum": 16          one entry covering every part of Q16
    "qNum": "23(a)"     one entry per part
    "qNum": "19(b)(i)"  one entry per sub-part

Each bank `qNum` is parsed into a base number plus a part path, and its expected marks are
the **sum of every official leaf part whose path starts with that path**. `16` sums all of
Q16's parts; `19(b)` sums (b)(i) and (b)(ii); `19(b)(i)` matches that leaf alone. Merged
and split storage reconcile under one rule, and the 2020/2021-vs-later difference stops
mattering. `omittedParts` marks are added back before comparing.

### Three extraction bugs, each caught by a total that didn't reconcile

The first run looked plausible and was wrong in three places. Every one was found by
checking totals against the papers' own stated section marks, not by reading output.

- **A naive digit regex over the block over-counts** (the handover said so; confirmed at
  117 for 2020 Maths against a true 85). The marks live in a right-hand column at x ≈ 485,
  so they are read **positionally** instead.
- **`Answers could include:` is the other spelling of `Sample answer:`.** Only stopping on
  the latter let the marks scan run into the answer body and swallow the page footer —
  `Page 18 of 23` gave 2022 Maths a phantom 23-mark Q35 (104 marks for the paper).
- **Extended-response criteria use mark *ranges*, and the text layer splits them.**
  Multimedia Section III prints `9–10`, `7–8`, … and `9–10` comes out as two words on the
  same line (`9–1` + `0`, the same fragmentation that renders `Marks` as `Mar` + `ks`).
  The marks column is now joined left-to-right per line before parsing, and a range takes
  its upper bound. Before this, Section III scored 6 instead of 10.
- A fourth, related: VET 2021 read **2077 marks**, because the last part had no answer
  heading at all, so its block ran to the end of the document and picked the year `2021`
  out of the trailing mapping grid. Filtering page furniture from the criteria scan (not
  just the answer text) fixed it.

### The totals reconcile exactly, against an independent source

Every paper, every year, matches the marks the exam paper's own front page states:

| Subject | Paper's front page | Extracted |
|---|---|---|
| Mathematics Standard 2 | Section II — 85 | **85** ×6 years |
| Multimedia | II 15 + III 15 = 30 | **30** ×6 years |
| VET Construction | II 35 + III 15 + IV 15 = 65 | **65** ×5 years |

This is the check that matters: it is not self-consistency, it is agreement with a
document the extractor never reads.

### A coverage gap found, and a way to record it

`check_written_key.cjs` reports correctness, not coverage — VET's written bank is a
deliberate *selection* (2021 holds 2 entries against a 35-mark Section II), so a
paper-total assertion would fail by design. Coverage was checked separately, once:
**Multimedia 2021 Q12 (2 marks)** is the only gap in an otherwise complete six-year
Section II port.

It turned out to be a *legitimate* omission that had simply never been recorded: the paper
asks the student to **draw** a digital audio wave pattern, and the guidelines award the
marks for "sketches a diagram of a stepped waveform". The engine cannot present or mark a
drawn diagram — exactly the class of Maths 2020 Q24(a), which *is* recorded via
`omittedParts`. There was no way to record it, because `omittedParts` hangs off a question
that exists and this whole question is absent.

Added a subject-level **`omittedQuestions`** key (multimedia.json) so the gap lives in the
data rather than only in prose, per §10 rule 5. The checker validates each declaration
rather than trusting it: the question must exist in the official key, the declared marks
must match it, and it must **not** also be present in the bank — so a stale declaration
cannot quietly excuse nothing. `validate_subjects.cjs` reads only known keys, so the new
top-level key needed no validator change.

### Verified

`node scripts/check_written_key.cjs` → 203 checked, 0 wrong, 0 unverifiable, 1 declared
omission. **Negative controls were run, because a check that has never failed is not known
to work:** perturbing a merged-part question (2020 Q16 → 3), a split-part question
(2020 Q23(a) → 5), and removing 2020 Q24's `omittedParts` produced exactly three failures
with the right expected values and exit 1; corrupting the declared omission's marks
(2 → 7) produced the fourth. All restored afterwards. Full local CI green: validate
(MC=646, Written=243, 0 issues), answer key 225/0/0, written 203/0/0, all Cloudflare
functions parse, `npm test` 67 passed / 0 failed. `validate.yml` gains one step; the YAML
parses and the step order is correct.

**Next.** Sample answers are committed but unenforced — the obvious follow-up is a
reviewer-facing diff of bank `answer` against the official `sampleAnswer` for the subjects
where the extraction is clean prose (Multimedia and VET; Maths is mathematical layout and
extracts badly). That is a human-judgement pass, not a CI check.

## 2026-08-27 (later) — HMS written questions were rendering no marks badge

Found while measuring the four subject files to see whether a porting playbook could
be grounded in what shipped rather than in recollection. It could not, quite: the four
ports do not share a schema, and one of the divergences was live on production.

**`index.html`'s written-question badge read `q.marks || q.totalMarks || ''`.** All 40
HMS written questions store the value as **`maxMark`** and carry no `marks` field, so
the expression fell through to `''` and the badge was suppressed entirely — a student
practising HMS written responses was never told what a question was out of.

Scoring was never affected. Every scoring path already reads `q.maxMark || q.marks`
(`renderResults()`, the AI-marking result, the keyword fallback, the submission
payload), and one other display path reads `q.marks || q.maxMark || q.totalMarks`.
Line ~1758 was the only read that omitted `maxMark`, so this was display-only and
silent — nothing threw, nothing scored wrong, the badge simply wasn't there.

Fixed by matching the order already used elsewhere: `q.marks || q.maxMark ||
q.totalMarks || ''`.

**Verified in the browser**, not from the diff: served the app and rendered the first
three HMS written questions (badges now read `4 marks`, `5 marks`, `4 marks`, matching
their `maxMark` values) plus two each from VET, Multimedia and Maths, all unchanged and
still correct on singular/plural (`1 mark` vs `2 marks`). No console errors. Local CI
green — validate (MC=646, Written=243, 0 issues, 0 missing images), answer key 225/0/0,
written marks 203/0/0.

**The underlying cause is schema drift between ports, and this fix does not address
it.** Measured across the four subject files:

| | Maths | Multimedia / VET | HMS |
|---|---|---|---|
| Topic field | `category` | *(none)* | `topic` |
| MC explanation | `solution` | `optionExplanations` | `explanation` |
| Written marks | `marks` | `marks` | `maxMark` |
| Paper identity | `year` + `qNum` | `year` + `qNum` | *(none)* |
| `bandDescriptors` | yes | Multimedia yes, VET no | yes |
| `acceptableAnswers` / `minKeywords` | yes | yes | no |

Some of this is legitimate — HMS has no `year`/`qNum` because no HMS paper exists and
none can until after the 2026 HSC. The rest is accidental, and the engine has been
absorbing it through fallback chains rather than the data being normalised;
CLAUDE.md §10 already documents `q.answer || q.modelAnswer || q.sampleAnswer` as the
normal way to read a model answer. **This fix deliberately continues that pattern** —
it is the safe change for a display bug, touching no data. The real remediation is to
normalise HMS's 40 written questions onto `marks` and have
`scripts/validate_subjects.cjs` enforce the canonical field names, since it is
currently permissive of unknown keys and so cannot catch a new port inventing its own.
That is a data migration and belongs with the porting playbook, not with a badge fix.

## 2026-08-27 (later still) — Subject porting playbook

Written in response to "if I said let's add Extension Maths 2020-2025, would Claude know
how to execute this end to end?" The honest answer was no. CLAUDE.md §10's "Adding a new
subject" is five steps that all begin *after* the hard part — step 1 is "Create
`subjects/{id}.json`", i.e. the entire port compressed into one imperative. The rest was
scattered across §10 as rules written reactively, each after the failure that motivated it.

`docs/porting-playbook.md` is the missing procedure: nine stages, each with an artifact
and a gate, covering feasibility through to long-term operation, and mapped onto the
Blueprint's agent roster so each stage can later be handed to an agent without
restructuring.

**Stage 0 exists to make "no" cheap.** Four fit tests — format (portable mark share from
the papers' own front pages), renderer (there is no MathJax or KaTeX in this project;
every subject so far survived on `<sup>`/`<em>`/Unicode), content shape, and precedent.
Extension Maths is the worked example of a NO-GO: roughly 10 MC marks of 70, the rest
extended working, plus notation the app cannot display. Mathematics Advanced is named as
the honest first candidate, because it passes all four and so exercises the *process*
rather than the engine's limits.

**The playbook is grounded in measurements of what shipped, not recollection** — and the
measuring turned up a live bug, fixed separately this session (HMS marks badge). It also
turned up the finding that gets its own stage:

**The four ports do not share a schema.** `category`/`topic`/none, `solution`/
`optionExplanations`/`explanation`, `marks`/`maxMark`, `bandDescriptors` in three of four,
`acceptableAnswers` in three of four. The engine absorbed all of it in fallback chains —
CLAUDE.md already documents `q.answer || q.modelAnswer || q.sampleAnswer` as the normal
way to read a model answer, which is a symptom rather than a design. Stage 3 now fixes
canonical names, separates legitimate deviation (HMS has no `year`/`qNum` because no HMS
paper exists) from drift, and records that `validate_subjects.cjs` is permissive of
unknown top-level keys and so cannot catch the next port inventing its own — extending it
is named as the remediation, to land before the next port rather than after.

**On scaling.** The Blueprint caps the Content Agent at autonomy Level 1 permanently
("commits wrong questions to repo"). The playbook argues that Stage 6's human gate is
therefore not transitional: five wrong Maths answers, six wrong VET answers and four
questions whose option text described the wrong picture all passed every automated check
that existed at the time, because `check_answer_key.cjs` compares the official *letter*
and cannot see reordered options, wrong option text, or prose substituted for a missing
picture. Two design consequences are recorded — ground truth must precede autonomy, and
each stage emits a reviewable artifact so a human approves a *stage* rather than a diff,
which is what makes Level 1 tolerable at volume.

Claims were verified rather than asserted: no MathJax/KaTeX in `index.html` (0 matches),
no unknown-key enforcement in `validate_subjects.cjs`, `studyNotes` images genuinely
outside `imageRefs`, Maths 318 = 90 HSC + 228 variants, VET 19 image questions.

CLAUDE.md updated in three places (header pointer, §6 file tree, §10 preamble) to make the
playbook mandatory reading before a port. No code or question data changed.

**Not yet done:** the playbook has never been run. It is prose until exercised against a
real paper, which is the intended next step — Mathematics Advanced Stage 0, producing the
first `docs/paper-reports/` entry (that directory still does not exist; the Content Agent
has never run). `scripts/survey_paper.py` to automate Stage 1's mechanical measurements is
deliberately deferred until the playbook has been exercised once and its gaps are known.

### Follow-up — source acquisition documented (same day)

Owner asked whether the code goes to NESA directly for papers, marking guidelines and
syllabus banding. It does, but only for one of the three, and the playbook as first
written did not distinguish the human and agent acquisition paths at all.

Verified in `agent.js`: `discoverNewPapers()` uses Sonnet 5 with the `web_search` tool,
system-scoped to `educationstandards.nsw.edu.au`, returning one direct `pdfUrl` per paper;
`downloadFile()` is a plain `https.get` (3 redirects, rejects >25MB) that holds the PDF
**in memory only** — base64'd for the API, never written to disk, never committed.

**The gap: it fetches the exam paper and nothing else.** The discovery prompt asks only
for "HSC exam papers"; marking guidelines are never requested and the syllabus is never
referenced anywhere in the code. Since `build_answer_key.py` and `build_written_key.py`
both parse the *marking guidelines* rather than the paper, the Content Agent can triage
and generate but **cannot produce ground truth** — agent-generated questions are
unverifiable by construction. That is a second, independent justification for the
Blueprint's permanent Level 1 cap, alongside the accuracy history already recorded.

Playbook updated with a "Source acquisition" subsection in Stage 0 (Path A human/local vs
Path B agent/automated, with a per-source table), and §10 now names extending discovery to
return the `-mg` URL as the highest-value single change to the agent. A compliance note was
added: automated retrieval of NESA material is a terms-of-use question at Path B's cadence,
assigned to the Compliance Agent (12) in the Blueprint; nothing fetched by either path is
committed or redistributed.

No code changed — documentation only.

---

## 2026-08-27 (later still) — Stage 0 run for real: Mathematics Advanced is a GO

First live use of `docs/porting-playbook.md`. Two things were being tested at once — whether
Mathematics Advanced is portable, and whether the playbook actually works. Both got an answer.

**Verdict: GO.** `docs/paper-reports/mathematics-advanced.md` — the first file ever written into
`docs/paper-reports/`, which did not exist before this session.

**What was measured, not assumed.** All six papers (2020–2025) are 100 marks: Section I = 10 MC,
Section II = 90 written, identical every year, read off the papers' own front pages. Section II
decomposes into 37–42 separately-marked parts per paper, almost all 1–5 marks — the same shape
Standard 2 already ports as 151 written questions. The unportable content is drawing tasks:
~42 of 540 marks across the six papers (~7.8%), about 14 parts, destined for `omittedParts`.
Portable share ≈ 93%, well inside the playbook's >70% band.

**The predicted blocker did not materialise.** Renderer fit was the flagged risk. The full
non-ASCII inventory across all six papers contains **no ∑, no matrices, no vectors, no complex
numbers and no radical sign** — Advanced lives inside the same `<sup>`/`<sub>`/Unicode constraint
Standard 2's 318 questions already do. Three constructs need a Stage 3 decision and none blocks:
integrals in a stem or option (~6 of 60 MC), stacked fractions in those same options, and a
braced piecewise function (2–3 across six papers). Notation complexity recorded as `basic`.

**The real cost is somewhere the four fit tests don't point.** Test 3 came back at roughly
**100 image assets** — 24 MC stimulus crops, 11 MC option-image sets (44 crops), 39 Section II
questions referencing a stimulus or table. The playbook's own appendix calls VET Construction's
19 image questions the heaviest load of the four existing subjects; this is several times that.
Compounding it, the papers' **text layer is garbled**: NESA typesets via a MathType-style font
mapping where `(x − 1)²` extracts as `^x - 1h2`, `#` is ×, and `ƒ` stands in for *f*. Section II
must be transcribed from rendered pages, not extracted. Both are scheduling facts rather than
blockers, but neither shows up in the mark-share arithmetic that drives the verdict.

**A Stage 6 dry run was done at Stage 0, and it was the best signal in the report.** Both
ground-truth builders were run read-only, writing nothing: `find_papers()` classified all six
years correctly, `extract_mc_key()` returned 10/10 answers for every year (60 total), and
`parse_paper()` returned 37–42 parts per paper with **zero unresolved** and an **exact 90/90
reconciliation against the front-page Section II total on all six papers**. Better than any
existing subject managed first time. This is now a Gate 0 checklist item.

**Playbook and tooling findings (recorded, not worked around):**

1. **`build_written_key.py` would have silently skipped this subject.** It globs
   `-mg\.pdf$`, so `2020_marking_guidelines.pdf` never matches and it exits with "no
   marking-guideline PDFs". Its sibling `build_answer_key.py` uses the tolerant
   `find_papers()` and handles the folder fine. Everything above came from calling
   `parse_paper()` directly. Recorded in the playbook as a **Stage 6 prerequisite** — not
   fixed here, because no gate has been passed that licenses editing shared tooling.
2. **A third PDF per year exists in this folder** that no other subject has —
   `{year}_marking_feedback.pdf`, NESA's notes from the marking centre. `find_papers()`
   classifies it correctly *only* because it tests `"feedback"` before `"marking"`; that
   ordering is load-bearing and invisible. Now stated in the playbook's input table.
3. **"One report per paper" is redundant when the paper format is stable across years.** Six
   near-identical files carry no more than one subject-level report with per-year rows. The
   per-paper convention comes from `agent.js`'s `triagePaper()`, which genuinely runs once per
   paper; a human Stage 0 does not. Playbook and CLAUDE.md §6 updated.
4. **A naive digit regex over a marking-guideline block over-counts — confirmed live.** A first
   pass here read Section II as 106 / 113 / 117 marks against a true 90, reproducing exactly the
   failure CLAUDE.md §10 rule 8 documents for 2020 Standard 2. The positional Marks-column reader
   got 90 on every paper. The rule holds.

**Stage 2 is blocked.** The official Mathematics Advanced syllabus is not saved locally and must
not be downloaded without asking the owner first. The 14 `MA-*` content codes pulled from the
marking guidelines' mapping grids are recorded in the Fit Report **explicitly labelled a
secondary proxy** — presenting a mapping-grid list as syllabus-grounded is the rule already
broken twice (Multimedia, VET) and it was not broken a third time here.

No code changed. Documentation and one new Fit Report only. Nothing was ported, no subject was
registered in `build_answer_key.py`, `build_written_key.py` or `index.html`.

---

## 2026-08-27 (later again) — Stage 2 done the same day: the syllabus, and `category` becomes derivable

Owner pushed back on Stage 2 being reported as "blocked" — correctly. The playbook's own
"ask before downloading" rule had been raised three stages *after* the GO decision, which turned
a predictable, known input into a stop. Owner supplied the NESA syllabus-development page and
said go. Fixed in the playbook: **that question now belongs at Stage 0**, asked once alongside
confirming the papers exist, and the answer covers the download — Stage 2 does not re-ask.

Second playbook correction, found by doing it: **Stage 2 does not depend on Stage 1.** Stage 1
surveys questions, Stage 2 reads the syllabus, neither consumes the other's artifact — and
Stage 2 is the one needing owner sign-off, so it should start early rather than queue behind the
survey. Everything else in the pipeline is genuinely sequential. Noted as the one exception to
"do not start a stage before its predecessor's gate passes".

**Stage 2 artifact:** `docs/subject-plans/mathematics-advanced.md` — a new convention. Stages
1–3 now share one living working document per port; Stage 0's Fit Report stays separate in
`docs/paper-reports/`, because it is the artifact that decides whether the rest happens.

**The syllabus.** `mathematics-advanced-stage-6-syllabus-2017.docx` (1.63 MB) downloaded from
nsw.gov.au and saved into `NESA Exams Folder/Maths Advanced/` under the same copyright treatment
as the papers, with `mathematics-standard-and-advanced-common-content.pdf` alongside. Read with
`python-docx`, paragraphs **and** tables: 1122 paragraphs, 10 tables, **14 subtopics, 358 content
dot points** across Year 11 and Year 12. The first URL tried returned an HTML wrapper with a
`.pdf` name — the real document is a DOCX, which is what the playbook already warns about.

**Two live syllabuses, and this port has a shelf life.** The 2017 syllabus governs every paper
we hold *and* the 2026 HSC; the **2024** syllabus takes over from the **2027 HSC** (Year 11
teaching from Term 1 2026). Grounding in 2017 is correct for this bank, but the topic list is
dated to a known HSC year — a decision to take deliberately, not discover. The 2024 syllabus is
web-only on curriculum.nsw.edu.au with no downloadable file found. Recorded in the playbook.

**The real find: `category` does not have to be guessed.** Every NESA marking guideline ends
with a **Mapping Grid** giving each question part's marks, syllabus content code and outcome
code. New `scripts/build_mapping_grid.py` extracts it to `data/mapping-grid/{subject}.json` —
committed, because CI can never regenerate it, exactly like the answer keys. Results:

- **All six papers reconcile to exactly 100 marks, zero uncoded rows** (the script refuses to
  write otherwise).
- Independently cross-checked against `build_written_key.py`'s positional reader: **the two
  agree on every Section II part in all six papers**, with one benign structural difference
  (2023 Q31 — the grid splits it as `31(b)`, the guidelines head it as `31`; totals match).
- Two extraction traps, each of which produced a wrong number before being found, are recorded
  in the script's docstring: the code can be **split across words** in the text layer (`MA- M1`,
  the same family as the `9–1` + `0` mark-range split already documented), and a row's cell text
  is **vertically centred so it can begin above its own label line** — reading forward from the
  label attributes it to the previous row. First pass captured 583 of 600 marks and left six
  rows uncoded; with both fixed, 600 of 600.

**Scope vs examination, measured on both axes for the first time in this project.** This is the
check the VET incident produced the rule for, and Advanced diverges harder than VET did:

| | Syllabus scope | Examined, 6 papers |
|---|---:|---:|
| MA-C1 Introduction to Differentiation | 10.6% | **1.3%** |
| MA-F1 Working with Functions | 15.6% | 6.8% |
| MA-C3 Applications of Differentiation | 5.3% | **15.7%** |
| MA-T3 Trigonometric Functions and Graphs | 1.7% | **6.8%** |

MA-C1 is the second-largest subtopic in the syllabus and near-invisible across six years of
papers — Year 11 foundation content that Year 12 calculus questions silently assume. A
grid-derived topic list would have all but deleted it, and bloated T3 and C3. **Rule now in the
playbook: use the grid for per-question `category`, the syllabus for topic weighting.**

Also recorded: Advanced's `F1`, `M1`, `S1` and `S2` collide with Standard 2's category codes and
mean different things (Standard 2's `F1` is financial "Money Matters"; Advanced's is "Working
with Functions"). Nothing breaks — separate files, separate filters — but never key a shared
lookup on the bare code.

Nothing ported. The subject is still registered nowhere in `index.html`,
`build_answer_key.py` or `build_written_key.py`. `validate_subjects.cjs` green and unchanged
(646 MC / 243 written / 0 missing images).

---

## 2026-08-27 (later still, again) — Exam-trend data: both axes, measured, for two subjects

Owner shared a 2025 Word document — *"Breakdown of Year 12 HSC Mathematics Standard 2 Exam
Trends"* — from their Drive, wanting that kind of frequency/weighting analysis built into the
app's Study Mode notes, and observed that the two-axis data from the Maths Advanced Stage 2 work
already provides it per subject. Correct, and it turned out to be buildable the same session.

**What the source document actually is** (stated plainly, because it should not be copied
verbatim): despite the filename, its content is **Mathematics Standard 1**, not Standard 2 —
its own title says so and it quotes Section II as 70 marks, where Standard 2 is 85. Its year
table covers 2020, 2021, 2023, 2024 with **2022 missing**; one of its three tables is empty; and
its weightings are explicitly *word-frequency* estimates ("Area & Measurement… 33 mentions",
"Financial Mathematics (20–25% of Marks)"). Word counts are not marks. The *idea* is good; the
numbers are not reusable. It also carries third-party study links (Khan Academy, MathSpace,
HSC Study Lab) that would need their own decision before appearing in-app.

**Built instead — two new scripts and two committed data sets.**

`scripts/build_mapping_grid.py` extended from one subject to two. Findings on the way:

- **All four subjects' marking guidelines carry a Mapping Grid**, but only the two maths
  subjects state a syllabus *code*; Multimedia and VET give prose topic names, a different
  parse. Only the coded ones are registered.
- Standard 2 uses `MS-` content codes and `MS11-n` / `MS2-12-n` outcome codes. The old regex
  conflated the two shapes; the rule that separates them cleanly is that **an outcome code has
  digits before the hyphen**. Content is now `\b([A-Z]{2})-\s?([A-Z])\s?(\d)\b`.
- **NESA has a typo in its own 2020 Standard 2 grid**: Q22 reads `MS2-F4` where every other row
  in six years reads `MS-F4` (Q21 directly above, same topic and same outcome, is spelled
  correctly). Handled by an explicit `SOURCE_TYPOS` table that prints every substitution it
  makes — not by loosening the regex until it passes. The script's refusal-to-write caught this;
  it reported `BAD 2020 << 22: no syllabus content code` and exited non-zero.
- All twelve papers across both subjects now reconcile to **100 marks with zero uncoded rows**.

**The grid validates the live bank.** Cross-checked against `subjects/mathematics-standard-2.json`:
its 16 `category` codes match the grid's 16 exactly, and **all 90 original (non-variant) MC
questions agree with NESA's official topic tagging — 0 disagreements, 0 unmatched**. That is
the first independent verification the Standard 2 topic tags have ever had.

`scripts/build_exam_trends.py` (new) joins syllabus **scope** to examined **marks** and emits
`data/exam-trends/{subject}.json`: per topic, the dot-point count and share, marks and share
across all papers, marks per paper, how many years it appeared in, the MC/written split, a
per-year series for a sparkline, and a `yieldRatio` (examShare ÷ scopeShare). The Mathematics
Standard syllabus DOCX was downloaded to `NESA Exams Folder/Maths Standard 2/` alongside the
papers (the obvious URL 404s — the real link is `…-2017-syllabus-word.docx`).

**The result is the point.** Standard 2, 6 papers, 600 marks, 282 syllabus dot points:

| | scope | exam | yield |
|---|---:|---:|---:|
| F5 Annuities | 1.8% | 7.3% | **×4.14** (43 of its 44 marks are written) |
| M6 Non-right-angled Trigonometry | 4.6% | 11.7% | ×2.53 |
| M7 Rates and Ratios | 5.0% | 9.0% | ×1.81 |
| S1 Data Analysis | **13.5%** | 3.9% | ×0.29 |
| F1 Money Matters | 11.3% | 6.6% | ×0.58 |
| A2 Linear Relationships | 3.2% | 1.3% | ×0.42 — only **3 of 6** papers |

Mathematics Advanced runs the same way: C3 ×2.96, T3 ×4.03, against C1 ×0.12 and F1 ×0.44.

**Both axes must be shown, never one.** Ranking study time by marks alone tells a Standard 2
student to skip Data Analysis (13.5% of the syllabus) and an Advanced student to skip
Introduction to Differentiation (10.6% of the syllabus, 1.3% of marks) — the Year 11 foundation
every Year 12 calculus question assumes. Ranking by scope alone hides that Annuities is five
dot points earning 7.3% of the paper. The `yieldRatio` is the interesting number precisely
because it is a ratio of the two.

No UI was built. This is the data layer only; where it renders in Study Mode is a design
decision for the owner. `validate_subjects.cjs` green and unchanged (646 MC / 243 written /
0 missing images); no subject JSON was modified; no PDF or DOCX is in the repo.

---

## 2026-08-27 (last) — Port runbook: one stage per session

Owner will execute each remaining porting stage in its own fresh session. Restructured the
Mathematics Advanced documentation so a cold session can open one file, run one stage, tick its
gate and write the result back — without re-deriving anything.

`docs/subject-plans/mathematics-advanced.md` is now the **runbook and single entry point**:
a stage/status/session-count table, a paste-in session prompt, the standing rules, and an
"established facts" block carrying forward every measured number (294 question parts — 60 MC
plus 234 Section II parts across 131 questions; asset counts; the garbled text layer; the
pre-verified ground-truth reconciliation). Each stage then has its own section with its gate,
its traps and its exact commands.

Session estimate recorded: Stage 4 is **~6 sessions, one paper per year**, suggested order
2024 → 2025 → 2023 → 2022 → 2021 → 2020 (2024 is the lightest asset load and cleanest text, so
it establishes the pattern; 2020 is heaviest). Stage 5 is 2–3 sessions for ~100 crops.

Two things were carried into the runbook that would otherwise have been lost between sessions:
the Stage 6 prerequisite to **fix `build_written_key.py`'s `-mg.pdf` glob** before registering
the subject, and the correction that the Stage 0 stem sweep used a regex **missing
`could represent`** and therefore undercounted pictorial MC stems — Stage 1 must use the
corrected pattern.

`docs/handover-maths-advanced-playbook-test.md` gets a **⛔ SUPERSEDED banner** redirecting to
the runbook. It is kept, not deleted, as the historical record of the brief that produced
Stages 0 and 2 — but two overlapping handover documents is exactly the confusion that damages a
cold session, so the redirect is unambiguous.

Documentation only. No code, no data, no subject JSON changed.

---

## 2026-08-28 — Mathematics Advanced Stage 1 (Survey): all 294 parts classified

First stage run under the new one-stage-per-session runbook. Every part in
`data/mapping-grid/mathematics-advanced.json` was located in its exam paper by *(page, y)* and
classified for presentation — type, stimulus, options, aspect ratio, text-layer quality. Nothing
was left unresolved, and the full result is written into
`docs/subject-plans/mathematics-advanced.md` under Stage 1, with Gate 1 ticked.

**Method, and the finding that matters most about it: no single detector is complete.** Three
were run and unioned — text-gap bands (ink in a band carrying no body text), `page.find_tables()`
filtered to ≥6 cells, and an ink profile (dark pixels outside every text-block bbox at 72 dpi) —
and then *every* candidate was rendered onto labelled contact sheets and looked at. Each detector
missed assets the others caught: the band detector loses a chart whose axis labels are wide text
blocks (it lost 2022 Q11(b)'s Pareto chart), the ink profile loses a diagram whose labels sit
inside one large text block, and `find_tables()` reads graph axes as 2×2 tables in both
directions. **Four Section II diagrams — 2022 Q28, 2024 Q20, 2025 Q28, 2025 Q29 — surfaced only
in the union plus the visual pass.** Had this been a single-detector sweep, four questions would
have shipped with a missing stimulus. This is now recorded in the playbook's Stage 1.

**Numbers (all measured, none estimated):**

- **121 crops and 28 tables**, against Stage 0's "~100 image assets". Section I: 25 stimulus
  images, 12 option-image sets (48 crops), 10 tables, 22 plain-text stems. Section II: 48 crops,
  18 tables. Stage 5's session estimate moves from 2–3 to 3.
- **17 unportable parts, 41 marks** — 7.6% of Section II, 6.8% of the paper, portable share
  **93.2%**, confirming Stage 0's ~93%. Five are whole single-part questions (2020 Q16, Q24;
  2021 Q19, Q21; 2024 Q19 — 17 marks) and belong in `omittedQuestions`; the other 12 are
  `omittedParts`.
- **124 of 294 parts (42%) carry a detectable text-layer corruption**, and 91 contain at least
  one stacked fraction (599 fraction bars across the six papers).

**Two corrections to Stage 0's Section I table**, both found by rendering the page rather than
reading the stem: **2020 Q9** has four option images (normal curves, different regions shaded)
and **2021 Q6** has a probability-tree stimulus — both had been counted as plain text.

**A correction to Stage 0's notation verdict.** Stage 0 recorded "no radical sign" from a
non-ASCII inventory of the *text layer*. **√ and ∞ are printed on these papers but drawn as
vector paths, so neither character exists in the text layer at all** — zero occurrences of either
across 2020–2025. 2022 Q4's options extract as `( − , 1` for `(−∞, 1]`; 2020 Q1 is
`y = √(2x − 3)`. Both are ordinary Unicode and the GO is unaffected, but the line would have
misled Stage 4. Corrected in the Fit Report and the runbook.

**A correction to "the text layer is garbled on every paper".** It is — but **not the same way
each year, and only 2024 uses the MathType bracket mapping** that Stage 0 quoted (`^x - 1h2` for
`(x − 1)²`). Searching a 2021 paper for that pattern finds nothing. What *is* common to all six:
∞ and √ absent, **π extracting as the letter `p`** (`0 ≤ x ≤ 2p` means `2π`; only 2020 contains a
single genuine `π`), and stacked fractions split and re-ordered — "Show that P = 2x + 72/x"
extracts as `72 (a)  Show that P = 2x + . x`. 2022 additionally scrambles reading order.

**Stem sweep run; 13 hits, all resolved.** Twelve are complete (the paper prints four separate
diagrams, already in the option-image list); one — 2021 Q3 — is genuinely a text question with
interval-notation options. **No question was found where prose stands in for a missing picture**,
so the Multimedia 2022 Q2 failure has no analogue in this subject. **The playbook's regex was
incomplete and has been fixed there**: it misses `which of these …` (2024 Q8) and
`a possible sketch` (2023 Q6), both picture-option questions.

**Trap 2 resolved as not-applicable.** Every MC question whose options look like bare letters
(2020 Q10, 2023 Q5, 2024 Q10, 2025 Q10) has *numeric* options — 0/1/2/3, not labels pointing into
a shared stimulus. Nothing here resembles VET 2021 Q15.

**Two new schema cases were handed to Stage 3**, which now has six decisions rather than two:
options printed as **rows of a table** (2020 Q2, 2020 Q3, 2022 Q2, 2023 Q4 — flatten each row
into a text option, or render the table in the stem?), and **blank tables the student fills in**
(2024 Q11, Q13 — reproduce as HTML, answer as a keyword-marked text list). Also recorded: seven
portable parts lean on a part we omit, of which **2021 Q27(d) is the only one that cannot stand
alone** ("Explain your answer by referring to the graph drawn in part (a)") — a Stage 4 decision,
deliberately not resolved by rewording NESA.

A false positive worth remembering: a drawing-verb sweep flags roughly 40 parts, but *the* shaded
region means the paper drew it. 2020 Q27 was a false positive twice over — "box-**plot**" matched
the verb, and the box plot is a given stimulus.

Documentation only. No code, no data, no subject JSON changed; nothing is ported and the subject
is still registered nowhere. Stage 3 is next.

---

## 2026-08-28 (later) — Mathematics Advanced Stage 3 (Schema): ten decisions, measured in a browser

Stage 3 is nominally the short stage — write the field mapping down before authoring any
question. It stayed short in output and got longer in findings: **the six decisions the runbook
carried are taken, and four more came out of reading the engine rather than the papers.** Two of
those four are live defects that would have shipped.

**Method.** Stage 3 is a documentation stage, so no code changed. But the decisions turn on how
`index.html` actually renders things, and this project has a standing rule that correct data is
not the same as correct output. Every rendering claim below was **measured in a browser at a
430 px viewport**, on a scratch page carrying `index.html`'s own CSS rules verbatim — not
inferred from reading markup. The scratch page lived in the git-ignored `diagrams/_debug/` and
was deleted; the working tree is untouched.

**The field mapping (the Gate 3 artifact) is fully canonical, with zero deviations.** Maths
Advanced has past papers, an official syllabus code per question and an official mark, so every
canonical field is available: `year`, `qNum`, `category`, `marks`, `answer`, `optionExplanations`,
`omittedParts`, `omittedQuestions`. Two additions carry provenance rather than rename anything:
`gridCodes` (below) and `section`, which Standard 2 already carries on all 151 written questions.

**Four engine facts worth having written down**, all confirmed by reading `index.html`:

- `q.q` renders through `formatQuestionText()`, which passes HTML through untouched — and also
  parses **pipe-delimited markdown tables**, a path Maths has never used (Standard 2 writes
  `<table>` HTML in all 34 of its tables).
- Option strings may contain HTML, **but with `optionImages` the same string is reused as
  `alt="${opt}"`** — an option carrying a double quote breaks the tag.
- The results breakdown injects `q.q` and `q.options[i]` **raw** into a 12 px card, bypassing
  `formatQuestionText()`. A table-shaped option renders a whole table there.
- `validate_subjects.cjs` **fails** a written question with neither `keywords` nor
  `acceptableAnswers`. A scoring mechanism is mandatory, not a nicety.

**The two live defects.**

*The category-label map collides.* Stage 2 warned abstractly: "never key a shared lookup on the
bare code." `NESA_CAT_LABELS` **is** that lookup — one flat global map, consulted for whichever
subject is on screen. **Five of Advanced's fourteen codes collide with Standard 2's**, each
meaning something different: `F1` would render "Money Matters" for Working with Functions, `M1`
"Measurement" for Modelling Financial Situations, `S1` "Data Analysis" for Probability, `S2`
"Probability" for Descriptive Statistics, `F2` "Investment" for Graphing Techniques. Decision:
**the data keeps bare syllabus codes** — they match Standard 2, the mapping grid and the syllabus,
and prefixing them would put `MA-` in front of the student on every filter chip. The *map* becomes
subject-aware instead, at Stage 7. Noticed in passing: `M6` is live in the Standard 2 bank and
absent from the map, so it already renders bare — pre-existing, not this port's to fix.

*Written questions render no topic badge.* The MC renderer badges with `q.category || q.topic`;
the written renderer reads `q.topic` alone. Canonical `category` therefore shows a year badge and
nothing else — **which means all 151 Standard 2 written questions have shown no topic since their
port**. This is the HMS missing-marks-badge defect exactly: nothing throws, nothing scores wrong,
no validator can see it. Decision: keep `category` (it is canonical, and it already drives the
written *filter*), fix the one line at Stage 7, which lights up Standard 2 as a side-effect. The
playbook now records this alongside the HMS case, so the next port does not work around it by
writing `topic`.

**A third finding corrects both the runbook and the playbook.** Both said mobile tables are fine
because "`.study-dtable` collapses to stacked cards." **It does not** — that class is applied in
exactly one place, `renderStudyBlock()`, and the question renderer never uses it. Question tables
get `.q-table` or `.nesa-table`, and neither collapses *or* scrolls. Measured at 430 px, where the
stem is 390 px wide: a 6-column table fits (`width:100%` compresses it); an **8-column table
renders 513 px and pushes `body.scrollWidth` to 533** — and since `body` sets
`overflow-x: hidden`, its right-hand columns are **silently clipped**. No scrollbar, no error,
just missing data on a lookup table the student needs to answer the question. Six of the 28
tables are future-value / z-score grids. Rule: **7 or more columns goes in an `overflow-x:auto`
wrapper** — measured at 390 px visible, 520 px scrollable, page overflow gone. Corrected in
`docs/porting-playbook.md` with the markup and the numbers.

**The remaining decisions, each fixed so Stage 4 never re-decides:** piecewise braces as an
inline `rowspan` table (measured — the brace cell and the two-row block are both 48.3 px, so it
spans exactly), inline Unicode for integrals and fractions following Standard 2's existing bank
(`1/48`, `(4/3)π` — it has no stacked-fraction markup anywhere), table-row options **flattened**
to text (a flattened option measured 52 px, one button), blank tables reproduced as HTML with a
keyword-marked cell-value answer, and the Unicode character set matched to Standard 2's live
inventory (`−` U+2212 883×, `×` 1024×, `π` 61×, `√` 16×, Unicode superscripts over `<sup>` by
300:5). Every character was width-measured in the app's fonts — all render real glyphs, none
falls back to a notdef box. `∫` renders narrow but real.

**One decision the runbook had not anticipated: 21 of 294 parts carry two or three syllabus
codes.** The mapping grid stores `codes` as a *sorted set*, so "take the first" means "take the
alphabetically first" — which would file 2025 Q28(b), a trig-graphs question, under `T1`. Rule:
the 273 single-code parts take their code mechanically; for the 21 (2020 ×3, 2023 ×2, 2024 ×6,
2025 ×10, all enumerated in the runbook) Stage 4 picks the code naming the skill the marks are
awarded for and records the full official list as `gridCodes`, so the pick is auditable and
NESA's tagging is not lost.

**Closing out the session surfaced one more contradiction, and Stages 4 and 5 were merged.**
`validate_subjects.cjs` **exits 1** on a question whose `image` path has no file yet — verified
by running it, not assumed. Stage 4 authors questions; Stage 5 crops the 121 images. So porting
all six papers before cropping would leave the validator, and CI on every push, red for six
sessions — and **Gate 4's own wording, "validator green, `missingImages: 0`", is unsatisfiable
under that order**. Owner's decision: **interleave**. Each session now ports one year *and*
crops that year's assets, finishing green, with every question answerable the moment it is
authored. Stage 5 survives as the asset *method* reference the sessions consult; its three
checks moved into Gate 4, applied per year. Owner also chose to run the six sessions on a
**`port/maths-advanced` branch**, merging to `main` only when the subject is complete — `main`
keeps a clean CI signal, and Cloudflare's branch preview serves the mobile-width check instead
of a half-ported subject going live.

**That merge made per-year asset load the thing that sizes a session, which overturned the
suggested order.** Splitting Stage 1's own lists per year (reconciling exactly to 121 crops and
28 tables) shows **2024 is the heaviest paper at 30 assets, not the lightest**. The runbook had
2024 leading on the strength of a Stage 0 sentence — "lightest asset load, 2 graphic-bearing
MC" — that Stage 1's measurements had already contradicted without anyone noticing: 2024
Section I has **seven** graphic-bearing MC. **2020 leads instead** (joint-lightest at 22 assets,
lowest corruption rate at 37%, and it exercises three Stage 3 decisions early — options as table
rows, two `omittedQuestions`, one `omittedParts`). Order is now 2020 → 2023 → 2022 → 2025 →
2021 → 2024, with a per-year tracker table in the runbook that each session ticks so the next
cold session knows which paper is next.

Documentation only. No code, no data, no subject JSON changed; nothing is ported and the subject
is still registered nowhere. **Stage 4 is next: six sessions, one paper each, starting with 2020,
on `port/maths-advanced`.**

---

## 2026-08-28 (later still) — Mathematics Advanced Stage 4, paper 1 of 6: the 2020 port

First session of the six-session port, on a new `port/maths-advanced` branch. One paper: all
49 question parts of the 2020 HSC, plus that year's 18 crops, finishing with local CI green.

**What shipped.** A new `subjects/mathematics-advanced.json` — 10 MC, 19 written entries, 2
`omittedQuestions`, 1 `omittedParts` — and 18 JPGs in `/diagrams/`, cut by a new
`scripts/crop_maths_advanced.py`. The subject is deliberately registered **nowhere**: no
`subjects/index.json` row, no `SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no card. That is Stage 7.
`validate_subjects.cjs` globs `subjects/*.json`, so CI covers the file from now on regardless;
the two key checkers skip it until Stage 6 commits its keys.

**Marks reconcile to exactly 100.** Not just as a paper total — per question, against
`data/mapping-grid/mathematics-advanced.json`, using the same prefix-sum join
`check_written_key.cjs` will apply at Stage 6. A build-time assertion also refuses to write the
file unless every `category` is one of NESA's own codes for that question.

**The MC answers were checked before they were authored.** `extract_mc_key()` from
`build_answer_key.py`, called read-only on `2020_marking_guidelines.pdf`, returns
`D B A B C B A A C D`. Ten independent derivations from the paper agreed with all ten. This is
not a substitute for Stage 6 — it just means the port did not begin from guesses, and it cost
one function call rather than an "audit", which CLAUDE.md §10 forbids for exactly the reason
this avoids.

### Five decisions Stage 3 could not have taken

Stage 3 fixed every field name, character and markup form, and all ten of its decisions held.
Five more things only surface once questions are actually being written, and they are now
recorded in the runbook as inherited by every later year:

1. **One bank entry per NESA question, not per part.** Mathematics Standard 2 stores 140 of its
   151 written entries that way, and the checker's join sums every official leaf part under a
   bank entry's `qNum` prefix, so merged storage reconciles trivially.
2. **A merged entry spanning parts with different syllabus codes** takes one `category` — the
   skill the marks are awarded for — and keeps NESA's full list in `gridCodes`. That is Stage 3
   decision 7 applied one level up. Used on Q18, Q21, Q25, Q30 and Q31.
3. **An omitted part inside a question the bank still carries forces the merged form.** 2020 Q11
   loses part (a) (draw the model on a printed grid). Stored as two entries `11(b)` and `11(c)`,
   each would match only its own leaf and the dropped mark would vanish with nothing reporting
   it — precisely what `omittedParts` exists to prevent. Stored as one entry `"11"` with
   `marks: 3` and `omittedParts: [{part: "a", marks: 1}]`, the checker adds it back to 4.
4. **NESA's part letters stay even when a part is dropped.** Q11 presents "(b)" and "(c)" with no
   "(a)", followed by a visibly separate italic note saying what part (a) asked for. Re-lettering
   would be rewording NESA; leaving "the grid on the previous page" dangling unexplained would be
   worse for the student.
5. **Options carrying `optionImages` must be plain text.** The engine reuses the option string as
   `alt="${opt}"`, so Q5 and Q9 describe their graphs in bare text with literal `μ`/`σ`, while
   every other option string in the paper uses `<em>`/`<sup>`.

### The crop that looked right and was wrong

Cropping is where this port loses money, and the first pass lost some.

The new `scripts/crop_maths_advanced.py` is deliberately **not** an entry in
`scripts/diagram_registry.json`. That registry's coordinates are raw pixels verified at
`RENDER_DPI = 150`, `save_crop()` overwrites unconditionally, and a bare run with no `--year`
re-cuts every Mathematics Standard 2 crop — none of which this port needs to touch. The new
script stores **PDF points**, so its DPI can change without moving a crop, and takes `--year`, so
each remaining session adds one registry block.

Its coordinates come from an **ink profile** — dark pixels at 150 dpi, grouped into bands with a
configurable gap — because on these papers the option letters and most axis labels are outline
paths, so `extract_maths_diagrams.py --calibrate`, which finds labels through `get_text()`, finds
nothing at all.

⚠️ **The standing rule "exclude the paper's own `A.`/`B.` glyph" cannot be met with an x-cut
here.** The letter sits in the cell's top-left corner and the graph runs underneath it: on 2020
Q5 option A the letter spans x 100.8–111.3 pt and the graph's own x-axis starts at x 102.2 pt.
The first pass cropped from x = 114 pt and silently amputated the left arm of the parabola and
the end of the axis. Files written, non-empty, plausible, wrong — the same failure signature as
the `RENDER_DPI` trap, caught only by putting the crops in a contact sheet and looking at them.
The fix is an `erase` rectangle: crop the whole cell, then paint white over the letter's own
bounding box, with an ink profile of that x-strip confirming first that nothing but the letter
is inside it. All 18 crops were then compared against the paper option by option.

### Measured at 430 px, not inferred

Stage 3 measured its rendering claims in a browser and this session re-measured them against the
real questions:

| Case | Measured | Verdict |
|---|---|---|
| Q3's 4-column table, bare `.q-table` | 390 px, `body.scrollWidth` 430 | fits |
| Q20's **7-column** table in the `overflow-x:auto` wrapper | wrapper 390 px, scrolls to 520 px internally, `body.scrollWidth` **430** | decision 9 works |
| Q23's piecewise brace (decision 1) | brace cell 38.0 px, two-row block 38.0 px | glyph spans the rows exactly |
| Q5 / Q9 option images in `.options-grid-2x2` | 160 × 143 px and 160 × 90 px | legible |
| `∫ ∞ √ ≠ → π σ μ − ≤ ² ³` | 4.9–18.0 px, all distinct from `�` at 17.5 px | real glyphs, no notdef |

**`optionImagesWide` confirmed unnecessary**, as Stage 1 predicted — nothing like the VET
160 × 35 px case that created the flag.

One process note for sessions 2–6: `subjects/mathematics-advanced.json` round-trips
**byte-for-byte** through `json.dumps(indent=2, ensure_ascii=False)` plus a trailing newline
(verified). Unlike `multimedia.json`, which has hand-authored compact inline arrays and must
never be round-tripped, this file is safe to load, extend with a year, and dump.

**Local CI green:** `validate_subjects.cjs` reports `MC=656 Written=262 imageRefs=206
missingImages=0`, 0 issues; the answer-key and written-key checks still pass on the three
subjects that have keys. Gate 4 is ticked for 2020 in the runbook, and the tracker now says
**2023 is next**.

---

## 2026-08-28 (later still, again) — Mathematics Advanced Stage 4, paper 2 of 6: the 2023 port

**The 2023 HSC paper is ported and cropped, on the `port/maths-advanced` branch.** Same shape as
the 2020 session: Section I, then Section II, then that year's crops, then the validator — and
the session finishes green rather than leaving CI red for a later asset stage.

**What landed.** `subjects/mathematics-advanced.json` gains **10 MC + 22 written entries**, one
bank entry per NESA question, plus **three `omittedParts`** — Q18(a) (plot the mean point and
the intercept on a printed grid, 3 marks), Q19(a) (sketch two functions on a printed grid, 2)
and Q30(b) (sketch *y* = e⁻ˣ sin *x*, 2). **2023 adds nothing to `omittedQuestions`**: no whole
question on this paper is a drawing task, exactly as Stage 1's survey predicted. The file now
holds 20 MC and 41 written entries across two years.

**Marks reconcile to exactly 100** — 10 MC + 83 written + 7 omitted — against
`data/mapping-grid/mathematics-advanced.json`, using the same prefix-sum join
`check_written_key.cjs` applies. The build script refuses to write unless four things hold at
once: that join, the paper total, every `category` being one of NESA's own codes for that
question, and every `gridCodes` list equalling NESA's own union. It also refuses if the existing
file does not round-trip byte-for-byte first, so a reformatting accident cannot ride along with
the append.

**Answers were confirmed before authoring, not audited afterwards.** `extract_mc_key()` from
`build_answer_key.py` was called read-only on `2023_marking_guidelines.pdf` — **`D D A B A C A B
D C`** — and ten independent derivations from the paper agreed with all ten. That is not a substitute for Stage 6, which commits the key and puts it
under CI; it just means the port did not start from guesses. (CLAUDE.md §10 forbids re-reading
a marking guideline to "audit" answers; calling the extractor is the sanctioned path.)

**Assets: 17 crops**, via a new `--year 2023` registry block in `scripts/crop_maths_advanced.py`.
Section I: Q1, Q2, Q4, Q5 and Q10 stimulus, plus Q6's four option cells. Section II: Q16, Q22,
Q23, Q24, Q26, Q27, Q28, Q32. Boxes came from an ink profile at 150 dpi rather than the text
layer; every crop was then assembled into contact sheets and compared against the paper, option
by option.

**Two findings that correct the Stage 1 survey, both recorded in the runbook.**

1. **The Section II crop list was one short.** 2023 **Q16** — the shape *APQBCD*, a labelled
   geometry diagram with an arc, a radius and an angle — is not on Stage 1's list and surfaced
   only when the question was read for porting. Stage 1 unioned three detectors and looked at 23
   contact sheets, and still missed it, so the list is now documented as a **lower bound**; the
   subject total moves 121 → 122 crops. Each remaining session should read its own questions'
   pages rather than trusting the list to be complete.
2. **"Lookup table" is not the test for the scroll wrapper — the column count is.** Stage 1
   flagged six "future-value / z-score lookup tables" as needing Stage 3 decision 9's
   `overflow-x:auto` wrapper, and 2023 Q15 is on that list. It has **5 columns** and fits at
   390 px unwrapped. The table that actually needed the wrapper on this paper is **Q23's
   11-column z-table**, which is not on the list at all. Measured: Q23's wrapper stays 390 px
   wide and scrolls to 694 px internally, with `body.scrollWidth` unchanged at 430.

**A tie-break the merged-entry rule needed.** Stage 3 decision 7 and the 2020 session both say a
merged entry spanning several syllabus codes takes "the code naming the skill the marks are
actually awarded for". Two 2023 questions split their marks **evenly** between two codes, so
that rule decides nothing: Q26 (`C4`/`T3`, 2 marks each) and Q32 (`C4`/`F1`, 3 each). The
tie-break taken, and inherited by the remaining four papers: **take the part carrying the heavier
mathematical demand** — the calculus part in both cases — and keep NESA's full list in
`gridCodes`. It agrees with 2020's Q30, which took `C4` of `C4/F1`. Q24 (`C3` of `C3/F1`),
Q27 (`F2` of `C1/C4/F2`) and Q28 (`C4` of `C1/C4`) were settled by mark weight.

**The option-letter trap did not recur here — but it was checked, not assumed.** On 2020's paper
the `A.`/`B.` glyphs are outline paths sitting on top of the graph, and a first pass amputated a
parabola by cropping to their right. On 2023 page 6 the letters are real **text**
(`get_text("words")` returns exact boxes) and `get_drawings()` reports **zero** vector paths
intersecting any of the four letter boxes, so the white `erase` rectangle removes the letter and
nothing else. Every remaining year should be checked the same way rather than inheriting either
answer.

**Verified in a browser at a 430 px viewport** (stem 390 px), rendering all 32 questions through
the app's own CSS and `formatQuestionText()`:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 32 questions | **430**, never more | nothing clipped |
| Q23's 11-column z-table, wrapped | wrapper 390 px, scrolls to 694 px | decision 9 works |
| Q15's 5-column table, bare `.q-table` | 390 px | fits |
| Q12 (6 col), MC Q2 (6 col), MC Q6 (4 col) | 390 px each | fit |
| Q29's piecewise brace | brace cell **48.3 px**, two-row block **48.3 px** | glyph spans the rows exactly |
| MC Q6 option images in `.options-grid-2x2` | 160 × 131 px each | legible |
| MC Q4's flattened table-row options | 52 px per button | one line each, no wrap |
| All 17 stimulus/option images | load, `naturalWidth` non-zero | none broken |
| 40 distinct non-ASCII characters | 3.4–15.7 px, all distinct from `�` at 17.5 px | real glyphs, no notdef |

Zero console errors. `optionImagesWide` again unnecessary — the option crops are 1.22:1.

**Local CI green:** `validate_subjects.cjs` reports `MC=666 Written=284 imageRefs=222
missingImages=0`, 0 issues. The subject is still **registered nowhere in code** — no
`subjects/index.json` row, no `SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no card; that is Stage 7,
and the two key checkers skip the file until Stage 6. Gate 4 is ticked for 2023 in the runbook,
and the tracker now says **2022 is next**.

---

## 2026-08-28 (later still, ×3) — Mathematics Advanced Stage 4, paper 3 of 6: the 2022 port

**Branch `port/maths-advanced`, not `main`.** The 2022 HSC is ported and cropped:
`subjects/mathematics-advanced.json` now holds **three years — 30 MC + 63 written entries**,
with 2022 contributing 10 MC + 22 written entries and **2 `omittedParts`** (Q12(b) 2 marks, a
blank table plus a graph on a printed grid; Q27(c) 3 marks, a curve sketch). **No new
`omittedQuestions`** — no whole 2022 question is a drawing task, as Stage 1 predicted. Marks
reconcile to **exactly 100**: 10 MC + 85 written + 5 omitted.

**Ground truth first, as §10 requires.** All ten MC answers were confirmed against the official
key *before* authoring, by calling `extract_mc_key()` read-only on `2022_marking_guidelines.pdf`
— `A D B A D B C C A B`. Ten independent derivations from the paper agreed with all ten. The
guidelines were not re-read for anything else.

**The build script refuses to write** unless: the existing file round-trips byte-for-byte
through `json.dumps(indent=2, ensure_ascii=False)` + newline; 2022 is not already present; every
MC answer matches the official key; every bank entry's marks equal the prefix-sum of the
official leaf parts under its `qNum` plus its own `omittedParts` (the join
`check_written_key.cjs` applies); every `category` is one of NESA's own codes for that question;
every `gridCodes` list is exactly NESA's union; every grid part has a bank entry; and every
referenced image file exists.

**Assets: 21 crops**, via a new 2022 registry block in `scripts/crop_maths_advanced.py`
(PDF points, `--year 2022`). Section I: Q3, Q7, Q8 and Q10 stimulus, plus Q1's and Q10's four
option cells each. Section II: Q11, Q14, Q16, Q17, Q24, Q28 (×2), Q29, Q31. Coordinates from an
ink profile at 150 dpi, then every crop built into a contact sheet and compared against the
paper.

### Two things this paper taught, both inherited by the remaining three years

⚠️ **Stage 1's crop list under-counts a second way: one list entry can be two diagrams.**
2022 **Q28** appears once on the Section II list, but the paper draws the circle twice — with
the sector shaded for part (a), then again on the next page with the hyperbola added for part
(c). Both are needed and the stem carries both. A **naming convention is set here**: a second
diagram inside one question takes the part letter as a suffix on the question number,
`mathematics-advanced_2022_Q28b_stimulus.jpg` beside `…_Q28_stimulus.jpg`. 2025's list has
`Q25(c)` and `Q28(b)` entries and will need it. The subject crop total moves 122 → **123**.
(2023 corrected the same list the other way, by finding a question missing from it entirely.)

⚠️ **Decision 1's piecewise brace is sized for two rows.** 2022 Q30's cumulative distribution
function has three. At the template's `font-size:2.6em` the glyph no longer spans the block;
`rowspan="3"` with **`3.9em`** matches it exactly — brace cell 72.5 px against a 72.5 px
three-row block, measured at 430 px. Scale the em value with the row count and re-measure.
Recorded in Stage 3 decision 1 as well as the session note.

### The option-letter trap: checked, did not recur, but nearly mattered

On 2022's option pages the `erase`-rectangle method held — `get_drawings()` reports **zero**
vector paths intersecting any of the eight letter boxes. Two wrinkles worth recording:

- **Page 2's text layer is garbled where the letters are.** Q1's `A.` glyph extracts as the
  word `Mul` and `B.` as a 154 pt-wide span. `C.` and `D.` extract cleanly, and the two option
  rows are a fixed 156.7 pt apart, which places `A.`/`B.` exactly on the garbled span's box.
  Geometry, not the text layer, gave the erase boxes.
- **An x-cut would still have been wrong on Q10.** Option A's lower-left branch starts at
  x = 103.6 pt, *left* of the letter's right edge at 114.9 pt — they miss only in *y*. Cropping
  to the right of the letter would have amputated the branch, exactly as it did on 2020 Q5.
  Crop the whole cell and erase.

### Category picks

Three multi-code merges settled by the rules already in the runbook, NESA's full list kept in
`gridCodes`: Q18 (`C2` of `C2`/`C4`, 2 marks against 1), Q27 (`C3` of `C2`/`C3` — `C3` carries
5 of the 7 marks, counting the omitted part) and Q31 (`C3` of `C3`/`F1`, 4 against 2). Q28
(`C4` of `C4`/`F1`/`T1`) and Q29 (`C4` of `C4`/`M1`) went the same way on mark weight. **Q20 is
the year's even split** — `E1` 2 marks, `C3` 2 marks — so 2023's tie-break applies: take the
part carrying the heavier mathematical demand, here differentiating the exponential model in
(c), giving `C3`.

### Browser verification at 430 px

All 32 questions were rendered through `index.html`'s own CSS in a throwaway harness (fetched
the app's `<style>` blocks at runtime and reproduced `renderQuestion()`'s markup), deleted
afterwards. Screenshots were unavailable in this session (the Browser pane was not displayed),
so everything below is a DOM measurement rather than an eyeball.

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 32 questions | **430**, never more; no `.question-area` overflows | nothing clipped |
| Q21's **7-column** future-value table in the `overflow-x:auto` wrapper | wrapper 390 px, scrolls to 560 px internally | decision 9 works |
| Q11's 4-column complaints table, bare `.q-table` | 390 px | fits — no wrapper |
| Q30's three-row piecewise brace | brace cell 72.5 px, block 72.5 px, table 171 px | spans exactly |
| MC Q1 option images in `.options-grid-2x2` | 160 × 163 px (0.98:1) | legible |
| MC Q10 option images in `.options-grid-2x2` | 160 × 174 px (0.92:1) | legible |
| All 21 images | load, `naturalWidth` non-zero, stimulus 388–390 px | none broken |
| 31 distinct non-ASCII characters | 3.4–18.0 px; `→` and `…` also rasterised — 74 and 30 ink pixels against notdef's 380 | real glyphs |
| `<sup>` exponents (Q27, Q29, Q32, MC Q6) | 15 px against an 18 px base, `vertical-align: super` | real superscripts |

Zero console errors. `optionImagesWide` unnecessary again.

Note on **Q21**: it *is* on Stage 1's list of six "wide lookup tables" and it *is* 7 columns, so
the wrapper was needed. That does not rehabilitate the list — 2023's listed table fitted while an
unlisted one overflowed. The rule stays: **count the columns of every table you build**.

**Local CI green:** `validate_subjects.cjs` reports `MC=676 Written=306 imageRefs=243
missingImages=0`, 0 issues; `check_answer_key.cjs` and `check_written_key.cjs` still pass on the
three ground-truthed subjects and correctly skip Mathematics Advanced until Stage 6. The subject
is still **registered nowhere in code** — no `subjects/index.json` row, no `SUBJECT_ID_MAP`, no
`SUBJECT_CATALOGUE`, no card; that is Stage 7. Gate 4 is ticked for 2022 in the runbook, and the
tracker now says **2025 is next**.

---

## 2026-08-28 (later still, ×4) — Mathematics Advanced Stage 4, paper 4 of 6: the 2025 port, and a ground-truth extractor fixed

**Branch: `port/maths-advanced`, not `main`.** Runbook:
`docs/subject-plans/mathematics-advanced.md`.

### What was ported

`subjects/mathematics-advanced.json` now carries **four years — 40 MC + 84 written entries + 2
`omittedQuestions` + 8 `omittedParts`**. 2025 adds 10 MC + 21 written and **two `omittedParts`
worth 3 marks** (Q15(b) sketch 2, Q16(b) complete-the-graph 1); no whole 2025 question is a
drawing task, so there are no new `omittedQuestions` — exactly as the Stage 1 survey predicted.

Marks reconcile to **exactly 100**: 10 MC + 87 written + 3 omitted. A build script refuses to
write unless six things hold — the `check_written_key.cjs` prefix-sum join per question, the paper
total, every `category` being one of NESA's own codes for that question, every `gridCodes` list
matching NESA's union, every grid part having a bank entry, and every referenced image file
existing — and unless the existing file round-trips byte-for-byte first.

All ten MC answers were confirmed against the official key **before** authoring, by calling
`extract_mc_key()` read-only on `2025_marking_guidelines.pdf` — `B A D C B C A D B C`. Ten
independent derivations from the paper agreed with all ten. That is not a substitute for Stage 6;
it just means the port did not start from guesses. §10 forbids re-reading a marking guideline to
"audit the answers", and this session did not.

### The mapping grid was wrong, and the extractor was fixed rather than worked around

Porting Q18 — a plain composite-functions question — turned up `codes: ["MA-F1","MA-M1"]` in
`data/mapping-grid/mathematics-advanced.json`. Modelling Financial Situations on a function
question is not plausible, so NESA's printed Mapping Grid page was rendered and read: it says
`MA-F1` alone.

The cause is in `scripts/build_mapping_grid.py`. Its Pass 2 gave each row *"the lines from just
after the PREVIOUS label to just before the NEXT one, because vertically-centred cell text can
start above its own label line"* — a comment that names the very failure it produces. A Content
cell holding two or three codes is centred vertically, so its **first** line sits above its own
label line and its **last** line below, and the codes leak into the neighbouring rows in *both*
directions. 2025 Q17(c) (`E1`/`M1`) pushed `E1` up into Q17(b) and `M1` down into Q18; Q27(c)
(`C3`/`C4`/`E1`) pushed `C3` up into Q27(b) and `E1` down into Q28(a).

**20 rows across the two maths subjects carried a code NESA never assigned** — 14 in Mathematics
Advanced (2020 Q2, Q13, Q26(c); 2023 Q27(b); 2024 Q21, Q22(b), Q29, Q31(a); 2025 Q17(b), Q18,
Q21(a), Q27(b), Q28(a), Q29(a)) and 6 in Mathematics Standard 2 (2021 39(b), 2021 41, 2023 32(b), 2023 34(a), 2024 28, 2024 30). **Marks were never
affected**, which is precisely why nothing caught it: every paper still reconciled to its
front-page total with zero uncoded rows, and the build script's own gate passed.

**The fix reads the grid's own drawn horizontal rules.** The Mapping Grid is a real ruled table,
so its row boundaries are printed on the page; new `row_rules()` collects the y positions of every
horizontal rule spanning the Content column, `band_of()` bisects a y into its band, and each text
line is assigned to the band it falls in. The old label-bracketing path survives only as a
fallback for a page carrying no usable rules. All twelve papers across both subjects still
reconcile to 100 marks with zero uncoded rows.

Consequences, all handled in this session:

- Both mapping grids regenerated; `data/exam-trends/` rebuilt on top of them (small shifts —
  Advanced `E1` moves 3.6% → 3.0% of examined marks, `C2` 4.7% → 4.4%; no ranking changes).
- The Standard 2 corrections are **all in Section II**, so CLAUDE.md §10's statement that all 90
  original Standard 2 MC questions agree with NESA's tagging is untouched.
- Four already-ported Mathematics Advanced questions carried a `gridCodes` list that became
  spurious once corrected (2020 MC Q2, 2020 Q13, 2020 Q26, 2023 Q27). The key is now absent on
  all four. **No `category` changed anywhere in any subject, and no answer or mark moved.**
- The runbook's Stage 3 decision 7 table drops from **21 multi-code parts to 7 of 294**, and 2020,
  2021 and 2022 turn out to have none at all.

### Assets — 23 crops

`scripts/crop_maths_advanced.py --year 2025`, a new registry block. Section I: Q6, Q9, Q10
stimulus plus Q2's, Q4's and Q6's four option cells each. Section II: Q11, Q14, Q24, Q25, Q27,
Q28 (×2), Q29. Boxes came from an ink profile at 150 dpi; every crop was then built into a contact
sheet and compared against the paper, option by option.

⚠️ **Stage 1's Section II crop list under-counts a third way: 2025 Q29 is missing from it.** The
mountain-peak diagram is not in Stage 1's 2025 row, even though Stage 1's own *method* paragraph
names "2025 Q29" among the four Section II diagrams that only the union of its three detectors
found. The table and the prose disagreed and the table was believed. Subject crop total moves
123 → **124**. Conversely, **Q25 needed no part-letter suffix**: its only diagram sits in part (c),
so it is `…_2025_Q25_stimulus.jpg`; the suffix convention set in the 2022 session is for a *second*
diagram inside one question, which for 2025 means only Q28.

⚠️ **A crop can be clipped by trusting the ink profile alone.** Q28(b)'s first cut used the ink
band's left edge, x = 85 pt, and silently removed the graph's y-axis labels 1, 2 and 3 — those
start at x = 78.4 pt, which `get_text("words")` gives exactly and the banded profile had merged
away. Files written, non-empty, plausible, wrong. Found by looking at the contact sheet. Rule
recorded: cross-check any crop edge running close to axis labels against the text layer before
accepting it.

**The 2020 option-letter amputation trap did not recur, and was checked rather than assumed.** On
pages 3, 4 and 5 all twelve `A.`/`B.`/`C.`/`D.` glyphs are real text with exact boxes, and
`get_drawings()` reports **zero** vector paths intersecting any of the twelve — so the white
`erase` rectangle removes the letter and nothing else. On Q2 an x-cut would also have been safe (a
blank column separates the letter at x ≤ 109.4 from the graph at x ≥ 127.7), but on Q4 and Q6 the
graph runs straight through the letter's x-range, so `erase` stays the uniform method.

### Port decisions this paper needed

- **Q25 is the year's even three-way split** (`C2` 2 / `C4` 2 / `M1` 2, one code per part) and the
  hardest call of the four papers so far. The 2023 tie-break — heavier mathematical demand —
  does not settle it, since the sting is in (c)'s arithmetic series. Filed under **`C4`**: (a)
  exists only to supply the primitive that (b) and (c) integrate with, and the series is a step
  inside an area calculation rather than the subject of the question. Same reading that put 2022
  Q28 under `C4`. NESA's full list is kept in `gridCodes`.
- **Q15 is the "leans on an omitted part" case for 2025, and it is kept.** Part (b) asks for P₂
  to be sketched on the printed diagram and is dropped; part (c) says "Hence, find the values of
  t … for which P₁ and P₂ are BOTH decreasing." Unlike 2021 Q27(d) — which points at "the graph
  drawn in part (a)" and nothing else — part (c) names two functions whose **equations are both
  given**, so it is fully answerable analytically. P₂'s definition is repeated inline in (c), and
  the omission note says so explicitly rather than letting the substitution pass as NESA's
  wording. **Q15's diagram was deliberately not cropped**: it exists to be drawn on, and supplying
  a grid carrying only P₁ would invite the student to read P₂ off a curve that is not there.
- Q9 is the MC worth re-reading: the straight-line estimate lands exactly on 6.2, and the answer
  is `[6.0, 6.2)` because `f′` is *falling* across the interval, so the true rise is strictly under
  0.2. The half-open intervals are deliberate on NESA's part.

### Verified in the browser at 430 px

All 31 questions rendered through `index.html`'s own CSS in a throwaway harness (stem 390 px):
`body.scrollWidth` never exceeds **430** and no `.question-area` overflows; Q20's **7-column**
future-value table sits in the `overflow-x:auto` wrapper at 390 px and scrolls to 564 px
internally; MC Q1's 2-column table fits bare; Q21's **three-row** piecewise brace measures
**72.5 px against a 72.5 px three-row block** at `font-size:3.9em`, confirming the 2022 session's
scaling rule exactly; option images render 160×128, 160×154 and 160×166 px in the 2×2 grid, so
`optionImagesWide` is again unnecessary; plain-text option buttons are 52 px single-line; all 23
images load; all **38** distinct non-ASCII characters used render real glyphs (each rasterised and
compared against the notdef glyph's ink count); and `<sup>` exponents render 15 px against an
18 px base. Zero console errors.

As in the 2022 session, **screenshots were unavailable** — the Browser pane was not displayed, so
these are DOM measurements rather than pictures. The harness badges written questions with
`q.category || q.topic`, i.e. the *post-fix* engine; the live engine still reads `q.topic` alone
(Stage 3 decision 10), so these show no topic badge until the Stage 7 one-liner lands. Known
blocking item, not a new finding.

**Local CI green:** `validate_subjects.cjs` reports `MC=686 Written=327 imageRefs=266
missingImages=0`, 0 issues; `check_answer_key.cjs` (225) and `check_written_key.cjs` (203) still
pass on the three ground-truthed subjects and correctly skip Mathematics Advanced until Stage 6.
The subject is still **registered nowhere in code** — no `subjects/index.json` row, no
`SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no card; that is Stage 7. Gate 4 is ticked for 2025 in
the runbook, and the tracker now says **2021 is next**.

---

## 2026-08-29 — Mathematics Advanced Stage 4, paper 5 of 6: the 2021 port, and a silent image-clipping defect found

Fifth of six Stage 4 sessions, on the `port/maths-advanced` branch. **2021 is ported and
cropped**, leaving only 2024. `subjects/mathematics-advanced.json` now holds five years —
**50 MC + 106 written entries + 4 `omittedQuestions` + 4 `omittedParts`** — and **101 crops**
are in `/diagrams/`.

### What 2021 added

10 MC + 22 written entries, **2 `omittedParts`** (Q27(a) 2, Q28(b) 2) and **2 new
`omittedQuestions`** (Q19 3 marks, Q21 2 marks). 2021 is the second paper after 2020 to carry a
whole unportable question, and it carries two — Q19 asks for a sketch of *y* = 2 + 1/(*x* + 4)
without calculus, Q21 for a sketch of *y* = 4*f*(2*x*) from a printed graph. Both are the whole
question, so both are subject-level.

Marks reconcile to **exactly 100**: 10 MC + 81 written + 4 omitted parts + 5 omitted questions.
The build script refuses to write unless the file first round-trips byte-for-byte and then six
content gates hold — the `check_written_key.cjs` prefix-sum join per entry, the paper total,
every `category` being one of NESA's own codes for that question, every `gridCodes` list equalling
NESA's own union, **every one of the 48 official parts being covered by a bank entry or a declared
omission**, and every referenced image file existing on disk. That fifth gate is new this session
and is worth keeping: it is the one that would catch a question quietly dropped rather than
declared.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2021_marking_guidelines.pdf` — `B C D C A D A C B B`. Ten
independent derivations from the paper agreed with all ten. §10 forbids re-reading a marking
guideline to audit answers, and this is not that: the extractor is the committed path, called
read-only, and the derivations came from the paper.

Q7 is the one worth re-reading. It compares *f*″(−2), *f*(0) and *f*′(3) on a printed cubic, and
the answer turns on *f*(0) being **negative** — which the question never states and which is only
visible by rendering the origin at 400 dpi and looking: the curve crosses the *x*-axis just to the
*right* of the *y*-axis. At the paper's printed scale that is a few points of ink.

### The headline finding: nine stem images were being silently cut off

The browser pass at 430px flagged **eight `.question-area` elements whose `scrollWidth` ran to
975–1767px against a `clientWidth` of 430**. The cause: `index.html` has **no `.q-text img` rule
at all**. The only `max-width` on a question image is `.device-phone .q-image-wrap img` (line
306), which governs the separate `image` field — not an `<img>` written inline inside `q`, which
is how every written-question diagram in this project is embedded. An unstyled stem image
therefore renders at its natural crop width, and `body { overflow-x: hidden }` swallows the
overflow instead of scrolling it.

**Nothing reports this.** `body.scrollWidth` still read 430. `validate_subjects.cjs` was green
with `missingImages: 0` — it only existence-checks the path. No console error fired. The
diagrams simply had their right-hand side cut off, with Q17's 1767px scatterplot losing roughly
four-fifths of its width inside a 390px stem.

Every 2020/2022/2023/2025 entry carries
`style="max-width:100%;height:auto;display:block;margin:14px auto"` inline, and Mathematics
Standard 2 has carried the same inline style on all 71 of its stem images since its port — so
this is an established convention that the 2021 authoring simply failed to apply, not a new
engine defect. All nine 2021 tags were patched and the overflow list is now empty.

The check that found it is per-question, not page-level, and is now a Gate 4 item in the runbook
and a Gate 4/5 item in the playbook:

```js
[...document.querySelectorAll('.question-area')]
  .filter(a => a.scrollWidth > a.clientWidth + 1)   // must be empty
```

It is recorded as **Stage 4 decision 6** in `docs/subject-plans/mathematics-advanced.md`,
alongside the five decisions the 2020 session took, so the 2024 session inherits it. A
side-note found while sweeping for other unstyled tags: a naive `<img[^>]*>` regex reports a
false positive on 2020 Q29, whose `alt` text contains `c > 0` — a raw `>` inside an attribute
value is legal HTML and the browser parses it correctly; the regex was the thing that broke.

### `optionImagesWide` is needed after all — Stage 1 and Stage 3 were both wrong

Stage 1 measured all 12 of this subject's option-image sets at 0.8:1 to 2.6:1 and concluded
`optionImagesWide` was "not needed anywhere". Stage 3 hardened that into a field-table row
reading "**Never set.**" 2021 Q4 — four cumulative-download bar charts — crops at **2.94:1**
(1446 × 492px), outside the range Stage 1 quoted, and the browser settles it:

| Layout | Measured at 430px | Verdict |
|---|---|---|
| `.options-grid-2x2` (the default) | **160 × 54px** each | a 20-bar chart with a *y*-axis to 800 and days 1–20 labelled, in 54px |
| `.options-list-wide` (`optionImagesWide: true`) | **360 × 122px** each | legible |

160 × 54px is much closer to the VET 160 × 35px case that created the flag than to the
160 × 143px case that was cited to retire it. **The rule is not an aspect-ratio threshold and
never was — render the option set and read the height off the DOM.** Corrected in the runbook
(Stage 1 paragraph, Stage 3 field table, Stage 5 asset bullet) and in the playbook (the asset
bullet, the Stage 1 classification table, and Gate 4/5). 2024 Q8's histograms, whose ink extent
Stage 1 measured at 3.7:1, are the last set to check.

### Port decisions

**Q27(d) is the "leans on an omitted part" case Stage 1 left open for this session, and it is
kept.** Stage 1 singled it out as *the* exception across all six papers: it says *"Explain your
answer by referring to the graph drawn in part (a)"*, and (a) — sketch *P* for 0 ≤ *t* ≤ 12 — is
omitted. Neither of Stage 1's two suggested outs was taken. **Supplying the graph was rejected**:
NESA does not print it, so it would have to be drawn by us, and a fabricated diagram presented
inside a NESA question is not a crop. **Dropping (d) was rejected too**: the graph is just the
curve *P*(*t*) = 400 sin(π*t*/12), whose equation the stem already gives, so (d) is fully
answerable — the reasoning is that *P* peaks at *t* = 6, which reads straight off the function.
NESA's wording of (d) is kept **verbatim**, including the reference to part (a), and the visibly
separate italic note says what (a) asked for and describes the curve it produces. Contrast 2025
Q15, where the omitted part's *definition* had to be repeated inline because it was not in the
stem; here nothing needs repeating.

**Q33 is the year's even split and the hardest call**: (a) and (b) are `S3`, (c) and (d) are
`S1`, 4 marks each, and the 2023 tie-break on "heavier mathematical demand" does not separate
them cleanly. Filed under **`S3`**, because three of the four parts operate directly on the
continuous probability density function and the pdf is the question's subject — (d) is one
conditional-probability application of the result (c) produces. Same reading that put 2025 Q25
and 2022 Q28 under `C4`. Q27 (`T3` of `C4`/`T3`, 5 of 8 marks counting the omitted part) and
Q28 (`C4` of `C4`/`F2`, 4 of 6) went on mark weight, with NESA's full list kept in `gridCodes`.

### Assets

**22 crops** via a new 2021 block in `scripts/crop_maths_advanced.py`. Section I: Q4, Q6, Q7,
Q8, Q10 stimulus plus Q4's and Q5's four option cells each. Section II: Q12, Q17 (×2), Q18, Q22,
Q24, Q28, Q32, Q33. **Stage 1's counts were exactly right for this paper — 22 crops, 6 tables —
the first year they have been**, after 2023, 2022 and 2025 each came in over.

Q17 is the year's two-diagram question (height-vs-temperature and latitude-vs-temperature
scatterplots), taking the part-letter suffix convention set by 2022 Q28:
`…_2021_Q17b_stimulus.jpg` beside `…_2021_Q17_stimulus.jpg`. Q21 has a printed stimulus but the
whole question is omitted, so it is deliberately not cropped.

**The 2020 option-letter amputation trap did not recur, but was checked.** On both option pages
the letters are *not* real text — page 3's `A.` extracts as the word `Mul`, page 4's as `ap`,
the same garbling 2022 page 2 showed — so the letter boxes came from an **ink profile of the
x-strip they sit in** rather than the text layer, cross-checked against the fixed 128.8pt spacing
between option rows. `get_drawings()` then reported **zero vector paths intersecting any of the
eight letter boxes**, so the white `erase` rectangle removes the letter and nothing else. One
geometric wrinkle worth recording: Q5's two columns are **not symmetric about the page centre** —
the left cell's content runs x 100.6–249.4 and the right cell's x 345.1–493.9, so a mirrored
crop box would have been wrong.

### Browser verification, 430px viewport, all 32 questions

Rendered through `index.html`'s own `<style>` block and its own option/stem markup in a
throwaway harness. Measured, not inferred:

- `body.scrollWidth` **430**, never more.
- `.question-area` scrollWidth equals clientWidth on all 32 **after** the `max-width` fix; **8
  overflowed to 975–1767px before it**.
- Q22's **7-column** *z*-table and Q34's **8-column** distribution table both wrap correctly —
  wrapper 390px, scrolling to 520px internally.
- Q25's **6-column** future-value table renders **399.1px** bare, spanning x 20 → 419.1 in a
  430px viewport: it spills 9px into the question-area's 20px right padding but **nothing is
  clipped**. Decision 9's "7 or more columns" threshold stands, with that measurement recorded.
- Q30 and Q33's two-row piecewise braces measure **51.0px and 48.4px** against two-row blocks of
  **51.0px and 48.4px** — the glyph spans the rows exactly at `font-size:2.6em`, confirming
  decision 1's two-row template (2022 and 2025 confirmed the three-row `3.9em` variant).
- All 17 images load with non-zero `naturalWidth`; the 9 stem images render at 390px.
- All 32 plain-text option buttons are 52px, single line.
- **27 distinct non-ASCII characters** used (`° ² ³ × θ μ π σ ′ ″ ⁰ ⁴ ∑ − √ ∞ ∠ ∫ ≈ ≤ ≥` and
  punctuation): each rasterised in the app's own font and compared against the notdef box's ink
  count of 50px² — **none matches**, and only `&nbsp;` is blank.
- `<sup>` exponents render 15px against an 18px base with `vertical-align: super`.
- Q17 renders both its diagrams; Q27 and Q28 show NESA's remaining part letters with the omitted
  one absent and the italic note present.
- Zero console errors.

As in the 2022 and 2025 sessions, **screenshots were unavailable** — the Browser pane was not
displayed, so the page does not composite frames — so these are DOM measurements rather than
pictures. The harness badges written questions with `q.category || q.topic`, i.e. the *post-fix*
engine; the live engine still reads `q.topic` alone (Stage 3 decision 10), so these show no topic
badge until the Stage 7 one-liner lands.

### Verification

Local CI green: `validate_subjects.cjs` reports `MC=696 Written=349 imageRefs=288
missingImages=0`, 0 issues; `check_answer_key.cjs` (225) and `check_written_key.cjs` (203) still
pass on the three ground-truthed subjects and correctly skip Mathematics Advanced until Stage 6.
No other subject's content was touched.

The subject is still **registered nowhere in code** — no `subjects/index.json` row, no
`SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no card; that is Stage 7. Gate 4 is ticked for 2021 in
the runbook, and the tracker now says **2024 is next, and last**.

---

## 2026-08-31 — Mathematics Advanced Stage 4, paper 6 of 6: the 2024 port. **Stage 4 complete.**

**What changed.** The 2024 HSC Mathematics Advanced paper is ported and cropped, on the
`port/maths-advanced` branch. `subjects/mathematics-advanced.json` now holds **all six years —
60 MC + 126 written entries + 5 `omittedQuestions` + 12 `omittedParts`** — and **124 crops** are
in `/diagrams/`. Stage 1 predicted exactly 12 and 5, and the port landed on both. Local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`.

2024 adds 10 MC + 20 written entries, **two `omittedParts`** (Q17(a), sketch a graph, 2 marks;
Q25(b), find a cumulative distribution function and sketch it, 2 marks) and **one new
`omittedQuestion`** (Q19, 5 marks — sketch a quartic from its
stationary points and inflections). Marks reconcile to **exactly 100**: 10 MC + 81 written +
4 omitted parts + 5 omitted question, joined against `data/mapping-grid/` with the same
prefix-sum rule `check_written_key.cjs` applies. The build script refused to write until six
content gates held — the prefix-sum join, the paper total, every `category` being one of NESA's
own codes for that question, every `gridCodes` union (**and no spurious `gridCodes` on a
single-code question**), every official grid part being covered by a bank entry or a declared
omission, and every referenced image file existing — and until the existing file round-tripped
byte-for-byte first.

**Ground truth was consulted, not re-derived.** All ten MC answers were confirmed against the
official key *before* authoring, by calling `extract_mc_key()` read-only on
`2024_marking_guidelines.pdf` — `C B A C A D C D B B`. Ten independent derivations from the paper
agreed with all ten. Separately, the twenty written model answers were cross-checked against
NESA's own sample answers via `build_written_key.py`'s `parse_paper()` in dry-run (37 leaf parts,
reconciling to 90/90); every derivation agreed. Neither is the thing §10 forbids — that rule bans
*re-reading a marking guideline to audit answers by eye*, and both of these are the committed
extractors run read-only.

**Q8 was the question worth slowing down on.** Its box plot carries **no printed scale**, so the
quartiles have to be read off the seven histogram columns rather than off an axis. Measured from
the drawn rectangles: whiskers at columns 1 and 7, box from 2 to 6, median line on 4. Option D is
the only histogram whose running totals (1, 3, 7, 9, 13, 15, 16) put the 4th and 5th values in
column 3, giving a lower quartile of 3 instead of 2 — so D is the one that is *not* possible.

### The last open `optionImagesWide` question is closed — and Stage 1's flag was wrong

Stage 1 named **2024 Q8**'s four histograms as the subject's remaining `optionImagesWide`
candidate, having measured their ink extent at **3.7:1**. That measurement did not survive
cropping: it had banded the C/D *row* of the page, not a single option cell. Each Q8 crop is
**1.75:1** (184 × 105 pt) and renders **160 × 96 px** in `.options-grid-2x2` at a 430 px
viewport — squarely in 2020's 160 × 90 px territory, nowhere near 2021 Q4's 160 × 54 px. Q7's
four graphs render 160 × 161 px.

Both sets were re-rendered offline at exactly those measured boxes and read: every bar height,
the 0–4 axis and the −1/1/2/3 tick labels are legible. So the flag is not set here, and with all
twelve option sets across the six papers now measured, **2021 Q4 is the subject's only
`optionImagesWide`**. Corrected in the runbook in three places.

### Everything else that could have gone wrong, didn't — but was checked

- **The 2020 option-letter amputation trap did not recur.** All eight letters (Q7 A–D page 5,
  Q8 A–D page 6) are real text, `get_text("words")` returns their exact boxes, and
  `get_drawings()` reports **zero** vector paths intersecting any of the eight — so each white
  `erase` rectangle removes the letter and nothing else. Confirmed on contact sheets: every axis
  and curve intact.
- **Stage 1's asset counts were exactly right for this paper** — 23 crops and 7 tables (Section I
  Q3 plus six in Section II). That is the second year running after 2021, and the only two of the
  six. Unlike 2023, 2025 and 2022, no question turned up an unlisted diagram or a second diagram
  of its own.
- **The 2021 stem-image clipping defect did not recur**: all ten inline `<img>` tags carry
  `max-width:100%`, and no `.question-area` overflows its own client width.

### Port decisions this paper needed

**Stage 3 decision 4 (blank tables) is used for the first and only time.** 2024 Q11 and Q13 are
the subject's only two blank-table questions — 2022 Q12(b), the third on Stage 1's list, is
omitted anyway. Both are reproduced as `.q-table` HTML with `<td>&nbsp;</td>` in the blanks
(measured: every empty cell renders 34 px tall, so it reads as a table to fill in) and the model
answer lists the cell values labelled by their column. Q13's table is *partially* completed in
the paper — NESA prints *A* = 34 and the 61 — and those printed values are kept in place.

**Three multi-code calls, two of them even splits.** Q22 (`C3` of `C2`/`C3`/`C4`) splits 3 marks
of concavity against 3 of trapezoidal rule and is filed under **`C3`**, because part (c) is
answered *from* part (a)'s concavity result — the mirror of the 2025 Q25 reading, where (a)
existed only to serve (b) and (c). Q31 (`C3` of `C3`/`T1`) splits 3–3 between sector geometry and
minimisation and is filed under **`C3`** on the 2023 tie-break of heavier mathematical demand.
**Q30 was the hardest call in the paper**: a single 3-mark part carrying `F2`/`M1`, where most of
the working is a reciprocal-graph transformation but the question's subject is the limiting sum
of a geometric series. Filed under **`M1`**, because the stem offers the graph as *"or
otherwise"* — an optional scaffold — while the mark-bearing insight is that a limiting sum exists
only for −1 < *x* < 1. That is the 2021 Q33 reading (file under the question's subject) applied
to a single part rather than to a merge. Four merged entries also span codes: Q14 (`C4` of
`C4`/`F1`), Q17 (`C3` of `C3`/`F2`), Q18 (`E1` of `E1`/`S1`) and Q27 (`C4` of `C2`/`C4`).

**Both omissions sit inside a question the bank still carries, so both force the merged form.**
Q17 keeps NESA's part letters (b) and (c) with a visibly separate italic note saying (a) asked
for a sketch of *V*(*t*); (b) and (c) work from the equation alone, so nothing needed repeating.
Q25 keeps (a) and (c) with a note about the omitted (b); (c) asks for the median of *f*(*x*)
itself and needs only *h* from (a). Contrast 2025 Q15, where the omitted part's definition had to
be repeated inline.

### Verified in the browser at 430 px

All 30 questions rendered through `index.html`'s own CSS in a throwaway harness (stem 390 px):
`body.scrollWidth` never exceeds **430**; **no `.question-area` overflows its own client width**;
Q23's **10-column** *z*-table works inside the `overflow-x:auto` wrapper (wrapper 390 px,
scrolling to 630 px); the six narrower tables (3–6 columns) all fit bare at 390 px; Q25's
**three-row** piecewise brace measures **72.5 px against a 72.5 px block** at `font-size:3.9em`,
confirming 2022's scaling rule a second time; all 23 images load with stem images 390 px wide;
all 32 plain-text option buttons are 52 px single-line; all 31 distinct non-ASCII characters
rasterise to something other than the notdef glyph; `<sup>` exponents render 15 px against an
18 px base; and both omission notes render with the dropped part letter appearing only inside
the note. Zero console errors.

As in the 2021, 2022 and 2025 sessions, **screenshots were unavailable** — the Browser pane was
not displayed — so these are DOM measurements. Option-image legibility was therefore judged by
re-rendering each crop offline at its measured display box and reading it, which is the honest
substitute for looking at a screenshot, not a claim to have seen one.

Both existing key checkers still pass untouched: 225 MC and 203 written questions across the
other three subjects.

### Where the port stands

**Stage 4 is complete** — all six papers ported and cropped, every one reconciling to exactly
100 marks. The subject is still **registered nowhere in code**: no `subjects/index.json` row, no
`SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE` entry, no card. That is Stage 7, and it is still blocked
on the two one-line `index.html` fixes recorded at Stage 3 — the subject-aware `NESA_CAT_LABELS`
(5 of Advanced's 14 codes collide with Standard 2's) and the written-question badge reading
`q.category || q.topic`. **Stage 6 (ground truth — commit and CI-enforce this subject's answer
and written keys) is next.** Work stays on the `port/maths-advanced` branch until the subject is
complete.

**Files touched:** `subjects/mathematics-advanced.json`, `scripts/crop_maths_advanced.py` (new
2024 registry block), 23 new files in `diagrams/`, `docs/subject-plans/mathematics-advanced.md`,
`docs/HISTORY.md`, `CLAUDE.md`. No credential, schema, pricing or engine fact changed; no other
subject's questions, answers or marks were altered.

---

## 2026-08-31 (later) — Mathematics Advanced Stage 6: ground truth built, committed and CI-enforced

**Stage 6 of the Mathematics Advanced port. The bank was right on its first check — nothing
needed correcting.** That is the outcome Stage 0's read-only dry runs predicted back on
2026-08-27, and it is the first stage of this port to find no defect in anything.

### What was built

| File | Contents |
|---|---|
| `data/answer-key/mathematics-advanced.json` | 6 papers, **60 MC answers**, 0 extraction problems |
| `data/answer-key/written/mathematics-advanced.json` | 6 papers, **234 parts, exactly 90 marks each**, 0 unresolved |

Results, first run, no iteration:

```
OK  mathematics-advanced:  60 answers   checked, 0 wrong, 0 unverifiable
OK  mathematics-advanced: 126 questions checked, 0 wrong, 0 unverifiable, 5 declared omissions
```

Subject-wide totals move to **285 MC answers** and **329 written questions** enforced in CI.

**No workflow edit was needed.** `validate.yml` already runs both checkers, and both enumerate
their key directory rather than naming subjects — so committing the two files is what wires
them in. The 60 MC answers match, letter for letter, the six strings recorded in `CLAUDE.md`
during the Stage 4 sessions, each of which was taken from `extract_mc_key()` read-only *before*
authoring that year's questions. This is the first time those six independent reads have been
compared against each other, and they agree.

### Tooling changes

1. `build_answer_key.py` — registered the subject (`Maths Advanced`, `mc_count: 10`).
2. `build_written_key.py` — registered the subject.
3. **The `-mg.pdf$` glob is fixed**, exactly as the runbook predicted at Stage 0. It selected
   guidelines with `re.search(r"-mg\.pdf$", …)`, which never matches Maths Advanced's
   `{year}_marking_guidelines.pdf` and exited *"no marking-guideline PDFs"*. It is now
   `is_guidelines()`, mirroring `build_answer_key.find_papers()`: `feedback` is tested
   **first** and excluded, then `-mg\b|marking` matches. That ordering is load-bearing —
   Multimedia's third PDF per year is named `{year} … HSC Marking Feedback.pdf`, which
   contains *both* words, and reversing the tests would parse marking-centre notes as
   guidelines. **Verified inert**: all three existing subjects regenerate byte-identical
   written keys.
4. Regenerating the other three **MC** keys changed only their `generatedAt` timestamp — the
   answers are byte-identical — so those three files were reverted. The committed data diff is
   the two new files alone.

### A hole in the written checker, now reported

`check_written_key.cjs` compares each bank entry against the key. It therefore sees a mark that
is *wrong*, but has never been able to see a question that is simply **absent** — which is the
exact failure that left 2020 Mathematics Standard 2 at 84/85 for over a year (`CLAUDE.md` §10
rule 5). It now also computes the reverse direction: how many official leaf parts are claimed by
a bank entry or a declared omission.

| Subject | Coverage |
|---|---|
| **mathematics-advanced** | **234 / 234** |
| mathematics-standard-2 | 235 / 235 |
| multimedia | 30 / 42 — Section III (Q16, 15 marks/paper) never ported |
| vet-construction | 23 / 76 — written bank covers 23 of 65 marks/paper |

It is **reported, not enforced**. Those last two gaps are deliberate, documented decisions
(Multimedia's Section III is a scheduled upgrade phase; VET's written port is partial), and
making this blocking would turn CI red on work already scoped out rather than on a regression.
The line is there so the gap is *visible in the check* instead of only in prose. If either gap
is closed, promote it to a hard assertion.

### Reconciliation — all six papers, both directions

| Year | MC | written | omittedParts | omittedQuestions | total |
|---|---|---|---|---|---|
| 2020 | 10 | 82 | 1 | 7 | **100** |
| 2021 | 10 | 81 | 4 | 5 | **100** |
| 2022 | 10 | 85 | 5 | 0 | **100** |
| 2023 | 10 | 83 | 7 | 0 | **100** |
| 2024 | 10 | 81 | 4 | 5 | **100** |
| 2025 | 10 | 87 | 3 | 0 | **100** |

Every official leaf part is claimed **exactly once** — 0 unclaimed, 0 double-claimed.

### The residual human gate, and why eyeballing was not the method

Gate 6's one item CI cannot cover: a passing check compares only the official *letter*, so it is
blind to reordered options, wrong option text, and a description standing in for a missing
picture (`CLAUDE.md` §10 rules 6 and 7). Reading 124 crops by eye is not a method, so three
checks were used, each covering what the others miss:

1. **Twelve option-set contact sheets, read one at a time.** Each sheet puts the NESA page's own
   option area above the four committed crops **in bank array order**, with the keyed option
   marked. All twelve match the paper's A/B/C/D ordering — no reordering, no wrong-picture
   pairing, and every crop's baked-in option letter cleanly erased. The two closest calls are
   **2024 Q7**, where options C and D differ only by a horizontal shift, and **2024 Q8**, four
   similar histograms; both are correct. 2021 Q4's sheet also shows visually why it is the
   subject's only `optionImagesWide`, and 2024 Q8's shows why it is not one.
2. **All 124 crops re-rendered from the PDF at their registry rectangle and pixel-compared to
   the committed file — 0 mismatches.** Every file on disk is a faithful cut of the paper at the
   place it claims to come from. This is the check that would have caught the 2020 option-letter
   amputation while it was happening.
3. **All 124 position-checked against the paper's own question labels — 0 mismatches.** No crop
   is attached to the wrong question.

⚠️ **Two traps in writing check 3**, both hit before it was right. A bare number in the left
margin is only a question label on a **Section I** page: on Section II pages body text starts at
x = 70.7, so `x = 4` in 2021 Q24's stem posed as "Q4" and flagged that crop spuriously. But
tightening the x threshold to exclude it breaks Section I entirely — its question numbers sit in
the *same* x band, and every one of the 73 Section I crops then reported "no label above". The
separator is not a coordinate, it is the **`Question N` header**: use headers on pages that have
them, bare margin numbers on pages that do not.

Crop reconciliation: **124 referenced, 124 on disk, 0 orphans, 0 missing.** One process note —
a first pass reported `mathematics-advanced_2023_Q2_stimulus.jpg` as an orphan, because it
scanned `image`/`optionImages` plus *written* stems. **MC stems carry inline `<img>` too**
(2023 Q2 embeds its die-and-spinner picture that way, between two sentences), so a reference
scan must read the `q` field of both question arrays.

### Verification

Full local CI green: `validate_subjects.cjs` `MC=706 Written=369 imageRefs=311 missingImages=0`,
`Issues: 0`; both key checkers pass; all Cloudflare functions syntax-check; `npm test` 67 pass,
0 fail. The other subjects' answers and marks were not touched and still pass.

No credential, schema, pricing or engine fact changed. No question content was altered — this
stage only reads the bank. The subject is still **registered nowhere in code**; that is Stage 7,
still blocked on the two one-line `index.html` fixes Stage 3 found. Work stays on the
`port/maths-advanced` branch.

---

## 2026-09-01 — Multimedia Section III planned as its own runbook; an audit gap recorded

Planning and record-keeping only. **No code, data, credential, schema or pricing fact changed,
and no question content was touched.**

### Multimedia Section III — the gap, and the plan

Prompted by the reverse-coverage line added at Mathematics Advanced Stage 6, which reported
Multimedia at **30/42** official written parts claimed. Confirmed from the data: the bank holds
**Q11–Q15 for all six years and no Q16 at all** — Section III, **15 marks per paper, 12 official
parts, 90 marks across 2020–2025**, never ported.

Read from the papers (page 9 in all six years):

| Year | (a) | marks | (b) | marks |
|---|---|---|---|---|
| 2020 | Environmental factors in site selection | 5 | Minimising continuing environmental impact | 10 |
| 2021 | Industrial Relations issues from modified operations | 5 | Career and training opportunities | 10 |
| 2022 | Role of WHS legislation | 5 | Strategies to improve workplace safety | 10 |
| 2023 | How ONE new technology is improving the industry | **3** | Mass production and automation, with examples | **12** |
| 2024 | Marketing across a hierarchical partnership vs a flat sole trader | 5 | Organisational structure vs production/efficiency | 10 |
| 2025 | Legislative requirements and sustainable practices | 5 | Historical developments in manufacturing | 10 |

The shape is stable — (a) *Describe* 5, (b) *Discuss/Explain/Analyse* 10 — with **2023 the only
year that shifts, at 3 + 12**.

**This is a different strand from everything already in the subject.** Environment/
sustainability, industrial relations, WHS, careers, automation, organisational structure,
marketing, historical development — **none of the seven Study Mode topics touches any of it**
(Text & Document Design, Graphics, Animation, Video, Audio, WWW, IP & Ethics are all Section I/II
*production* content). There is no existing bank content to build from, which is exactly what
made Study Mode topics 1–7 comparatively cheap and makes this one not.

**New runbook: `docs/subject-plans/multimedia-section-iii.md`**, scheduled **after Mathematics
Advanced Stage 7** (owner decision). That supersedes the 2026-07-29 "after VET Study Mode"
sequencing, whose precondition was met on 2026-07-30 and then sat unstarted for a month.

**It is not a new subject port, and the runbook says so.** Multimedia is live, so Stage 0
(feasibility), Stage 2 (syllabus grounding, done for the 7 Study Mode topics) and Stage 3
(schema, fixed by the live file) do not re-run in their usual form. **It starts at Stage 1**,
and **Stage 6 is already complete** — `data/answer-key/written/multimedia.json` already holds
all 12 parts' official marks *and* NESA's sample answers, committed at Maths Advanced Stage 6,
so the marks cannot go wrong without CI catching it immediately.

⚠️ **The one genuine feasibility risk is flagged for Stage 1 to resolve or escalate:** whether
`mark-written.js` can mark a **10–12 mark band-marked extended response**. Its longest to date
is 5 marks. If it needs a different prompt, a band rubric or a larger `max_tokens`, that is an
engine change and must be known *before* Stage 4 starts, not discovered mid-port. HMS's
`writingScaffolds` (6–10 and 12 mark bands) are the nearest existing precedent.

Two smaller traps recorded in the runbook: **2024 carries shared stimulus prose** that both
parts depend on, so whatever bank shape Stage 1 picks must keep it attached to both; and
`multimedia.json` must **never** be round-tripped through `json.dumps` (it reformatted into a
461-line diff once by expanding `studyNotes`' compact inline arrays).

### The audit question, answered from the record

Owner asked directly whether the same audit checks against the marking guides had been done for
VET and Multimedia. Checked, changed nothing. The answer splits:

**Yes, for MC answers — and it was done properly.** 2026-08-27 (`docs/HISTORY.md:689`): all 11
answer-key tables read **from rendered page images** rather than trusted from the text layer;
`qNum` backfilled for all 135 questions on **exact option-set equality**, never a similarity
score; **option order verified separately**, because the official letter indexes the paper's
order. It found **6 wrong VET answers in 75 (8%)** — 2021 Q1, 2022 Q13, 2022 Q15, 2023 Q11,
2024 Q11, 2025 Q1 — each re-derived from the source rather than flipped to match the key.
Multimedia came back clean at 60/60. The same pass, plus its follow-up, also caught four
questions whose option *text* described the wrong picture (VET 2021 Q15, VET 2022 Q7/Q13,
Multimedia 2021 Q1, then Multimedia 2022 Q2's stimulus) — answers right, pictures wrong, which
the key check is structurally blind to. All 285 MC answers are now CI-enforced.

**No, for written model answers — and not for any subject.** `check_written_key.cjs` enforces
the **mark only**; the written-key session's own words were that the official sample answer is
committed *"as the source a reviewer needs when a bank answer looks wrong — not as an
assertion."* Prose cannot be compared for equality. So the **52 authored model answers** across
`multimedia.json` (29) and `vet-construction.json` (23) have never been read back against
NESA's sample answers by any session. The only time that comparison has ever been run in this
project was inside the Maths Advanced 2024 port session, on questions being authored right then
— never retrospectively.

Why it is worth a decision rather than a shrug: **every one of the six defective VET questions
also carried an `optionExplanations` entry arguing for the wrong answer.** Same authoring, same
subjects, same period — and the written prose from that period has never been read back. Ground
truth already sits in `data/answer-key/written/` from Stage 6, so the work is reading, not
extraction.

Recorded as a §11 roadmap row. **No decision taken, nothing changed.**

---

## 2026-09-01 (later) — Written-answer review designed as a standing mechanism

Design and planning only. **No code, data, credential, schema or pricing fact changed.**

Follows the audit gap recorded earlier today. Owner's direction: add the written model answer
to the plan, and **design it so it generalises to future subject additions** — so the output is
a playbook mechanism, not a Multimedia to-do.

### The finding that reframed the design

Read `mark-written.js` and the client call site rather than assuming. **The AI marker is never
sent the model answer.** It receives `question`, `maxMarks`, `keywords`, `studentAnswer`,
`bandDescriptors` (`functions/mark-written.js:38`, `index.html:2057`). Meanwhile `index.html`
renders `q.answer || q.modelAnswer || q.sampleAnswer` **directly to the student** after they
answer (lines 1823 and 2227).

So the intuition that the AI is where the risk sits is backwards. **A wrong model answer is a
pure teaching defect** — no AI involved, no error thrown, nothing reporting it. It is the most
invisible failure in the pipeline, and it is the one CI can never assert on.

That splits one vague "model answer review" into three artefacts with different consumers:

| Field | Consumer | Failure mode |
|---|---|---|
| `modelAnswer` | **Shown directly to the student** | Teaches the wrong thing, silently |
| `keywords` | `mark-written.js` **and** the offline keyword-grid fallback | Mis-marked in both paths |
| `bandDescriptors` | `mark-written.js` band rubric | Marked against the wrong standard; absent, falls back to a generic 0/50%/100% scale |

### Measured coverage — all 369 written questions in the repo

| Subject | Written | `modelAnswer` | `keywords` | `bandDescriptors` |
|---|---|---|---|---|
| health-movement-science | 40 | 40 | 40 | 40 |
| mathematics-advanced | 126 | 126 | 126 | 126 |
| mathematics-standard-2 | 151 | 151 | **111** | 151 |
| multimedia | 29 | 29 | **25** | **25** |
| vet-construction | 23 | 23 | **20** | **0** |
| **Total** | **369** | 369 | **322** | **342** |

**0 of 369 have ever been reviewed against NESA's sample answers.**

⚠️ **VET has 0 of 23 `bandDescriptors`** — every VET written question is AI-marked on the
generic fallback rubric. That is the worst cell in the table, and it is *missing data*, not an
unreviewed one. VET is also the subject where the 2026-08-27 pass found 6 wrong MC answers in
75, **each carrying an `optionExplanations` entry arguing for the wrong answer** — same
authoring, same period, and its written prose has never been read back. **If the backlog is
ever prioritised rather than done in full, VET goes first.**

### The design — make the review the artifact

The project's own rule is that *an audit is a claim about one moment; a test is a standing
guarantee*. Prose cannot be asserted on — but **whether a human compared it, and whether that
comparison is still current, can be.** So the review itself becomes committed and checkable.

**A ledger at `data/answer-key/written/reviews/{subject-id}.json`**, holding per part a
`reviewedAt`, a verdict (`ok` / `corrected` / `divergent-accepted`), which fields were covered,
and a **fingerprint of NESA's sample answer as it read at review time**.

Three decisions worth recording:

- **Sidecar, not a field on the question.** `subjects/*.json` is downloaded by every student, so
  review metadata there is dead weight on the wire; `validate_subjects.cjs` globs that folder
  and would have to learn to ignore it; and the ledger belongs beside the ground truth it cites,
  exactly as the keys do.
- **The fingerprint is the whole point.** Regenerate the key and any part whose official text
  changed has its fingerprint diverge, so the review is **automatically void** rather than
  quietly stale. That is the standing guarantee prose otherwise cannot have.
- **Report before enforcing**, the same ramp used for reverse coverage on 2026-08-31: print
  per-subject review coverage and stale reviews, exit 0; promote to a hard failure per subject
  once that subject reaches 100%. A new port lands reviewed and stays reviewed, without turning
  CI red on subjects carrying historical debt.

⚠️ **Mechanical triage orders the reading queue and never decides anything.** This project has
been burned repeatedly by similarity scoring — `backfill_qnum.py` exists because of it, and §10
rule 3 is explicit that fuzzy text-matching is not a join. Keyword-absent-from-model-answer,
keyword-absent-from-sample-answer, low substantive-term overlap and length-vs-marks are *read
this one first* signals. They are never verdicts and never a substitute for reading.

**Legitimate divergence is recorded, not hidden.** Maths sample answers extract as mangled
equation layout (`x2 102 82 = + 2 = 164`), so a Maths model answer *should* read nothing like
NESA's — that is `divergent-accepted` with a note, neither a silent pass nor a failure.

⚠️ **`bandDescriptors` have no ground truth.** `build_written_key.py` extracts the mark and the
sample answer but **not the criteria table** the marks are banded against, so band descriptors
can only be reviewed for plausibility. Extending the extractor to capture the criteria rows is a
scoped prerequisite — worth doing once, not per subject.

### Where it landed

- **`docs/porting-playbook.md` §6** — the full design, as "the second residual gate", symmetric
  with the existing image/option gate. Added to **Gate 6** and to **§11 Definition of Done**, so
  it applies to every future port rather than to Multimedia alone.
- **`docs/subject-plans/multimedia-section-iii.md`** — a new **Stage 6b**, covering Section III's
  12 new parts **and** Multimedia's existing 29 in one session. Doing them together is
  deliberate: the reviewer is already holding the sample answers and the subject's conventions,
  and it takes one subject to 100% as the reference the others are measured against. It also
  flags the 4 Multimedia questions with **neither** `keywords` nor `bandDescriptors`, and notes
  that Section III's 10–12 mark band-marked responses are exactly where a generic rubric
  produces a meaningless mark.
- **CLAUDE.md** — §10 rule 8 now states plainly that the mark is the only thing CI sees, and the
  roadmap row is rewritten from "never reviewed" to the designed, scheduled mechanism.

### Two corrections made in passing

- The playbook's `-mg.pdf$` glob warning described a live bug that was **fixed on 2026-08-31**.
  Marked fixed, keeping the rule that outlives it: **test `feedback` FIRST, then `-mg|marking`**,
  because some folders carry a third PDF per year containing both words.
- The Multimedia runbook, written earlier today, said `mark-written.js` marks against
  `keywords` + `modelAnswer`. It does not — `keywords` + `bandDescriptors`. Corrected, and it is
  the finding the whole design turns on.

---

## 2026-09-01 (later still) — VET Construction written-answer review: the first one ever run, and six real defects

Branch `review/vet-written` (cut from `port/maths-advanced`, because `main` does not yet
carry the Mathematics Advanced keys and the inertness check below needed all four written
keys present). **Not merged.** Runbook:
`docs/subject-plans/vet-construction-written-review.md`.

The mechanism designed earlier today (`docs/porting-playbook.md` §6) run for real, on the
subject the Multimedia runbook's backlog table nominated to go first: worst data coverage
in the repo (**0 of 23 `bandDescriptors`**) and the only subject with a demonstrated
authoring-accuracy problem — the 2026-08-27 MC pass found 6 wrong answers in 75, every one
carrying an `optionExplanations` entry arguing for the wrong answer. **That expectation was
right. Six of the 23 written questions carried a real defect, and CI passed on all six
throughout, because the mark was correct in every case.**

### Prerequisite: `bandDescriptors` now have ground truth

`scripts/build_written_key.py` previously extracted a part's mark and NESA's sample answer
but **not the criteria table**, so band descriptors could be reviewed for plausibility and
nothing else. It now also keeps each criteria row's **text** beside the mark it already read
positionally, as `criteria: [{marks, text}]`.

⚠️ **A criteria row's mark is vertically CENTRED in its cell.** 2024 VET Q16(a) is the proof:
its `2` sits beside the bare word `OR`, on the middle of the row's three lines, between the
two clauses it applies to. Bracketing a row by the mark-bearing lines around it leaks wording
in **both** directions — bit-for-bit the bug `build_mapping_grid.py` was fixed for on
2026-08-28, in a different file, three days apart. These tables are genuinely ruled, so
`row_rules()`/`band_of()` were lifted from that script and read the boundaries the page
itself draws. An unruled table degrades to one row per mark-bearing line; it never merges
rows silently.

**Inertness was the condition on the change and it was machine-checked, not asserted.** All
four committed written keys regenerate with **every previously existing field byte-identical**
— verified by stripping `criteria` from the regenerated files and comparing against `HEAD`:
all four inert, **1 446 criteria rows added** (Maths Advanced 540, Standard 2 510, Multimedia
146, VET 250), **0 parts with no criteria**, every paper still reconciling to its front-page
total. The raw diff corroborates: of 591 removed lines, **587 are `sampleAnswer` lines that
gained a trailing comma** and 4 are the `note` blocks. HMS has no key and is untouched.

### The decision: N official bands to the engine's three

`bandDescriptors` is fixed at `{full, partial, minimal}` (both consumers read exactly those
keys), while VET's criteria tables carry 1–5 rows: 3 questions with 1 band, 7 with 2, 7 with
3, 1 with 4, and 5 with 5 — including the 10- and 15-mark extended responses banded
`[10,8,6,4,2]` and `[15,12,9,6,3]`.

**Rule adopted, applied to all 23 without exception: `full` = NESA's top row verbatim,
`minimal` = NESA's bottom row verbatim, `partial` = every row between them, verbatim, joined
with " OR ".**

Rejected: mapping the slots onto the engine's mark arithmetic. `buildKeywordFeedback()` picks
`full` at 70% or more of the maximum, `partial` above zero and `minimal` at exactly zero — **and
NESA prints no row for zero at all**, so honouring that arithmetic would force *authored* prose
into the `minimal` slot on every question. Top/middle/bottom keeps all three slots as NESA's
own sentences, which is the whole point of building the extractor, and it lines up with the
prompt `mark-written.js` already sends (10 / 5–9 / 0–4 against NESA's 10 / 8-6-4 / 2).

Two degenerate shapes: **N = 2** has no middle row, so `partial` repeats the bottom row —
repeating an official sentence is truthful where inventing a third is not. **N = 1** (the
three 1-mark identify questions) has neither, so `partial` and `minimal` state the row's
non-attainment. ⚠️ **That is the only authored, non-NESA descriptor text in the subject**, it
is flagged on all three ledger entries, and it is low-consequence: those three questions score
through `acceptableAnswers`, where the engine reads only `full` and `minimal`.

One presentation liberty: NESA prints some criteria as separate bulleted lines in one cell,
which the extractor faithfully joins into a run-on; nine substitutions across 2025 20(b) and
2025 21 punctuate them ("…industry Provides…" becomes "…industry; provides…"). **No word
added, removed or reordered**, and every substitution printed at build time — `SOURCE_TYPOS`
discipline.

### The six corrections

1. **2023 Q19(b)(i) — the model answer's headline result was simply wrong: 2.61 m³ against
   NESA's 2.99 m³.** It computed the footing volume from the shed's outer perimeter,
   **omitting the centre beam entirely** and double-counting the corners — on a stimulus NESA
   itself captions *"the hidden detail of the edge and centre beams"*, with the centre beam
   drawn on the page. It then explained the gap away as *"corners (overlap) giving
   approximately 2.61–2.99 m³ depending on method"*: a fabricated reconciliation of its own
   error. The bank stem compounded it, saying *"300mm × 300mm **perimeter** beam footings"*.
   Stem restored to the paper's wording, answer rewritten to NESA's method (17 m of long beams
   at 1.53 m³ plus three 5.4 m cross beams at 1.46 m³ = 2.99 m³), with 2.61 kept and *named*
   as the common error. Keywords `29` and `2.61` removed — they credited the wrong method.
2. **2022 Q19(a) — both of the stimulus table's band labels were fabricated.** The answer
   claimed 3700 kg falls in a "3001–4000 kg" range and 54 km in a "51–60 km" range. The table
   (crop opened and read) is in **tonnes** — 0–2.99 / 3.00–4.99 / 5.00–6.99 / 7.00–8.99 — with
   columns 1–30 / 31–50 / **51–70**. Neither quoted band exists on the page, and the kg to
   tonne conversion the question actually tests was absent. `$450` was right, so nothing
   reported it. **The same failure class as Multimedia 2022 Q2 (§10 rule 7), in the model
   answer this time.**
3. **2023 Q16(a)(i) — `acceptableAnswers` omitted one of NESA's own accepted answers.** NESA
   lists *"Sliding saw • Compound saw • Mitre saw • Cut off saw"*; "sliding" was missing, so a
   student writing NESA's first listed alternative was marked **incorrect**.
4. **2022 Q17(c) — the stem gave away one of the two marks**, reading *"…the symbols shown
   (RWT and **tree symbol**)"* where the paper says only *"Identify each of the architectural
   symbols shown."* The answer also attributed removal to *"(the specific marking on the
   plan)"*, which says nothing — the real indicator, visible in the committed crop, is the
   **broken outline** against RWT's continuous one.
5. **2025 Q18(b) — the stem gave away the third of three marks**, naming *"the **horizontal
   sliding window** symbol shown"*. Restored to the paper's wording.
6. **2021 Q16(a) — no keywords at all** (with 2022 19(a) and 2023 16(a)(i)). All three score
   through `acceptableAnswers`, so `validate_subjects.cjs`'s "no scoring mechanism" warning
   never fired — but `mark-written.js` was being sent an **empty concept list**. Filled from
   NESA's own alternatives; the offline path is unchanged because `acceptableAnswers` takes
   priority, verified in the browser rather than assumed.

Two questions are **`divergent-accepted`**: 2024 Q19(a) and Q19(b), whose NESA samples extract
as mangled equation layout (`!3! 4! + = 5 …`, `pr2 12 ´ ´ ´ depth`), compared numerically
instead — 5 and 26 m; 7.2, 0.471 and 6.73 m³ — all agreeing. The standing Maths exception,
appearing in a VET calculation question. Never a silent pass.

### The standing mechanism

- **Ledger** at `data/answer-key/written/reviews/vet-construction.json` — a sidecar, not
  fields on the question, because `subjects/*.json` is downloaded by every student. Built by
  new **`scripts/build_review_ledger.py`** from a hand-typed verdict table at new
  **`scripts/reviews/vet_construction.py`**; the script computes fingerprints and shape and
  **decides nothing**, refusing to write on a missing question, an unknown verdict, or a
  non-`ok` verdict with no note.
- **Fingerprint** — sha256 of NESA's sample answer for that entry, whitespace-normalised, *as
  it read at review time*, so regenerating the key **voids** an affected review rather than
  letting it go quietly stale.
- **Checker ramp** — `check_written_key.cjs` prints review coverage for every subject and
  **enforces it for any subject that has committed a ledger**. Opting in by committing a
  ledger is what makes the ramp work: the four subjects with historical debt report 0% and
  stay green, while VET can no longer regress. **Proved, not assumed** — corrupting one
  fingerprint byte yields `1 STALE`, the right message and **exit 1**; restoring it, exit 0.
- **Triage** — `scripts/review_triage.py <subject-id>` (generalised from the VET-only version;
  smoke-tested on Multimedia) prints each question beside NESA's mark, sample and criteria so
  no marking guideline is ever re-read, and `--triage` orders the queue. ⚠️ **Ordering only.**
  Worth recording how weak the signals proved: the queue's **top** entry was a
  `divergent-accepted`, while **2022 17(c) and 2025 18(b) sat at the very bottom on overlap
  1.00** — a stem that gives the answer away and an answer that misdescribes a picture both
  score as *perfect agreement*. Two of six defects were invisible to every mechanical signal.

### Schema drift — the brief's premise corrected

VET stores its model answer as `answer`, and carries `acceptableAnswers` and `minKeywords`.
All three are **load-bearing** (`acceptableAnswers` is a complete all-or-nothing scoring
branch at `index.html:1994` that **takes priority over `keywords`**; `minKeywords` is the
half-marks threshold at `:2012`) and **none was canonicalised**. But the premise that these
are VET-only fields is **wrong**, and it would have misdirected the next reviewer: measured
across all five subject files, `acceptableAnswers` appears on Maths Advanced (6), Standard 2
(47), Multimedia (4) and VET (3), and `minKeywords` on 126 / 111 / 25 / 23. **No subject
anywhere uses `modelAnswer`** — `answer` is the de facto canonical name. The real outlier is
**HMS**, which uses `topic`/`maxMark` and carries no `year` or `section`. Nothing was changed
on that basis.

### Verified

Full local CI green: `validate_subjects.cjs` (`MC=706 Written=369 imageRefs=311
missingImages=0`, `Issues: 0`), `check_answer_key.cjs` (**285 answers, 0 wrong, 0
unverifiable**), `check_written_key.cjs` (**329 written questions, 0 wrong, 0 unverifiable**;
VET review **23/23**), `node --check` on all five Cloudflare function files, `npm test`
**67 pass / 0 fail**.

Browser at **430 px** against the local preview: all 23 VET written questions rendered one by
one — `body.scrollWidth` never exceeds 430 and **no `.question-area` overflows**; all 13
stimulus images load at 388 px (⚠️ forced to `loading='eager'` and awaited first, or every one
reads `naturalWidth` 0). **2025 Q20(b), 10 marks**: badge renders `10 marks`, a deliberately
partial answer scores **4/10, 36% matched**, and the feedback is now **NESA's own middle band**
in place of the old generic "Good — solid understanding…"; the model answer renders in full.
All five corrected questions re-read on screen with their restored stems live.

⚠️ **The live AI marking call was NOT made.** The client payload was captured from
`tryAiMarking()` with `fetch` stubbed — it now carries the three real descriptors where it
previously sent `bandDescriptors: null` — and that payload was run through
`functions/mark-written.js`'s **own prompt source, sliced from the file rather than retyped**,
confirming the band block is well formed for a 10-mark question with no `undefined` in it. But
no `ANTHROPIC_API_KEY` exists in this environment (only `ANTHROPIC_BASE_URL`), and the function
also needs a verified Supabase JWT and an active subscription row. **Marking behaviour is
verified to the prompt boundary and no further**; whoever next has a key should submit one
10-mark and one 15-mark VET answer against the deployed function.

### Found and deliberately not acted on

- ⚠️ **Ten VET 2025 stems end with a literal `(N marks)`**, duplicating the badge the renderer
  already draws — and **Mathematics Standard 2 has the same on 90 stems**. Fixing VET's ten
  alone would leave the repo *less* consistent, so it is left for one pass across both.
- ⚠️ **`parse_paper()` swallows the Mapping Grid into the last question of every paper**
  (the final `Question N` header has no successor, so its sample block runs to the end of the
  document). **Pre-existing**, harmless to the mark check, noted on the 2025 Q21 ledger entry
  because that fingerprint therefore covers more text than the sample alone. Fixing it would
  change committed `sampleAnswer` bytes in every subject and break this session's inertness
  guarantee.
- Loose keywords (`pi` is two characters, so `keywordHit()` fires on "pipe"). An engine change,
  not a data one.

**No mark, MC answer, `omittedParts` or `omittedQuestions` declaration was altered anywhere.**
No credential, schema, pricing or engine fact changed. Remaining backlog: **346 of 369**
written answers unreviewed — Maths Advanced 126, Standard 2 151, Multimedia 29, HMS 40;
Standard 2 also still missing 40 `keywords`, Multimedia 4.

---

## 2026-09-01 (later still, again) — VET Construction written completion port: 23 of 76 official parts → 76/76

Same branch, `review/vet-written`, still **not merged**. Runbook (now covering both halves):
`docs/subject-plans/vet-construction-written-review.md`.

The review earlier today covered the 23 written questions the bank held — but VET's written
section is **65 marks a paper** and the bank carried barely a third of it. This closes that
gap. **49 questions added plus one declared omission; the bank goes 23 → 72 written
questions and coverage 23/76 → 76/76.** `check_written_key.cjs` prints
`coverage: 76/76` for VET with no "not ported" line for the first time, so that
reverse-coverage check could now be promoted to a hard assertion for this subject.

| Year | Was | Added | Omitted | Now |
|---|---|---|---|---|
| 2021 | 2/15 | 13 | — | 15/15 |
| 2022 | 3/16 | 13 | — | 16/16 |
| 2023 | 3/15 | 12 | — | 15/15 |
| 2024 | 4/15 | 11 | — | 15/15 |
| 2025 | 11/15 | 0 | 4 (Q19) | 15/15 |

### ⚠️ 2025 Q19 cannot be ported — NESA redacted the stimulus from its own paper

Page 16 of `2025-hsc-vet-construction.pdf` carries only *"Due to copyright restrictions,
this material cannot be displayed until permission has been obtained."* All four parts —
slab cost, where surface water exits, fence panels required, paver pallets required — read
dimensions and levels off that site plan. There is nothing to crop and nothing to answer
from. Declared as a subject-level `omittedQuestions` entry (11 marks), validated by the
checker. **The `reason` explicitly distinguishes an ABSENT SOURCE from an engine
limitation** — every other omission in the repo is "the engine cannot present a drawing
task", and this one is categorically different.

⚠️ **The same redaction hits 2025 Q16**, whose tool photo is also absent from the paper —
yet that question, ported long ago, carries `/diagrams/vet-construction_2025_Q16_stimulus.jpg`:
**a substituted third-party line drawing of a plunge router with a visible brand mark**,
migrated from Imgur in `221e377`. It is self-hosted and does depict the right tool (NESA's
own sample answer says "the tool/router pictured"), so the question works — but its
provenance is not NESA and its licence is unknown. **Flagged, deliberately not changed**:
replacing a working image is the owner's call, and it belongs with the unplaced Flaticon
attribution as a licensing question, not a correctness one. Also confirmed while checking
this: **there are no Imgur URLs left anywhere in the repo** — zero external URLs in all
five subject JSON files; the only `imgur` grep hits are the variable names `imgUrl`/`imgUrl2`
in `index.html`.

### An extractor bug, found by the survey and fixed before any content was written

Surveying 2021 Q20 showed **4 criteria bands where the paper prints 5**. The fifth band's
sentence wraps so its last word `a` lands at x 441.9–447.9 — past `MARKS_COL_MIN_X = 440` —
while the real mark `1–3` sits at x 479.1. Joining everything past the boundary gave
`a1-3`, `MARK_VALUE` rejected it, and `criteria_rows()` drops a bandless row, so the band
vanished entirely.

`marks_cell()` now takes the **rightmost cluster** of tokens past the boundary, split on a
15 pt gap — which still joins the case the concatenation exists for, a range split across
two words (`9-1` + `0`). Criteria wording is now defined by **exclusion** of the marks cell
rather than by the x threshold, so a wrapped sentence keeps its last word.

**Blast radius measured across all four committed keys: exactly ONE row recovered, 0 marks
changed, 0 sample answers changed, 0 existing criteria text changed.** The part's own
`marks` was never wrong — it is a `max()` over the bands and the surviving four still gave
15 — which is exactly why nothing caught it. 2021 Q20 was not yet in the bank, so no
committed `bandDescriptors` moved. Committed separately as `743e13b`.

### Assets — only two new crops were needed

New tool **`scripts/crop_vet_construction.py`**, the same mechanism as
`crop_maths_advanced.py`: PDF **points** not pixels, one registry per year, and deliberately
**not** an entry in `scripts/diagram_registry.json`, whose pixels-at-150-dpi coordinates and
unconditional overwrite would re-cut all 36 existing VET images. The registry holds only the
two new crops.

- **2021 Q18** — 6 m × 5 m slab with a semicircular end; serves parts (b) and (c).
- **2022 Q19(b)** — L-shaped bathroom plan, 1200/2400 across and 1200/1500 down; serves (b).

Everything else reuses an existing crop (2023 Q16(a)'s saw for the new (a)(ii), 2023
Q19(b)'s footing drawing for the new (b)(ii)) or needs none — the Section III/IV extended
responses are pure prose and the Q19 calculation parts carry their data in the stem.
**2022 Q16(b) is a table, not a crop**: reconstructed as HTML per §10, 3 columns, 390 px
inside 430 px so no scroll wrapper, blank `&nbsp;` cells 34 px tall.

⚠️ **On these papers a diagram's dimension labels are outline PATHS, not text** — the only
strings the text layer carries near either figure are broken caption fragments (`Pic`/`nic`/
`table`; `Bath`/`room`/`pla`/`n`), so `get_text()` cannot find "5 m" or "1200" at all.
Boxes come from `get_drawings()` widened, and because an ink profile alone once cost the
Maths port a graph's y-axis labels, the script has a **`--verify`** mode that renders a 6 pt
band inside each edge and fails if any dark pixel touches the boundary. Both crops report
**clear on all four edges**, and both were then opened and read. The question's caption is
stem text and sits outside both boxes.

### Authoring

Stems from the **exam papers** (checked for section, number, marks and wording); marks,
sample answers and criteria from the **committed key** — the marking guidelines were never
re-read to derive a mark. **Every stem is self-contained**, because the engine shuffles the
list and a stem reading "this tool" with no stimulus is unanswerable alone; where NESA's
wording depends on context the **stimulus was attached rather than the wording changed**.
Exactly one stem needed a word altered and it is recorded in both the script's `STEM_NOTES`
and its ledger entry: 2021 18(d) reads "on this building site" in the paper and is rendered
"on a building site".

`bandDescriptors` are **not** written by the port script — they are regenerated for all 72
questions by `_vet_review_apply.py` from the committed criteria, so the band-collapse rule
has one implementation and new questions cannot drift from it. The port script refuses to
write unless every question joins an official part, its marks match exactly, and
`answer`/`keywords`/`minKeywords` are all present.

### Verdicts across all 72: 55 `ok`, 6 `corrected`, 11 `divergent-accepted`

The 6 corrected are this morning's review findings. Of the 11 `divergent-accepted`, 2 came
from the review and **9 are calculation questions from the port** whose NESA sample extracts
as mangled equation layout (`× = 2.5 $62.00 $155.00 (Tradesperson)`,
`m3 m3 ÷ 11.6 6 parts = 1 part = 1.93`). Each was compared **numerically** and the agreeing
figures are quoted in its ledger note — the standing Maths exception, now appearing across
VET's calculation questions, and never a silent pass. Two authoring decisions are flagged in
their entries rather than buried: **2023 Q21** separates Isolate as its own hierarchy level
where NESA prints it inside Engineering (presentation, not content), and **2022 Q20**'s
client section is written from the syllabus because NESA's extracted sample truncates before
reaching clients, which the question explicitly asks about.

### Verified

Full local CI green: `validate_subjects.cjs` (`MC=706 Written=418 imageRefs=318
missingImages=0`, `Issues: 0`), `check_answer_key.cjs` (**285 answers, 0 wrong**),
`check_written_key.cjs` (**378 written questions, 0 wrong, 0 unverifiable**; VET **76/76**
coverage, **72/72** reviewed), five Cloudflare functions syntax-check, `npm test` **67/0**.

Browser at **430 px**, all **72** VET written questions rendered one at a time: **0**
`.question-area` overflows, `body.scrollWidth` never above 430, and every question asserted
to carry a non-empty `answer`, at least one keyword and **all three** `bandDescriptors`. All
**20** image-bearing questions load their stimulus (15 distinct files, forced to
`loading='eager'` and awaited or `naturalWidth` reads 0). **2021 Q18(b)** screenshotted
end-to-end: the new crop renders at 388 px with both dimensions legible, badge reads
`3 marks`, a correct answer scores 3/3 at 88% matched, and the feedback is NESA's own top
criteria row.

⚠️ **The live AI marking call still has not been made** — no `ANTHROPIC_API_KEY` in this
environment. Unchanged: verified to the prompt boundary only.

### Still open on VET

Live AI marking (needs a key); the 2025 Q16 substituted image's provenance and licence; the
unplaced Flaticon attribution; and **ten VET 2025 stems ending in a literal `(N marks)`**
that duplicate the badge — which **Mathematics Standard 2 has on 90 stems too**, so it wants
one pass across both rather than a VET-only fix. None blocks the subject: VET's MC and
written banks are now both complete against every official question in the five papers, and
both are enforced in CI.

---

## 2026-09-01 (Maths Advanced Stage 7) — Mathematics Advanced released: the subject is live in the app

**Stage 7 is the last stage, and the port is finished.** Through Stages 4–6 the subject was
deliberately **registered nowhere in code** — 60 MC + 126 written questions, 124 crops and two
committed ground-truth keys, all sitting in the repo with no way for a student to reach them.
This session wired it in, landed the two engine fixes Stage 3 predicted, found a third Stage 3
did not, and exercised the whole bank in a browser. Runbook:
`docs/subject-plans/mathematics-advanced.md`; branch `port/maths-advanced`, **not merged**.

### Registered

`subjects/index.json` gains the file. `index.html` gains `SUBJECT_ID_MAP.mathsadv`, a
`SUBJECTS.mathsadv` config (year + category filters, `hasMC`/`hasWritten`, **no `hasStudy`** —
Study Mode is deferred), a `SUBJECT_CATALOGUE` row, a `.subject-card.mathsadv` teal gradient, a
new `CARD_ART` SVG (axis + cubic curve + shaded area under it + ∫) and a `CLASS_MAP` entry.

⚠️ **Two identifiers were chosen once and are expensive to change**, the same way
`pdhpe-hms` is: `id` (`mathematics-advanced`) is written to Supabase
`subject_selections.subject_id`, and `quizKey` (`mathsadv`) to `user_progress.subject_key`.
`quizKey` is deliberately **not** `maths` — four call sites branch on
`currentSubjectKey === 'maths'` for Standard 2 alone (Extended-318 toggle, Formula Hint button,
Key Concepts suppression, trial-wall copy), and a distinct key keeps Advanced out of three of
them by construction.

### The two engine fixes Stage 3 flagged as blocking

**`NESA_CAT_LABELS` is now subject-aware.** It was one flat global map keyed on the bare
syllabus code, and **five of Advanced's fourteen codes collide with Standard 2's** — Advanced's
`M1` is Modelling Financial Situations, Standard 2's is Measurement. It is now
`{ maths: {…}, mathsadv: {…} }`, read through a new `catLabel()` helper doing
`NESA_CAT_LABELS[currentSubjectKey]?.[code] || code`, with Standard 2's entries moved under
`maths` unchanged and the two chip call sites switched. **Seen working in the browser**:
Advanced's `F1` chip reads *Working with Functions*, Standard 2's still reads *Money Matters*.
Subjects with no map entry still fall through to the bare code.

**The written-question topic badge now reads `q.category || q.topic`**, mirroring the MC path
one function above it. This one is worth stating plainly because it was never about this port:
**Standard 2's 151 written questions carry `category` and zero carry `topic`, so every one of
them has shown no topic badge since their port** — the HMS missing-marks-badge defect, second
instance. Measured before and after: 151/151 now show one, as do Advanced's 126. HMS's 40
(which use `topic`) are unaffected; Multimedia's 29 and VET's 23 still show none, correctly —
those banks carry neither field.

### A third fix Stage 3 did not predict

`buildKeywordFeedback()` hid its **Key Concepts** checklist behind
`currentSubjectKey !== 'maths'`. Advanced's keywords are the same kind of thing as Standard 2's
— answer fragments (`3 ln 3`, `0.0918`, `z = 0.8`), not concepts — so on the offline fallback
grid the checklist would have listed the answer for the student. The test is now a
`MATHS_SUBJECT_KEYS` array. Confirmed suppressed for `maths` and `mathsadv`, still shown for
`vet`, with the score line and the NESA-derived band descriptor rendering either way.

### Verified

The Browser pane went hidden partway through, so pointer clicks timed out and the flow was
driven through the page's own handlers (`.click()` on the real elements, `renderQuestion()` on
the real renderer) — the home and picker screenshots did come through.

- Real flow: card → picker → **Start Practice** → **2020 Q7 answered correctly** (score 1,
  correct option green, all four `optionExplanations` shown, 6-step solution rendered) →
  **2025 Q4 answered incorrectly** (chosen red, correct green, score held) — and that second
  question happened to carry `optionImages`.
- **All 186 questions rendered at 430 px**: **0** `.question-area` overflows, `body.scrollWidth`
  never above 430, **60/60 MC and 126/126 written topic badges**, **126/126 marks badges**.
- **All 7 tables of 7+ columns wrapped and scrolling inside their wrapper** — 2023 Q23's
  11-column *z*-table widest at 694 px inside a 390 px stem.
- **All 124 crops load**, 0 failures (forced `loading='eager'` first — lazy images read
  `naturalWidth` 0 while the pane is hidden).
- Billing surfaces: subscribe modal lists `mathematics-advanced`; trial wall reads
  *"Unlock all 60 questions in Mathematics Advanced"*.
- **No console errors** at any point.
- Full local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`, `Issues: 0`;
  **285** MC answers and **329** written questions checked, 0 wrong, 0 unverifiable; all 5
  Cloudflare functions syntax-check; `npm test` 67 pass / 0 fail.

No credential, schema, pricing or ground-truth fact changed, and **no question content was
altered** — this stage only registers and renders the bank.

### Still open on this subject, deliberately

**Study Mode** (`studyNotes`), the **Exam Trends panel** (data already built at
`data/exam-trends/mathematics-advanced.json`; UI placement is an open design decision) and
**Extended variant questions** are all deferred and recorded as such in the runbook. The card
gradient (teal, `#7FA9A0 → #55867D`) and the 14 shortened chip labels were picked this session
to sit beside Standard 2's amber without colliding with HMS green, Multimedia blue or VET
slate — a routine port choice, but a visual one, so it is called out rather than buried.

---

## 2026-09-02 — VET Construction's Written Response count silently ignored the year filter

The owner reviewed VET Construction in the app and noticed two things: the Written Response
card always read "23 questions" regardless of which year chip was selected, while the Start
Test (MC) card's count did change. Both observations were correct, and only one was a bug.

**23 total written questions is correct, not a defect.** VET's written bank is a deliberate
partial port — 23 of 76 official written parts, documented in CLAUDE.md §6/§11 and reported
(not enforced) by `check_written_key.cjs`'s reverse-coverage line. Nothing to fix there.

**The year filter genuinely did nothing for Written Response, and it was a real bug, not just
a display glitch.** `SUBJECTS.vet.getWritten` (`index.html`) was defined as
`() => shuffle([...(subjectCache.vet?.writtenQuestions ?? [])])` — no `filters` parameter at
all — while every other subject's `getWritten` takes `filters` and applies
`if (filters.year && filters.year !== 'all') qs = qs.filter(...)`, matching its own `getMC`.
VET's `getMC` already filtered correctly, which is why Start Test's count changed and Written
Response's did not. Fixed to match the other four subjects' pattern exactly.

⚠️ **This was not a display-only bug.** `startQuiz('written')` calls
`s.getWritten(pickerFilters)` to build the actual question set a student answers, not just the
picker's preview count. A subscribed student who selected a single year and started Written
Response was silently served all 23 questions across every year, not the year they picked —
confirmed in the browser before the fix (`activeQuestions.length` stayed 23 for `year: '2025'`)
and after (`11`, all `year === 2025`). VET's 23 written questions carry `year` on every one
(2021: 2, 2022: 3, 2023: 3, 2024: 4, 2025: 11), so the filter was never a no-op by data shape,
only by code.

**Verified**: simulated a subscribed user (trial users see a different mode-card markup with no
`#written-count`/`#mc-count` span at all, so `updateModeCounts()` cannot be exercised in trial
regardless of this fix — that is existing, unrelated behaviour). With `pickerFilters.year`
toggled via `applyFilter('year', ...)`, `#written-count` moved 23 → 11 for 2025 and
`startQuiz('written')` then produced exactly those 11 questions. Regression-checked all four
other subjects' `getWritten({year})` against `getWritten({})` — all filter correctly, none
changed behaviour. Full local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`,
`Issues: 0`; all 5 Cloudflare functions syntax-check; `npm test` 67/0. No JSON, schema, pricing
or credential fact changed — `index.html` only.

---

## 2026-09-02 (later) — Two VET written questions with no stimulus, and a genuinely tall crop capped

The owner reported three things while reviewing VET Construction's expanded written bank
(23 → 72 questions, merged earlier today): an oversized picture, a chisel question where
"some parts show it, others don't," and a 2023 two-part question repeating text between the
picture and the stem. They also asked directly whether multi-part questions should be
shuffled at all.

**Two real missing-image bugs found and fixed, not one.** 2021 Q16(b) ("Describe TWO
suitable uses for the chisel shown") had no `image`, while its siblings 16(a)/(c)/(d) all
carry `/diagrams/vet-construction_2021_Q16_stimulus.jpg` — the exact bug reported. A text
sweep for "shown"/"this tool"/"pictured"/similar phrasing across every VET written question
with no `image` field turned up a second, unreported instance of the same defect: **2025
Q16(b)** ("...using the router shown") also had no `image`, while sibling 16(a) carries
`/diagrams/vet-construction_2025_Q16_stimulus.jpg`. Both fixed by adding the sibling's image
path. The sweep's one other hit, 2022 17(a) ("levelling information can be shown on
construction plans"), is not a defect — it isn't referring to a picture at all.

⚠️ **The apparent "many inconsistent" pattern was mostly a false trail.** Grouping all 72
written questions by NESA question number found 23 of 29 questions are multi-part, and a
crude same-image-across-siblings check flagged 13 of those 23 as "inconsistent." Reading each
one showed nearly all of them are legitimately different: 2022 Q19's three parts have three
different stimuli (a vehicle-load table, a bathroom plan, and no image at all for the
calculation part), and 2021 Q18's (a) and (d) are a labour-cost calculation and a WHS
question that were never about the concrete-slab diagram (b)/(c) share. Only a stem that
explicitly points at a picture ("shown", "this tool") with no `image` attached is a genuine
bug — checking for that directly, not for whether siblings' images merely differ, is what
actually catches these.

**The oversized picture is 2022 Q16(a)'s stimulus, and it isn't a bad crop.** The image is
246×644px, a 0.38 aspect ratio versus every other VET stimulus's 1.0–2.6 landscape range.
Rendering the source PDF page confirmed why: the tool NESA drew is a **plumb bob** —
genuinely a long thin string above a tall narrow cone — and the crop is tight and accurate.
At `.q-image-wrap img`'s existing `width:100%; height:auto` (uncapped), that renders roughly
390×1020px on a phone, nearly two full screens for one image. Fixed with `max-height:50vh`
plus `object-fit:contain` on `.q-image-wrap img` (`index.html`) — measured in the browser:
the plumb bob now renders 333×406px (aspect ratio preserved, no distortion), while a normal
landscape crop (2021 Q16(c), ratio 1.46) is untouched at 333×228px, well under the 50vh cap.
This protects every subject's stimulus images against any future outlier crop, not just this
one.

**The direct question — "are we handling multi-part questions the right way?" — the answer
is no, and this is the real root cause behind all three reports, not three separate issues.**
Mathematics Advanced and Standard 2 already store one bank entry per whole NESA question,
with every part's text, its own `(N marks)` badge, and one shared image folded into a single
`q` field (e.g. Advanced 2020 Q14: three sub-parts, one `keywords` list spanning all three,
one 5-mark total) — confirmed by reading a live example. **VET's bank instead stores each
part as its own array entry**, so `getWritten()`'s `shuffle()` treats every sub-part as an
independent quiz card: a shared stimulus can land on-screen for one part and be gone by the
time a sibling part is drawn minutes later, and a genuinely shared intro sentence (2023 Q19(b)
i/ii, both "A shed is to be built on a concrete slab...") gets restated verbatim in both cards
because each was authored to be self-contained for exactly this shuffle. **VET is the outlier
subject, not the norm** — the fix that would resolve all three symptoms at once is re-merging
VET's split multi-part entries into the same one-entry-per-question shape Advanced and
Standard 2 already use, matching a proven, already-shipped pattern rather than inventing a new
one. **Not done in this session**: it touches 23 of 29 NESA questions (66 of 72 sub-entries),
the review ledger (`data/answer-key/written/reviews/vet-construction.json`, keyed per current
qNum), and needs editorial judgment merging `bandDescriptors`/`keywords` per question rather
than mechanical concatenation — recorded as a scoped follow-up, not executed without the
owner's sign-off on approach.

**Verified**: full local CI green (`MC=706 Written=418 imageRefs=320 missingImages=0`,
`Issues: 0`; VET still 76/76 coverage, 72/72 reviewed — adding an `image` field doesn't touch
marks/keywords/bandDescriptors, so no review verdict was invalidated; 285 MC answers checked,
0 wrong; 5 functions syntax-check; `npm test` 67/0); both fixed questions confirmed to carry
the correct image in the browser; the plumb bob and a normal landscape image measured
side-by-side post-fix. No mark, MC answer, `category`, or review verdict was altered —
`index.html` (CSS only) and `subjects/vet-construction.json` (two `image` fields added) only.

---

## 2026-09-02 (later still) — VET Construction's Section II multi-part questions merged into one bank entry per NESA question

The owner asked directly whether multi-part written questions were being handled correctly,
after the chisel/oversized-image/duplicate-text reports turned out to share one root cause:
VET's written bank stored each NESA sub-part (`"16(a)"`, `"16(b)"`, `"16(c)"`, `"16(d)"`, …)
as its own independent array entry, so `shuffle()` in `getWritten()` scattered a single NESA
question's parts across the quiz session as unrelated cards — a shared stimulus could render
on one part and be absent minutes later on a sibling, and a genuinely shared intro sentence had
to be duplicated into every part because each was authored to stand alone.

**Mathematics Advanced and Standard 2 already do this correctly** — confirmed by reading a
live example (Advanced 2020 Q14: three sub-parts, one `keywords` list, one 5-mark total, one
`q` field with each part's own `<strong>(N marks)</strong>` badge inline). VET was the outlier,
not the norm, so this port re-merges VET's split entries into that same established shape
rather than inventing a new one.

**Scope: Section II (Q16–19) only — 23 NESA questions, 18 of them split (59 sub-entries) —
not Section III/IV (Q20/Q21).** Re-reading all five papers' Section II AND Section III/IV text
directly from the source PDFs (not reconstructed from the already-split JSON) surfaced a
structural difference the initial ask hadn't accounted for: Section III/IV explicitly directs
students to answer each part **in a separate writing booklet** ("Answer part (a) of the
question in a writing booklet... Use the other writing booklet to answer part (b)"). Those are
genuinely independent responses on different topics, not a shared short-answer sequence —
merging them into one card would misrepresent the real exam rather than fix anything, so they
were left as they were. Q17 (2021), Q20 (2022) and Q21 (2023/2024/2025) were already single,
un-split entries in the bank; nothing there needed touching either.

**Method**: a one-off script (`scripts/archive/vet_merge_multipart.py`, run then archived, not
part of CI) merges the 18 groups. Marks are summed and validated against
`data/answer-key/written/vet-construction.json` **before** any write — all 18 reconciled
exactly on the first attempt (e.g. 2021 Q16: 1+2+2+3=8, 2022 Q17: 2+2+2+4=10). `keywords` are
the union of all constituent parts' lists (352 total → no duplicates within a merged entry);
`acceptableAnswers` on a short identification part (e.g. 2021 16(a)'s chisel ID) is folded into
the merged `keywords` list instead, since `acceptableAnswers`' exact-match mechanism doesn't
suit a combined multi-sentence response. **Every merged question also switches from the
top-level `image` field to an inline `<img>`** (matching Advanced/Standard 2's own convention,
which never uses the top-level field on a written question), positioned in the stem exactly
where the sentence introducing the picture sits — critical for questions like 2022 Q19, whose
three parts have three different stimuli (a delivery-cost table, a bathroom plan, no image at
all), where a single top-level image field could never have placed each picture correctly.

⚠️ **`bandDescriptors` needed fresh synthesis, not concatenation.** NESA's marking guidelines
grade each part separately; there is no official combined rubric for an 8-or-13-mark merged
question. Each of the 18 merged entries got a newly authored three-tier `{full, partial,
minimal}` descriptor summarising performance across all its parts, in the same concise,
mark-tied style as the rest of the bank (e.g. 2021 Q16: "Correctly identifies the chisel,
describes TWO suitable uses, ONE consequence of poor maintenance, and both care and
maintenance procedures in detail").

**The review ledger was rebuilt through the project's own tooling, not hand-edited.**
`scripts/reviews/vet_construction.py`'s 72 per-part verdicts were consolidated to 34
per-question verdicts — `corrected` if any constituent part required a correction, else
`divergent-accepted` if any part was divergent, else `ok` — with every constituent part's
original note concatenated and prefixed by its old part label, so none of the hard-won
review history (six real defects found across the subject) was lost. `check_written_key.cjs`'s
strict 1:1 bank↔table check caught a real bug in the process: the merge script's `qNum` was
written as a bare Python int (`16`) where every other VET entry uses a string (`"17"`,
`"21(a)"`); fixed before the ledger rebuild, verified with an explicit missing/extra diff
against the live bank (both empty) before running `scripts/build_review_ledger.py
vet-construction`.

**Verified**: full local CI green (`MC=706 Written=380 imageRefs=313 missingImages=0`,
`Issues: 0`; VET **76/76 coverage unchanged, 34/34 reviewed — 6 corrected, 2
divergent-accepted, 26 ok**; 285 MC answers checked, 0 wrong; `npm test` 67/0). Browser-verified
at 430px: **all 34 written questions render with 0 `.question-area` overflow and a marks
badge on every one**; all 15 distinct inline images load; the 2021 chisel card now shows the
tool **once** with all four parts flowing beneath it (previously 4 separate cards, one with no
image); the 2023 shed question's shared intro sentence now appears **once** before (i) and
(ii) (previously duplicated); a full practice-mode answer flow was exercised end-to-end on the
merged chisel question — typed answer → scored 2/8 against the unified 35-keyword list → the
newly authored "partial" band text displayed → the four-part model answer revealed correctly
labelled. The one console error seen (`POST /mark-written → 404`) is pre-existing and
unrelated: the local static file server has no Cloudflare Functions runtime, so AI marking
always falls back to the offline keyword grid in this environment, which is exactly what was
observed working. No MC question, MC answer, or `omittedQuestions`/`omittedParts` declaration
was touched — only VET's written bank shape, its `image` mechanism, and its review ledger.

---

## 2026-09-02 (later still, again) — Checked how the merged VET questions are actually marked; one harmless tidy-up, one claim retracted after testing it

The owner asked how a merged 3-part written question is marked now, from a screenshot of
**Test Mode**. Traced the render path directly rather than assuming: Test Mode has never
auto-marked written answers, before or after the merge — `nextQuestion()`'s test-mode branch
says so in its own comment ("no AI marking"), and `showResults()` for written Test Mode only
lays the student's answer next to the model answer for self-comparison. Unaffected by
2026-09-02's merge.

That prompted a closer look at **Practice Mode**, where written answers genuinely are scored,
since omitting `minKeywords` on all 18 merged entries and letting the engine default to
`Math.ceil(keywords.length / 2)` looked, on paper, like it raised the threshold above the sum
of the three-or-four original per-part values (e.g. 2021 Q16: auto 18 vs the original parts'
1+3+3+5=12). ⚠️ **That concern does not survive testing and is retracted as a real
scoring difference.** `buildKeywordFeedback()`'s cap rule is
`if (matched < minKw) marksEarned = min(marksEarned, floor(maxMark/2))` — a sweep of every
possible `matched` value from 0 to `keywords.length`, on five representative merged questions,
produced **zero cases** where the auto-default and the original-sum threshold gave a different
`marksEarned`. The reason: `Math.ceil(N/2)` sits almost exactly at the same "matched ⁄ N > 0.5"
point where the cap's own condition (`raw > floor(maxMark/2)`) stops being reachable, so the
cap is structurally near-inert whenever `minKeywords` is anywhere close to half the keyword
count — which both the auto-default and the original per-part sums are, for every one of
these 18 questions.

**`minKeywords` was still set explicitly** (`subjects/vet-construction.json`, sum of each
merged question's original constituent parts, matching the position convention
`keywords` → `minKeywords` → `bandDescriptors` used everywhere else in the file) — not
because it changes any score, but because it documents the actually-tuned intent rather than
silently deferring to a formula default, and costs nothing (`check_written_key.cjs`'s
review-ledger fingerprint only tracks `modelAnswer`/`keywords`/`bandDescriptors`, so this
touches nothing CI enforces). **Verified inert, not verified beneficial** — stated plainly
rather than oversold.

**How the merged questions are actually marked, confirmed by reading the code, not
assumed:** Practice Mode with a signed-in user sends `mark-written.js` the **whole merged
`q` text** (all parts), `maxMarks` (the summed total, e.g. 10), the **union `keywords`
list**, the **freshly authored merged `bandDescriptors`**, and the student's one combined
answer — Claude marks it as **one holistic assessment across all parts**, not per-part.
Practice Mode without a signed-in user (or while the AI call is pending/erroring) falls back
to the same keyword-matching grid described above, against the same union list. Test Mode:
not marked at all, by design, in either the old or new bank shape.

No mark, MC answer, `category`, or review verdict was altered. `index.html` was not touched.

---

## 2026-09-02 (later still, again) — Split written parts now shuffle adjacently, and show a "Part X of Y" indicator

The owner asked, of VET's 2025 Q20 (deliberately kept as two separate bank entries,
5 marks + 10 marks, because NESA sends them to separate writing booklets — CLAUDE.md §10
rule 9): if `shuffle()` scatters the whole written array, how would a student ever know
their two separate scores belong to one original NESA question? They suggested keeping such
parts adjacent instead of fully random, and asked if there's a better way.

**There was, and it's a general engine fix, not a VET patch.** Two additions to `index.html`:

- **`shuffleGrouped(arr)`** groups written questions by `(year, base NESA question number)`
  before shuffling, so the shuffle happens at the whole-question level — a group's internal
  order and adjacency are fixed (NESA's own (a)/(b) order), only the order *between* groups
  is randomised. A no-op for any question with no split siblings, so it's safe to wire into
  every subject's `getWritten()` unconditionally, which it now is (all 5: maths, mathsadv,
  hms, multimedia, vet) — not just VET.
- **`writtenPartInfo(subjectKey, q)`** returns `{ index, total, base }` for a question that
  has 2+ siblings sharing its base number, or `null` otherwise. Rendered as a
  "Q20 · Part 2 of 2" badge next to the year badge in `renderQuestion()`, and as "— Q20,
  part 2 of 2" in the Test Mode results breakdown — the two places a student could otherwise
  see two disconnected scores with nothing telling them they're related, since `qNum` itself
  is never shown anywhere in the UI.

⚠️ **Checking whether this needed to be VET-specific surfaced a second subject with the
exact defect the 2026-09-02 merge fixed for VET, still live.** Mathematics Standard 2 has
**11 split entries across five 2020/2021 questions** (Q23, Q34, Q35, Q26, Q27) with the same
signature as VET's pre-merge state — shared context sentences duplicated verbatim across
sibling parts (2020 Q23(a) and Q23(b) both open "In a tropical drink, the ratio of pineapple
juice..."). These are genuine Section II short-answer sub-parts sharing one response space
on the page, **not** NESA-directed separate-booklet responses, so per CLAUDE.md §10 rule 9
the correct fix is the same merge treatment VET got — not a permanent "Part X of Y" badge.
**Not done in this session** — today's fix makes the current state safe and honest (adjacent,
labelled) for whichever subject has split siblings at any given time, but it is explicitly a
safety net, not a substitute for merging Standard 2's 11 entries. Recorded here as a known
gap, not actioned without the owner's sign-off, matching how the Multimedia Section III
finding was handled the same session.

**Verified**: `shuffleGrouped` swept 50 shuffles each for VET's 2025 Q20(a)/(b) and Standard
2's 2020 Q23(a)/(b) — 100% adjacent, always in NESA's own order, in both directions;
non-split subjects (Advanced, Multimedia) unaffected, confirmed `writtenPartInfo` returns
null for every one of their questions. Browser-verified the badge renders "Q20 · Part 1 of 2"
/ "Part 2 of 2" correctly on the live question card and in the Test Mode results screen;
full local CI green (`MC=706 Written=380 imageRefs=313 missingImages=0`; `npm test` 67/0);
no console errors. `getMC()` was deliberately left on plain `shuffle()` for every subject —
Standard 2's Extended-318 MC variants share a base qNum with their original question but are
meant to be fully independent draws, not grouped, so grouping was scoped to written mode
only. No mark, MC answer, or review verdict was touched — `index.html` only.

---

## 2026-09-05 — Per-part answer boxes and per-part marks, as the engine-wide standard

**What changed.** A written question that NESA prints with lettered parts now gets **an
answer box and a mark per part**, instead of one box scored as a lump. `subjects/vet-construction.json`'s
18 merged multi-part questions carry a new `parts[]` array; `index.html` renders them as an
accordion with auto-advance; `functions/mark-written.js` marks every part in one API call and
returns a mark for each; `scripts/validate_subjects.cjs` asserts the per-part marks total the
question's own mark; `tests/mark-written.test.js` gains 6 tests. Schema and rationale are
CLAUDE.md §10 rule 10; the gate for future ports is in `docs/porting-playbook.md` Stage 3.

**Why.** The 2026-09-02 merge fixed the *card* (parts no longer scatter across a shuffled
quiz) and left the *answering* wrong. 2024 Q19 is four parts worth 2+3+2+2; a student who
answered (a), (b) and (d) and skipped (c) saw `6 / 9` and one paragraph of general feedback,
with nothing saying which part cost them the 3 marks. The owner asked how a student would
know "whether they got 5 out 5 and 5 out 10".

**The design was mocked up before it was built**, twice, at the owner's request — first a
current-vs-proposed side-by-side, then three mobile layouts (straight scroll / accordion /
step-through) live in a 390×720 frame. Straight scroll is the most faithful to the printed
paper but runs 2.1 screens for 2024 Q19; step-through is the most focused but forces a linear
order, which the real paper does not. **Accordion won** — 1.0 screens, free navigation between
parts, progress visible without scrolling — with a **Next part** button added afterwards for
forward momentum. A shared `stem` is sticky (capped `34vh`) so a stimulus every part refers to
stays on screen; that is what the 2021 chisel question needs, and it renders once, not four times.

**Nothing in the data was authored.** Per-part marks came from the merged `q`'s own
`<strong>(N marks)</strong>` badges; per-part `answer`/`keywords`/`acceptableAnswers`/
`minKeywords`/`bandDescriptors` came from the **pre-merge bank recovered from git at
`12a2c31^`**, where every part was its own entry. `scripts/archive/vet_add_parts.py` refuses to
write unless, for every question, the split finds exactly as many parts as the pre-merge group,
every label matches, every part's marks match its pre-merge entry, and the parts sum to the
question total. 18/18 passed, 0 failures.

**Two bugs the build itself hit, both found by running it rather than reading it:**
- The marks badge is **not always last in a part** — on 2022 Q19(a) and Q16(a) the stimulus
  image is printed *after* it. Anchoring the regex to end-of-segment silently reclassified
  those parts as intros and lost them (2 of 18 questions). Fixed by not anchoring.
- **In-progress text cannot live in `answers[]`.** `renderQuestion()` derives `answered` from
  `answers[currentIdx] !== null`, so writing a draft there on a part toggle flipped the
  question straight into its already-checked state on the first *Next part* click. Drafts now
  live in `partDrafts`, and a single `saveWritten()` keeps the two in step — a second bug,
  where a stale draft outranked a fresher committed answer after Next/Prev, showed up in
  test-mode navigation and is fixed by the same helper.

**Verified.**
- **The scorer refactor is proven inert**: `scoreOne()` is now the single implementation of
  the offline marking formula, shared by `buildKeywordFeedback()` and the per-part path. It
  was compared against a reimplementation of the original inline formula over **2 280
  comparisons** — every written question in all five subjects × six probe answers each —
  with **0 mismatches**.
- **All 380 written questions in all five subjects render at 430 px with 0 overflow** and a
  marks badge on every one; VET's 18 multi-part questions were walked **part by part**, every
  part rendered and measured. All 15 distinct part images load.
- Real practice-mode flow driven end to end: (a)→(b)→(c)→(d) via *Next part*, progress
  tracking 0→3 of 4, text surviving jumps back to earlier parts, then submitted for
  **`6 / 9 marks`** with rows `(a) 2/2`, `(b) 2/3`, `(c) 0/2`, `(d) 2/2` — genuinely
  computed, not the mockup's typed-in numbers. Part (b)'s note is NESA's own *partial*
  band wording ("the volume of the concrete slab", against full's "minus the hole"),
  which is exactly what that answer omitted.
- **Single-part questions are untouched**: one `#written-input`, no accordion, keyword grid,
  no part rows — checked on 2025 Q21.
- Test mode: per-part editor, answers surviving Next/Prev, **still never auto-scores**, and
  the results breakdown flattens to labelled lines (`(a) … (d) …`) with skipped parts omitted.
- *Try again* fully resets a multi-part question; all 34 VET written questions re-rendered in
  a loop with **0 errors**; no console errors anywhere.
- Full local CI: `MC=706 Written=380 imageRefs=327 missingImages=0`, `Issues: 0`; 285 MC
  answers and 340 written questions checked, 0 wrong, 0 unverifiable; VET coverage 76/76 and
  34/34 reviewed, unchanged; 5 functions syntax-check; **`npm test` 73/73** (was 67).

⚠️ **The live AI marking call was still NOT made** — there is no `ANTHROPIC_API_KEY` in this
environment — so the multi-part marking path is verified to the prompt boundary and no
further: the prompt is built from `mark-written.js`'s **own source**, sliced from the file,
and carries every part with its own maximum, key concepts and band descriptors, no
`undefined`, and an explicit instruction not to pool marks across parts. The *response*
handling **is** covered by real tests: a part awarded more than its own maximum is clamped, a
negative is floored at 0, an invented label is discarded, the total is derived from the parts
rather than trusted, and a one-element `parts` array falls back to the single-question shape.

**One improvement to the prompt, deliberately scoped to the new path only:** part questions
are sent as plain text with `<img>` collapsed to `[diagram: <alt text>]`. The model cannot see
an image, so the tag was pure noise while the alt text is a real description (3 847 → 3 584
chars on 2024 Q19). The **single-question** prompt still sends raw HTML — left alone on
purpose, so this change cannot move any existing question's mark.

**Not done, and recorded as backlog rather than missing:** only VET carries `parts[]`.
Mathematics Advanced (126 written), Standard 2 (151), Multimedia (29) and HMS (40) store
multi-part questions as one merged entry with **no per-part keywords or band descriptors
anywhere in the file**. Their per-part *marks* are recoverable from `data/answer-key/written/`,
but the scoring data would have to be authored from NESA's criteria rows — a content job per
subject, not a port of existing data. Those subjects keep the single box until then, which is
exactly the behaviour they have today.
