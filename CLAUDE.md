# CLAUDE.md — CramIT Project Instructions

> **Strategy for every task: Explore → Plan → Code → Verify → Commit → Docs**
> Before touching a single line of code, read the relevant files. Then write a plan in plain English. Only then write code.

> **Global rules (API cost optimisation, file safety, security, git, communication) also apply — see `~/.claude/CLAUDE.md`**

> **This file is deliberately short.** Full session-by-session history (what changed, why, and how it was verified) lives in [`docs/HISTORY.md`](docs/HISTORY.md) — not auto-loaded, read it only when investigating why something was built a certain way. Agent-infrastructure planning (Stage 9) lives in [`docs/agents-plan.md`](docs/agents-plan.md) — not needed for day-to-day app/billing/content work. **Adding a new subject? [`docs/porting-playbook.md`](docs/porting-playbook.md) is a mandatory read before you start** — §10's five steps are only its final stage.

---

## 1. What CramIT Is

CramIT is an AI-powered HSC exam practice platform for NSW students. It is a subscription-based Progressive Web App (PWA) that:
- Automatically monitors NESA for new exam papers nightly via a GitHub Actions agent *(built 2026-07-04 — Content Agent, PR-only; needs `ANTHROPIC_API_KEY` GitHub Secret to run, see §4.4)*
- Generates quiz questions using Claude AI and stores them as JSON files in the repo
- Delivers quizzes through a mobile-friendly PWA students can install on any device
- Handles billing via Stripe with per-subject pricing and a $19.99 cap

**The owner is a beginner-to-intermediate developer. Always explain the "why", not just the "what". Give complete, copy-paste-ready code. Never leave placeholders without explaining exactly what to fill in.**

---

## 2. The Workflow

Every task, no matter how small, follows this process:

1. **EXPLORE** — Read every file the task touches before writing anything. For billing tasks: read `functions/create-checkout.js`, `functions/update-subscription.js`, `functions/customer-portal.js`, `functions/_lib/auth.js`. For quiz/content tasks: read the relevant `subjects/{id}.json` and the rendering code in `index.html`.
2. **PLAN** — State which files will change and why, and flag risks (RLS policies, Stripe webhook order, auth state). Get confirmation before touching billing, auth, or DB schema.
3. **CODE** — Complete, working, copy-paste-ready. Use `Edit`/`str_replace` on large files — never truncate with "…rest of code here…". Preserve existing functionality.
4. **VERIFY** — For anything observable in the browser (UI, quiz flow, billing modals), start the preview and actually exercise the change before calling it done. JSON/code being *correct* is not the same as the rendered output being *correct* — a change that "should work" has shipped broken more than once in this project (see `docs/HISTORY.md` — the submit-test modal crash was exactly this). State what you checked.
5. **COMMIT** — exact git instructions:
   ```bash
   git add <specific files>
   git commit -m "feat: <short description>"
   git push origin main
   ```
   Cloudflare Pages auto-deploys on every push to `main`.
6. **DOCS** (mandatory after every non-trivial task) — Add one entry to `docs/HISTORY.md` describing what changed and how it was verified. Only touch `CLAUDE.md` itself if an instruction, credential, schema, or file-structure fact changed — this file should stay a stable reference, not a changelog. Update Blueprint V4 (Word doc, NOT in repo — `C:\Claude Code Space\CRAMIT QUIZ Code Folder\Documents\CramIT_Autonomous_Operations_Blueprint_V4.docx`, via `/docx` skill) only for agent architecture, DB schema, infra, or pricing changes.

---

## 3. Tech Stack — Never Suggest Alternatives

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Three HTML files — vanilla HTML/CSS/JS | No React, no Vue, no frameworks. See §9 for three-file architecture. |
| Hosting | Cloudflare Pages (free tier) | Functions at `/functions/` folder → served at `/{name}` — NEVER `/.netlify/functions/` |
| Auth | Supabase Auth — email/password + Google OAuth | |
| Database | Supabase (Postgres) — RLS enabled | Client always uses `sbClient` |
| Payments | Stripe — subscription billing | Webhooks verified server-side |
| Webhook handler | Supabase Edge Function named `clever-action` | NOT `stripe-webhook` — this was auto-named |
| AI Agent | Node.js + Anthropic Claude API | Content Agent (`agent.js`) runs nightly via GitHub Actions, PR-only — see §4.4 |
| Repo | GitHub — `bustachat/CramIT-Quiz` | Public repo, main branch |
| Diagram images | Cloudflare Pages static files at `/diagrams/` | Served from git repo — NOT Supabase Storage. Unlimited bandwidth free. |

---

## 4. Live Credentials & Configuration

### ⚠️ Security Rule
Never commit API keys to GitHub. All keys go in environment variables. This file documents **where to find** each key — not the actual values.

### 4.1 Supabase
| Setting | Value |
|---|---|
| Project URL | `https://ohqtefjawaphtsebnaxg.supabase.co` |
| Edge Function URL | `https://ohqtefjawaphtsebnaxg.supabase.co/functions/v1/clever-action` |
| Region | ap-southeast-2 (Sydney) |
| Edge Function name | `clever-action` |
| Auth providers | Email/password + Google OAuth (Testing mode — not yet published) |
| RLS | Enabled on all tables — manual policies |

**Where to find Supabase keys:** Project URL + Anon Key → Dashboard → Settings → API → Project URL / anon public. Service Role Key → Settings → API → Legacy → service_role.

**Supabase Edge Function Secrets:** `STRIPE_SECRET_KEY` (Stripe → Developers → API keys), `STRIPE_WEBHOOK_SECRET` (Stripe → Webhooks → endpoint → Signing secret), `SUPABASE_SERVICE_ROLE_KEY` (auto-injected).

### 4.2 Cloudflare Pages
| Setting | Value |
|---|---|
| Project name | `cramit-quiz` |
| Live URL | `https://cramit-quiz.pages.dev` |
| Build command | `npm install` |
| Build output directory | `/` (root) |
| Functions directory | `functions/` (auto-detected) |
| Node version | 22 |

**Cloudflare Secrets** (Workers & Pages → cramit-quiz → Settings → Environment variables):
| Secret | Source |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe → **Sandbox** → Developers → API keys — use the Sandbox key, not plain Test mode |
| `SUPABASE_URL` | `https://ohqtefjawaphtsebnaxg.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Legacy → service_role |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `STRIPE_PRICE_CAP` | `price_1TEdW3Pvnbx5MPYykHvvk7gf` |
| `STRIPE_PRICE_FLEX_BASE` | `price_1TEdZRPvnbx5MPYylioNhNQI` |

⚠️ **Stripe Sandbox gotcha:** Stripe has two test environments — "Test mode" and "Sandbox". Customer/subscription data lives in the **Sandbox**. Always use the Sandbox key in Cloudflare. Both look like `sk_test_...` but have different prefixes after `51T`.

### 4.3 Stripe
| Setting | Value |
|---|---|
| Mode | **Sandbox/Test** — NOT live yet |
| Webhook endpoint | Points to the Supabase Edge Function URL above |
| Transaction fee (live) | 1.75% + 30¢/txn |

**Stripe Products:**
| Product Name | Code Key | Billing | Notes |
|---|---|---|---|
| Quiz Base — Starter | `base` | $7.99/mo | Covers 2 subjects |
| Quiz Extra — Add-on | `extra` / `flex_extra` | $2.99/mo per unit | Per subject above 2 |
| Quiz Unlimited | `cap` | $19.99/mo | Up to 7 subjects |
| Quiz Flex — Power | `flex_base` | $19.99/mo | Base for 7+ subjects |

Price IDs are constants in `create-checkout.js` and `update-subscription.js` (the only two files that need updating when Stripe switches to live mode — create new Price objects first).

### 4.4 GitHub Actions
Two workflows in `.github/workflows/`:
| Workflow | Trigger | What it does |
|---|---|---|
| `validate.yml` | Every push + PR | Validates subject JSON (`scripts/validate_subjects.cjs`), **checks HSC MC answers against the official key** (`scripts/check_answer_key.cjs`), **checks written-question marks against the official key** (`scripts/check_written_key.cjs`), syntax-checks Cloudflare functions, runs billing tests |
| `content-agent.yml` | Nightly `0 13 * * *` (11pm Sydney) + manual Run-workflow button | Runs `agent.js` (NESA discovery → paper triage → question generation), opens a PR on an `agent/content-*` branch — **never pushes to main** |
| `security-scan.yml` | Push/PR to `main` + weekly Monday `0 6 * * 1` + manual dispatch | Semgrep + Trivy (report-only, SARIF → Security → Code scanning tab) and Gitleaks (**blocking** — fails the build on a hardcoded secret; repo is public and holds live Stripe integration, no staging gate before main auto-deploys) |

Requires the `ANTHROPIC_API_KEY` repository secret (GitHub → Settings → Secrets and variables → Actions) — not yet set, see pre-launch checklist #2. ⚠️ Gotcha: PRs opened with the default `GITHUB_TOKEN` do **not** trigger `validate.yml`; the content-agent workflow runs the validator itself as an explicit step to compensate (swap in a PAT later for real CI on agent PRs).

### 4.5 Google OAuth
Status: **Testing mode** — only approved test users can sign in. To go public: Google Console → OAuth consent screen → Publish app (submit for verification). Client ID/Secret → Google Console → Credentials → used in Supabase Auth → Google provider.

---

## 5. Database Schema

Tables live in Supabase. RLS is enabled on all tables. Full definitions, including triggers, in `db/schema.sql` — keep it in sync with any live Supabase SQL Editor change (see the entitlement trigger pattern in that file for the expected style).

| Table | Purpose | Key Fields |
|---|---|---|
| `profiles` | Extends auth.users | `id`, `email`, `full_name` |
| `subscriptions` | Plan status, Stripe IDs | `user_id`, `plan`, `status`, `subject_count`, `stripe_subscription_id`, `stripe_customer_id` |
| `subject_selections` | Which subjects each user selected | `user_id`, `subject_id`, `added_at` — BEFORE INSERT trigger enforces `subject_count` limit |
| `pricing_config` | Pricing constants — edit here to change prices | `key`, `value` |
| `user_progress` | Per-question answer history — cross-device sync | `user_id`, `subject_key`, `question_idx`, `mode`, `is_correct`, `answered_at` — UNIQUE(user_id, subject_key, question_idx, mode) |

**Agent coordination tables** (from Blueprint V4 — planned, not yet deployed; see `docs/agents-plan.md`): `agent_tasks`, `agent_logs`, `escalations`, `agent_config`, `content_issues`, `known_issues`, `analytics_snapshots`, `band_descriptors`, `marking_criteria`, `band_mapping`, `written_submissions`.

**Staging Supabase project** — not yet created. See `docs/agents-plan.md` for why it's needed before any agent work starts.

---

## 6. File Structure

```
cramit-quiz/
├── .github/workflows/
│   ├── validate.yml            ← CI: validates subject JSON + syntax-checks Cloudflare functions on every push/PR
│   ├── content-agent.yml       ← Nightly Content Agent — runs agent.js, opens PR on agent/content-* branch (needs ANTHROPIC_API_KEY secret)
│   └── security-scan.yml       ← Semgrep + Gitleaks + Trivy on push/PR to main + weekly — Gitleaks blocks the build, Semgrep/Trivy are report-only to the Security tab
├── index.html                  ← Mobile PWA — student quiz experience (logged-in students)
├── landing.html                ← ⬜ PLANNED — Public marketing/landing page (pre-signup visitors)
├── portal.html                 ← ⬜ PLANNED Stage 10 — Desktop web portal (logged-in students)
├── manifest.json               ← PWA manifest (icons/icon-192/512.png, #FAF8F5 theme)
├── agent.js                    ← Content Agent: NESA discovery → paper triage → MC generation in app schema. `node agent.js --selftest` for offline checks. Only updates EXISTING subjects — never creates new ones (those need index.html work, see §10)
├── agent-state.json            ← Papers the agent has already processed (slug-year keys) — committed so state persists across runs
├── package.json                ← { "type": "module", "dependencies": { "stripe": "^14.0.0" } }
├── supabase.min.js             ← Local Supabase JS client (loaded via script tag)
├── generate_study_tool.py      ← ⚠️ SIDE PROJECT ONLY — generates olivier-hms-prep.html. NOT part of CramIT app or architecture.
├── olivier-hms-prep.html       ← ⚠️ SIDE PROJECT ONLY — standalone assessment study tool for one student (Focus Area 2 only). No auth, no billing, no Supabase. Do NOT integrate into index.html or reference in any CramIT architecture docs.
├── olivier-hms-exam-prep.html  ← ⚠️ SIDE PROJECT ONLY — standalone FULL-COURSE HMS study tool (both Focus Areas, 9 topics: Study/Practice MC/Written/Mock). Self-contained, no Supabase. Same "do NOT integrate" rule as above. Mock Exam mirrors the real NESA HMS paper (100 marks: 20 MC + Section II `SECTION2_SLOTS` 56 + Section III `SECTION3_BANK` 2×12); 190 original MC; scaffolds match the real bands (Short 2–4 / Extended 6–10 / Extended Response 12); FA2 depth (principles, tapering-type diagram, inverted-U SVG, HOWSCSE, carb-loading/RED-S) ported from the older FA2-only `olivier-hms-prep.html`. Each Study topic card also ends with a click-to-reveal "Revision Questions" block (74 total across the 9 cards, `.revision-block`/`toggleRevision()`) — original model answers, curated from `pdhpe-net-cache/`. Recalibration/enrichment plan: docs/olivier-hms-exam-plan.md.
├── olivier-hms-exam-diagrams/  ← ⚠️ SIDE PROJECT ONLY — cropped diagram JPGs for olivier-hms-exam-prep.html (NOT the app's /diagrams/ folder). Regenerate with scripts/crop_olivier_hms_exam.py.
├── scripts/crop_olivier_hms_exam.py ← ⚠️ SIDE PROJECT ONLY — one-off PyMuPDF cropper (fraction-of-page clips) for the ATAR Notes HMS summary book. Not part of app tooling.
├── written_q_extracts.json     ← Pre-extracted NESA PDF text/blocks for written questions — read this, never re-extract from PDFs
├── diagram_audit.json          ← Written-stimulus image audit results — permanent reference
├── audit_*.py / crop_*.py / fix_*.py / update_written_images.py ← audit/crop scripts of record (see docs/HISTORY.md for what each was for)
├── data/
│   └── answer-key/             ← ✅ GROUND TRUTH — official HSC answers, extracted from the NESA
│       │                          marking guidelines. Immutable; never hand-edit — regenerate
│       │                          with scripts/build_answer_key.py. NOT in subjects/
│       │                          (validate_subjects.cjs enumerates that folder).
│       ├── mathematics-advanced.json    ← 60 MC answers, 2020–2025 (added 2026-08-31, Stage 6)
│       ├── mathematics-standard-2.json  ← 90 MC answers, 2020–2025
│       ├── multimedia.json              ← 60 MC answers, 2020–2025
│       └── vet-construction.json        ← 75 MC answers, 2021–2025
│       ├── written/                     ← Official WRITTEN marks + sample answers, same
│       │                                immutability rule. Built by scripts/build_written_key.py,
│       │                                enforced by scripts/check_written_key.cjs. 329 bank
│       │                                questions check against it; only the MARK is enforced —
│       │                                sample answers are prose, stored for human review only.
│       │                                No HMS file: no past papers exist yet.
│                                  All 285 MC answers are enforced in CI and all 285 are
│                                  verifiable — every MC question in all FOUR subjects with
│                                  past papers carries `qNum`.
│   └── mapping-grid/           ← ✅ GROUND TRUTH — NESA's official question→syllabus-code grid
│       │                          (marks + content code + outcome code per question part), from
│       │                          the end of the marking guidelines. Same immutability rule;
│       │                          regenerate with scripts/build_mapping_grid.py, never hand-edit.
│       │                          Use it to DERIVE `category`. It reflects what was EXAMINED, not
│       │                          syllabus SCOPE — the two diverge sharply, so never weight topics
│       │                          from it (see docs/subject-plans/mathematics-advanced.md).
│       │                          ⚠️ REGENERATED 2026-08-28: the extractor bracketed each row by
│       │                          the labels around it, and a Content cell holding 2–3 codes is
│       │                          vertically CENTRED, so its codes leaked into the rows above
│       │                          AND below. 20 rows across the two maths subjects carried a
│       │                          code NESA never assigned. Marks were never wrong, so every
│       │                          paper still reconciled to 100 and nothing flagged it. It now
│       │                          reads the grid's own drawn horizontal rules. If you extend
│       │                          this to a new subject, spot-check a multi-code row against
│       │                          the rendered page — reconciliation cannot catch this class.
│       ├── mathematics-advanced.json  ← 6 papers, 2020–2025, all reconciling to 100 marks
│       │                                with zero uncoded rows. Not yet wired into CI —
│       │                                the subject is not ported.
│       └── mathematics-standard-2.json ← 6 papers. Verified against the LIVE bank: its 16
│                                        `category` codes match the grid's exactly and all 90
│                                        original MC questions agree with NESA's tagging,
│                                        0 disagreements. Multimedia/VET have grids too, but
│                                        theirs name topics in prose, not codes — not parsed.
│                                        The 2026-08-28 corrections here are all Section II,
│                                        so the 90-MC agreement above is unaffected.
│   └── exam-trends/            ← Per-topic study weighting: syllabus SCOPE vs examined MARKS.
│       │                          Built by scripts/build_exam_trends.py from the syllabus DOCX
│       │                          + the mapping grid. Holds scopeShare, examShare, marksPerPaper,
│       │                          yearsPresent, MC/written split, a per-year series, and
│       │                          yieldRatio (examShare ÷ scopeShare).
│       │                          ⚠️ ALWAYS SHOW BOTH AXES. Ranking by marks alone tells a
│       │                          Standard 2 student to skip Data Analysis (13.5% of the
│       │                          syllabus, 3.9% of marks) and an Advanced student to skip
│       │                          Introduction to Differentiation (10.6% / 1.3%) — the Year 11
│       │                          foundation every Year 12 calculus question assumes.
│       ├── mathematics-standard-2.json  ← 16 topics. F5 Annuities: 1.8% of syllabus, 7.3% of
│       │                                  marks (×4.14), 43 of 44 marks written.
│       └── mathematics-advanced.json    ← 14 topics. C3 ×2.96, T3 ×4.03 vs C1 ×0.12.
├── db/
│   └── schema.sql              ← Supabase tables + RLS + triggers (incl. user_progress + entitlement trigger)
├── migrations/
│   └── 2026-07-02_subject_entitlement.sql ← entitlement trigger (already run in Supabase)
├── icons/                      ← PWA icons (icon-192.png, icon-512.png), generated from CramIT_Logo_Transparent.png
├── scripts/                    ← Extraction/audit tooling + registries
│   ├── extract_maths_diagrams.py      ← PDF diagram extractor v3 (PyMuPDF + Pillow + calibration)
│   ├── extract_written_diagrams.py    ← Written-question stimulus extractor
│   ├── validate_subjects.cjs          ← Structural validation for all subject JSON (also runs in CI)
│   ├── build_answer_key.py            ← Extracts official MC answer keys from NESA marking-guideline
│   │                                    PDFs (page 1 only) → data/answer-key/. Run locally; needs the
│   │                                    PDFs, which are NOT in the repo, so CI can never regenerate.
│   ├── check_answer_key.cjs           ← CI: compares original (non-variant) MC answers against the
│   │                                    committed key. Reads no PDFs. Questions without `qNum` are
│   │                                    reported UNVERIFIABLE, never passed silently.
│   ├── build_written_key.py           ← Extracts official WRITTEN marks + sample answers from the
│   │                                    marking guidelines → data/answer-key/written/. Reads the
│   │                                    Marks column POSITIONALLY (x>440) and stops at the answer
│   │                                    heading; a digit regex over the block over-counts. Needs
│   │                                    the local PDFs, so CI can never regenerate it.
│   │                                    ⚠️ Guidelines are selected by `is_guidelines()`, mirroring
│   │                                    build_answer_key.find_papers(): filenames differ per
│   │                                    subject (`-mg.pdf` vs `_marking_guidelines.pdf`), and
│   │                                    `feedback` must be tested FIRST — Multimedia's third PDF
│   │                                    per year is `… HSC Marking Feedback.pdf`, containing both
│   │                                    words. Fixed 2026-08-31; the old `-mg.pdf$` glob silently
│   │                                    excluded Mathematics Advanced entirely.
│   ├── check_written_key.cjs          ← CI: compares each written question's `marks` against the
│   │                                    committed key, aggregating parts (see §10). Reads no PDFs.
│   │                                    Also REPORTS (never fails on) reverse coverage — how
│   │                                    many official leaf parts have a bank entry or a
│   │                                    declared omission — the forward check cannot see a
│   │                                    question that is simply ABSENT. Maths Advanced
│   │                                    234/234, Standard 2 235/235, Multimedia 30/42
│   │                                    (Section III unported), VET 23/76. Those two gaps
│   │                                    are deliberate; promote to a hard assertion if
│   │                                    either is ever closed.
│   ├── build_mapping_grid.py          ← Extracts NESA's official question→syllabus-code Mapping
│   │                                    Grid (marks + content code + outcome code per part) from the
│   │                                    end of the marking guidelines → data/mapping-grid/. This is
│   │                                    how `category` is DERIVED rather than guessed. Refuses to
│   │                                    write unless every paper reconciles to its front-page total
│   │                                    with zero uncoded rows. Two traps in its docstring: the code
│   │                                    can split across words (`MA- M1`), and a row's cell text is
│   │                                    vertically centred so it can start ABOVE its own label line.
│   │                                    NESA's own 2020 Standard 2 grid has a typo (`MS2-F4`),
│   │                                    normalised via an explicit SOURCE_TYPOS table that prints
│   │                                    every substitution — never by loosening the regex.
│   │                                    A THIRD trap, found 2026-08-28: do NOT bracket a row by
│   │                                    the labels around it. A 2–3 code cell is vertically
│   │                                    centred and leaks both ways. row_rules()/band_of() read
│   │                                    the table's own drawn horizontal rules instead.
│   │                                    Needs the local PDFs, so CI can never regenerate it.
│   ├── build_exam_trends.py           ← Joins syllabus SCOPE (dot points per subtopic, from the
│   │                                    syllabus DOCX) to examined MARKS (from the mapping grid)
│   │                                    → data/exam-trends/. This is the measured replacement for
│   │                                    hand-written "exam trends" analyses based on word counts.
│   │                                    Note Section I's last question number differs per subject
│   │                                    (Standard 2 = 15, Advanced = 10) — it's in the config.
│   ├── backfill_qnum.py               ← Proposes `qNum` by matching questions to the exam paper.
│   │                                    Reads Section I by (page, y) — a linear text read
│   │                                    mis-associates questions. Matches ONLY on exact option-set
│   │                                    equality, never a similarity score; reports what it can't
│   │                                    resolve instead of guessing. `--write` refuses unless every
│   │                                    question in the subject resolved. Needs the local PDFs.
│   ├── diagram_registry.json          ← Crop coordinates for MC diagram images
│   ├── crop_vet_2021_q15_options.py   ← One-off: crops VET 2021 Q15's four cross-section
│   │                                    OPTION diagrams. Boxes derived from an ink profile of the
│   │                                    rendered page — on that page the option letters and axis
│   │                                    labels are outline PATHS, so `get_text()` and
│   │                                    `get_drawings()` both miss them. Excludes the paper's own
│   │                                    A./B./… glyph (index.html renders its own label).
│   ├── crop_multimedia_2022_q2_stimulus.py ← One-off: crops the three-star stimulus for
│   │                                    Multimedia 2022 Q2 (see §10 rule 7).
│   ├── crop_maths_advanced.py         ← Mathematics Advanced diagram cropper, `--year {YEAR}`,
│   │                                    one registry block per exam year. Coordinates are PDF
│   │                                    POINTS, not pixels, so RENDER_DPI can change freely.
│   │                                    ⚠️ Deliberately NOT in diagram_registry.json — that
│   │                                    registry is pixels-at-150-dpi and a bare run re-cuts
│   │                                    every Standard 2 crop. Option letters are outline paths
│   │                                    here and the graph runs UNDER the letter, so the letter
│   │                                    is removed with a white `erase` rect, never an x-cut.
│   ├── written_diagram_registry.json  ← Crop registry for written stimulus images
│   ├── process_maths_backlog.js       ← Backlog processor for question generation
│   └── archive/                       ← Completed one-off migration scripts (kept for reference)
├── diagrams/                   ← Exam diagram images — served by Cloudflare Pages at /diagrams/
│   ├── .gitignore              ← Excludes _debug/ folder from git
│   └── {subject}_{year}_Q{n}_{suffix}.jpg|png  (suffix = stimulus | A | B | C | D)
├── subjects/                   ← ✅ All question data lives here (one JSON per subject)
│   ├── index.json              ← List of subject files (⚠️ informational only — the app hardcodes subjects in SUBJECT_ID_MAP/SUBJECT_CATALOGUE)
│   ├── mathematics-standard-2.json    ← 318 MC + 151 written + 73 tips + studyNotes (all 16 topics, alphabetically ordered A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5; no writingScaffolds — see docs/HISTORY.md)
│   ├── health-movement-science.json    ← 193 MC + 40 written + studyNotes (9 topics, block-ordered content + 84 revision questions) + writingScaffolds (3 mark-band scaffolds) — prototype content for the Study Mode/Exam Mode front page (index.html, HMS only, see §11)
│   ├── mathematics-advanced.json      ← 🔶 PORT IN PROGRESS (Stage 4 COMPLETE — all 6 papers;
│   │                                    Stage 6 next). 2020–2025: 60 MC + 126 written +
│   │                                    5 omittedQuestions + 12 omittedParts, 124 crops.
│   │                                    Registered NOWHERE in code until Stage 7 — no
│   │                                    index.json row, no SUBJECT_ID_MAP, no catalogue
│   │                                    entry, no card. validate_subjects.cjs still covers
│   │                                    it (it globs subjects/*.json). One bank entry per
│   │                                    NESA question. Round-trips byte-for-byte through
│   │                                    json.dumps(indent=2, ensure_ascii=False)+newline.
│   │                                    ⚠️ Every inline <img> in a written stem carries its
│   │                                    own style="max-width:100%..." — there is no
│   │                                    .q-text img rule, so an unstyled one is silently
│   │                                    clipped (see §10 and docs/HISTORY.md 2026-08-29).
│   │                                    Runbook: docs/subject-plans/mathematics-advanced.md
│   ├── multimedia.json                ← 60 MC + 29 written
│   └── vet-construction.json          ← 75 MC + 23 written
├── docs/
│   ├── HISTORY.md              ← Full session log — read on demand, not auto-loaded
│   ├── agents-plan.md          ← Stage 9 agent roster/build order — read on demand
│   ├── subject-plans/          ← Port RUNBOOK, one per in-flight port — the single entry point a
│   │   │                          fresh session opens. One stage per session, every established
│   │   │                          fact carried forward so a cold session never re-derives them.
│   │   ├── mathematics-advanced.md  ← Stages 0 + 2 done; 1, 3–7 open with gates, traps, commands
│   │   │                              and a paste-in session prompt. 294 question parts to port.
│   │   └── multimedia-section-iii.md ← ⬜ PLANNED, scheduled AFTER Maths Advanced Stage 7.
│   │                                  Multimedia's one remaining hole: Section III (Q16),
│   │                                  never ported, 12 parts / 90 marks / 2020–2025. Not a
│   │                                  new subject port — starts at Stage 1, since Stages 0/2/3
│   │                                  don't re-run for a live subject. Ground truth already
│   │                                  committed (Stage 6, 2026-08-31), so the marks cannot go
│   │                                  wrong. ⚠️ The one real risk is whether mark-written.js
│   │                                  handles a 10–12 mark band-marked response — resolve at
│   │                                  Stage 1, not mid-port.
│   ├── porting-playbook.md     ← MANDATORY read before adding any new subject — the 9-stage
│   │                             pipeline (feasibility → survey → syllabus → schema → port →
│   │                             assets → ground truth → release → operate), each with a gate,
│   │                             plus the canonical field names and how it scales to the agents
│   └── paper-reports/          ← Stage 0 Fit Reports + Content Agent triage reports — briefing docs for porting new subjects.
│       └── mathematics-advanced.md  ← First file ever written here (2026-08-27): Stage 0 verdict = GO.
│                                  Human Stage 0 writes ONE subject-level report ({subject}.md) with per-year
│                                  rows; the per-paper {subject}-{year}.md shape is the Content Agent's, since
│                                  triagePaper() runs once per paper. The agent has still never run.
└── functions/                  ← Cloudflare Pages Functions — served at /{name} (NOT /functions/{name})
    ├── _lib/auth.js            ← Shared JWT verification + CORS allowlist (underscore = not routed)
    ├── create-checkout.js      ← POST /create-checkout — creates Stripe Checkout Session (JWT required)
    ├── update-subscription.js  ← POST /update-subscription — syncs Stripe with the caller's subject count (JWT required)
    ├── customer-portal.js      ← POST /customer-portal — opens the caller's Stripe billing portal (JWT required)
    └── mark-written.js         ← POST /mark-written — AI marking via Claude API (JWT required)
```

NOT in the repo (removed or never existed, kept out intentionally): `sw.js` (service worker disabled), `billing.js` (deleted — was dead code), `subject-selector.html`, `functions/upgrade-flex.js` (deleted — unauthenticated Stripe mutation), `subjects/mathematics-advanced-2024.json` (deleted — old agent schema, unloadable by the app).

**Branch structure (planned, only `main` exists today):**
```
main          → cramit-quiz.pages.dev         (LIVE — students, protected, PR required)
staging       → staging.cramit-quiz.pages.dev  (TEST — you only, agents can self-merge)
agent/*       → auto-preview URLs              (AGENT SANDBOX — agents commit here first)
```
**Rule: No agent ever commits directly to main. All agent commits go to `agent/*` branch → PR → staging → main.** See `docs/agents-plan.md` for the full release pipeline.

---

## 7. Current Subjects

| Subject | Quiz Key | Subject ID | Type | Questions | Standalone reference file |
|---|---|---|---|---|---|
| Mathematics Standard 2 | `maths` | `mathematics-standard-2` | MC + written | 90 HSC + 318 extended (variants), 151 written | ✅ `2020-25 HSC Maths Quiz v5.4 (...).html` |
| Health & Movement Science (HMS) | `hms` | `pdhpe-hms` *(billing id; file is `health-movement-science.json`)* | MC + written | 193 MC, 40 written | ✅ `CLAUDE.AI - HMS_In_Depth_Study_YR12_quiz.html` |
| VET Construction | `vet` | `vet-construction` | MC + written | 75 MC, 23 written, 2021–2025 | ✅ `VET_Construction_Quiz_v6 (...).html` |
| Industrial Technology — Multimedia | `multimedia` | `multimedia` | MC + written | 60 MC, 29 written, 2020–2025 | ✅ `CLAUDE.AI - HSC_Multimedia_Quiz (...).html` |

⚠️ **HMS is a new subject for 2026**, superseding PDHPE, and **2026 is its first HSC exam year** — so there are **no historical HMS past papers** and none until after the 2026 HSC. PDHPE (2020–2024) is a reference point with real content overlap, but is a different exam — see the citation rule in §10 before attributing anything. The subject **file** is now `subjects/health-movement-science.json`, but `pdhpe-hms` survives as the **billing/entitlement id** (`SUBJECT_CATALOGUE[].id`, written to Supabase `subject_selections.subject_id`), as the subject-artwork SVG key and reverse id→quizKey map keyed off it, and as the prefix on the 15 `/diagrams/pdhpe-hms_*` images. Renaming the billing id requires a migration against live user rows (`UPDATE subject_selections SET subject_id=…`) or every existing subscriber loses HMS access — owner's decision, not a tidy-up. Note `SUBJECT_ID_MAP` (which builds the JSON fetch URL) and `SUBJECT_CATALOGUE[].id` (billing) are **separate** and no longer share a value.

**Standalone HTML files are the source of truth for question data** when first porting a subject — extract `mcQuestions[]`/`writtenQuestions[]`, never rewrite from scratch.

**NESA exam PDFs** (NOT committed to GitHub — copyright) live locally at `C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\`, one subfolder per subject, papers + marking guidelines (`-mg` suffix).

**More subjects planned:** Mathematics Advanced, English Advanced/Standard, Biology, Chemistry, Physics, Legal Studies, Business Studies, Economics.

---

## 8. Pricing Model

| Subjects Selected | Plan | Monthly Price |
|---|---|---|
| 1 | Free (trial) | $0 |
| 2 | Base | $7.99 |
| 3 | Base + 1 Extra | $10.98 |
| 4 | Base + 2 Extra | $13.97 |
| 5 | Base + 3 Extra | $16.96 |
| 6 | Base + 4 Extra (`base_plus`) | $19.95 — stays base_plus; Unlimited would cost MORE at $19.99, so no forced upgrade |
| 7 | Unlimited | $19.99 |
| 8+ | Flex (Unlimited + $2.99/subject above 7) | $22.98+ |

**Critical rules:**
- The 7th subject is effectively free (price plateaus at 6-subject price then rounds to Unlimited)
- Students on Unlimited can swap subjects freely — price stays $19.99
- Never change pricing without updating: `pricing_config` table, `create-checkout.js`, `update-subscription.js`, AND creating new Stripe Price objects. (`billing.js` no longer exists — do not recreate it.)

**10-question trial** (replaces the old permanent 1-subject free tier): counter in `localStorage` keyed by subject ID (`cramit_trial_{subjectId}`), increments once per question index per session in `nextQuestion()`. After 10: trial wall with score + subject-specific unlock CTA. Picker locks year filters/categories/Extended 318/Test Mode/Written Response during trial. Stats only persist for logged-in users.

---

## 9. Key Code Patterns — Always Follow These

### Cloudflare Pages Function (ESM only, `env.VAR` not `process.env.VAR`)
```js
import Stripe from 'stripe';
import { corsHeaders, requireUser, unauthorized } from './_lib/auth.js';

export async function onRequestOptions(context) {
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const CORS = corsHeaders(request);
  const user = await requireUser(request, env);   // verified Supabase JWT — never trust the body
  if (!user) return unauthorized(CORS);
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);
  const body = await request.json();
  // ... business logic, using user.id — not anything from body ...
  return new Response(JSON.stringify(result), { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } });
}
```

⚠️ **Critical Cloudflare routing rule:** `functions/create-checkout.js` is served at `/create-checkout` — NOT `/functions/create-checkout`, NOT `/.netlify/functions/...` (Netlify is gone). The `functions/` folder name is invisible in the URL.

⚠️ **All 5 functions require a Supabase JWT.** The client sends it via `authHeaders()` (below); a function never trusts `user_id`/`customer_id`/`subscription_id` from the request body — that identity comes only from `requireUser()`.

⚠️ **Other Cloudflare gotchas:** no `wrangler.toml` (blocks the dashboard from managing secrets on a git-connected Pages project — delete if it reappears); build command must be `npm install` so `stripe` gets installed before functions compile; when doing find-replace on `index.html` in PowerShell 5.1, always use `[System.IO.File]::ReadAllText(path, UTF8NoBOM)`/`WriteAllText` — never `Get-Content | Set-Content`, it corrupts UTF-8.

### Client-side auth header helper (index.html)
```js
async function authHeaders() {
  // Races getSession() against a timeout — Supabase's cross-tab lock
  // (navigator.locks) can hang indefinitely with a stale lock.
  const result = await Promise.race([
    sbClient.auth.getSession(),
    new Promise(resolve => setTimeout(() => resolve(null), 4000)),
  ]);
  const token = result?.data?.session?.access_token;
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}
// Usage: fetch('/mark-written', { headers: { 'Content-Type': 'application/json', ...(await authHeaders()) }, ... })
```

### Supabase client init
```js
// Loaded via <script src="/supabase.min.js"> in <head>. Init once on DOMContentLoaded.
// Always use sbClient — never new createClient(...) a second time.
const { data, error } = await sbClient.from('profiles').select('*');
```

### Google OAuth redirect
```js
const APP_URL = 'https://cramit-quiz.pages.dev'; // always this constant, never window.location.origin
sbClient.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: APP_URL } });
```

### Subject access check
```js
function canAccess(subjectId) {
  if (canAccessViaSubscription(subjectId)) return true;
  return !isTrialExhausted(subjectId); // trial works even when logged out
}
```

### Subject data loading (index.html)
```js
// subjectCache persists in memory for the session. loadSubjectData(key) fetches
// /subjects/{id}.json once, caches it, and patches SUBJECTS[key].categories/topics.
// SUBJECTS[key].getMC(filters)/.getWritten(filters) always read from subjectCache[key].
// getMasterArray(subjectKey, mode) returns the UNFILTERED array — indexOf() on it
// gives a shuffle/filter-safe stable ID used for progress tracking.
```

### CSS variables (warm earth-tone design system — never change these)
```css
:root {
  --bg: #FAF8F5; --surface: #FFFFFF; --surface2: #F2EFE9; --border: #E0D9CF;
  --accent: #C17D3C;  /* amber */  --accent2: #7B9E6B; /* green */  --accent3: #5B7FA6; /* blue */
  --text: #2C2420; --muted: #8C7B6E; --radius: 16px;
  --font-display: 'Syne', sans-serif; --font-body: 'DM Sans', sans-serif;
}
```

### Preserve when touching index.html
The warm earth-tone tokens above; `initSupabase()`, `loadUserState()`, `canAccess()`, and billing modal code (don't touch without deliberate reason); the subject-card routing logic; the PWA manifest.

---

## 10. Question Data Reference

### MC question object
```js
{
  year: 2024, category: 'F2', variant: true, // omit variant for original HSC questions
  q: "Question text here.",
  image: "/diagrams/mathematics-standard-2_2024_Q6_stimulus.jpg", // stimulus above question, omit if none
  optionImages: [ "/diagrams/..._A.jpg", "..._B.jpg", "..._C.jpg", "..._D.jpg" ], // per-option images, omit if text options
  optionImagesWide: true, // Keeps option images one-per-row instead of in the 2×2 grid, where they
                          // shrink to ~160px wide on a 430px phone. ⚠️ The test is the RENDERED
                          // HEIGHT, not the aspect ratio: a 2.94:1 crop (Maths Advanced 2021 Q4)
                          // renders 160×54px in the grid vs 360×122px one-per-row. Render the set
                          // at 430px and read the height off the DOM before deciding.
  options: ["Option A", "Option B", "Option C", "Option D"], // required even with optionImages (results screen, accessibility, shuffle)
  answer: 2, // 0-indexed, into options[] before shuffle
  solution: `<div class="step"><span class="step-number">1.</span> Step one.</div>...`
}
```
Written questions add: `type: 'written'`, `marks`, `keywords: [...]`, `modelAnswer` (stored as `answer` on most files — the renderer checks `q.answer || q.modelAnswer || q.sampleAnswer`).

### Image paths
```
/diagrams/{subject}_{year}_Q{n}_stimulus.jpg   ← question diagram
/diagrams/{subject}_{year}_Q{n}_A.jpg  _B.jpg  _C.jpg  _D.jpg   ← per-option
```
Do NOT use Supabase Storage for diagrams (retired `exam-images` bucket) or the old `MATHS_IMG` lookup table (retired).

### Subject JSON file shape
```json
{ "id": "mathematics-standard-2", "name": "Mathematics Standard 2", "icon": "📐", "accentColor": "#C17D3C",
  "mcQuestions": [ /* MC objects */ ], "writtenQuestions": [ /* written objects */ ], "tips": { /* Formula Hint data, Maths only */ } }
```
**Study Mode & Exam Mode (HMS full, Maths pilot — see §11):** `health-movement-science.json` (9 topics) and `mathematics-standard-2.json` (1 topic so far, F1) have `studyNotes: [ { id, icon, title, focusArea, accentColor, blocks: [...], revisionQuestions: [{q, a}] } ]` (`focusArea` is HMS-only metadata, unused by the renderer — safe to omit) and, optionally, `writingScaffolds: [ { id, label, introNote, steps: [{heading, html}], modelAnswerLabel, modelAnswer } ]` (Maths has none yet — `renderWritingHelpHtml()` shows an empty-state message when absent, no engine change needed). The engine (`renderStudyBlock()`, `hasStudy` flag) is fully subject-agnostic — enabling Study Mode for a new subject is just adding the `studyNotes` key to its JSON and `hasStudy: true` to its entry in `index.html`'s `SUBJECTS` object. `blocks[]` is an **ordered** sequence preserving the source content's exact layout — each entry is `{type:'noteGrid', boxes:[{heading,html}]}` (1 or 2 boxes; 2 renders as a side-by-side 2-column pair), `{type:'image'|'imageGrid', ...}` (image objects carry `src`/`alt`/`title`/`caption`/`style` — `style` preserves any inline sizing like `max-height` so paired images stay visually uniform), `{type:'table', caption, headers, rows}` (rendered as `.study-dtable`, a mobile-responsive stacked-card table reusing the pattern from `olivier-hms-exam-prep.html`'s `.dtable`), `{type:'examTip'|'linkIt', ...}`. Rendered by `index.html`'s `renderPicker()`, which shows a Study Mode/Exam Mode segmented-control toggle (`.seg-control`, reusing the same component as the Year/Category/Assessment filters — not a bespoke button style) as the front page for any subject with `hasStudy: true`; Exam Mode is exactly today's existing quiz picker (`renderExamModeHtml()`), unchanged. Study Mode has its own nested Notes/Writing Help toggle. Gating is a free-preview model, not the usual all-or-nothing trial lock: `STUDY_FREE_TOPIC_COUNT` (currently 1) topics are always free, the rest show locked with a 🔒 and no body HTML rendered into the DOM; Writing Help is fully gated. `validate_subjects.cjs` ignores these keys (permissive of unknown top-level keys) — no validator changes were needed.

### Study Mode topic lists — mandatory syllabus check (never skip this)
Before finalizing a Study Mode topic list for any subject (new or expanded), the actual **official NESA syllabus/curriculum-framework document** must be located and read — not just marking-guideline mapping grids, and never just keyword-matching the existing question bank. This is a hard rule, established after two incidents (Multimedia, then VET Construction) where a mapping-grid-only topic list was presented as "syllabus-grounded" and turned out incomplete or mis-proportioned when the primary source was actually checked — VET Construction's "Working in the industry" focus area has 80 rows of official scope-of-learning content vs Safety's 48 (nearly double), and includes content (cultural diversity, anti-discrimination) that has never appeared in any exam question — invisible to mapping-grid analysis, which only reflects exam history, not full syllabus scope.
1. Search for the syllabus PDF/DOCX (`site:educationstandards.nsw.edu.au` or `site:nsw.gov.au` — NESA has moved syllabus hosting to nsw.gov.au for some subjects; old links 301-redirect). Check `NESA Exams Folder/{subject}/` first, but expect it's usually not pre-saved (only past papers + marking guidelines tend to be).
2. Ask the user for explicit permission before downloading it, then save into `NESA Exams Folder/{subject}/` alongside the past papers (same copyright treatment — not committed to GitHub).
3. Read the actual content. For DOCX syllabus files, `pandoc` was unavailable in this environment; `python3 -c "import docx"` (python-docx) worked — extract both `document.paragraphs` and `document.tables`, since NESA's VET syllabus template puts the substantive "scope of learning" content in tables, not paragraphs.
4. Marking-guideline mapping grids (§ below) are still useful as a secondary cross-check — they show which parts of the syllabus actually get examined and at what weight — but the syllabus document's own section structure and content density should drive the final topic list and proportions, not exam history.
5. State plainly whether a topic list is drawn from the primary syllabus source or a secondary proxy — never present a mapping-grid- or keyword-derived list as syllabus-grounded.

### Written question stimulus text — never re-extract from PDFs
All NESA PDF text/block positions for written questions are pre-extracted into `written_q_extracts.json` (repo root). **Always read this file first** — re-extracting from a PDF wastes tokens every session. Content rule: plain text → `q` field; diagram → `<img>` tag embedded inline in `q`, `image` field set `null`; table → `<table>` HTML reconstructed from the extract data; no SVGs, always crop from the PDF as JPG.

⚠️ **An inline `<img>` inside a `q` stem needs its own `max-width` — there is no CSS rule for it.** `index.html` has **no `.q-text img` rule**; the only `max-width` on a question image is `.device-phone .q-image-wrap img`, which governs the separate `image` field, not an `<img>` written inside `q` — which is how *every* written-question diagram in this project is embedded. An unstyled stem image renders at its natural crop width (measured: **1767px inside a 390px stem**) and `body { overflow-x: hidden }` swallows the overflow rather than scrolling it. **Nothing reports this** — `body.scrollWidth` still reads 430, `validate_subjects.cjs` only existence-checks the path, and no console error fires; the diagram is simply cut off on the right. Always write `<img src="…" alt="…" style="max-width:100%;height:auto;display:block;margin:14px auto">`, as Mathematics Standard 2 does on all 71 of its stem images. The check that catches it is per-question, not page-level: `[...document.querySelectorAll('.question-area')].filter(a => a.scrollWidth > a.clientWidth + 1)` must be empty at a 430px viewport. Found 2026-08-29, on nine Mathematics Advanced 2021 questions.

⚠️ **A question table with 7+ columns is clipped on a phone unless it is wrapped.** Question stems render their tables as `.q-table` or `.nesa-table` — **not** Study Mode's `.study-dtable`, which the question renderer never applies — and neither of those collapses to stacked cards *or* scrolls. Measured at a 430px viewport (stem width 390px): a 6-column table fits; an 8-column table renders 513px, and because `body` sets `overflow-x: hidden` its right-hand columns are **silently clipped** — no scrollbar, no error, just missing data. Wrap it: `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0"><table class="q-table" style="min-width:520px;margin:0">…</table></div>`. Lookup tables (future value, z-scores) are where this bites.

### Exam citations — verify against the actual paper, never a third-party claim
Never label a question with an HSC/NESA citation (year, section, question number, marks) on the strength of a workbook, textbook or tutoring handout. Papers are local at `NESA Exams Folder/{subject}/` and have real text layers (`python -c "import fitz"` extracts them; only the photographed workbooks are image-only). Open the paper and confirm **all four** of section, question number, marks and wording. If any don't match, drop the citation — the question is still fine as ordinary practice content. Never restate a third-party source's provenance claim as verified fact in `docs/HISTORY.md` or a commit message. This rule exists because a session shipped a question labelled "HSC 2024, PDHPE Exam, Section I, Part B, Q31.b" that was wrong on section (really Section II), marks (12, not 8) and wording — see `docs/HISTORY.md`, 2026-08-25.

### HSC answers are ground truth in `data/answer-key/` — never re-derive them by reading
Official HSC answers never change, so they are derived **once**, committed, and enforced by CI
(`scripts/check_answer_key.cjs`, wired into `validate.yml`). Do **not** "audit the answers" by
reading a marking guideline again — that has been attempted repeatedly and produced a *different
result every time*, including a clean bill of health for a bank that had five wrong answers
(see `docs/HISTORY.md`, 2026-08-26). **All 225 answers across the three subjects with past
papers are now committed, carry `qNum`, and pass** — Maths 90, Multimedia 60, VET 75.

Rules:
1. **Never assume array position equals question number.** Multimedia 2022 stores its ten
   questions in the order 1, 3, 4, 5, 6, 8, 9, 10, 7, 2. A positional join produced six phantom
   "errors" in one pass and a different six in the next. Join on `qNum` or not at all. Every
   *other* year in every subject happens to be in paper order, which is exactly what makes
   position such a tempting and dangerous shortcut.
2. **A question with no `qNum` is unverifiable, not correct.** None are outstanding today, but
   a newly ported subject arrives without `qNum` and is in that state until one is derived.
   `python scripts/backfill_qnum.py <subject-id>` proposes them, matching **only** on exact
   option-set equality and reporting the rest for a human — it never guesses.
3. **Fuzzy text-matching against the exam PDFs is not a join.** NESA's text layers are uneven
   (2020 p4 renders Q7's stem as `mul\ntip\nle graphs`); every fuzzy build mis-aligned questions
   while reporting high confidence. Where a check genuinely needs the paper, **render the page to
   an image and read it** — that works where the text layer does not. Two structural traps when
   reading a paper at all: the question number sits in its own left-margin text column, so a
   linear `get_text()` emits every number on a page before any body text (read by *(page, y)*);
   and the page footer / copyright line lands under the last option, so it gets swallowed into
   option D unless filtered.
4. **The answer key is regenerated only when new papers arrive**, via
   `python scripts/build_answer_key.py <subject-id>`. It parses page 1 of the marking guidelines
   and nothing else. CI cannot regenerate it (the PDFs are not in the repo, by copyright) — which
   is precisely why the generated file is committed.
5. **Deliberate omissions must be recorded, not silently absent.** A question part dropped because
   the engine can't mark it (e.g. graph-drawing) gets an `omittedParts` entry on the question —
   otherwise the paper's marks quietly fail to total 100, as 2020 did at 84/85 for over a year.
6. **A passing check does not mean the options are right.** The official letter indexes the
   *paper's* option order, so reordered options would be compared against the wrong letter — and
   option *text* is invisible to the check entirely. Both have failed for real. Where a question's
   options are images, whoever ported it sometimes invented descriptive labels and got them wrong:
   VET 2022 Q13 called a spade bit "Y - masonry bit", VET 2021 Q15 called a north-to-south slope
   "Flat", Multimedia 2021 Q1 listed "Helvetica"/"Calibri" where the paper prints "Comic Sans"/
   "Century Gothic", and Maths 2025 Q2/Q8 had option labels paired with the wrong image. A student
   is then marked correct against a description of the wrong picture. When touching a question with
   an `image` or `optionImages`, open the paper **and** the committed crop and compare the options
   one by one. Prefer the paper's own wording — if it prints bare `W / X / Y / Z` and the crop
   carries those labels, the options are `W / X / Y / Z`, not invented descriptions.
7. **A question with no image at all can still be an image question.** Where a paper's
   stimulus was never cropped, a port has sometimes *described* the missing picture in the
   stem or options instead — and the description can be wrong while the answer stays right,
   so the check passes and the question is still unanswerable. Multimedia 2022 Q2 described
   three star shapes as `outline star / filled circle / filled star` when the paper prints a
   filled star with no outline, an unfilled star with one, and a filled star with one: a
   student reasoning correctly from that text picks A and is marked wrong against the correct
   key answer D. Finding these needs a **stem sweep** ("which of the following best
   represents/shows…"), not an option sweep — bare-letter options miss them entirely, because
   the giveaway is prose standing in for a picture. Crop the stimulus and restore the paper's
   own wording rather than improving the description.
8. **Written marks are ground truth too, in `data/answer-key/written/`.** Built by
   `python scripts/build_written_key.py <subject-id>`, enforced by
   `node scripts/check_written_key.cjs`. **329 questions across the four subjects with past
   papers pass; HMS is excluded and stays excluded until after the 2026 HSC.** Only the *mark*
   is enforced — the official sample answer is committed alongside it for human review, but
   prose cannot be compared for equality (and Maths sample answers extract as mangled equation
   layout). Three things to know before touching it:
   - **Join by aggregating to the question, never part-for-part.** The bank stores parts as
     `16` (one entry for all parts), `"23(a)"` (one per part) and `"19(b)(i)"` (one per
     sub-part), and 2020/2021 Maths split questions that 2022–2025 merge. A bank entry's
     expected marks are the **sum of every official leaf part whose path starts with its
     path**, plus any `omittedParts`. That one rule reconciles all three storage shapes.
   - ⚠️ **The check is one-directional and cannot see an ABSENT question.** It compares
     bank entries against the key, so a question missing from the bank entirely produces no
     finding — the failure that left 2020 Standard 2 at 84/85 for a year. Since 2026-08-31 it
     also **reports** reverse coverage (official leaf parts claimed by a bank entry or a
     declared omission) but does **not** fail on it, because Multimedia's Section III (30/42)
     and VET's partial written port (23/76) are deliberate, documented gaps. Maths Advanced is
     234/234 and Standard 2 235/235; if a gap is ever closed, make it a hard assertion.
   - **A whole question the engine can't present is declared in subject-level
     `omittedQuestions`**, the companion to per-question `omittedParts` — e.g. Multimedia
     2021 Q12, which asks the student to *draw* a waveform. The checker validates each
     declaration (must exist in the key, marks must match, must not also be in the bank), so
     it can't rot into an empty excuse.
   - **The extractor reads the Marks column positionally and stops at the answer heading.** A
     digit regex over the block over-counts (2020 Maths reads 117 against a true 85). Watch
     the three traps that each broke a real paper: `Answers could include:` is the other
     spelling of `Sample answer:`; extended-response criteria use mark *ranges* whose text
     layer splits mid-number (`9–1` + `0`); and page furniture must be filtered from the
     criteria scan, not just the answer text, or `Page 18 of 23` becomes a 23-mark question.
     Reconcile every paper against the section totals printed on the exam's own front page —
     Maths 85, Multimedia 30, VET 65 — an independent check, not a self-consistent one.

⚠️ **HMS has no past papers, and cannot have any yet.** Health and Movement Science is a **new subject for 2026**, superseding PDHPE — **2026 is the first year it is examined**, so no historical HMS HSC paper exists. `NESA Exams Folder/Health and Movement Science/` holds only NESA's **sample** materials (`HMS SAMPLE HSC PAPER 2026.pdf`, `health-and-movement-science-11-12-2023-annotated-sample-examination-materials.pdf`) plus study resources — no past papers, and none to come until after the 2026 HSC. **PDHPE (2020–2024, in `NESA Exams Folder/PDHE/`) is a legitimate reference point with real content overlap, but a PDHPE question is not an HMS question:** cite it explicitly as PDHPE with its year, never as HMS, and never imply an HMS exam precedent that doesn't exist. The same applies to the Content Agent — there is no HMS paper for it to discover. (Legacy naming: the subject id is still `pdhpe-hms` and §7 still lists it as "PDHPE — HMS Depth Study", from when this content was a PDHPE depth study. The id is load-bearing across `subjects/`, `index.html` and `/diagrams/` filenames — don't rename it casually.)

### Editing an existing Study Mode topic — diff before you insert
An accuracy audit is not an editorial review. Verifying every claim against a source says nothing about whether the same claim already appears three blocks earlier. **Before inserting a block into an existing topic, diff it against its neighbours** — if the content is already there in prose, either don't add the block or remove the prose, never both. Then render the topic and *read* it end-to-end; asserting blocks are non-empty and throw no exceptions is not reading it. Assign each fact to the block whose syllabus dot point owns it and state it once (deliberate reinforcement, e.g. in the exam tip, is fine when it's a conscious choice). Scripted duplicate-count assertions on key phrases are cheap and catch what eyeballing misses.

⚠️ **`scripts/validate_subjects.cjs` only existence-checks images referenced by questions** (`image`/`optionImages`) — `studyNotes` block images are **not** covered, so a broken study-image path passes validation silently and `imageRefs` won't move when you add one. Study images must be browser-verified. Related gotcha: study images render with `loading="lazy"`, so `naturalWidth` reads 0 while the Browser pane is hidden — force `loading='eager'` before asserting they loaded.

### Adding a new subject

> ⚠️ **Read [`docs/porting-playbook.md`](docs/porting-playbook.md) first — it is mandatory, and the five steps below are only its last stage.** The playbook is the full SDLC: feasibility (GO/NO-GO — not every HSC subject fits this engine, and the answer for Extension Maths is likely no), per-question survey, syllabus grounding, canonical schema, port, assets, ground truth, release, and ongoing operation — each with a gate. It also records the **canonical field names**: the four existing subjects drifted apart (`marks` vs `maxMark`, `category` vs `topic`, `solution` vs `optionExplanations`), the engine absorbed it in fallback chains, and it cost a live bug — HMS written questions rendered no marks badge at all until 2026-08-27. A new port uses canonical names; existing deviations are debt, not precedent.

1. Create `subjects/{subject-id}.json` following the shape above.
2. Add the filename to `subjects/index.json` (informational — the app itself still hardcodes the subject in `SUBJECT_ID_MAP`/`SUBJECT_CATALOGUE` in `index.html`, so add it there too).
3. Add a subject card to `index.html`.
4. Run `node scripts/validate_subjects.cjs` before committing.
5. Commit and push — Cloudflare Pages deploys within ~60 seconds.

---

## 11. Current State, Known Issues & Roadmap

**Quiz engine feature parity is complete** — practice/test mode, step-by-step solutions, category/topic filters, HSC 90/Extended 318 toggle, option shuffle, results breakdown, written response + AI marking. Full history of how each stage was built is in `docs/HISTORY.md`.

### Known issues (still open)
| Issue | Notes |
|---|---|
| **Content Agent has never run for real** | Rebuilt 2026-07-04 (correct app schema, triage phase, PR-only) but blocked on the `ANTHROPIC_API_KEY` GitHub Secret. First run should be manual via the workflow_dispatch button, with the PR reviewed carefully. Offline selftest passes. |
| Content Agent handles MC only | Written-question generation deferred — triage reports flag written counts for human follow-up. Diagram questions always skipped (need the Python crop tooling). |
| `mark-written.js` never logs to a `written_submissions` table | Table doesn't exist yet either (see §5 agent coordination tables). |
| Stripe is in Sandbox/test mode | Switch to live before public launch — new Price objects + secret rotation. |
| Google OAuth is in Testing mode | Submit for verification before public launch. |
| Blueprint V4 may still reference Netlify | Migrated to Cloudflare Pages May 2026 — verify/update via `/docx` skill when next editing it. |
| VET Construction's 27 tool/PPE icons need a Flaticon attribution credit somewhere in the app | Free licence requires one visible credit line for author `juicy_fish` (not per-icon) — covers the whole set. No "About"/"Credits" screen exists yet to host it; placement is a UI/brand decision, not picked unilaterally. Not urgent (the free licence is valid to use right now without it being placed yet), but should be resolved before public launch. |

### Pre-launch checklist
| # | Task | Notes |
|---|---|---|
| 1 | Test full payment flow end-to-end | Stripe sandbox, card `4242 4242 4242 4242`: trial → subscribe → add subject → remove subject → cancel |
| 2 | Set `ANTHROPIC_API_KEY` in GitHub Secrets | Agent rebuilt — this is now the only blocker; then trigger content-agent.yml manually once and review the PR |
| 3 | Submit Google OAuth for verification | Google Console |
| 4 | Add custom domain `cramit.com.au` | Cloudflare Pages → Custom domains; also update `APP_URL` in index.html, `_lib/auth.js` origin allowlist, and Supabase redirect URLs |
| 5 | Switch Stripe to live mode | New live Price objects; update `create-checkout.js` + `update-subscription.js` |
| 6 | Create staging Supabase project + `staging` branch + branch protection | Required before any agent goes live — see `docs/agents-plan.md` |

### Roadmap
| What | Status |
|---|---|
| Core quiz engine (all 4 subjects, MC + written, AI marking) | ✅ Done |
| Cross-device progress sync (`user_progress`) | ✅ Done |
| Cloudflare Function auth + subject entitlement DB enforcement | ✅ Done |
| Multimedia/HMS "Extended" variant question generation | ⬜ Pending — decision + rules in `docs/HISTORY.md` |
| Study Mode & Exam Mode front page (HMS prototype + Maths complete) | 🔶 HMS built 2026-07-26 (full — diagrams, comparison tables, 74 revision questions, free-preview gating). Maths started and finished 2026-07-28 — all 16 syllabus categories done, built one topic at a time by owner's explicit preference, then reordered alphabetically A-first (A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5; original-wording notes since Maths has no standalone prose source to port from, unlike HMS) — see docs/HISTORY.md for per-topic detail. ⚠️ The free-preview topic (`STUDY_FREE_TOPIC_COUNT`, gates by array position) shifted from F1 to **A1** as a side-effect of the reorder. No Notes/Writing Help toggle for Maths at all (hidden when `writingScaffolds` is empty — data-driven, HMS unaffected). **Multimedia complete 2026-07-29** (all 7 Study Mode topics built, see `docs/HISTORY.md`): topic list re-grounded in the real NESA syllabus (pulled all 6 years of official marking-guideline mapping grids, not just keyword-matched against the exam bank) — Text & Document Design, Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics, all ✅ (47 blocks, 42 revision questions total). Scope is deliberately Sections I & II content only (matches the existing 89-question bank); Section III (15 marks/exam, rotating business/industry themes — WHS, environmental factors, industrial relations, automation, etc. — never ported into the bank) is a known, deferred gap, same treatment as the Content Agent's written-question-generation gap. **Section III now has its own runbook, `docs/subject-plans/multimedia-section-iii.md`, scheduled AFTER Mathematics Advanced Stage 7** (owner decision, 2026-09-01 — supersedes the 2026-07-29 "after VET Study Mode" sequencing, whose precondition was met 2026-07-30): would add an 8th Study Mode topic plus new written questions (Section III has no existing bank content to build from, unlike topics 1–7). Writing Help — a single "Short Answer — 1–5 marks" scaffold (not HMS's two-tier split), since the in-scope written bank tops out at 5 marks — is a separate, smaller follow-up, **not built yet**. No standalone prose source exists (original authoring, like Maths); the 89-question bank has no `category`/`topic` field, so topics were defined from the syllabus, not filtered from existing data. **VET Study Mode complete 2026-07-30** (all 9 topics built in two sessions — topic 1 alone, then topics 2–9 in one continuous pass after the owner said "continue until complete"; see `docs/HISTORY.md` for full per-topic detail): Safety split into 2 topics (WHS & Risk Management; Safe Work Practices & Emergencies), Skills in Construction into 2 (Plans/Drawings/Specifications; Measurements & Calculations), Tools of the Trade into 2 (Hand & Power Tools; Tool Selection/Safety/Care/Security), Working in the Industry into 3 (Industry Structure/Careers/Employment; Work Instructions/Teamwork/Workplace Conduct — includes cultural diversity/anti-discrimination content that has **never appeared in any of the 4 years of exam papers checked**; Task Planning & Sustainability) — all ✅, 71 blocks and 54 revision questions total, proportional to the syllabus's actual scope-of-learning table sizes (Working in the Industry = 80 rows, nearly double Safety's 48), not exam-history mapping grids alone — this is the topic list §10's mandatory syllabus-check rule was written to enforce. `vet-construction.json`'s 75 MC/23 written questions have no `category`/`topic` field (same as Multimedia) — topics defined from the syllabus, not filtered from existing data. One icon bug (topic 6's 🔒 colliding with the gating lock badge) was caught by browser regression, not JSON validation, and fixed to 🧰 — a reminder that icon/visual choices still need the browser check even when content is syllabus-verified. **Tool/PPE reference icons added same day** (27 small PNGs — hammer, chisel, drill bits, PPE items etc. — self-hosted in `icons/vet-construction/`, sourced from Flaticon author `juicy_fish`'s "Flat" style, free with attribution): wired as inline `<img>` tags into the Hand & Power Tools and Safe Work Practices & Emergencies topics' existing tables/bullets — see `docs/HISTORY.md` for the full sourcing/licensing story, including two links the owner initially picked that turned out broken (a Vecteezy preview thumbnail, a style-mismatched freesvg.org icon) and were dropped rather than faked. **Flaticon attribution is still unplaced** — see known issues below. HMS's 4 non-photo diagrams (SMART goals grid, tapering bar chart, inverted-U SVG, HOWSCSE grid) still deferred — need bespoke CSS ported, not just an image copy. |
| **Exam Trends panel in Study Mode** | 🔶 **Data layer built 2026-08-27, UI not started.** `data/exam-trends/{subject}.json` holds, per topic: syllabus scope share, examined mark share, marks per paper, years present (e.g. "6 of 6 papers"), MC/written split, a per-year series for a sparkline, and `yieldRatio`. Live for **Maths Standard 2** and **Maths Advanced**. Origin: owner's own Drive analysis of exam trends — the idea is theirs, the numbers are now measured from NESA's mapping grids rather than word-frequency estimates. **Open decision: where it renders** (per-topic Study Mode header badge, a dedicated topic-ranking screen, or both) — a design call, not taken unilaterally. Multimedia/VET need a prose-grid parser first. |
| Design aesthetics review (all subjects) | ⬜ Not started — flagged 2026-07-27 as a next-focus item. Warm earth-tone tokens (§15) are locked, but overall visual polish/consistency across screens hasn't had a dedicated pass since early stages. |
| **Mathematics Advanced — new subject port** | 🔶 **Stages 0–6 complete; Stage 7 (Release) next (2026-08-27/31).** **Stage 6 landed 2026-08-31 and found nothing wrong**: `data/answer-key/mathematics-advanced.json` (60 MC) and `data/answer-key/written/mathematics-advanced.json` (234 parts, 90 marks/paper) are committed and enforced — **60 answers and 126 written questions checked, 0 wrong, 0 unverifiable, 5 declared omissions**, on the first run. No `validate.yml` edit was needed (both checkers enumerate their key directory). Both key builders now register the subject, and `build_written_key.py`'s `-mg.pdf$` glob — which silently excluded this subject — is fixed to `is_guidelines()`, verified inert for the other three. All six papers reconcile to **exactly 100** with every official leaf part claimed **exactly once**. The residual human gate was discharged three ways rather than by eyeballing: 12 option-set contact sheets read one by one (all match the paper's A/B/C/D order; closest calls 2024 Q7 and Q8, both correct), **all 124 crops pixel-compared against their PDF source rectangle (0 mismatches)**, and **all 124 position-checked against the paper's own question labels (0 mismatches)**. ⚠️ Two traps in that last check: a bare left-margin number is a question label only on a **Section I** page (Section II body text starts at x = 70.7, so `x = 4` posed as "Q4"), and tightening the x threshold breaks Section I instead — the separator is the `Question N` header, not a coordinate. Also: **MC stems carry inline `<img>` too** (2023 Q2), so a crop-reference scan must read the `q` field of *both* question arrays or it reports a phantom orphan. **All six papers (2020–2025) are ported and cropped** — `subjects/mathematics-advanced.json` holds 60 MC + 126 written + 5 `omittedQuestions` + 12 `omittedParts`, each paper's marks reconcile to **exactly 100, per paper and per question** against the mapping grid, and 124 crops are in `/diagrams/`; local CI green with `MC=706 Written=369 imageRefs=311 missingImages=0`. Per-year detail lives in the runbook. **The last paper, 2024, also closed the `optionImagesWide` question for the subject**: Stage 1 flagged its Q8 histograms at 3.7:1, but that banded the C/D *row* — a single cell cuts at 1.75:1 and renders 160 × 96 px, so the flag is not set and **2021 Q4 remains the only one**. ⚠️ **The 2021 session found that nine of its own stem images were being silently clipped** — there is no `.q-text img` rule in `index.html`, so an inline `<img>` without its own `max-width:100%` renders at natural crop width (1767px inside a 390px stem) and `body{overflow-x:hidden}` cuts it off with nothing reporting it; see the new §10 rule. The per-question check `.question-area` scrollWidth > clientWidth is now a Gate 4 item in the runbook and the playbook. **`optionImagesWide` is also needed after all** — Stage 1's "not needed anywhere" and Stage 3's "never set" were both wrong: 2021 Q4 crops at 2.94:1 and renders 160×54px in the 2×2 grid against 360×122px one-per-row, so the test is the rendered height, not the ratio (2024 Q8 is the last set to check). Q27(d) — Stage 1's one "leans on an omitted part" exception across all six papers — is **kept**, with NESA's wording verbatim and a visibly separate note, because the graph it refers to is just the curve whose equation the stem already gives. ⚠️ **The 2025 session found and fixed a defect in the committed mapping grid** — see the `data/mapping-grid/` note in §6 and `docs/HISTORY.md`; no `category`, answer or mark changed anywhere, but the runbook's multi-code-part count drops from 21 to **7 of 294**. Findings that correct the Stage 1 survey and are inherited by the remaining papers: its **Section II crop list is a lower bound, three times over**: 2023 Q16's geometry diagram is missing from it entirely, **2025 Q29's is too** (though Stage 1's own method paragraph names it), and 2022 Q28 is a single list entry whose circle the paper draws **twice** (once per page) — read each question's own page rather than trusting the list; a second diagram inside one question takes the part letter as a suffix, `…_2022_Q28b_stimulus.jpg`. **An ink profile alone can clip a crop**: 2025 Q28(b)'s first cut lost the graph's y-axis labels, which start 6.6 pt left of the ink band — cross-check any edge near axis labels against `get_text("words")`. **"Lookup table" is not the test for the scroll wrapper, the column count is** (2023 Q15's 5-column future-value table fits; the table that needed wrapping that year was Q23's 11-column z-table, which the list never flagged — though 2022's listed Q21 table genuinely is 7 columns and genuinely needed it). And **Stage 3 decision 1's piecewise brace is sized for two rows**: a three-row brace (2022 Q30) needs `rowspan="3"` and `font-size:3.9em`, measured at 72.5 px against a 72.5 px block — scale the em value with the row count and re-measure. A third: where a merged entry splits its marks **evenly** between two syllabus codes, the "code the marks are awarded for" rule decides nothing — **tie-break on the heavier mathematical demand**, keeping NESA's full list in `gridCodes`. Five decisions the port took that every later year inherits: **one bank entry per NESA question** (not per part — matches Standard 2 and `check_written_key.cjs`'s prefix-sum join); a merged entry spanning parts with different codes takes one `category` and keeps NESA's list in `gridCodes`; an omitted part inside a question the bank still carries **forces** the merged form, or the dropped mark vanishes silently; **NESA's part letters stay** even when a part is dropped, with a visibly separate note saying what is missing; and options carrying `optionImages` must be **plain text**, since the engine reuses the string as `alt`. Assets use a new **`scripts/crop_maths_advanced.py`** (points, not pixels; never `diagram_registry.json`) — ⚠️ on these papers the option letter **cannot be excluded with an x-cut**, because the graph runs underneath it (2020 Q5 A: letter x 100.8–111.3 pt, x-axis starts x 102.2 pt), and a first pass silently amputated the axis; the letter is removed with a white `erase` rect instead. `optionImagesWide` confirmed unnecessary (160×143 px and 160×90 px in the 2×2 grid at 430 px). Stage 0 = **GO** (`docs/paper-reports/mathematics-advanced.md`): Stage 0 = **GO** (`docs/paper-reports/mathematics-advanced.md`): 2020–2025 papers + guidelines local, 10 MC + 90 written marks/paper, notation `basic`. Stage 2: official **2017** syllabus read (14 subtopics, 358 dot points), `category` codes fixed, `data/mapping-grid/mathematics-advanced.json` gives every question's official topic. ⚠️ The **2024** syllabus takes over at the **2027 HSC** — this topic list is dated. **Stage 1 (Survey) complete**: all **294 parts classified**, with per-question crop, table and omission lists in `docs/subject-plans/mathematics-advanced.md`. Measured cost: **121 crops + 28 tables** (Stage 0's "~100" was low), **17 unportable drawing parts / 41 marks**, portable share **93.2%**, and **42% of parts carry a detectable text-layer corruption**. Two Stage 0 facts corrected there: **√ and ∞ are printed but drawn as paths, so neither exists in the text layer** ("no radical sign" was an artefact of reading it), and **only 2024 uses the MathType `^…h` bracket mapping** — every year loses π to the letter `p` and re-orders stacked fractions. **Stage 3 (Schema) complete (2026-08-28)**: field mapping is **fully canonical, zero deviations**, and all **ten** decisions are recorded in the runbook (the six carried, plus four found by reading the engine) — piecewise braces, integrals/fractions, table-row options, blank tables, the two omission keys, the Unicode set, the 7 multi-code parts, the label collision, wide tables, and the written badge. Every rendering claim was **measured in a browser at 430px**, not inferred. **Two one-line engine fixes are blocking for Stage 7**: `NESA_CAT_LABELS` is a flat global map and **5 of Advanced's 14 codes collide with Standard 2's** (`F1 F2 M1 S1 S2`, each meaning something different) — the data keeps bare codes and the map becomes subject-aware; and the **written-question badge reads `q.topic`, not `category`**, so all 151 Standard 2 written questions have shown no topic badge since their port (the HMS marks-badge defect, second instance). **Stages 4 and 5 are now merged** (2026-08-28): `validate_subjects.cjs` exits 1 on a question whose `image` path has no file yet, so porting all six papers before cropping would hold CI red for six sessions and makes Gate 4's own "validator green, `missingImages: 0`" unsatisfiable — each session now ports **one year and crops that year's assets**, finishing green, on a **`port/maths-advanced` branch** merged to main only when the subject is complete. Stage 5 survives as the asset-method reference. Per-year load splits Stage 1's lists exactly (121 crops + 28 tables) and **overturned the suggested order: 2024 is the heaviest paper at 30 assets, not the lightest** — its "2 graphic-bearing MC" claim came from Stage 0 and Section I actually has seven. **Order is now 2020 → 2023 → 2022 → 2025 → 2021 → 2024**, tracked per year in the runbook. The subject is still **registered nowhere in code** — that is Stage 7. |
| **Multimedia — Section III port** | ⬜ **Planned 2026-09-01, scheduled after Mathematics Advanced Stage 7.** Runbook: `docs/subject-plans/multimedia-section-iii.md`. Multimedia's one remaining coverage hole — **Question 16, 15 marks/paper, 12 official parts, 90 marks across 2020–2025, never ported**; the bank holds Q11–Q15 for all six years and no Q16 at all. Surfaced by the reverse-coverage line added at Maths Advanced Stage 6 (**30/42** official parts claimed; porting these closes it to 42/42). **Not a new subject port** — it starts at **Stage 1**, since Stage 0 (feasibility), Stage 2 (syllabus, done for the 7 Study Mode topics) and Stage 3 (schema, fixed by the live file) don't re-run for a live subject, and **Stage 6 is already done** — `data/answer-key/written/multimedia.json` holds all 12 parts' official marks *and* NESA's sample answers, so the marks cannot go wrong without CI catching it. Every year is the same shape: (a) *Describe* 5 marks, (b) *Discuss/Explain/Analyse* 10 — **2023 alone is 3 + 12**. ⚠️ **A different strand from everything already in the subject**: environment/sustainability, industrial relations, WHS, careers, automation, organisational structure, marketing, historical development — **none of the seven Study Mode topics touches any of it**, and there is no existing bank content to build from. ⚠️ **The one genuine risk is whether `mark-written.js` handles a 10–12 mark band-marked extended response** (its longest to date is 5 marks) — Stage 1 must resolve or escalate that before Stage 4 starts, not discover it mid-port. An 8th Study Mode topic is optional and separate. |
| **Multimedia + VET written model answers never reviewed** | ⬜ **Raised 2026-09-01, no decision yet.** `check_written_key.cjs` enforces the written **mark** only — prose cannot be compared for equality — so the **52 authored model answers** in `multimedia.json` (29) and `vet-construction.json` (23) have never been checked against NESA's official sample answers by any session. MC answers *were* audited properly (2026-08-27: all 11 key tables read from rendered page images, `qNum` backfilled on exact option-set equality, option order verified separately) — that pass found **6 wrong VET answers in 75**, and **every one had an `optionExplanations` entry arguing for the wrong answer**. Same authoring, same subjects, same period, and the written prose from it has never been read back. Ground truth already sits in `data/answer-key/written/`, so this is reading, not extraction. |
| `landing.html` — public marketing/conversion page | ⬜ Not started — needed for organic signups |
| `portal.html` — desktop web portal (Stage 10) | ⬜ Not started |
| Agent infrastructure (Stage 9) | 🔶 Phase 1 Content Agent built (2026-07-04, PR-only, awaiting API key secret) — rest of roster not started, see `docs/agents-plan.md` |

**Three-track architecture (do not merge these):** `landing.html` (public, no auth, static) → `index.html` (mobile PWA, logged-in students, live) → `portal.html` (desktop, logged-in students, planned). All three share the warm earth-tone design tokens and, once built, the same `sbClient`/`user_progress`/pricing logic — but never modify `index.html` when building either of the other two.

---

## 12. Testing Checklist

**Before every deploy:**
- [ ] Quiz loads on mobile (iPhone Safari, Android Chrome)
- [ ] Practice mode: Check button appears, correct/incorrect colours show, explanation reveals
- [ ] Test mode: no Check button, answers hidden, results shown at end
- [ ] Year/category filters work and update counts live
- [ ] Prev/Next navigation doesn't skip questions or double-count trial usage
- [ ] Progress bar updates correctly; Reset returns to Q1 with defaults restored

**Billing-specific:**
- [ ] Trial-exhausted user sees the trial wall / upgrade prompt
- [ ] Subscribe modal shows the correct live price for the selected subject count
- [ ] Stripe Checkout opens (sandbox card `4242 4242 4242 4242`)
- [ ] After payment, subjects unlock (or the logged-out "sign in to unlock" banner shows)
- [ ] Customer portal opens via `/customer-portal` (JWT required — not `/.netlify/functions/...`)
- [ ] A call to any function without an `Authorization` header returns 401

---

## 13. Claude API Usage in This Project

| Where | Current model | Notes |
|---|---|---|
| `mark-written.js` (Cloudflare Function, live) | `claude-haiku-4-5` | Cheap, sufficient for structured JSON marking. System prompt cached (`cache_control`) — see global CLAUDE.md for the caching minimum-prefix caveat. |
| `agent.js` (Content Agent, nightly GitHub Action) | `claude-sonnet-5` (discovery + triage) / `claude-opus-4-8` (question generation) | Deliberately NO `cache_control` — prompts are under the minimum cacheable prefix and each is called at most a few times per run; see comment in agent.js. |
| Diagram extraction scripts (`scripts/extract_*.py`) | `claude-sonnet-4-6` vision | Re-evaluate against `claude-sonnet-5` next time these scripts are touched. |

Never expose `ANTHROPIC_API_KEY` in browser code — always proxy through a Cloudflare Pages Function (`env.ANTHROPIC_API_KEY`, not `process.env`).

---

## 14. Cost Reference

| Service | Free Tier | Current Cost |
|---|---|---|
| Supabase | 50,000 users, 500MB DB | $0 |
| Cloudflare Pages | Unlimited bandwidth, 100K function requests/day | $0 |
| GitHub | Unlimited public repos | $0 |
| Stripe | No monthly fee | 1.75% + 30¢/txn of revenue only |
| Claude API (agent, once live) | Pay per use | ~$2–5/mo |
| Claude Pro (owner) | N/A | $20/mo |
| **TOTAL** | | **~$22–25/mo + % of revenue** |

At 1,000 active subscribers: ~$105/mo in AI + infra costs (≈1.3% of revenue).

---

## 15. Design System

- **Warm earth-tone system is locked** — `--accent: #C17D3C` amber, Syne + DM Sans fonts, `--bg: #FAF8F5` (see §9 for the full token block). The standalone Maths v5.4 reference file uses a different dark-navy design — that's the standalone study tool only, not the CramIT brand.
- **Mobile-first:** touch targets `min-height: 52px` on touchscreen devices, safe-area-inset on the quiz footer, all design decisions must translate to native mobile (same hex values usable in React Native/Flutter later).
- **Three-track product architecture** — see §11.

---

*CLAUDE.md — CramIT Project — Last updated: 2026-09-01 — **Multimedia Section III planned as its own runbook, and an audit gap recorded.** No code, data, credential, schema or pricing fact changed — this was a planning and record-keeping pass only. Facts changed here: a new **`docs/subject-plans/multimedia-section-iii.md`** (§6 tree, §11 roadmap) plans Multimedia's one remaining coverage hole — **Section III, Question 16, 15 marks/paper, 12 official parts, 90 marks across 2020–2025, never ported.** The bank holds Q11–Q15 for all six years and **no Q16 at all**; the gap surfaced from the reverse-coverage line added at Maths Advanced Stage 6 (**30/42** official parts claimed). **Scheduled after Mathematics Advanced Stage 7** (owner decision), superseding the 2026-07-29 "after VET Study Mode" sequencing, whose precondition was met 2026-07-30 and then sat unstarted. **It is not a new subject port**: it starts at **Stage 1**, because Stage 0, Stage 2 and Stage 3 don't re-run for a live subject, and **Stage 6 is already complete** — `data/answer-key/written/multimedia.json` already holds all 12 parts' official marks *and* NESA's sample answers, so the marks cannot go wrong without CI catching it. Every year is the same shape — (a) *Describe* 5, (b) *Discuss/Explain/Analyse* 10, **2023 alone 3 + 12** — and the strand is business-and-industry (environment, industrial relations, WHS, careers, automation, organisational structure, marketing, historical development), which **none of the seven Study Mode topics touches**. ⚠️ **The one genuine risk is whether `mark-written.js` can mark a 10–12 mark band-marked extended response** — its longest to date is 5 marks — and Stage 1 must resolve or escalate that before Stage 4 starts. ⚠️ **Second fact recorded, in answer to a direct question: the MC answers for Multimedia and VET WERE properly audited against the marking guides, but their written MODEL ANSWERS never were.** The 2026-08-27 pass read all 11 answer-key tables from rendered page images, backfilled `qNum` on exact option-set equality, verified option order separately, and found **6 wrong VET answers in 75 (8%)** plus four questions whose option *text* described the wrong picture; Multimedia came back clean at 60/60. But `check_written_key.cjs` enforces the **mark only** — prose cannot be compared for equality — so the **52 authored model answers** across `multimedia.json` (29) and `vet-construction.json` (23) have never been read back against NESA's committed sample answers by any session. That matters because **every one of the six defective VET questions also carried an `optionExplanations` entry arguing for the wrong answer** — same authoring, same subjects, same period. Ground truth already sits in `data/answer-key/written/` from Stage 6, so the work would be reading, not extraction. Recorded as a §11 roadmap row; **no decision taken and nothing changed.** Previously (2026-08-31, later) — **Mathematics Advanced Stage 6 is COMPLETE: the subject's answer and written keys are built, committed and enforced in CI — and the bank was right on its first check.** Facts changed here: **`data/answer-key/mathematics-advanced.json`** (6 papers, **60 MC answers**) and **`data/answer-key/written/mathematics-advanced.json`** (6 papers, **234 parts, exactly 90 marks each**) now exist (§6 tree, §10 rule 8, §11 roadmap). First run, no iteration: **60 answers checked, 0 wrong, 0 unverifiable** and **126 written questions checked, 0 wrong, 0 unverifiable, 5 declared omissions**. Subject-wide CI totals move to **285 MC answers** and **329 written questions**. **No `validate.yml` edit was needed** — both checkers enumerate their key directory rather than naming subjects, so committing the two files is what wires them in. The 60 answers match, letter for letter, the six strings recorded in this file during the Stage 4 sessions; this is the first time those six independent reads have been compared against each other, and they agree. ⚠️ **`build_written_key.py`'s `-mg.pdf$` glob is fixed**, exactly as the runbook predicted at Stage 0: it never matched Mathematics Advanced's `{year}_marking_guidelines.pdf` and exited *"no marking-guideline PDFs"*, silently excluding the subject. It is now `is_guidelines()`, mirroring `build_answer_key.find_papers()` — and **`feedback` must be tested FIRST**, because Multimedia's third PDF per year is `… HSC Marking Feedback.pdf`, which contains *both* words. Verified inert: all three existing subjects regenerate byte-identical written keys, and regenerating their MC keys changes only the `generatedAt` timestamp (so those three files were reverted — the committed data diff is the two new files alone). ⚠️ **A hole in `check_written_key.cjs` is now reported, not enforced**: it compares bank entries against the key, so it can see a mark that is *wrong* but never a question that is simply **ABSENT** — the failure that left 2020 Standard 2 at 84/85 for over a year. It now also prints reverse coverage: **Maths Advanced 234/234, Standard 2 235/235, Multimedia 30/42** (Section III never ported), **VET 23/76** (written bank covers 23 of 65 marks/paper). It is deliberately non-blocking — those last two are documented decisions, and failing on them would turn CI red on work already scoped out; promote it to a hard assertion if either gap is closed. All six papers reconcile to **exactly 100** (2020 10+82+1+7, 2021 10+81+4+5, 2022 10+85+5+0, 2023 10+83+7+0, 2024 10+81+4+5, 2025 10+87+3+0) with **every official leaf part claimed exactly once** — 0 unclaimed, 0 double-claimed. **The residual human gate was discharged three ways rather than by eyeballing 124 crops**: twelve option-set contact sheets read one at a time (each putting the NESA page's own option area above the four committed crops **in bank array order** — all twelve match the paper's A/B/C/D ordering, the closest calls being **2024 Q7**, whose C and D differ only by a horizontal shift, and **2024 Q8**'s four similar histograms, both correct); **all 124 crops re-rendered from the PDF at their registry rectangle and pixel-compared to the committed file, 0 mismatches**; and **all 124 position-checked against the paper's own question labels, 0 mismatches**. ⚠️ **Two traps in writing that last check**, both hit before it was right: a bare number in the left margin is a question label only on a **Section I** page — on Section II pages body text starts at x = 70.7, so `x = 4` in 2021 Q24's stem posed as "Q4" — but tightening the x threshold breaks Section I entirely, whose numbers sit in the *same* band (all 73 Section I crops then reported no label). **The separator is the `Question N` header, not a coordinate.** Crop reconciliation is **124 referenced, 124 on disk, 0 orphans, 0 missing** — and note that **MC stems carry inline `<img>` too** (2023 Q2 embeds its die-and-spinner picture between two sentences), so a reference scan reading `image`/`optionImages` plus *written* stems alone reports a phantom orphan. Full local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`, `Issues: 0`, both key checkers pass, all Cloudflare functions syntax-check, `npm test` 67 pass / 0 fail. No credential, schema, pricing or engine fact changed, and **no question content was altered** — this stage only reads the bank. The subject is still **registered nowhere in code**; that is **Stage 7 (Release), which is next**, still blocked on the two one-line `index.html` fixes Stage 3 found (`NESA_CAT_LABELS` collides on 5 of 14 codes; the written badge reads `q.topic` not `category`). Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-31, later). Previously (2026-08-31) — **Mathematics Advanced Stage 4 is COMPLETE: the 2024 HSC, the sixth and last paper, is ported and cropped.** Facts changed here: `subjects/mathematics-advanced.json` now holds **all six years — 60 MC + 126 written entries + 5 `omittedQuestions` + 12 `omittedParts`** (§6 tree, §11 roadmap), and **124 crops** are in `/diagrams/`. 2024 adds 10 MC + 20 written, **two `omittedParts`** (Q17(a) 2, Q25(b) 2) and **one new `omittedQuestion`** (Q19 5, a whole sketch question). Marks reconcile to **exactly 100** (10 MC + 81 written + 4 + 5). All ten answers were confirmed against the official key **before** authoring by calling `extract_mc_key()` read-only (`C B A C A D C D B B`), and the twenty written model answers were cross-checked against NESA's own sample answers via `build_written_key.py`'s `parse_paper()` in dry-run (37 leaf parts, 90/90) — never by re-reading the guidelines, which §10 forbids. ⚠️ **The headline finding closes an open question rather than opening one: `optionImagesWide` is NOT needed for 2024 Q8**, the last candidate in the subject. Stage 1 measured its histograms' ink extent at 3.7:1, but that banded the C/D *row* of the page — a single option cell cuts at **1.75:1** and renders **160 × 96 px** in the 2×2 grid, squarely in 2020's 160 × 90 px territory, not 2021 Q4's 160 × 54 px. With all twelve option sets now measured, **2021 Q4 is the subject's only `optionImagesWide`**; corrected in the runbook in three places. Two traps were checked and did not recur: the 2020 option-letter amputation (all eight letters are real text and `get_drawings()` reports zero paths intersecting any of them) and the 2021 stem-image clipping (all ten inline `<img>` tags carry `max-width:100%`, and no `.question-area` overflows). **Stage 1's asset counts were exactly right for this paper — 23 crops, 7 tables — the second year running after 2021 and the only two of six.** Port decisions: **Stage 3 decision 4 (blank tables) is used here for the first and only time** (Q11 and Q13; empty `<td>&nbsp;</td>` cells render 34 px tall), and there are **three multi-code calls, two of them even splits** — Q22 filed under `C3` (part (c) is answered *from* part (a)'s concavity, the mirror of 2025 Q25), Q31 under `C3` (heavier demand), and **Q30, the hardest, under `M1`**: the stem offers the graph as *"or otherwise"*, an optional scaffold, while the mark-bearing insight is that a limiting sum exists only for −1 < *x* < 1 — the 2021 Q33 reading applied to a single part. Re-measured at a 430 px viewport across all 30 questions: `body.scrollWidth` never exceeds 430 and **no `.question-area` overflows**, Q23's 10-column *z*-table scrolls inside its wrapper (390 px → 630 px), the six narrower tables fit bare, the **three-row** piecewise brace measures 72.5 px against a 72.5 px block at `font-size:3.9em` (confirming 2022's scaling rule a second time), all 23 images load, all 32 text options are 52 px single-line, and all 31 non-ASCII characters render real glyphs. Screenshots were unavailable (the Browser pane was not displayed), so these are DOM measurements; option-image legibility was judged by re-rendering each crop offline at its measured display box. Local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`; the other subjects' 225 MC and 203 written key checks still pass and were not touched. The subject is still **registered nowhere in code** — that is Stage 7, still blocked on the two one-line `index.html` fixes from Stage 3. **Stage 6 (commit and CI-enforce this subject's answer and written keys) is next.** No credential, schema, pricing or engine fact changed; no subject's answers or marks were altered. Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-31). Previously (2026-08-29) — **Mathematics Advanced Stage 4, paper 5 of 6: the 2021 HSC is ported and cropped — and nine of its stem images were found to be silently clipped.** Facts changed here: `subjects/mathematics-advanced.json` now holds **five years — 50 MC + 106 written entries + 4 `omittedQuestions` + 4 `omittedParts`** (§6 tree, §11 roadmap), and **101 crops** are in `/diagrams/`. 2021 adds 10 MC + 22 written, **two `omittedParts`** (Q27(a) 2, Q28(b) 2) and — unlike 2023, 2022 and 2025 — **two new `omittedQuestions`** (Q19 3, Q21 2), both whole sketch questions. Marks reconcile to **exactly 100** (10 MC + 81 written + 4 + 5). All ten answers were confirmed against the official key **before** authoring by calling `extract_mc_key()` read-only (`B C D C A D A C B B`) — never by re-reading the guidelines, which §10 forbids. ⚠️ **The headline finding is a live rendering defect, and it is now a new §10 rule: an inline `<img>` inside a `q` stem needs its own `max-width`.** `index.html` has **no `.q-text img` rule** — the only `max-width` on a question image is `.device-phone .q-image-wrap img`, which governs the separate `image` field, not the inline `<img>` that every written-question diagram in this project uses. Nine 2021 stem images shipped without the style every other ported year carries and rendered at natural crop width — **1767px inside a 390px stem** — with `body{overflow-x:hidden}` cutting them off. **Nothing reported it**: `body.scrollWidth` still read 430, `validate_subjects.cjs` was green with `missingImages: 0`, no console error fired. All nine are fixed, and the per-question check (`.question-area` scrollWidth > clientWidth, which page-level measurement misses) is now a Gate 4 item in the runbook **and** in `docs/porting-playbook.md`, which was corrected in the same session. ⚠️ **`optionImagesWide` is needed for this subject after all** — Stage 1's "not needed anywhere" (from a 0.8:1–2.6:1 ratio sweep) and Stage 3's "**Never set**" were both wrong: 2021 Q4 crops at **2.94:1** and renders **160×54px** in the 2×2 grid against **360×122px** one-per-row, close to the VET 160×35px case the flag was created for. **The test is the rendered height, not the aspect ratio** — corrected in §10's schema comment, the runbook (three places) and the playbook (three places); 2024 Q8 is the last set to check. Port decisions: **Q27(d) is kept** — Stage 1's single "leans on an omitted part" exception across all six papers, whose (a) is an omitted sketch. Supplying the graph was rejected (NESA does not print it, so it would be fabricated) and dropping (d) was rejected (the graph is just *P*(*t*) = 400 sin(π*t*/12), already given in the stem), so NESA's wording stands **verbatim** with a visibly separate note. **Q33 is the year's even split** (`S3` 4 marks, `S1` 4) and is filed under **`S3`**, since three of four parts operate on the continuous pdf and (d) is one application of (c)'s result — the same reading that put 2025 Q25 and 2022 Q28 under `C4`. Assets: **Stage 1's counts were exactly right for this paper (22 crops, 6 tables) — the first year they have been.** The 2020 option-letter amputation trap **did not recur** but was checked: the letters are not real text on either option page (`A.` extracts as `Mul` / `ap`), so the boxes came from an ink profile cross-checked against the fixed 128.8pt row spacing, and `get_drawings()` reports zero paths intersecting any of the eight. Q5's two option columns are **not symmetric about the page centre**. Re-measured at a 430px viewport across all 32 questions: `body.scrollWidth` never exceeds 430 and **no `.question-area` overflows after the fix (8 did before)**, Q22's 7-column and Q34's 8-column tables both scroll inside their wrappers, Q25's 6-column table renders 399.1px and spills 9px into the padding **without being clipped**, both two-row piecewise braces match their blocks exactly (51.0/48.4px at `2.6em`), all 17 images load, all 32 text options are 52px single-line, and all 27 non-ASCII characters render real glyphs. Screenshots were unavailable (the Browser pane was not displayed), so these are DOM measurements. Local CI green: `MC=696 Written=349 imageRefs=288 missingImages=0`; the other subjects' 225 MC and 203 written key checks still pass and were not touched. The subject is still **registered nowhere in code** — that is Stage 7. **2024 is next, and last.** No credential, schema, pricing or engine fact changed; no subject's answers or marks were altered. Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-29). Previously (2026-08-28, later still, ×4) — **Mathematics Advanced Stage 4, paper 4 of 6: the 2025 HSC is ported and cropped — and a ground-truth extractor was found wrong and fixed.** Facts changed here: `subjects/mathematics-advanced.json` now holds **four years — 40 MC + 84 written entries + 2 `omittedQuestions` + 8 `omittedParts`** (§6 tree, §11 roadmap), and **79 crops** are in `/diagrams/`. 2025 adds 10 MC + 21 written and **two `omittedParts` worth 3 marks** (Q15(b) sketch 2, Q16(b) complete-the-graph 1) but **no new `omittedQuestions`**. Marks reconcile to **exactly 100** (10 MC + 87 written + 3 omitted). All ten answers were confirmed against the official key **before** authoring by calling `extract_mc_key()` read-only (`B A D C B C A D B C`) — never by re-reading the guidelines, which §10 forbids. ⚠️ **The headline finding is not about 2025 at all: `data/mapping-grid/` was wrong.** Porting Q18 — a composite-functions question — turned up `MA-F1`+`MA-M1`, and NESA's printed grid says `MA-F1` alone. `scripts/build_mapping_grid.py` gave each row *“the lines from just after the PREVIOUS label to just before the NEXT one”*, and a Content cell holding two or three codes is **vertically centred**, so its first line sits above its own label line and its last below — the codes leaked into the neighbouring rows in **both** directions. **20 rows across the two maths subjects carried a code NESA never assigned** (14 Advanced, 6 Standard 2). **Marks were never affected**, which is exactly why nothing caught it: every paper still reconciled to its front-page total with zero uncoded rows and the script's own gate passed. The fix reads the grid's **own drawn horizontal rules** (`row_rules()` / `band_of()`), with the old label-bracketing kept only as a fallback. Both grids were regenerated and `data/exam-trends/` rebuilt on top of them; four now-spurious `gridCodes` keys were removed from already-ported questions (2020 MC Q2, 2020 Q13, 2020 Q26, 2023 Q27). **No `category` changed anywhere in any subject, and no answer or mark moved** — and because the Standard 2 corrections are all Section II, §10's claim that all 90 original Standard 2 MC questions agree with NESA's tagging is untouched. The runbook's multi-code-part count drops from 21 to **7 of 294**, and 2020, 2021 and 2022 turn out to have none. ⚠️ **Two asset findings inherited by the remaining two papers.** Stage 1's Section II crop list under-counts a **third** way — **2025 Q29** (the mountain-peak diagram) is absent from its 2025 row even though Stage 1's own *method* paragraph names it; the table and the prose disagreed and the table was believed. Subject crop total moves 123 → **124**. And **an ink profile alone can clip a crop**: Q28(b)'s first cut used the ink band's left edge at x = 85 pt and silently removed the graph's y-axis labels, which start at x = 78.4 pt — cross-check any edge running near axis labels against `get_text("words")`. Conversely **Q25 needed no part-letter suffix** (its only diagram is in part (c)); the suffix is for a *second* diagram in one question, here only Q28. The 2020 option-letter amputation trap **did not recur** — all twelve letters are real text and `get_drawings()` reports zero paths intersecting any of them — but it was checked, not assumed. Port decisions: **Q25 is the year's even three-way split** (`C2`/`C4`/`M1`, 2 marks each) and is filed under **`C4`**, since (a) exists only to supply the primitive (b) and (c) integrate with; and **Q15 is kept despite leaning on an omitted sketch**, because part (c) names two functions whose equations are both given — P₂'s definition is repeated inline and the omission note says so, rather than letting the substitution pass as NESA's wording. Re-measured at a 430 px viewport across all 31 questions: `body.scrollWidth` never exceeds 430 and no `.question-area` overflows, Q20's 7-column table works in the wrapper (390 px, scrolling to 564 px), the **three-row** piecewise brace measures 72.5 px against a 72.5 px block at `font-size:3.9em` (confirming 2022's scaling rule), option images render 160×128/154/166 px in the 2×2 grid (`optionImagesWide` again unnecessary), all 23 images load, and all 38 non-ASCII characters used render real glyphs. Screenshots were unavailable (the Browser pane was not displayed), so these are DOM measurements. Local CI green: `MC=686 Written=327 imageRefs=266 missingImages=0`. The subject is still **registered nowhere in code** — that is Stage 7. **2021 is next.** No credential, schema, pricing or engine fact changed; no subject's questions, answers or marks were altered. Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-28, later still, ×4). Previously (2026-08-28, later still, ×3) — **Mathematics Advanced Stage 4, paper 3 of 6: the 2022 HSC is ported and cropped.** Facts changed here: `subjects/mathematics-advanced.json` now holds **three years — 30 MC + 63 written entries + 2 `omittedQuestions` + 6 `omittedParts`** (§6 tree, §11 roadmap), and **56 crops** are in `/diagrams/`. 2022 adds 10 MC + 22 written and **two `omittedParts`** (Q12(b) blank table + graph-on-a-grid 2, Q27(c) sketch 3) but **no new `omittedQuestions`** — no whole 2022 question is a drawing task. Marks reconcile to **exactly 100** (10 MC + 85 written + 5 omitted) against the mapping grid; the build script refuses to write unless the prefix-sum join, the paper total, every `category` being one of NESA's own codes, every `gridCodes` union, every grid part having a bank entry and every referenced image file existing all hold, and unless the existing file round-trips byte-for-byte first. All ten answers were confirmed against the official key **before** authoring by calling `extract_mc_key()` read-only (`A D B A D B C C A B`) — never by re-reading the guidelines, which §10 forbids. ⚠️ **Two findings inherited by the remaining three papers.** First, **Stage 1's Section II crop list under-counts a second way: one list entry can be two diagrams.** 2022 **Q28** appears once, but the paper draws its circle **twice** — sector shaded for part (a), then again with the hyperbola added for part (c) — and the stem needs both. Naming convention set here: a second diagram inside one question takes the part letter as a suffix on the question number, `mathematics-advanced_2022_Q28b_stimulus.jpg` beside `…_Q28_stimulus.jpg`; 2025's `Q25(c)` and `Q28(b)` list entries will need it. The subject crop total moves 122 → **123**. Second, **Stage 3 decision 1's piecewise brace is sized for two rows**: 2022 Q30's three-row cumulative distribution function needs `rowspan="3"` and **`font-size:3.9em`** (measured, brace cell 72.5 px against a 72.5 px three-row block) — scale the em value with the row count and re-measure. On the wide-table rule: 2022's Q21 future-value table **is** on Stage 1's "wide lookup table" list **and** is genuinely 7 columns, so the wrapper was needed (wrapper 390 px, scrolls to 560 px, `body.scrollWidth` stays 430) — but that does not rehabilitate the list; the test remains **count the columns of every table you build**. On the 2020 option-letter trap: it **did not recur** — `get_drawings()` reports zero paths intersecting any of the eight letter boxes — but two wrinkles are worth carrying: page 2's text layer is garbled exactly where Q1's letters are (`A.` extracts as the word `Mul`), so the erase boxes came from the **geometry** (the two option rows are a fixed 156.7 pt apart) rather than the text layer; and an x-cut would still have been wrong on Q10, whose option-A branch starts at x = 103.6 pt, *left* of the letter's right edge at 114.9 pt — they miss only in *y*. Re-measured at a 430 px viewport across all 32 questions: `body.scrollWidth` never exceeds 430 and no `.question-area` overflows, Q11's 4-column table fits bare at 390 px, option images render 160×163 px and 160×174 px in the 2×2 grid (`optionImagesWide` again unnecessary), all 21 images load, the 31 non-ASCII characters used all render real glyphs (`→` and `…` rasterised and compared against notdef to be sure), and `<sup>` exponents render at 15 px against an 18 px base. Screenshots were unavailable (the Browser pane was not displayed), so these are DOM measurements. Local CI green: `MC=676 Written=306 imageRefs=243 missingImages=0`. The subject is still **registered nowhere in code** — that is Stage 7. **2025 is next.** No credential, schema, pricing or engine fact changed; no other subject's content was touched. Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-28, later still, ×3). Previously (2026-08-28, later still, again) — **Mathematics Advanced Stage 4, paper 2 of 6: the 2023 HSC is ported and cropped.** Facts changed here: `subjects/mathematics-advanced.json` now holds **two years — 20 MC + 41 written entries + 2 `omittedQuestions` + 4 `omittedParts`** (§6 tree, §11 roadmap), and 35 crops are in `/diagrams/`. 2023 adds 10 MC + 22 written and **three `omittedParts`** (Q18(a) plot-on-a-grid 3, Q19(a) sketch 2, Q30(b) sketch 2) but **no new `omittedQuestions`** — no whole 2023 question is a drawing task. Marks reconcile to **exactly 100** (10 MC + 83 written + 7 omitted) against the mapping grid, and the build script refuses to write unless the prefix-sum join, the paper total, every `category` being one of NESA's own codes and every `gridCodes` union all hold, and the existing file round-trips byte-for-byte first. All ten answers were confirmed against the official key **before** authoring by calling `extract_mc_key()` read-only (`D D A B A C A B D C`) — never by re-reading the guidelines, which §10 forbids. ⚠️ **Two Stage 1 survey corrections, inherited by the remaining four papers.** Its **Section II crop list is a lower bound**: 2023 **Q16**'s geometry diagram is absent from it and surfaced only when the question was read for porting, so the subject total moves 121 → **122 crops** — read each question's own page rather than trusting the list. And **"lookup table" is not the test for §10's 7-column scroll wrapper, the column count is**: 2023 Q15's future-value table is on Stage 1's "wide lookup table" list but has **5 columns** and fits at 390 px, while the table that actually needed wrapping was **Q23's 11-column z-table**, which the list never flagged (measured: wrapper 390 px, scrolls to 694 px, `body.scrollWidth` stays 430). A third inherited rule: where a merged entry splits its marks **evenly** between two syllabus codes — 2023 Q26 (`C4`/`T3`) and Q32 (`C4`/`F1`) — the "code the marks are awarded for" rule decides nothing, so **tie-break on the heavier mathematical demand** and keep NESA's full list in `gridCodes`. On the 2020 option-letter trap: it **did not recur** on 2023 — there the `A.`/`B.` glyphs are real text and `get_drawings()` reports zero paths intersecting any letter box — but that was checked, not assumed, and every remaining year should be checked the same way. Re-measured at a 430 px viewport across all 32 questions: `body.scrollWidth` never exceeds 430, the piecewise brace cell matches its two-row block exactly (48.3 px each), option images render 160×131 px in the 2×2 grid (`optionImagesWide` again unnecessary), the flattened table-row options are 52 px single-line buttons, all 17 images load, and all 40 non-ASCII characters used render real glyphs. Local CI green: `MC=666 Written=284 imageRefs=222 missingImages=0`. The subject is still **registered nowhere in code** — that is Stage 7. **2022 is next.** No credential, schema, pricing or engine fact changed; no other subject's content was touched. Work stays on the **`port/maths-advanced`** branch. Full detail in `docs/HISTORY.md` (2026-08-28, later still, again). Previously (2026-08-28, later still) — **Mathematics Advanced Stage 4, paper 1 of 6: the 2020 HSC is ported and cropped.** Facts changed here: **`subjects/mathematics-advanced.json` now exists** (§6 tree) with 2020's 10 MC + 19 written entries + 2 `omittedQuestions` + 1 `omittedParts`, and 18 crops are in `/diagrams/`. Marks reconcile to **exactly 100 — per paper and per question** — against the mapping grid, using the same prefix-sum join `check_written_key.cjs` applies; a build-time assertion also refuses to write the file unless every `category` is one of NESA's own codes for that question. All ten MC answers were confirmed against the official key **before** authoring, by calling `extract_mc_key()` read-only (`D B A B C B A A C D`) — not by re-reading the guidelines, which §10 forbids. The subject remains **registered nowhere in code** (no `subjects/index.json` row, no `SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no card) — that is Stage 7; `validate_subjects.cjs` covers the file anyway because it globs `subjects/*.json`, and the two key checkers skip it until Stage 6. New script of record: **`scripts/crop_maths_advanced.py`** (§6), `--year {YEAR}`, coordinates in **PDF points** rather than pixels, one registry block per exam year. ⚠️ It is deliberately **not** an entry in `scripts/diagram_registry.json` — that registry is pixels-verified-at-150-dpi and a bare run re-cuts every Standard 2 crop. ⚠️ **A new asset trap, found the hard way:** the standing rule "exclude the paper's own `A.`/`B.` glyph" **cannot be met with an x-cut on these papers** — the letter sits in the cell's top-left corner with the graph running underneath it (2020 Q5 option A: letter spans x 100.8–111.3 pt, the graph's own x-axis starts at x 102.2 pt), and a first pass cropping from x = 114 pt silently amputated the parabola's left arm and the end of the axis. Files written, non-empty, plausible, wrong — the `RENDER_DPI` failure signature, caught only by building contact sheets and looking. The letter is now removed with a white `erase` rectangle over its own bounding box, ink-profiled first to confirm nothing else is inside it. Five port decisions Stage 3 could not have taken are recorded in the runbook and inherited by every later year: **one bank entry per NESA question** rather than per part (matches Standard 2's 140-of-151 and the checker's prefix-sum join); a merged entry spanning parts with different codes takes one `category` and keeps NESA's full list in `gridCodes`; **an omitted part inside a question the bank still carries forces the merged form**, or the dropped mark vanishes with nothing reporting it; **NESA's part letters stay** even when a part is dropped, with a visibly separate note saying what is missing; and options carrying `optionImages` must be **plain text**, because the engine reuses the option string as `alt`. Re-measured at a 430 px viewport: the 7-column table wrapper works (390 px wrapper scrolling to 520 px, `body.scrollWidth` stays 430), the piecewise brace cell matches its two-row block exactly (38.0 px each), option images render 160×143 px and 160×90 px in the 2×2 grid, and every Unicode glyph used is real, none falling back to notdef — so **`optionImagesWide` is confirmed unnecessary** for this subject. One process fact for the remaining five sessions: this file **round-trips byte-for-byte** through `json.dumps(indent=2, ensure_ascii=False)` plus a trailing newline, unlike `multimedia.json`, so loading, extending with a year and dumping is safe. No credential, schema, pricing or engine fact changed; no other subject's content was touched. Work is on the **`port/maths-advanced`** branch, not `main`. Full detail in `docs/HISTORY.md` (2026-08-28, later still). Previously (2026-08-28, later) — **Mathematics Advanced Stage 3 (Schema) complete: the field mapping is canonical with zero deviations, and two live engine defects were found.** Facts changed here: the §11 roadmap row now records **Stages 0–3 done, with Stage 4 (Port) next**, and all ten schema decisions live in `docs/subject-plans/mathematics-advanced.md`. §10 gains a new rendering rule: **a question table with 7+ columns is silently clipped on a phone unless wrapped in `overflow-x:auto`** — question stems render tables as `.q-table`/`.nesa-table`, **never** Study Mode's `.study-dtable` (the question renderer never applies it), and neither collapses *or* scrolls; measured at a 430px viewport, an 8-column table renders 513px into a 390px stem and `body{overflow-x:hidden}` cuts the rest off with no scrollbar and no error. The same correction landed in `docs/porting-playbook.md`, which had asserted the opposite. **Two one-line `index.html` fixes are now blocking for that port's Stage 7**, both recorded in the runbook: `NESA_CAT_LABELS` is one flat global map keyed on the bare syllabus code, and **5 of Mathematics Advanced's 14 codes collide with Mathematics Standard 2's** (`F1 F2 M1 S1 S2` — e.g. Advanced's `M1` is Modelling Financial Situations, Standard 2's is Measurement), so the map must become subject-aware while the data keeps bare codes; and the **written-question renderer badges `q.topic` while the MC renderer badges `q.category || q.topic`**, so every written question following the canonical field shows no topic badge — **all 151 Standard 2 written questions have been in that state since their port**, the same silent, CI-invisible defect as HMS's missing marks badge. The playbook records this second instance beside the first. No credential, schema, pricing or file-structure fact changed; no question content was touched, and Mathematics Advanced is still registered nowhere in code. Stages 4 and 5 of that port are also **merged into one interleaved stage** run on a **`port/maths-advanced` branch** — the validator exits 1 on an image path with no file, which made the old order hold CI red for six sessions; the per-year split also **corrected the suggested paper order to 2020-first**, since 2024 turns out to be the heaviest paper rather than the lightest. Full detail in `docs/HISTORY.md` (2026-08-28, later). Previously (2026-08-28) — **Mathematics Advanced Stage 1 (Survey) complete: all 294 parts classified.** Facts changed here: the §11 roadmap row now records Stages 0, 1 and 2 done, with **Stage 3 next**. The full per-question crop, table and omission lists live in `docs/subject-plans/mathematics-advanced.md`. Measured, not estimated: **121 crops + 28 tables** (Stage 0's "~100 image assets" was low), **17 unportable drawing parts / 41 marks** (7.6% of Section II; portable share **93.2%**, confirming Stage 0), and **124 of 294 parts (42%) carrying a detectable text-layer corruption**. **Two Stage 0 facts are corrected**, both because they were read off the text layer rather than the page: **√ and ∞ are printed but drawn as vector paths**, so neither character exists in any paper's text layer ("notation `basic` — no radical sign" was an artefact); and while the text layer is garbled on every paper, **only 2024 uses the MathType `^…h` / `]…g` bracket mapping** Stage 0 quoted — what all six share is π extracting as the letter `p`, ∞/√ missing, and stacked fractions split and re-ordered (91 of 294 parts contain one). Two Section I classifications are corrected too (2020 Q9 has option images, 2021 Q6 has a stimulus). **Playbook corrected in two places** (§2): its stem-sweep regex misses `which of these …` and `a possible sketch`, both picture-option questions; and a new method rule — **no single graphic detector is complete, union three and then look at the pages** (text-gap bands, `find_tables()`, ink profile; four Section II diagrams surfaced only in the union). Stage 3 now carries six schema decisions rather than two, including **options printed as rows of a table** (2020 Q2/Q3, 2022 Q2, 2023 Q4) and **blank tables the student fills in** (2024 Q11, Q13). `optionImagesWide` is **not** needed for this subject — all 12 option sets measure 0.8:1 to 2.6:1. No code, credential, schema or pricing fact changed; nothing ported, subject still registered nowhere. Full detail in `docs/HISTORY.md` (2026-08-28). Previously (2026-08-27, latest+2) — **Exam-trend data built: syllabus scope vs examined marks, for both maths subjects.** Facts changed here: a new **`data/exam-trends/`** (§6) holds per-topic study weighting for `mathematics-standard-2` and `mathematics-advanced`, built by new **`scripts/build_exam_trends.py`** from the syllabus DOCX plus the mapping grid — scope share, exam share, marks per paper, years present, MC/written split, per-year series, and `yieldRatio`. **⚠️ Always show both axes**: marks alone tells a Standard 2 student to skip Data Analysis (13.5% of syllabus, 3.9% of marks) and an Advanced student to skip Introduction to Differentiation (10.6% / 1.3%), the Year 11 foundation every Year 12 calculus question assumes; scope alone hides that Annuities is 5 dot points earning 7.3% of the paper. §11 gains an **Exam Trends panel** roadmap row — data layer done, **UI placement is an open design decision**. `build_mapping_grid.py` now covers **Standard 2** as well (§6): all twelve papers across both subjects reconcile to 100 marks with zero uncoded rows, and the grid **independently verifies the live Standard 2 bank** — its 16 `category` codes match exactly and all 90 original MC questions agree with NESA's tagging, 0 disagreements. Three tooling facts: an outcome code is distinguished from a content code by **having digits before the hyphen** (`MS2-12-5` vs `MS-F4`); NESA's own 2020 Standard 2 grid contains a **typo** (`MS2-F4`), normalised through an explicit `SOURCE_TYPOS` table that prints every substitution rather than by loosening the regex; and **Section I's last question number differs per subject** (Standard 2 = 15, Advanced = 10). Multimedia and VET have mapping grids too, but theirs name topics in prose rather than codes — not parsed. The Mathematics Standard syllabus DOCX is now saved alongside its papers. No subject JSON, code path, credential, schema or pricing fact changed; no UI was built. Full detail in `docs/HISTORY.md` (2026-08-27, later still, again). Previously (2026-08-27, latest+1) — **Mathematics Advanced Stage 2 complete; `category` is now derived, not guessed.** Facts changed here: the official **Mathematics Advanced Stage 6 Syllabus (2017)** DOCX is saved in `NESA Exams Folder/Maths Advanced/` (with the Standard/Advanced common-content PDF) and has been read in full — 14 subtopics, **358 content dot points**, both years. The topic list and `category` code set live in a new **`docs/subject-plans/{subject}.md`** convention (§6): Stages 1–3 share one working document per in-flight port, while Stage 0's Fit Report stays in `docs/paper-reports/`. New **`scripts/build_mapping_grid.py`** (§6) extracts NESA's official **Mapping Grid** — marks + syllabus content code + outcome code per question part — to a new **`data/mapping-grid/`** (§6), committed on the same grounds as the answer keys; all six Maths Advanced papers reconcile to 100 marks with zero uncoded rows, and it agrees with `build_written_key.py` on every Section II part. **Use the grid for per-question `category`; use the syllabus for topic weighting** — they diverge sharply (MA-C1 is 10.6% of scope and 1.3% of examined marks; MA-T3 is 1.7% and 6.8%), and getting it backwards is the VET failure repeating. Two new extraction traps recorded: a syllabus code can **split across words** in the text layer (`MA- M1`), and a grid row's cell text is **vertically centred so it can begin above its own label line**. ⚠️ Advanced's `F1`/`M1`/`S1`/`S2` collide with Standard 2's category codes and mean different things — never key a shared lookup on the bare code. ⚠️ NESA runs **two live syllabuses**: 2017 governs every paper we hold and the 2026 HSC; **2024 takes over at the 2027 HSC**, so this topic list is dated. Playbook corrected in three places: the syllabus-download question now belongs at **Stage 0**, not Stage 2 (raising it three stages after the GO turned a predictable input into a blocker); **Stage 2 does not depend on Stage 1** — the one exception to strict stage ordering; and Gate 2 gains the mapping-grid reconciliation. No code, credential, schema or pricing facts changed; nothing ported, subject still registered nowhere. Full detail in `docs/HISTORY.md` (2026-08-27, later again). Previously (2026-08-27, latest) — **Porting playbook run for real; Mathematics Advanced Stage 0 = GO.** Facts changed here: `docs/paper-reports/` now exists and holds its first file ever, **`mathematics-advanced.md`** (§6) — the Stage 0 Fit Report. A **human Stage 0 writes one subject-level report (`{subject}.md`) with per-year rows**; the per-paper `{subject}-{year}.md` shape belongs to the Content Agent, whose `triagePaper()` genuinely runs once per paper (it has still never run). §11 gains a **Mathematics Advanced** roadmap row: papers 2020–2025 are local, 10 MC + 90 written marks per paper, ~93% portable, notation `basic` — nothing ported, subject registered nowhere in code, Stage 1 next, **Stage 2 blocked until the owner is asked about the syllabus**. Three tooling facts worth knowing before Stage 6: **`build_written_key.py`'s `-mg.pdf` glob does not match `{year}_marking_guidelines.pdf`** and exits "no marking-guideline PDFs" (its sibling `build_answer_key.py` uses the tolerant `find_papers()` and is fine) — recorded as a Stage 6 prerequisite, deliberately not fixed at Stage 0; this folder carries a **third PDF per year**, `{year}_marking_feedback.pdf`, which `find_papers()` classifies correctly only because it tests `"feedback"` before `"marking"`; and §10 rule 8's digit-regex warning was **reproduced live** (a naive pass read Section II as 106/113/117 against a true 90). Read-only dry runs of both key builders reconciled **exactly 90/90 on all six papers with zero unresolved parts** — that dry run is now a Gate 0 checklist item in the playbook. No code, credential, schema or pricing facts changed; no question content was touched. Full detail in `docs/HISTORY.md` (2026-08-27, later still). Previously (2026-08-27, later still) — **Written-answer key built and enforced in CI.** Facts changed here: a new **`data/answer-key/written/`** (§6) holds the official maximum marks and sample answers for every written question part in the three subjects with past papers, built by **`scripts/build_written_key.py`** and enforced by **`scripts/check_written_key.cjs`**, now a step in `validate.yml` (§4.4) — **203 bank questions check, 0 wrong, 0 unverifiable**. Only the *mark* is enforced; sample answers are committed for human review, since prose cannot be compared for equality. **New §10 rule 8** records the three things that matter: join by **aggregating to the question** rather than part-for-part (the bank stores parts as `16`, `"23(a)"` and `"19(b)(i)"`, and 2020/2021 Maths split what 2022–2025 merge — one prefix-sum rule reconciles all three); a whole question the engine can't present is declared in a new subject-level **`omittedQuestions`** key, the companion to `omittedParts`, with the checker validating each declaration so it can't rot; and the extractor reads the Marks column **positionally**, stopping at the answer heading, because a digit regex over the block over-counts (2020 Maths reads 117 against a true 85). Three extraction traps are recorded, each of which broke a real paper: `Answers could include:` is the other spelling of `Sample answer:`; extended-response criteria use mark *ranges* that the text layer splits mid-number (`9–1` + `0`); and page furniture must be filtered from the criteria scan or `Page 18 of 23` becomes a 23-mark question. Every paper reconciles against the section totals printed on the exam's own front page (Maths 85, Multimedia 30, VET 65). Content changed: `subjects/multimedia.json` gains an `omittedQuestions` entry recording that **2021 Q12 is a drawing task** the engine cannot mark — a legitimate omission that had never been recorded, and the only coverage gap in an otherwise complete six-year Section II port. No NESA wording was altered; no question content, answers or marks changed. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27, later still). Previously (2026-08-27, later) — **VET 2021 Q15's option images cropped; the sweep found a worse case in Multimedia.** Facts changed here: the §11 known issue for VET 2021 Q15 is **closed and its row removed** — the four cross-sections are cropped and wired as `optionImages`, with no answer or option-text change. Two new scripts of record in §6: **`scripts/crop_vet_2021_q15_options.py`** and **`scripts/crop_multimedia_2022_q2_stimulus.py`**, both deriving crop boxes from an **ink profile** of the rendered page rather than the text layer — on VET 2021 p7 the option letters and axis labels are outline **paths**, so `get_text()` and `get_drawings()` both miss them. The VET crops deliberately **exclude** the paper's own `A.`/`B.` glyph (unlike the 56 existing Maths option crops) because `index.html` renders its own option label; option order is safe to depend on, since `shuffle()` shuffles the question list, never options. A new MC schema key **`optionImagesWide`** (§10) opts a question out of the `.options-grid-2x2` layout: these cross-sections are ~4.6:1 and rendered **160×35px** at a 430px viewport, which the existing 380px single-column fallback does not catch; they now render 360×78. **New §10 rule 7: a question with no image at all can still be an image question** — where a stimulus was never cropped, a port has sometimes *described* the missing picture, and the description can be wrong while the answer stays right, so CI passes and the question is still unanswerable. Content changed: **Multimedia 2022 Q2** — stimulus cropped, stem restored to the paper's wording, and all four `optionExplanations` rewritten, after its parenthetical descriptions (`outline star / filled circle / filled star`) were found to be wrong about all three pictures, sending a correctly-reasoning student to A against the correct key answer D. **The answer did not change**, and no NESA wording was altered. Process note recorded in `docs/HISTORY.md`: **never round-trip a subject JSON through `json.dumps` for a small edit** — it reformatted `multimedia.json` into a 461-line diff by expanding the compact inline arrays in `studyNotes`; use targeted text replacement. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27, later). Previously (2026-08-27) — **Answer-key coverage completed for Multimedia and VET; six wrong VET answers fixed.** Facts changed here: `data/answer-key/` now holds **all three** subjects with past papers — `multimedia.json` (60 answers, 2020–2025) and `vet-construction.json` (75, 2021–2025) join Maths' 90 — and **every MC question in all three carries `qNum`, so all 225 are verifiable and CI enforces all 225** (§6). A new **`scripts/backfill_qnum.py`** (§6) derives `qNum` by matching questions to the exam paper on **exact option-set equality only**, reporting what it cannot resolve rather than scoring similarity; `--write` refuses unless a subject resolves completely. §10's answer-key rule block is updated throughout: rule 1 now names Multimedia 2022's actual stored order (1, 3, 4, 5, 6, 8, 9, 10, 7, 2) and warns that *every other* year being in paper order is what makes position tempting; rule 2 no longer says 135 questions are unauditable (none are) and points at the new script; rule 3 gains the two structural traps in reading a NESA paper — the question number sits in its own left-margin text column (so a linear `get_text()` emits every number before any body text; read by *(page, y)*) and the page footer/copyright line gets swallowed into option D unless filtered. **New rule 6: a passing check does not mean the options are right** — the official letter indexes the *paper's* option order and option *text* is invisible to the check, and four questions were found where an image question's invented option labels described the wrong picture. `docs/handover-answer-key-multimedia-vet.md` is **deleted** (task complete); its forward-looking notes on the written-answer table live in `docs/HISTORY.md` (2026-08-27). Content changed: VET 2021 Q1 → C, 2022 Q13 → B, 2022 Q15 → A, 2023 Q11 → D, 2024 Q11 → D, 2025 Q1 → C, each re-derived from the paper and all six `optionExplanations` sets rewritten; option text corrected on VET 2021 Q15, VET 2022 Q7/Q13 and Multimedia 2021 Q1. Multimedia's 60 answers were already correct. §11 gains one **known issue**: VET 2021 Q15's four cross-section *option* images were never cropped (only its site-plan stimulus was), so the question runs on text descriptions of the four curves — accurate as of this pass, but not the paper's own form; the entry also asks for a sweep of other image questions with bare-letter options in case the same gap exists elsewhere. No NESA wording was altered. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27). Previously (2026-08-26) — **HSC answer-key database added; five wrong Maths answers fixed.** Facts changed then: a new top-level **`data/answer-key/`** holds the official HSC answers as committed ground truth (§6), generated by **`scripts/build_answer_key.py`** and enforced in CI by **`scripts/check_answer_key.cjs`**, now a step in `validate.yml` (§4.4). §10 gains a mandatory rule block — **HSC answers are ground truth in `data/answer-key/`, never re-derive them by reading** — written after a prior audit passed a bank that had five wrong 2025 Maths answers, and after this session's own first two passes produced twelve phantom errors by joining on array position. Key points: never assume array position equals question number; a question with no `qNum` is *unverifiable*, not correct (Multimedia and VET have none — 135 questions unauditable); fuzzy text-matching the exam PDFs is not a join (render the page and read it instead); and deliberate omissions get an `omittedParts` entry rather than vanishing (2020 Q24's graph-drawing part, which left Section II at 84/85). Content changed: 2025 Maths Q1/Q2/Q3/Q8/Q13 answers corrected to B/A/C/A/A with all five solutions rewritten, Q2 and Q8 option labels re-aligned to their own images, and Q2's stem corrected from `4<em>x</em>` to `4<sup><em>x</em></sup>`. No NESA wording was altered. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-26). Previously (2026-08-25) — **HMS de-PDHPE'd and audited.** Facts changed here: the subject file is now `subjects/health-movement-science.json` (§6 tree, §10), the §7 row reads **Health & Movement Science (HMS)** at 193 MC / 40 written, and §7 now records that HMS is a **new subject for 2026** superseding PDHPE — **2026 is its first HSC exam year, so no HMS past papers exist** (only NESA sample materials; PDHPE 2020–2024 is a reference point but a different exam). Critically, `SUBJECT_ID_MAP` (JSON fetch URL) and `SUBJECT_CATALOGUE[].id` (billing id, written to Supabase `subject_selections.subject_id`) are **separate and no longer share a value** — `pdhpe-hms` survives only as the billing id, the artwork SVG key, the reverse id→quizKey map and the `/diagrams/pdhpe-hms_*` prefix; renaming it needs a migration against live user rows. Two new mandatory rules in §10, both written after real failures: **verify exam citations against the actual paper** (a session shipped "HSC 2024, PDHPE, Section I Part B, Q31.b" — wrong section, marks and wording — without opening the paper already on disk) and **diff a new block against its neighbours before inserting it** into an existing Study Mode topic, since an accuracy audit is not an editorial review. §10 also records that `validate_subjects.cjs` does **not** existence-check `studyNotes` images and that those images are `loading="lazy"` (so `naturalWidth` reads 0 in a hidden Browser pane). No credential, schema or pricing facts changed. The HMS `biomechanics-recovery-injury` topic was audited against the owner's school workbook and rebuilt (2→19 blocks over two sessions): three factual fixes, topics refiled from the FA1 to the FA2 picker bucket, a CC BY 4.0 OpenStax fracture diagram added, two syllabus concept maps built natively as `table` blocks, and a full de-duplication pass. Full detail in `docs/HISTORY.md` (2026-08-25 entries). Earlier (2026-08-08): CI security scanning added — `.github/workflows/security-scan.yml` (Semgrep + Trivy report-only to the Security tab, Gitleaks **blocking**), additive alongside `validate.yml`/`content-agent.yml`.*
*Repo: https://github.com/bustachat/CramIT-Quiz*
*Supabase: https://ohqtefjawaphtsebnaxg.supabase.co*
