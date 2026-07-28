# CLAUDE.md — CramIT Project Instructions

> **Strategy for every task: Explore → Plan → Code → Verify → Commit → Docs**
> Before touching a single line of code, read the relevant files. Then write a plan in plain English. Only then write code.

> **Global rules (API cost optimisation, file safety, security, git, communication) also apply — see `~/.claude/CLAUDE.md`**

> **This file is deliberately short.** Full session-by-session history (what changed, why, and how it was verified) lives in [`docs/HISTORY.md`](docs/HISTORY.md) — not auto-loaded, read it only when investigating why something was built a certain way. Agent-infrastructure planning (Stage 9) lives in [`docs/agents-plan.md`](docs/agents-plan.md) — not needed for day-to-day app/billing/content work.

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
| `validate.yml` | Every push + PR | Validates subject JSON (`scripts/validate_subjects.cjs`) + syntax-checks Cloudflare functions |
| `content-agent.yml` | Nightly `0 13 * * *` (11pm Sydney) + manual Run-workflow button | Runs `agent.js` (NESA discovery → paper triage → question generation), opens a PR on an `agent/content-*` branch — **never pushes to main** |

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
│   └── content-agent.yml       ← Nightly Content Agent — runs agent.js, opens PR on agent/content-* branch (needs ANTHROPIC_API_KEY secret)
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
├── db/
│   └── schema.sql              ← Supabase tables + RLS + triggers (incl. user_progress + entitlement trigger)
├── migrations/
│   └── 2026-07-02_subject_entitlement.sql ← entitlement trigger (already run in Supabase)
├── icons/                      ← PWA icons (icon-192.png, icon-512.png), generated from CramIT_Logo_Transparent.png
├── scripts/                    ← Extraction/audit tooling + registries
│   ├── extract_maths_diagrams.py      ← PDF diagram extractor v3 (PyMuPDF + Pillow + calibration)
│   ├── extract_written_diagrams.py    ← Written-question stimulus extractor
│   ├── validate_subjects.cjs          ← Structural validation for all subject JSON (also runs in CI)
│   ├── diagram_registry.json          ← Crop coordinates for MC diagram images
│   ├── written_diagram_registry.json  ← Crop registry for written stimulus images
│   ├── process_maths_backlog.js       ← Backlog processor for question generation
│   └── archive/                       ← Completed one-off migration scripts (kept for reference)
├── diagrams/                   ← Exam diagram images — served by Cloudflare Pages at /diagrams/
│   ├── .gitignore              ← Excludes _debug/ folder from git
│   └── {subject}_{year}_Q{n}_{suffix}.jpg|png  (suffix = stimulus | A | B | C | D)
├── subjects/                   ← ✅ All question data lives here (one JSON per subject)
│   ├── index.json              ← List of subject files (⚠️ informational only — the app hardcodes subjects in SUBJECT_ID_MAP/SUBJECT_CATALOGUE)
│   ├── mathematics-standard-2.json    ← 318 MC + 151 written + 73 tips + studyNotes (all 16 topics, alphabetically ordered A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5; no writingScaffolds — see docs/HISTORY.md)
│   ├── pdhpe-hms.json                 ← 165 MC + 35 written + studyNotes (9 topics, block-ordered content + 74 revision questions) + writingScaffolds (3 mark-band scaffolds) — prototype content for the Study Mode/Exam Mode front page (index.html, HMS only, see §11)
│   ├── multimedia.json                ← 60 MC + 29 written
│   └── vet-construction.json          ← 75 MC + 23 written
├── docs/
│   ├── HISTORY.md              ← Full session log — read on demand, not auto-loaded
│   ├── agents-plan.md          ← Stage 9 agent roster/build order — read on demand
│   └── paper-reports/          ← Content Agent triage reports ({subject}-{year}.md) — briefing docs for porting new subjects
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
| PDHPE — HMS Depth Study | `hms` | `pdhpe-hms` | MC + written | 165 MC, 35 written | ✅ `CLAUDE.AI - HMS_In_Depth_Study_YR12_quiz.html` |
| VET Construction | `vet` | `vet-construction` | MC + written | 75 MC, 23 written, 2021–2025 | ✅ `VET_Construction_Quiz_v6 (...).html` |
| Industrial Technology — Multimedia | `multimedia` | `multimedia` | MC + written | 60 MC, 29 written, 2020–2025 | ✅ `CLAUDE.AI - HSC_Multimedia_Quiz (...).html` |

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
**Study Mode & Exam Mode (HMS full, Maths pilot — see §11):** `pdhpe-hms.json` (9 topics) and `mathematics-standard-2.json` (1 topic so far, F1) have `studyNotes: [ { id, icon, title, focusArea, accentColor, blocks: [...], revisionQuestions: [{q, a}] } ]` (`focusArea` is HMS-only metadata, unused by the renderer — safe to omit) and, optionally, `writingScaffolds: [ { id, label, introNote, steps: [{heading, html}], modelAnswerLabel, modelAnswer } ]` (Maths has none yet — `renderWritingHelpHtml()` shows an empty-state message when absent, no engine change needed). The engine (`renderStudyBlock()`, `hasStudy` flag) is fully subject-agnostic — enabling Study Mode for a new subject is just adding the `studyNotes` key to its JSON and `hasStudy: true` to its entry in `index.html`'s `SUBJECTS` object. `blocks[]` is an **ordered** sequence preserving the source content's exact layout — each entry is `{type:'noteGrid', boxes:[{heading,html}]}` (1 or 2 boxes; 2 renders as a side-by-side 2-column pair), `{type:'image'|'imageGrid', ...}` (image objects carry `src`/`alt`/`title`/`caption`/`style` — `style` preserves any inline sizing like `max-height` so paired images stay visually uniform), `{type:'table', caption, headers, rows}` (rendered as `.study-dtable`, a mobile-responsive stacked-card table reusing the pattern from `olivier-hms-exam-prep.html`'s `.dtable`), `{type:'examTip'|'linkIt', ...}`. Rendered by `index.html`'s `renderPicker()`, which shows a Study Mode/Exam Mode segmented-control toggle (`.seg-control`, reusing the same component as the Year/Category/Assessment filters — not a bespoke button style) as the front page for any subject with `hasStudy: true`; Exam Mode is exactly today's existing quiz picker (`renderExamModeHtml()`), unchanged. Study Mode has its own nested Notes/Writing Help toggle. Gating is a free-preview model, not the usual all-or-nothing trial lock: `STUDY_FREE_TOPIC_COUNT` (currently 1) topics are always free, the rest show locked with a 🔒 and no body HTML rendered into the DOM; Writing Help is fully gated. `validate_subjects.cjs` ignores these keys (permissive of unknown top-level keys) — no validator changes were needed.

### Written question stimulus text — never re-extract from PDFs
All NESA PDF text/block positions for written questions are pre-extracted into `written_q_extracts.json` (repo root). **Always read this file first** — re-extracting from a PDF wastes tokens every session. Content rule: plain text → `q` field; diagram → `<img>` tag embedded inline in `q`, `image` field set `null`; table → `<table>` HTML reconstructed from the extract data; no SVGs, always crop from the PDF as JPG.

### Adding a new subject
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
| Study Mode & Exam Mode front page (HMS prototype + Maths complete) | 🔶 HMS built 2026-07-26 (full — diagrams, comparison tables, 74 revision questions, free-preview gating). Maths started and finished 2026-07-28 — all 16 syllabus categories done, built one topic at a time by owner's explicit preference, then reordered alphabetically A-first (A1, A2, A4, F1, F4, F5, M1, M2, M6, M7, N2, N3, S1, S2, S4, S5; original-wording notes since Maths has no standalone prose source to port from, unlike HMS) — see docs/HISTORY.md for per-topic detail. ⚠️ The free-preview topic (`STUDY_FREE_TOPIC_COUNT`, gates by array position) shifted from F1 to **A1** as a side-effect of the reorder. No Notes/Writing Help toggle for Maths at all (hidden when `writingScaffolds` is empty — data-driven, HMS unaffected). **Multimedia complete 2026-07-29** (all 7 Study Mode topics built, see `docs/HISTORY.md`): topic list re-grounded in the real NESA syllabus (pulled all 6 years of official marking-guideline mapping grids, not just keyword-matched against the exam bank) — Text & Document Design, Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics, all ✅ (47 blocks, 42 revision questions total). Scope is deliberately Sections I & II content only (matches the existing 89-question bank); Section III (15 marks/exam, rotating business/industry themes — WHS, environmental factors, industrial relations, automation, etc. — never ported into the bank) is a known, deferred gap, same treatment as the Content Agent's written-question-generation gap. Writing Help — a single "Short Answer — 1–5 marks" scaffold (not HMS's two-tier split), since the in-scope written bank tops out at 5 marks — is the next possible follow-up, **not built yet**. No standalone prose source exists (original authoring, like Maths); the 89-question bank has no `category`/`topic` field, so topics were defined from the syllabus, not filtered from existing data. VET not yet started. HMS's 4 non-photo diagrams (SMART goals grid, tapering bar chart, inverted-U SVG, HOWSCSE grid) still deferred — need bespoke CSS ported, not just an image copy. |
| Design aesthetics review (all subjects) | ⬜ Not started — flagged 2026-07-27 as a next-focus item. Warm earth-tone tokens (§15) are locked, but overall visual polish/consistency across screens hasn't had a dedicated pass since early stages. |
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

*CLAUDE.md — CramIT Project — Last updated: 2026-07-29 — Multimedia Study Mode complete: all 7 topics built (Text & Document Design, Graphics, Animation, Video, Audio, World Wide Web, Intellectual Property & Ethics — 47 blocks, 42 revision questions), topic list grounded in the official NESA marking-guideline mapping grids (all 6 years, 2020–2025) rather than keyword-matched against the exam bank, surfacing a known gap — Section III (15 marks/exam, rotating business/industry themes) was never ported into the bank and is deliberately out of scope; topics 1–2 built one-at-a-time per the owner's standing pacing preference, then the owner explicitly said "keep going until complete" so topics 3–7 were built in one continuous pass — a one-off override, not a change to the standing preference; Writing Help (single "Short Answer 1–5 marks" scaffold) is the next possible follow-up, not yet built (§6/§11); earlier (2026-07-28): Study Mode Maths build completed and reordered: all 16 syllabus categories now have notes, alphabetically ordered A1→S5 (§6/§10/§11 — note the free-preview topic shifted from F1 to A1 as a result), Notes/Writing Help toggle hidden when a subject has no writingScaffolds; earlier (2026-07-27): an automated billing test harness, a "Manage subjects" removal feature, and deferred-downgrade billing (Stripe Subscription Schedules) were built, broke live, rolled back, and were fixed and confirmed working — see `docs/HISTORY.md`; that session also phased the Study Mode rollout (P1 Maths, P2 VET, then Multimedia — superseded now that Maths work has started) and flagged a design aesthetics review as next focus (§11); before that: Study Mode/Exam Mode front page added to index.html (HMS prototype); before that: Content Agent rebuilt (triage + generation, PR-only, nightly via content-agent.yml); before that: restructured, session history moved to docs/HISTORY.md.*
*Repo: https://github.com/bustachat/CramIT-Quiz*
*Supabase: https://ohqtefjawaphtsebnaxg.supabase.co*
