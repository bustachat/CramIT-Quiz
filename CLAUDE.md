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
│       ├── mathematics-standard-2.json  ← 90 MC answers, 2020–2025
│       ├── multimedia.json              ← 60 MC answers, 2020–2025
│       └── vet-construction.json        ← 75 MC answers, 2021–2025
│       ├── written/                     ← Official WRITTEN marks + sample answers, same
│       │                                immutability rule. Built by scripts/build_written_key.py,
│       │                                enforced by scripts/check_written_key.cjs. 203 bank
│       │                                questions check against it; only the MARK is enforced —
│       │                                sample answers are prose, stored for human review only.
│       │                                No HMS file: no past papers exist yet.
│                                  All 225 are enforced in CI and all 225 are verifiable —
│                                  every MC question in all three subjects carries `qNum`.
│   └── mapping-grid/           ← ✅ GROUND TRUTH — NESA's official question→syllabus-code grid
│       │                          (marks + content code + outcome code per question part), from
│       │                          the end of the marking guidelines. Same immutability rule;
│       │                          regenerate with scripts/build_mapping_grid.py, never hand-edit.
│       │                          Use it to DERIVE `category`. It reflects what was EXAMINED, not
│       │                          syllabus SCOPE — the two diverge sharply, so never weight topics
│       │                          from it (see docs/subject-plans/mathematics-advanced.md).
│       ├── mathematics-advanced.json  ← 6 papers, 2020–2025, all reconciling to 100 marks
│       │                                with zero uncoded rows. Not yet wired into CI —
│       │                                the subject is not ported.
│       └── mathematics-standard-2.json ← 6 papers. Verified against the LIVE bank: its 16
│                                        `category` codes match the grid's exactly and all 90
│                                        original MC questions agree with NESA's tagging,
│                                        0 disagreements. Multimedia/VET have grids too, but
│                                        theirs name topics in prose, not codes — not parsed.
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
│   ├── check_written_key.cjs          ← CI: compares each written question's `marks` against the
│   │                                    committed key, aggregating parts (see §10). Reads no PDFs.
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
│   ├── multimedia.json                ← 60 MC + 29 written
│   └── vet-construction.json          ← 75 MC + 23 written
├── docs/
│   ├── HISTORY.md              ← Full session log — read on demand, not auto-loaded
│   ├── agents-plan.md          ← Stage 9 agent roster/build order — read on demand
│   ├── subject-plans/          ← Port RUNBOOK, one per in-flight port — the single entry point a
│   │   │                          fresh session opens. One stage per session, every established
│   │   │                          fact carried forward so a cold session never re-derives them.
│   │   └── mathematics-advanced.md  ← Stages 0 + 2 done; 1, 3–7 open with gates, traps, commands
│   │                                  and a paste-in session prompt. 294 question parts to port.
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
  optionImagesWide: true, // omit unless the option images are very wide/short (>~3:1). Keeps them one-per-row
                          // instead of the 2×2 grid, where they shrink to ~160×35px on a 430px phone.
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
   `node scripts/check_written_key.cjs`. **203 questions across the three subjects with past
   papers pass; HMS is excluded and stays excluded until after the 2026 HSC.** Only the *mark*
   is enforced — the official sample answer is committed alongside it for human review, but
   prose cannot be compared for equality (and Maths sample answers extract as mangled equation
   layout). Three things to know before touching it:
   - **Join by aggregating to the question, never part-for-part.** The bank stores parts as
     `16` (one entry for all parts), `"23(a)"` (one per part) and `"19(b)(i)"` (one per
     sub-part), and 2020/2021 Maths split questions that 2022–2025 merge. A bank entry's
     expected marks are the **sum of every official leaf part whose path starts with its
     path**, plus any `omittedParts`. That one rule reconciles all three storage shapes.
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
| Study Mode & Exam Mode front page (HMS prototype + Maths complete) | 🔶 HMS built 2026-07-26 (full — diagrams, comparison tables, 74 revision questions, free-preview gating). Maths started and finished 2026-07-28 — all 16 syllabus categories done, built one topic at a time by owner's explicit preference, then reordered alphabetically A-first (A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5; original-wording notes since Maths has no standalone prose source to port from, unlike HMS) — see docs/HISTORY.md for per-topic detail. ⚠️ The free-preview topic (`STUDY_FREE_TOPIC_COUNT`, gates by array position) shifted from F1 to **A1** as a side-effect of the reorder. No Notes/Writing Help toggle for Maths at all (hidden when `writingScaffolds` is empty — data-driven, HMS unaffected). **Multimedia complete 2026-07-29** (all 7 Study Mode topics built, see `docs/HISTORY.md`): topic list re-grounded in the real NESA syllabus (pulled all 6 years of official marking-guideline mapping grids, not just keyword-matched against the exam bank) — Text & Document Design, Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics, all ✅ (47 blocks, 42 revision questions total). Scope is deliberately Sections I & II content only (matches the existing 89-question bank); Section III (15 marks/exam, rotating business/industry themes — WHS, environmental factors, industrial relations, automation, etc. — never ported into the bank) is a known, deferred gap, same treatment as the Content Agent's written-question-generation gap. **Section III is scheduled as a Multimedia "upgrade phase" — sequenced AFTER VET Study Mode is complete** (owner decision, 2026-07-29): would add an 8th Study Mode topic plus new written questions (Section III has no existing bank content to build from, unlike topics 1–7). Writing Help — a single "Short Answer — 1–5 marks" scaffold (not HMS's two-tier split), since the in-scope written bank tops out at 5 marks — is a separate, smaller follow-up, **not built yet**. No standalone prose source exists (original authoring, like Maths); the 89-question bank has no `category`/`topic` field, so topics were defined from the syllabus, not filtered from existing data. **VET Study Mode complete 2026-07-30** (all 9 topics built in two sessions — topic 1 alone, then topics 2–9 in one continuous pass after the owner said "continue until complete"; see `docs/HISTORY.md` for full per-topic detail): Safety split into 2 topics (WHS & Risk Management; Safe Work Practices & Emergencies), Skills in Construction into 2 (Plans/Drawings/Specifications; Measurements & Calculations), Tools of the Trade into 2 (Hand & Power Tools; Tool Selection/Safety/Care/Security), Working in the Industry into 3 (Industry Structure/Careers/Employment; Work Instructions/Teamwork/Workplace Conduct — includes cultural diversity/anti-discrimination content that has **never appeared in any of the 4 years of exam papers checked**; Task Planning & Sustainability) — all ✅, 71 blocks and 54 revision questions total, proportional to the syllabus's actual scope-of-learning table sizes (Working in the Industry = 80 rows, nearly double Safety's 48), not exam-history mapping grids alone — this is the topic list §10's mandatory syllabus-check rule was written to enforce. `vet-construction.json`'s 75 MC/23 written questions have no `category`/`topic` field (same as Multimedia) — topics defined from the syllabus, not filtered from existing data. One icon bug (topic 6's 🔒 colliding with the gating lock badge) was caught by browser regression, not JSON validation, and fixed to 🧰 — a reminder that icon/visual choices still need the browser check even when content is syllabus-verified. **Tool/PPE reference icons added same day** (27 small PNGs — hammer, chisel, drill bits, PPE items etc. — self-hosted in `icons/vet-construction/`, sourced from Flaticon author `juicy_fish`'s "Flat" style, free with attribution): wired as inline `<img>` tags into the Hand & Power Tools and Safe Work Practices & Emergencies topics' existing tables/bullets — see `docs/HISTORY.md` for the full sourcing/licensing story, including two links the owner initially picked that turned out broken (a Vecteezy preview thumbnail, a style-mismatched freesvg.org icon) and were dropped rather than faked. **Flaticon attribution is still unplaced** — see known issues below. HMS's 4 non-photo diagrams (SMART goals grid, tapering bar chart, inverted-U SVG, HOWSCSE grid) still deferred — need bespoke CSS ported, not just an image copy. |
| **Exam Trends panel in Study Mode** | 🔶 **Data layer built 2026-08-27, UI not started.** `data/exam-trends/{subject}.json` holds, per topic: syllabus scope share, examined mark share, marks per paper, years present (e.g. "6 of 6 papers"), MC/written split, a per-year series for a sparkline, and `yieldRatio`. Live for **Maths Standard 2** and **Maths Advanced**. Origin: owner's own Drive analysis of exam trends — the idea is theirs, the numbers are now measured from NESA's mapping grids rather than word-frequency estimates. **Open decision: where it renders** (per-topic Study Mode header badge, a dedicated topic-ranking screen, or both) — a design call, not taken unilaterally. Multimedia/VET need a prose-grid parser first. |
| Design aesthetics review (all subjects) | ⬜ Not started — flagged 2026-07-27 as a next-focus item. Warm earth-tone tokens (§15) are locked, but overall visual polish/consistency across screens hasn't had a dedicated pass since early stages. |
| **Mathematics Advanced — new subject port** | 🔶 **Stages 0–3 complete (2026-08-27/28).** Stage 0 = **GO** (`docs/paper-reports/mathematics-advanced.md`): 2020–2025 papers + guidelines local, 10 MC + 90 written marks/paper, notation `basic`. Stage 2: official **2017** syllabus read (14 subtopics, 358 dot points), `category` codes fixed, `data/mapping-grid/mathematics-advanced.json` gives every question's official topic. ⚠️ The **2024** syllabus takes over at the **2027 HSC** — this topic list is dated. **Stage 1 (Survey) complete**: all **294 parts classified**, with per-question crop, table and omission lists in `docs/subject-plans/mathematics-advanced.md`. Measured cost: **121 crops + 28 tables** (Stage 0's "~100" was low), **17 unportable drawing parts / 41 marks**, portable share **93.2%**, and **42% of parts carry a detectable text-layer corruption**. Two Stage 0 facts corrected there: **√ and ∞ are printed but drawn as paths, so neither exists in the text layer** ("no radical sign" was an artefact of reading it), and **only 2024 uses the MathType `^…h` bracket mapping** — every year loses π to the letter `p` and re-orders stacked fractions. **Stage 3 (Schema) complete (2026-08-28)**: field mapping is **fully canonical, zero deviations**, and all **ten** decisions are recorded in the runbook (the six carried, plus four found by reading the engine) — piecewise braces, integrals/fractions, table-row options, blank tables, the two omission keys, the Unicode set, the 21 multi-code parts, the label collision, wide tables, and the written badge. Every rendering claim was **measured in a browser at 430px**, not inferred. **Two one-line engine fixes are blocking for Stage 7**: `NESA_CAT_LABELS` is a flat global map and **5 of Advanced's 14 codes collide with Standard 2's** (`F1 F2 M1 S1 S2`, each meaning something different) — the data keeps bare codes and the map becomes subject-aware; and the **written-question badge reads `q.topic`, not `category`**, so all 151 Standard 2 written questions have shown no topic badge since their port (the HMS marks-badge defect, second instance). **Stages 4 and 5 are now merged** (2026-08-28): `validate_subjects.cjs` exits 1 on a question whose `image` path has no file yet, so porting all six papers before cropping would hold CI red for six sessions and makes Gate 4's own "validator green, `missingImages: 0`" unsatisfiable — each session now ports **one year and crops that year's assets**, finishing green, on a **`port/maths-advanced` branch** merged to main only when the subject is complete. Stage 5 survives as the asset-method reference. Per-year load splits Stage 1's lists exactly (121 crops + 28 tables) and **overturned the suggested order: 2024 is the heaviest paper at 30 assets, not the lightest** — its "2 graphic-bearing MC" claim came from Stage 0 and Section I actually has seven. **Order is now 2020 → 2023 → 2022 → 2025 → 2021 → 2024**, tracked per year in the runbook. Nothing ported; subject registered nowhere in code. |
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

*CLAUDE.md — CramIT Project — Last updated: 2026-08-28 (later) — **Mathematics Advanced Stage 3 (Schema) complete: the field mapping is canonical with zero deviations, and two live engine defects were found.** Facts changed here: the §11 roadmap row now records **Stages 0–3 done, with Stage 4 (Port) next**, and all ten schema decisions live in `docs/subject-plans/mathematics-advanced.md`. §10 gains a new rendering rule: **a question table with 7+ columns is silently clipped on a phone unless wrapped in `overflow-x:auto`** — question stems render tables as `.q-table`/`.nesa-table`, **never** Study Mode's `.study-dtable` (the question renderer never applies it), and neither collapses *or* scrolls; measured at a 430px viewport, an 8-column table renders 513px into a 390px stem and `body{overflow-x:hidden}` cuts the rest off with no scrollbar and no error. The same correction landed in `docs/porting-playbook.md`, which had asserted the opposite. **Two one-line `index.html` fixes are now blocking for that port's Stage 7**, both recorded in the runbook: `NESA_CAT_LABELS` is one flat global map keyed on the bare syllabus code, and **5 of Mathematics Advanced's 14 codes collide with Mathematics Standard 2's** (`F1 F2 M1 S1 S2` — e.g. Advanced's `M1` is Modelling Financial Situations, Standard 2's is Measurement), so the map must become subject-aware while the data keeps bare codes; and the **written-question renderer badges `q.topic` while the MC renderer badges `q.category || q.topic`**, so every written question following the canonical field shows no topic badge — **all 151 Standard 2 written questions have been in that state since their port**, the same silent, CI-invisible defect as HMS's missing marks badge. The playbook records this second instance beside the first. No credential, schema, pricing or file-structure fact changed; no question content was touched, and Mathematics Advanced is still registered nowhere in code. Stages 4 and 5 of that port are also **merged into one interleaved stage** run on a **`port/maths-advanced` branch** — the validator exits 1 on an image path with no file, which made the old order hold CI red for six sessions; the per-year split also **corrected the suggested paper order to 2020-first**, since 2024 turns out to be the heaviest paper rather than the lightest. Full detail in `docs/HISTORY.md` (2026-08-28, later). Previously (2026-08-28) — **Mathematics Advanced Stage 1 (Survey) complete: all 294 parts classified.** Facts changed here: the §11 roadmap row now records Stages 0, 1 and 2 done, with **Stage 3 next**. The full per-question crop, table and omission lists live in `docs/subject-plans/mathematics-advanced.md`. Measured, not estimated: **121 crops + 28 tables** (Stage 0's "~100 image assets" was low), **17 unportable drawing parts / 41 marks** (7.6% of Section II; portable share **93.2%**, confirming Stage 0), and **124 of 294 parts (42%) carrying a detectable text-layer corruption**. **Two Stage 0 facts are corrected**, both because they were read off the text layer rather than the page: **√ and ∞ are printed but drawn as vector paths**, so neither character exists in any paper's text layer ("notation `basic` — no radical sign" was an artefact); and while the text layer is garbled on every paper, **only 2024 uses the MathType `^…h` / `]…g` bracket mapping** Stage 0 quoted — what all six share is π extracting as the letter `p`, ∞/√ missing, and stacked fractions split and re-ordered (91 of 294 parts contain one). Two Section I classifications are corrected too (2020 Q9 has option images, 2021 Q6 has a stimulus). **Playbook corrected in two places** (§2): its stem-sweep regex misses `which of these …` and `a possible sketch`, both picture-option questions; and a new method rule — **no single graphic detector is complete, union three and then look at the pages** (text-gap bands, `find_tables()`, ink profile; four Section II diagrams surfaced only in the union). Stage 3 now carries six schema decisions rather than two, including **options printed as rows of a table** (2020 Q2/Q3, 2022 Q2, 2023 Q4) and **blank tables the student fills in** (2024 Q11, Q13). `optionImagesWide` is **not** needed for this subject — all 12 option sets measure 0.8:1 to 2.6:1. No code, credential, schema or pricing fact changed; nothing ported, subject still registered nowhere. Full detail in `docs/HISTORY.md` (2026-08-28). Previously (2026-08-27, latest+2) — **Exam-trend data built: syllabus scope vs examined marks, for both maths subjects.** Facts changed here: a new **`data/exam-trends/`** (§6) holds per-topic study weighting for `mathematics-standard-2` and `mathematics-advanced`, built by new **`scripts/build_exam_trends.py`** from the syllabus DOCX plus the mapping grid — scope share, exam share, marks per paper, years present, MC/written split, per-year series, and `yieldRatio`. **⚠️ Always show both axes**: marks alone tells a Standard 2 student to skip Data Analysis (13.5% of syllabus, 3.9% of marks) and an Advanced student to skip Introduction to Differentiation (10.6% / 1.3%), the Year 11 foundation every Year 12 calculus question assumes; scope alone hides that Annuities is 5 dot points earning 7.3% of the paper. §11 gains an **Exam Trends panel** roadmap row — data layer done, **UI placement is an open design decision**. `build_mapping_grid.py` now covers **Standard 2** as well (§6): all twelve papers across both subjects reconcile to 100 marks with zero uncoded rows, and the grid **independently verifies the live Standard 2 bank** — its 16 `category` codes match exactly and all 90 original MC questions agree with NESA's tagging, 0 disagreements. Three tooling facts: an outcome code is distinguished from a content code by **having digits before the hyphen** (`MS2-12-5` vs `MS-F4`); NESA's own 2020 Standard 2 grid contains a **typo** (`MS2-F4`), normalised through an explicit `SOURCE_TYPOS` table that prints every substitution rather than by loosening the regex; and **Section I's last question number differs per subject** (Standard 2 = 15, Advanced = 10). Multimedia and VET have mapping grids too, but theirs name topics in prose rather than codes — not parsed. The Mathematics Standard syllabus DOCX is now saved alongside its papers. No subject JSON, code path, credential, schema or pricing fact changed; no UI was built. Full detail in `docs/HISTORY.md` (2026-08-27, later still, again). Previously (2026-08-27, latest+1) — **Mathematics Advanced Stage 2 complete; `category` is now derived, not guessed.** Facts changed here: the official **Mathematics Advanced Stage 6 Syllabus (2017)** DOCX is saved in `NESA Exams Folder/Maths Advanced/` (with the Standard/Advanced common-content PDF) and has been read in full — 14 subtopics, **358 content dot points**, both years. The topic list and `category` code set live in a new **`docs/subject-plans/{subject}.md`** convention (§6): Stages 1–3 share one working document per in-flight port, while Stage 0's Fit Report stays in `docs/paper-reports/`. New **`scripts/build_mapping_grid.py`** (§6) extracts NESA's official **Mapping Grid** — marks + syllabus content code + outcome code per question part — to a new **`data/mapping-grid/`** (§6), committed on the same grounds as the answer keys; all six Maths Advanced papers reconcile to 100 marks with zero uncoded rows, and it agrees with `build_written_key.py` on every Section II part. **Use the grid for per-question `category`; use the syllabus for topic weighting** — they diverge sharply (MA-C1 is 10.6% of scope and 1.3% of examined marks; MA-T3 is 1.7% and 6.8%), and getting it backwards is the VET failure repeating. Two new extraction traps recorded: a syllabus code can **split across words** in the text layer (`MA- M1`), and a grid row's cell text is **vertically centred so it can begin above its own label line**. ⚠️ Advanced's `F1`/`M1`/`S1`/`S2` collide with Standard 2's category codes and mean different things — never key a shared lookup on the bare code. ⚠️ NESA runs **two live syllabuses**: 2017 governs every paper we hold and the 2026 HSC; **2024 takes over at the 2027 HSC**, so this topic list is dated. Playbook corrected in three places: the syllabus-download question now belongs at **Stage 0**, not Stage 2 (raising it three stages after the GO turned a predictable input into a blocker); **Stage 2 does not depend on Stage 1** — the one exception to strict stage ordering; and Gate 2 gains the mapping-grid reconciliation. No code, credential, schema or pricing facts changed; nothing ported, subject still registered nowhere. Full detail in `docs/HISTORY.md` (2026-08-27, later again). Previously (2026-08-27, latest) — **Porting playbook run for real; Mathematics Advanced Stage 0 = GO.** Facts changed here: `docs/paper-reports/` now exists and holds its first file ever, **`mathematics-advanced.md`** (§6) — the Stage 0 Fit Report. A **human Stage 0 writes one subject-level report (`{subject}.md`) with per-year rows**; the per-paper `{subject}-{year}.md` shape belongs to the Content Agent, whose `triagePaper()` genuinely runs once per paper (it has still never run). §11 gains a **Mathematics Advanced** roadmap row: papers 2020–2025 are local, 10 MC + 90 written marks per paper, ~93% portable, notation `basic` — nothing ported, subject registered nowhere in code, Stage 1 next, **Stage 2 blocked until the owner is asked about the syllabus**. Three tooling facts worth knowing before Stage 6: **`build_written_key.py`'s `-mg.pdf` glob does not match `{year}_marking_guidelines.pdf`** and exits "no marking-guideline PDFs" (its sibling `build_answer_key.py` uses the tolerant `find_papers()` and is fine) — recorded as a Stage 6 prerequisite, deliberately not fixed at Stage 0; this folder carries a **third PDF per year**, `{year}_marking_feedback.pdf`, which `find_papers()` classifies correctly only because it tests `"feedback"` before `"marking"`; and §10 rule 8's digit-regex warning was **reproduced live** (a naive pass read Section II as 106/113/117 against a true 90). Read-only dry runs of both key builders reconciled **exactly 90/90 on all six papers with zero unresolved parts** — that dry run is now a Gate 0 checklist item in the playbook. No code, credential, schema or pricing facts changed; no question content was touched. Full detail in `docs/HISTORY.md` (2026-08-27, later still). Previously (2026-08-27, later still) — **Written-answer key built and enforced in CI.** Facts changed here: a new **`data/answer-key/written/`** (§6) holds the official maximum marks and sample answers for every written question part in the three subjects with past papers, built by **`scripts/build_written_key.py`** and enforced by **`scripts/check_written_key.cjs`**, now a step in `validate.yml` (§4.4) — **203 bank questions check, 0 wrong, 0 unverifiable**. Only the *mark* is enforced; sample answers are committed for human review, since prose cannot be compared for equality. **New §10 rule 8** records the three things that matter: join by **aggregating to the question** rather than part-for-part (the bank stores parts as `16`, `"23(a)"` and `"19(b)(i)"`, and 2020/2021 Maths split what 2022–2025 merge — one prefix-sum rule reconciles all three); a whole question the engine can't present is declared in a new subject-level **`omittedQuestions`** key, the companion to `omittedParts`, with the checker validating each declaration so it can't rot; and the extractor reads the Marks column **positionally**, stopping at the answer heading, because a digit regex over the block over-counts (2020 Maths reads 117 against a true 85). Three extraction traps are recorded, each of which broke a real paper: `Answers could include:` is the other spelling of `Sample answer:`; extended-response criteria use mark *ranges* that the text layer splits mid-number (`9–1` + `0`); and page furniture must be filtered from the criteria scan or `Page 18 of 23` becomes a 23-mark question. Every paper reconciles against the section totals printed on the exam's own front page (Maths 85, Multimedia 30, VET 65). Content changed: `subjects/multimedia.json` gains an `omittedQuestions` entry recording that **2021 Q12 is a drawing task** the engine cannot mark — a legitimate omission that had never been recorded, and the only coverage gap in an otherwise complete six-year Section II port. No NESA wording was altered; no question content, answers or marks changed. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27, later still). Previously (2026-08-27, later) — **VET 2021 Q15's option images cropped; the sweep found a worse case in Multimedia.** Facts changed here: the §11 known issue for VET 2021 Q15 is **closed and its row removed** — the four cross-sections are cropped and wired as `optionImages`, with no answer or option-text change. Two new scripts of record in §6: **`scripts/crop_vet_2021_q15_options.py`** and **`scripts/crop_multimedia_2022_q2_stimulus.py`**, both deriving crop boxes from an **ink profile** of the rendered page rather than the text layer — on VET 2021 p7 the option letters and axis labels are outline **paths**, so `get_text()` and `get_drawings()` both miss them. The VET crops deliberately **exclude** the paper's own `A.`/`B.` glyph (unlike the 56 existing Maths option crops) because `index.html` renders its own option label; option order is safe to depend on, since `shuffle()` shuffles the question list, never options. A new MC schema key **`optionImagesWide`** (§10) opts a question out of the `.options-grid-2x2` layout: these cross-sections are ~4.6:1 and rendered **160×35px** at a 430px viewport, which the existing 380px single-column fallback does not catch; they now render 360×78. **New §10 rule 7: a question with no image at all can still be an image question** — where a stimulus was never cropped, a port has sometimes *described* the missing picture, and the description can be wrong while the answer stays right, so CI passes and the question is still unanswerable. Content changed: **Multimedia 2022 Q2** — stimulus cropped, stem restored to the paper's wording, and all four `optionExplanations` rewritten, after its parenthetical descriptions (`outline star / filled circle / filled star`) were found to be wrong about all three pictures, sending a correctly-reasoning student to A against the correct key answer D. **The answer did not change**, and no NESA wording was altered. Process note recorded in `docs/HISTORY.md`: **never round-trip a subject JSON through `json.dumps` for a small edit** — it reformatted `multimedia.json` into a 461-line diff by expanding the compact inline arrays in `studyNotes`; use targeted text replacement. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27, later). Previously (2026-08-27) — **Answer-key coverage completed for Multimedia and VET; six wrong VET answers fixed.** Facts changed here: `data/answer-key/` now holds **all three** subjects with past papers — `multimedia.json` (60 answers, 2020–2025) and `vet-construction.json` (75, 2021–2025) join Maths' 90 — and **every MC question in all three carries `qNum`, so all 225 are verifiable and CI enforces all 225** (§6). A new **`scripts/backfill_qnum.py`** (§6) derives `qNum` by matching questions to the exam paper on **exact option-set equality only**, reporting what it cannot resolve rather than scoring similarity; `--write` refuses unless a subject resolves completely. §10's answer-key rule block is updated throughout: rule 1 now names Multimedia 2022's actual stored order (1, 3, 4, 5, 6, 8, 9, 10, 7, 2) and warns that *every other* year being in paper order is what makes position tempting; rule 2 no longer says 135 questions are unauditable (none are) and points at the new script; rule 3 gains the two structural traps in reading a NESA paper — the question number sits in its own left-margin text column (so a linear `get_text()` emits every number before any body text; read by *(page, y)*) and the page footer/copyright line gets swallowed into option D unless filtered. **New rule 6: a passing check does not mean the options are right** — the official letter indexes the *paper's* option order and option *text* is invisible to the check, and four questions were found where an image question's invented option labels described the wrong picture. `docs/handover-answer-key-multimedia-vet.md` is **deleted** (task complete); its forward-looking notes on the written-answer table live in `docs/HISTORY.md` (2026-08-27). Content changed: VET 2021 Q1 → C, 2022 Q13 → B, 2022 Q15 → A, 2023 Q11 → D, 2024 Q11 → D, 2025 Q1 → C, each re-derived from the paper and all six `optionExplanations` sets rewritten; option text corrected on VET 2021 Q15, VET 2022 Q7/Q13 and Multimedia 2021 Q1. Multimedia's 60 answers were already correct. §11 gains one **known issue**: VET 2021 Q15's four cross-section *option* images were never cropped (only its site-plan stimulus was), so the question runs on text descriptions of the four curves — accurate as of this pass, but not the paper's own form; the entry also asks for a sweep of other image questions with bare-letter options in case the same gap exists elsewhere. No NESA wording was altered. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-27). Previously (2026-08-26) — **HSC answer-key database added; five wrong Maths answers fixed.** Facts changed then: a new top-level **`data/answer-key/`** holds the official HSC answers as committed ground truth (§6), generated by **`scripts/build_answer_key.py`** and enforced in CI by **`scripts/check_answer_key.cjs`**, now a step in `validate.yml` (§4.4). §10 gains a mandatory rule block — **HSC answers are ground truth in `data/answer-key/`, never re-derive them by reading** — written after a prior audit passed a bank that had five wrong 2025 Maths answers, and after this session's own first two passes produced twelve phantom errors by joining on array position. Key points: never assume array position equals question number; a question with no `qNum` is *unverifiable*, not correct (Multimedia and VET have none — 135 questions unauditable); fuzzy text-matching the exam PDFs is not a join (render the page and read it instead); and deliberate omissions get an `omittedParts` entry rather than vanishing (2020 Q24's graph-drawing part, which left Section II at 84/85). Content changed: 2025 Maths Q1/Q2/Q3/Q8/Q13 answers corrected to B/A/C/A/A with all five solutions rewritten, Q2 and Q8 option labels re-aligned to their own images, and Q2's stem corrected from `4<em>x</em>` to `4<sup><em>x</em></sup>`. No NESA wording was altered. No credential, schema or pricing facts changed. Full detail in `docs/HISTORY.md` (2026-08-26). Previously (2026-08-25) — **HMS de-PDHPE'd and audited.** Facts changed here: the subject file is now `subjects/health-movement-science.json` (§6 tree, §10), the §7 row reads **Health & Movement Science (HMS)** at 193 MC / 40 written, and §7 now records that HMS is a **new subject for 2026** superseding PDHPE — **2026 is its first HSC exam year, so no HMS past papers exist** (only NESA sample materials; PDHPE 2020–2024 is a reference point but a different exam). Critically, `SUBJECT_ID_MAP` (JSON fetch URL) and `SUBJECT_CATALOGUE[].id` (billing id, written to Supabase `subject_selections.subject_id`) are **separate and no longer share a value** — `pdhpe-hms` survives only as the billing id, the artwork SVG key, the reverse id→quizKey map and the `/diagrams/pdhpe-hms_*` prefix; renaming it needs a migration against live user rows. Two new mandatory rules in §10, both written after real failures: **verify exam citations against the actual paper** (a session shipped "HSC 2024, PDHPE, Section I Part B, Q31.b" — wrong section, marks and wording — without opening the paper already on disk) and **diff a new block against its neighbours before inserting it** into an existing Study Mode topic, since an accuracy audit is not an editorial review. §10 also records that `validate_subjects.cjs` does **not** existence-check `studyNotes` images and that those images are `loading="lazy"` (so `naturalWidth` reads 0 in a hidden Browser pane). No credential, schema or pricing facts changed. The HMS `biomechanics-recovery-injury` topic was audited against the owner's school workbook and rebuilt (2→19 blocks over two sessions): three factual fixes, topics refiled from the FA1 to the FA2 picker bucket, a CC BY 4.0 OpenStax fracture diagram added, two syllabus concept maps built natively as `table` blocks, and a full de-duplication pass. Full detail in `docs/HISTORY.md` (2026-08-25 entries). Earlier (2026-08-08): CI security scanning added — `.github/workflows/security-scan.yml` (Semgrep + Trivy report-only to the Security tab, Gitleaks **blocking**), additive alongside `validate.yml`/`content-agent.yml`.*
*Repo: https://github.com/bustachat/CramIT-Quiz*
*Supabase: https://ohqtefjawaphtsebnaxg.supabase.co*
