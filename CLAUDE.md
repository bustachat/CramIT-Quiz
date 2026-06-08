# CLAUDE.md — CramIT Project Instructions

> **Strategy for every task: Explore → Plan → Code → Commit**
> Before touching a single line of code, read the relevant files. Then write a plan in plain English. Only then write code. When done, provide exact commit instructions.

> **Global rules (API cost optimisation, file safety, security, git, communication) also apply — see `~/.claude/CLAUDE.md`**

---

## 1. What CramIT Is

CramIT is an AI-powered HSC exam practice platform for NSW students. It is a subscription-based Progressive Web App (PWA) that:
- Automatically monitors NESA for new exam papers nightly via a GitHub Actions agent
- Generates quiz questions using Claude AI and stores them as JSON files in the repo
- Delivers quizzes through a mobile-friendly PWA students can install on any device
- Handles billing via Stripe with per-subject pricing and a $19.99 cap

**The owner is a beginner-to-intermediate developer. Always explain the "why", not just the "what". Give complete, copy-paste-ready code. Never leave placeholders without explaining exactly what to fill in.**

---

## 2. The Explore → Plan → Code → Commit Workflow

Every task, no matter how small, follows this four-step process:

### Step 1 — EXPLORE
Before writing any code:
- Read every file that the task touches (`view` tool or `bash cat`)
- Check the GitHub repo for the latest version of any file you haven't seen: `https://github.com/bustachat/CramIT-Quiz`
- For billing tasks: read `billing.js`, `create-checkout.js`, `update-subscription.js`
- For quiz tasks: read the relevant subject HTML and compare against the reference design in `2020-25_HSC_Maths_Quiz_v5_4__With_New_additional_Variants_Questions___Design_.html`
- For agent tasks: read `agent.js` and the relevant GitHub Actions workflow

### Step 2 — PLAN
Write a plain-English plan before coding:
- State which files will be changed and why
- List each function/section being added or modified
- Flag any risks (RLS policies, Stripe webhook order, auth state, etc.)
- Get confirmation if the plan affects billing, auth, or database schema

### Step 3 — CODE
- Provide complete, working, copy-paste ready code
- When editing `index.html` or any large file, always use `str_replace` — show the exact old block and the new replacement block
- Never truncate code with "…rest of code here…"
- Always preserve all existing quiz functionality when adding features

### Step 4 — COMMIT
End every coding task with exact Git instructions:
```bash
git add <specific files>
git commit -m "feat: <short description>"
git push origin main
```
Cloudflare Pages auto-deploys on every push to `main`. Remind the owner of this.

### Step 5 — UPDATE DOCS (mandatory after every task)
After every commit, update both living documents:

**1. `CLAUDE.md` (this file — in the repo)**
- Mark completed tasks as `✅ Done (YYYY-MM-DD)`
- Update the relevant section with actual implementation details
- Update the footer timestamp
- Commit and push CLAUDE.md in the same session — never leave it stale

**2. Blueprint V4 (Word doc — NOT in the repo)**
Location: `C:\Claude Code Space\CRAMIT QUIZ Code Folder\Documents\CramIT_Autonomous_Operations_Blueprint_V4.docx`

Update Blueprint V4 after any change that affects:
- Agent architecture or behaviour
- Database schema
- Infrastructure or hosting
- Billing or pricing logic
- New stages completed or major features shipped

Use the `/docx` skill to read and edit it. Add a version note at the top of the changed section:
`[Updated YYYY-MM-DD — <one-line summary of what changed>]`

If a change is minor (bug fix, wording, small refactor) — CLAUDE.md only is sufficient. Use judgement: would a new developer need to read the Blueprint to understand the system? If yes, update it.

---

## 3. Tech Stack — Never Suggest Alternatives

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Three HTML files — vanilla HTML/CSS/JS | No React, no Vue, no frameworks. See §22 for three-file architecture. |
| Hosting | Cloudflare Pages (free tier) | Functions at `/functions/` folder → served at `/{name}` — NEVER `/.netlify/functions/` |
| Auth | Supabase Auth — email/password + Google OAuth | |
| Database | Supabase (Postgres) — RLS enabled | Client always uses `sbClient` |
| Payments | Stripe — subscription billing | Webhooks verified server-side |
| Webhook handler | Supabase Edge Function named `clever-action` | NOT `stripe-webhook` — this was auto-named |
| AI Agent | Node.js + Anthropic Claude API | Runs via GitHub Actions nightly |
| Repo | GitHub — `bustachat/CramIT-Quiz` | Public repo, main branch |
| Diagram images | Cloudflare Pages static files at `/diagrams/` | Served from git repo — NOT Supabase Storage. Unlimited bandwidth free. Agent auto-deploys new images via git commit. |

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

**Where to find Supabase keys:**
- Project URL + Anon Key → Supabase Dashboard → Settings → API → Project URL / anon public
- Service Role Key → Supabase Dashboard → Settings → API → Legacy → service_role

**Supabase Edge Function Secrets** (set via `supabase secrets set` or dashboard):
| Secret | Source |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Webhooks → Click endpoint → Signing secret |
| `SUPABASE_SERVICE_ROLE_KEY` | Auto-injected by Supabase |

### 4.2 Cloudflare Pages
| Setting | Value |
|---|---|
| Project name | `cramit-quiz` |
| Live URL | `https://cramit-quiz.pages.dev` |
| Build command | `npm install` |
| Build output directory | `/` (root) |
| Functions directory | `functions/` (auto-detected by Cloudflare) |
| Node version | 22 |

**Cloudflare Secrets** (Cloudflare → Workers & Pages → cramit-quiz → Settings → Environment variables → Add secret):
| Secret | Source |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe → **Sandbox** → Developers → API keys (use the Sandbox sk_test_ key — NOT the main test mode key) |
| `SUPABASE_URL` | `https://ohqtefjawaphtsebnaxg.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Legacy → service_role |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `STRIPE_PRICE_CAP` | `price_1TEdW3Pvnbx5MPYykHvvk7gf` |
| `STRIPE_PRICE_FLEX_BASE` | `price_1TEdZRPvnbx5MPYylioNhNQI` |

⚠️ **Stripe Sandbox gotcha:** Stripe has two test environments — "Test mode" and "Sandbox". The customer/subscription data lives in the **Sandbox**. Always use the Sandbox API key in Cloudflare, not the plain test mode key. They look the same (`sk_test_...`) but have different prefixes after `51T`.

### 4.3 Stripe
| Setting | Value |
|---|---|
| Mode | **Sandbox/Test** — NOT live yet |
| Webhook endpoint | Points to Supabase Edge Function URL above |
| Transaction fee (live) | 1.75% + 30¢/txn |

**Where to find Stripe keys:**
- Publishable Key / Secret Key → Stripe Dashboard → Developers → API keys
- Webhook Secret → Stripe Dashboard → Webhooks → Click endpoint → Signing secret

**Stripe Products:**
| Product Name | Code Key | Billing | Notes |
|---|---|---|---|
| Quiz Base — Starter | `base` | $7.99/mo | Covers 2 subjects |
| Quiz Extra — Add-on | `extra` / `flex_extra` | $2.99/mo per unit | Per subject above 2 |
| Quiz Unlimited | `cap` | $19.99/mo | Up to 7 subjects |
| Quiz Flex — Power | `flex_base` | $19.99/mo | Base for 7+ subjects |

Price IDs are stored as constants in `create-checkout.js` and `update-subscription.js`. **`billing.js` is dead code — do not update it.** When Stripe switches to live mode, create new Price objects and update `create-checkout.js` and `update-subscription.js` only.

### 4.4 GitHub Actions
| Setting | Value |
|---|---|
| Repo | `bustachat/CramIT-Quiz` |
| Branch | `main` |
| Agent schedule | `0 13 * * *` (1pm UTC = 11pm Sydney) |
| Trigger | Nightly + manual via GitHub Actions UI |
| Permissions | `contents: write` (to commit new subject files) |

**GitHub Secrets** (Settings → Secrets and variables → Actions):
| Secret | Source |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |

### 4.5 Google OAuth
- Status: **Testing mode** — only approved test users can sign in
- To go public: Google Console → OAuth consent screen → Publish app (submit for verification)
- Client ID / Secret → Google Console → Credentials → OAuth Client → used in Supabase Auth → Google provider

---

## 5. Database Schema

Tables live in Supabase. RLS is enabled on all tables.

| Table | Purpose | Key Fields |
|---|---|---|
| `profiles` | Extends auth.users | `id`, `email`, `full_name` |
| `subscriptions` | Plan status, Stripe IDs | `user_id`, `plan`, `status`, `subject_count`, `stripe_subscription_id`, `stripe_customer_id` |
| `subject_selections` | Which subjects each user selected | `user_id`, `subject_id`, `added_at` |
| `pricing_config` | Pricing constants — edit here to change prices | `key`, `value` |
| `user_progress` | Per-question answer history — cross-device sync | `user_id`, `subject_key`, `question_idx`, `mode`, `is_correct`, `answered_at` — UNIQUE(user_id, subject_key, question_idx, mode) |

**Agent coordination tables** (from Blueprint V4 — to be deployed):
`agent_tasks`, `agent_logs`, `escalations`, `agent_config` (includes `autonomy_level INT DEFAULT 0` — 0=notify, 1=propose, 2=act+notify, 3=autonomous), `content_issues`, `known_issues`, `analytics_snapshots`, `band_descriptors`, `marking_criteria`, `band_mapping`, `written_submissions`

**Staging Supabase project** (to be created — separate free-tier project for agent testing and staging environment)

Full schema in `schema.sql` in the repo root.

---

## 6. File Structure

```
cramit-quiz/
├── index.html                  ← Mobile PWA — student quiz experience (logged-in students)
├── landing.html                ← ⬜ PLANNED — Public marketing/landing page (pre-signup visitors)
├── portal.html                 ← ⬜ PLANNED Stage 10 — Desktop web portal (logged-in students)
├── manifest.json               ← PWA manifest (CramIT branding)
├── sw.js                       ← Service worker for offline caching
├── agent.js                    ← Nightly NESA monitor + AI question generator
├── billing.js                  ← ⚠️ DEAD CODE — placeholder keys, not imported by index.html. To be deleted.
├── subject-selector.html       ← Subject selection UI component
├── package.json                ← { "type": "module", "dependencies": { "stripe": "^14.0.0" } }
├── extract_maths_diagrams.py   ← PDF diagram extractor v3 (PyMuPDF + Pillow + calibration)
├── diagram_registry.json       ← Crop coordinates for all 76 diagram images (2020–2025)
├── process_maths_backlog.js    ← Backlog processor for question generation
├── schema.sql                  ← Supabase table definitions + RLS policies
├── supabase_min.js             ← Local Supabase JS client (loaded via script tag)
├── diagrams/                   ← Exam diagram images — served by Cloudflare Pages at /diagrams/
│   ├── .gitignore              ← Excludes _debug/ folder from git
│   └── mathematics-standard-2_{year}_Q{n}_{suffix}.jpg
│       suffix = stimulus | A | B | C | D
├── subjects/                   ← ⬜ MIGRATION IN PROGRESS — questions moving here from index.html
│   ├── index.json              ← List of all available subject files
│   ├── mathematics-standard-2.json    ← ⬜ To be created (migrated from index.html)
│   ├── pdhpe-hms.json                 ← ⬜ To be created (migrated from index.html)
│   ├── multimedia.json                ← ⬜ To be created (migrated from index.html)
│   ├── vet-construction.json          ← ⬜ To be created (migrated from index.html)
│   └── mathematics-advanced-2024.json ← Agent-generated (existing)
└── functions/                  ← Cloudflare Pages Functions — served at /{name} (NOT /functions/{name})
    ├── create-checkout.js      ← POST /create-checkout — creates Stripe Checkout Session
    ├── update-subscription.js  ← POST /update-subscription — updates Stripe when subjects change
    ├── customer-portal.js      ← POST /customer-portal — opens Stripe billing portal
    ├── upgrade-flex.js         ← POST /upgrade-flex — upgrades cap → flex plan (stub — replaced by Billing Agent)
    └── mark-written.js         ← POST /mark-written — AI marking via Claude API
```

**Branch structure:**
```
main          → cramit-quiz.pages.dev         (LIVE — students, protected, PR required)
staging       → staging.cramit-quiz.pages.dev  (TEST — you only, agents can self-merge)
agent/*       → auto-preview URLs              (AGENT SANDBOX — agents commit here first)
```
**Rule: No agent ever commits directly to main. All agent commits go to `agent/*` branch → PR → staging → main.**

---

## 7. Current Subjects

| Subject | Quiz Key | Subject ID | Type | Questions | Standalone file in repo? |
|---|---|---|---|---|---|
| Mathematics Standard 2 | `maths` | `mathematics-standard-2` | MC only | 90 HSC + 318 extended (variants) | ✅ `2020-25 HSC Maths Quiz v5.4 (With New additional Variants Questions & Design).html` |
| PDHPE — HMS Depth Study | `hms` | `pdhpe-hms` | MC + written | Yr 12 depth study | ✅ `CLAUDE.AI - HMS_In_Depth_Study_YR12_quiz.html` |
| VET Construction | `vet` | `vet-construction` | MC + written | 2021–2025 | ✅ `VET_Construction_Quiz_v6 (Includes Updated code and HSC 2025).html` |
| Industrial Technology — Multimedia | `multimedia` | `multimedia` | MC + written | 2020–2025 | ✅ `CLAUDE.AI - HSC_Multimedia_Quiz (v19 - with 2025 exam).html` |

**Standalone HTML files are the source of truth for question data.** When porting a subject to index.html, always extract `mcQuestions[]` and `writtenQuestions[]` from the standalone file — never rewrite questions from scratch.

**NESA exam PDFs** are stored locally (NOT committed to GitHub — copyright):
`C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\`
Subfolders: `Maths Standard 2\`, `Health and Movement Science\`, `Industrial Technology - Multimedia\`, `VET - Construction\`
Each folder contains exam papers + marking guidelines (`-mg` suffix). Marking guidelines are used to build NESA band descriptors for Stage 5.

**More subjects planned** — the AI agent auto-discovers and adds new ones from NESA.

---

## 8. Pricing Model

| Subjects Selected | Plan | Monthly Price |
|---|---|---|
| 1 | Free | $0 |
| 2 | Base | $7.99 |
| 3 | Base + 1 Extra | $10.98 |
| 4 | Base + 2 Extra | $13.97 |
| 5 | Base + 3 Extra | $16.96 |
| 6 | Base + 4 Extra | $19.95 → triggers Unlimited |
| 7 | Unlimited | $19.99 |
| 8+ | Flex (Unlimited + $2.99/subject above 7) | $22.98+ |

**Critical rules:**
- The 7th subject is free (price caps at the 6-subject price, then rounds up to Unlimited)
- Students on Unlimited can swap subjects freely — price stays $19.99
- Never change pricing without also updating: `pricing_config` table, `billing.js`, `create-checkout.js`, `update-subscription.js`, AND creating new Stripe Price objects

### ✅ 10-Question Trial — Implemented (Stage 6)
The permanent 1-subject free tier has been replaced with a 10-question trial per subject:
- Trial counter stored in `localStorage` keyed by subject ID (`cramit_trial_{subjectId}`)
- Counter increments in `nextQuestion()` when advancing past a question
- After 10 questions: trial wall appears mid-quiz with score + subject-specific unlock CTA
- Picker shows trial restrictions: year filters, category chips, Extended 318, Test Mode, Written Response all grayed out during trial
- Trial exhausted + not logged in → upgrade prompt with "Sign in to subscribe →" button
- Trial exhausted + logged in → upgrade prompt with "Subscribe now →" → Stripe checkout
- Stats (answered/accuracy/streak) only written to localStorage when logged in; show 0 when logged out
- `handleTrialCheckout()` always subscribes to base plan (2 subjects, $7.99/mo)

---

## 9. Key Code Patterns — Always Follow These

### Cloudflare Pages function path
```js
// ✅ CORRECT — Cloudflare Pages Functions in functions/ folder are served at /{name}
fetch('/create-checkout', { method: 'POST', ... })
fetch('/customer-portal', { method: 'POST', ... })
fetch('/mark-written', { method: 'POST', ... })

// ❌ WRONG — these are dead, Netlify is gone
fetch('/.netlify/functions/create-checkout', ...)
fetch('/functions/create-checkout', ...)  // also wrong — /functions/ is NOT the URL prefix
```

⚠️ **Critical Cloudflare routing rule:** A file at `functions/create-checkout.js` is served at `/create-checkout` — NOT `/functions/create-checkout`. The `functions/` folder name is invisible in the URL.

### Supabase client init
```js
// Supabase JS loaded via <script src="/supabase.min.js"> in <head>
// Init once on DOMContentLoaded — never create a second client
document.addEventListener('DOMContentLoaded', () => { initSupabase(); });

// Always use sbClient — never new createClient(...)
const { data, error } = await sbClient.from('profiles').select('*');
```

### Google OAuth redirect
```js
// Always use APP_URL constant — never window.location.origin
const APP_URL = 'https://cramit-quiz.pages.dev'; // Cloudflare Pages URL
sbClient.auth.signInWithOAuth({
  provider: 'google',
  options: { redirectTo: APP_URL }
});
```

### Subject access check
```js
function canAccess(subjectId) {
  if (!currentUser) return false;
  if (userSub.status !== 'active' && userSub.status !== 'trialing') return false;
  return userSubjects.includes(subjectId);
}
```

### CSS variables (warm earth-tone design system — never change these)
```css
:root {
  --bg: #FAF8F5;
  --surface: #FFFFFF;
  --surface2: #F2EFE9;
  --border: #E0D9CF;
  --accent: #C17D3C;       /* amber — primary accent */
  --accent2: #7B9E6B;      /* green */
  --accent3: #5B7FA6;      /* blue */
  --text: #2C2420;
  --muted: #8C7B6E;
  --radius: 16px;
  --font-display: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
}
```

---

## 10. The Quiz Engine — Reference Design

The standalone HTML files in the project are the **gold standard** for quiz functionality. The hosted `index.html` on Netlify must be brought up to match them. The reference file is:

**`2020-25_HSC_Maths_Quiz_v5_4__With_New_additional_Variants_Questions___Design_.html`**

### Features the hosted app MUST match:

| Feature | Reference Implementation | Status |
|---|---|---|
| Practice mode | Answers visible after each question. Check ✓ button appears after selecting an option | ✅ In reference |
| Test mode | Answers hidden until finish. No Check button. Results shown at end | ✅ In reference |
| Step-by-step solutions | `<div class="step">` blocks inside `.explanation-box` | ✅ In reference |
| Per-option feedback | Every option (A/B/C/D) gets an explanation, not just the correct one | ✅ In reference |
| Year filter | Dropdown filters questions by exam year (2020–2025) | ✅ In reference |
| Topic/category filter | Dropdown filters by syllabus topic. Updates dynamically with counts | ✅ In reference |
| Question set toggle | "HSC 90" (original) vs "Extended 318" (with variants) | ✅ In reference |
| Option shuffle | Answer options are shuffled on each question render | ✅ In reference |
| Progress bar | Slim glowing bar at top, updates per question | ✅ In reference |
| Results screen | Score %, correct/total, scrollable review list per question | ✅ In reference |
| Sticky bottom nav | Prev / Check / Next buttons always visible | ✅ In reference |
| Responsive/mobile | `clamp()` font sizing, safe area insets, touch targets ≥ 48px | ✅ In reference |
| Correct/incorrect colours | Green `#10B981` / Red `#F43F5E` highlight on options | ✅ In reference |
| Written response mode | Text input, keyword scoring, band descriptor, model answer reveal | ✅ HMS + VET files |
| Diagram support | `image` field → stimulus above question. `optionImages` array → per-option images inside each button. Paths point to `/diagrams/` (Cloudflare Pages). | ✅ Done Stage 3 |
| NESA band marking (AI) | AI marks written responses via `/mark-written` (Cloudflare Pages Function) | ✅ Done Stage 5 |

### Question data structure (JS object)
```js
{
  year: 2024,
  category: 'F2',       // syllabus topic code
  variant: true,         // optional — omit for original HSC questions
  q: "Question text here.",
  // --- Diagram fields (only add when the question has images) ---
  image: "/diagrams/mathematics-standard-2_2024_Q6_stimulus.jpg",
  //   ^ stimulus diagram shown ABOVE the question text (null/omit if none)
  optionImages: [
    "/diagrams/mathematics-standard-2_2022_Q1_A.jpg",
    "/diagrams/mathematics-standard-2_2022_Q1_B.jpg",
    "/diagrams/mathematics-standard-2_2022_Q1_C.jpg",
    "/diagrams/mathematics-standard-2_2022_Q1_D.jpg",
  ],
  //   ^ per-option images rendered INSIDE each A/B/C/D button (null/omit if text options)
  //   For stimulus_only questions: set image, omit optionImages
  //   For options_only questions:  omit image, set optionImages
  //   For stimulus_and_options:    set both
  // --- Answer fields ---
  options: ["Option A", "Option B", "Option C", "Option D"],
  //   ^ text labels for options — still required even when optionImages present
  //     (used in results screen, accessibility, and shuffle logic)
  answer: 2,             // 0-indexed — index into options[] before shuffle
  solution: `<div class="step"><span class="step-number">1.</span> Step one explanation.</div>
             <div class="step"><span class="step-number">2.</span> Step two explanation.</div>`
  // For written response questions, add:
  // type: 'written',
  // marks: 4,
  // keywords: ['keyword1', 'keyword2'],
  // modelAnswer: "Full Band 5/6 model answer text"
}
```

### Image hosting — Cloudflare Pages `/diagrams/` (NOT Supabase Storage)
All diagram images are committed to the git repo under `diagrams/` and served by Cloudflare Pages.

**Do NOT use Supabase Storage for exam diagrams.** The `exam-images` bucket in Supabase is retired — it contained old unsplit images (one image per question). The new images are split into stimulus + per-option files.

**Do NOT use `MATHS_IMG` lookup table** — retired in Stage 3. Images are referenced directly on each question object via `image` and `optionImages` fields.

**VET questions** now use `/diagrams/vet-construction_{year}_Q{n}_stimulus.jpg` paths — migrated from Imgur in Stage 4. All VET images are served from Cloudflare Pages at `/diagrams/`.

**Path convention:**
```
/diagrams/{subject}_{year}_Q{n}_stimulus.jpg   ← question diagram
/diagrams/{subject}_{year}_Q{n}_A.jpg          ← option A image
/diagrams/{subject}_{year}_Q{n}_B.jpg          ← option B image
/diagrams/{subject}_{year}_Q{n}_C.jpg          ← option C image
/diagrams/{subject}_{year}_Q{n}_D.jpg          ← option D image
```

### Subject JSON file structure (for `subjects/` folder)
```json
{
  "id": "mathematics-standard-2",
  "name": "Mathematics Standard 2",
  "year": "2020–2025",
  "questionCount": 90,
  "topics": ["F1", "M1", "F2", "S1S2", "A2", "T2", "N1", "P1"],
  "questions": [ ...array of question objects... ]
}
```

---

## 11. Diagram Extraction Pipeline

### ✅ Current state — v3 extractor with calibration (Stage 2 complete)

`extract_maths_diagrams.py` extracts diagrams from HSC PDF papers, correctly separating the **question stimulus** from the **answer option images** so the quiz can render them at different sizes.

**Three diagram types handled:**
| Type | Output files | Description |
|---|---|---|
| `stimulus_only` | `_Q{n}_stimulus.jpg` | Question has a diagram; options are text |
| `options_only` | `_Q{n}_A/B/C/D.jpg` | Each option A–D is a separate image |
| `stimulus_and_options` | `_Q{n}_stimulus.jpg` + `_Q{n}_A/B/C/D.jpg` | Both question diagram and image options |

**Three run modes:**
```bash
# CROP (default) — crops from registry, bootstraps if no registry exists
python extract_maths_diagrams.py
python extract_maths_diagrams.py --year 2024

# CALIBRATE (recommended after bootstrap) — reads PDF text to find exact
# A./B./C./D. label pixel positions, sets y_start = label_y - 10px, then crops
python extract_maths_diagrams.py --calibrate
python extract_maths_diagrams.py --calibrate --year 2023

# DETECT (requires ANTHROPIC_API_KEY) — Claude Vision auto-detects all
# diagrams on each MC page; use for new exam years
python extract_maths_diagrams.py --detect --year 2026
```

**Workflow for a new exam year:**
1. Copy PDF to `C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2\`
2. Add filename to `PAPERS` dict in `extract_maths_diagrams.py`
3. Run: `python extract_maths_diagrams.py --calibrate --year 2026`
4. Check images in `diagrams/` — verify each option shows one clean graph
5. Add `image` / `optionImages` to new question objects
6. Commit `diagrams/`, `diagram_registry.json`, `extract_maths_diagrams.py`

**Registry (`diagram_registry.json`):**
- Records all crop coordinates (y_start, y_end, x_start, x_end per option)
- `source` field: `hardcoded-bootstrap` | `calibrated` | `claude-vision`
- Version 3 — auto-upgrades old versions on load

**2x2 grid vs vertical stack:**
NESA uses two option layouts. The extractor handles both:
- **2x2 GRID**: A+B side-by-side on top row, C+D below. Each option has `x_start`/`x_end` to split left/right column.
- **VERTICAL STACK**: All 4 options full-width, stacked top-to-bottom. No x split needed.
Calibration auto-detects layout from whether A and B labels share the same y position (within 30px).

**Current coverage: 76 images across 2020–2025 (Maths Standard 2 only)**

### GitHub Actions integration for diagrams
When the nightly agent detects a new exam paper:
1. `agent.js` downloads the PDF
2. Runs `python extract_maths_diagrams.py --calibrate --year {year}`
3. Commits new images to `diagrams/` folder
4. Cloudflare Pages auto-deploys — images immediately available at `/diagrams/filename.jpg`

### Adding diagram support to other subjects
- **VET Construction**: Already migrated to `/diagrams/` paths ✅
- **HMS / Multimedia**: No image questions currently — add if needed post-launch
- **New subjects via agent**: Agent uses `--detect` mode (Claude Vision) for automatic extraction

---

## 12. AI Agent (`agent.js`) — How It Works

The nightly agent runs via GitHub Actions at 11pm Sydney time (1pm UTC):

```
GitHub Actions triggers → agent.js runs → 
  1. Monitor: checks NESA for new PDFs
  2. If new paper: downloads PDF
  3. Notify: emails admin
  4. Reader: Claude Vision extracts questions
  5. Quiz Builder: Claude generates MC questions + explanations
  6. Code Writer: creates subjects/new-subject.json
  7. Updates subjects/index.json
  8. Commits to agent/content-{date} branch (NOT main)
  9. Creates PR → staging branch
  10. Cloudflare Pages preview URL auto-created for review
  11. Human approves PR → merges to staging → merges to main → live deploy
```

**Agent environment:**
- Runs in GitHub Actions Node.js 22 environment
- Uses `ANTHROPIC_API_KEY` secret from GitHub Settings → Secrets
- Must have `contents: write` permission to commit files
- Claude model to use: `claude-opus-4-5` for quality (or `claude-sonnet-4-6` for speed/cost)
- **Agents NEVER commit directly to `main`** — always commit to `agent/*` branch first

**Agent safety — every agent must implement:**
```js
const config = await getAgentConfig(agentName);
if (!config.enabled) return;                          // kill switch
if (todaySpend >= config.max_daily_spend) { await escalate(...); return; } // spend limit
const DRY_RUN = config.autonomy_level === 0;          // level 0 = notify only
if (DRY_RUN) { await notify(action); return; }        // email owner instead of acting
await logAction(agentName, action, payload);           // log before acting
```

**Written response AI marking** (live — `/mark-written` Cloudflare Pages Function):
- Student submits written answer via POST
- Function calls Claude API with NESA marking criteria in system prompt
- Returns: band (1–6), marks awarded, specific feedback, model answer at next band up
- Costs ~$0.007 per submission
- Log to `written_submissions` Supabase table for auditability

---

## 13. What's Done / What's Not

### ✅ Completed
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

### Staged Implementation Roadmap

| Stage | What | Status |
|---|---|---|
| **Stage 1** | Quick wins: reset modal, year/topic badges, progress bar glow, touch targets, safe-area-inset | ✅ **DONE** |
| **Stage 2** | Diagram extractor v3 — stimulus/options split, calibration mode, 76 images committed to repo | ✅ **DONE** |
| **Stage 3** | Wire images into quiz renderer (`image` + `optionImages` on question objects, retire `MATHS_IMG`). Category filter + dynamic counts + HSC 90/Extended 318 toggle | ✅ **DONE** |
| **Stage 4** | Port Multimedia + HMS subjects into index.html | ✅ **DONE** |
| **Stage 5** | Written response + NESA band engine (keyword scoring → Band 1–6 feedback + band-tiered model answers) + AI marking via `/mark-written` Cloudflare Pages Function | ✅ **DONE** |
| **Stage 6** | Pricing model update — 10-question trial replaces 1-free-subject | ✅ **DONE** |
| **Stage 7A** | Per-user per-subject progress tracking — localStorage JSON map `{questionIdx: 0\|1}`, stable IDs via `indexOf()` on master array, last-attempt-wins, card badges | ✅ **DONE** |
| **Stage 7B** | Cross-device sync — Supabase `user_progress` table; `syncAnswerToSupabase()` fire-and-forget, `loadProgressFromSupabase()` on login | ✅ **DONE** |
| **Stage 8** | Maths Section II written questions — 101 questions (2020–2025), 47 diagram images, image audit + re-crop, Key Concepts hidden for Maths | ✅ **DONE** |
| **Stage 8.9** | Formula Hint widget — green Hint button in Practice mode for formula-based Maths MC questions; radio-button formula selector; correct/wrong feedback with explanations; full HSC 90 + Extended 318 coverage via `getTipForQuestion(q)` | ✅ **DONE** |
| **Stage 8.5** | Rebuild written question image extractor — Claude Vision `--detect` mode + full-width crop (x0=30, x1=565) to fix text label clipping at scale. | ✅ **DONE** |
| **Stage 9** | Agent infrastructure (QA/Testing, Content, Analytics) — separate project | ⬜ |
| **Stage 10** | Desktop web portal (`portal.html`) — sidebar nav, subject dashboard, progress history, split-panel written response | ⬜ |
| **Stage 11** | Migrate hosting from Netlify → Cloudflare Pages + Workers (completed May 2026) | ✅ **DONE** |

### ⬜ Still to do (non-staged)

#### Pre-launch — blocking
| # | Task | File(s) | Notes |
|---|---|---|---|
| ~~**1**~~ | ~~**Migrate questions → `subjects/*.json`**~~ | ~~`index.html`, `subjects/`~~ | ✅ Done (2026-06-05) — index.html 11,195 → 2,502 lines. All 4 subjects in `subjects/*.json`. `loadSubjectData(key)` async fetch with `subjectCache`. See §25 for details. |
| 2 | Fix `handleUpgradeFlex()` | `index.html` | Currently just shows an alert. Redirect to Customer Portal as stopgap until Billing Agent is built. |
| 3 | Fix `plan_type: flex` in `handleCheckout()` | `index.html` | Currently maps to `'unlimited'` for 8+ subjects — should be `'flex'` |
| 4 | Delete `billing.js` | `billing.js` | Dead code — placeholder keys, not imported by index.html. Safe to delete. |
| 5 | Test full payment flow end-to-end | Stripe sandbox | Use test card `4242 4242 4242 4242`. Test: trial → subscribe → add subject → remove subject → cancel |
| ~~6~~ | ~~Fix remaining 39 MC question texts~~ | ~~`index.html`~~ | ✅ Done — 60 question texts updated to exact NESA wording from PDFs (2020–2025). Also fixed 2021 Q8–15 one-position shift, bearing diagram image, and chocolates optionImages. |
| ~~7~~ | ~~Re-crop 2024 Q15 stimulus image~~ | ~~`diagrams/`~~ | ✅ Done — manually cropped, `hideQ:true` removed |
| 8 | Set `ANTHROPIC_API_KEY` in GitHub Secrets | GitHub Settings | Enables nightly Content Agent |
| 9 | Submit Google OAuth for verification | Google Console | Required for public launch |
| 10 | Add custom domain `cramit.com.au` | Cloudflare Pages → Custom domains | Update DNS, update `APP_URL` in index.html, update Supabase redirect URLs |
| 11 | Switch Stripe to live mode | Stripe dashboard + Cloudflare + Supabase secrets | Create new live Price objects, update `create-checkout.js` + `update-subscription.js` |

#### Pre-launch — infrastructure (required before any agent goes live)
| Task | File(s) | Notes |
|---|---|---|
| Create staging Supabase project | Supabase dashboard | Free tier. Separate from production. Used by all agents during testing. |
| Create `staging` branch + Cloudflare preview | GitHub + Cloudflare | Agents deploy here first. Preview URL auto-created by Cloudflare Pages. |
| Enable branch protection on `main` | GitHub Settings → Branches | Require PR + 1 approval. No direct pushes — not even from owner. |
| Add `autonomy_level` column to `agent_config` | Supabase SQL editor | `ALTER TABLE agent_config ADD COLUMN autonomy_level INT DEFAULT 0;` |
| Deploy all Blueprint V4 agent coordination tables | Supabase SQL editor | See §23 for full table list |
| Build shared agent safety wrapper | New file `agents/lib/safety.js` | Kill switch + spend limit + dry-run + action logging. Used by all agents. |

#### Post-launch roadmap
| Task | Notes |
|---|---|
| ~~Migrate questions from `index.html` → `subjects/*.json`~~ | ✅ Done 2026-06-05 |
| Build `landing.html` — public marketing page | See §22. Needed for organic traffic + conversion. |
| Build `portal.html` — desktop web portal | See §22 Stage 10. |
| Build agent fleet per Blueprint V4 phasing | See §24 for revised agent build order. |
| Launch | — |

---

## 14. What a "Complete Quiz Engine Upgrade" Means

The biggest priority is bringing `index.html` (the hosted Cloudflare Pages app) up to the standard of the reference standalone HTML files. Here is the exact feature gap:

### Quiz engine feature parity — all complete ✅

1. **Practice vs Test mode toggle** — ✅ Done
2. **Step-by-step solutions** — ✅ Done — numbered `<div class="step">` blocks
3. **Category/topic filter with live counts** — ✅ Done Stage 3
4. **Question set toggle (HSC 90 vs Extended 318)** — ✅ Done Stage 3
5. **Option shuffle per render** — ✅ Done
6. **Correct answer behaviour** — ✅ Done — green/red highlights, explanation animates in
7. **Results screen** — ✅ Done — score %, correct/total, per-question breakdown
8. **Year + topic badge** — ✅ Done Stage 1
9. **Written response + AI marking** — ✅ Done Stage 5

### When upgrading index.html, preserve:
- The warm earth-tone design system (`--accent: #C17D3C`, Syne + DM Sans fonts)
- All existing Supabase auth and billing code — do NOT touch `initSupabase()`, `loadUserState()`, `canAccess()`, billing modal code
- The 3 subject cards (Maths, HMS, VET) and their routing logic
- PWA manifest + service worker registration

---

## 15. How to Add a New Subject

### Manual method:
1. Create `subjects/{subject-id}-{year}.json` following the question data structure in §10
2. Add the filename to `subjects/index.json`
3. Add a subject card to `index.html`
4. Commit and push — Cloudflare Pages deploys within ~60 seconds

### Agent method (automatic):
- The nightly `agent.js` handles this automatically once `ANTHROPIC_API_KEY` is set in GitHub Secrets
- Agent commits directly to `main` → Cloudflare Pages auto-deploys

### Current subjects (all live in index.html):
- **Mathematics Standard 2** — 90 HSC + 318 extended variants, diagrams wired ✅
- **Multimedia** — MC + written, ported Stage 4 ✅
- **HMS** — MC + written, ported Stage 4 ✅
- **VET Construction** — MC + written, ported Stage 4 ✅

### Subjects in the pipeline (next to add):
- Mathematics Advanced
- English Advanced / Standard
- Biology, Chemistry, Physics
- Legal Studies, Business Studies, Economics

---

## 16. Testing Checklist

### Before every deploy:
- [ ] Quiz loads on mobile (iPhone Safari, Android Chrome)
- [ ] Practice mode: Check button appears after selecting, correct/incorrect colours show, explanation reveals
- [ ] Test mode: No Check button, answers hidden, results shown at end
- [ ] Year filter works — selecting 2023 shows only 2023 questions
- [ ] Category filter updates with counts
- [ ] Previous/Next navigation works and doesn't skip questions
- [ ] Progress bar updates correctly
- [ ] Reset returns to Q1 with all defaults restored

### Billing-specific:
- [ ] Free user sees lock icon on non-free subjects
- [ ] Clicking locked subject shows upgrade modal
- [ ] Upgrade modal shows correct price calculation
- [ ] Stripe Checkout opens (test mode: use card `4242 4242 4242 4242`)
- [ ] After payment, subject unlocks without page reload (or with clear reload instruction)
- [ ] Customer portal opens via `/customer-portal` (NOT `/.netlify/functions/customer-portal`)

---

## 17. Known Issues

| Issue | Status | Notes |
|---|---|---|
| Stripe is in test/sandbox mode | ⬜ Todo | Switch to live before launch |
| Google OAuth is in Testing mode | ⬜ Todo | Submit for verification |
| `APP_URL` and `SUPABASE_ANON_KEY` were placeholders | ✅ Fixed | Owner filled these in |
| Edge Function named `clever-action` not `stripe-webhook` | ✅ Known, working | Do not rename — webhook registered to this URL |
| Diagram images not rendering in hosted quiz | ✅ Fixed Stage 3 | Images wired via `image`/`optionImages` on question objects. `MATHS_IMG` retired. |
| Written response AI marking not yet built | ✅ Built Stage 5 | `/mark-written` Cloudflare Pages Function live. Quota by plan. Keyword grid fallback. |
| `billing.js` has placeholder credentials | ⬜ Delete it | Not imported by index.html — dead code. Safe to delete. |
| `handleUpgradeFlex()` is a stub | ⬜ Fix pending | Just shows alert. Fix: redirect to Customer Portal. Billing Agent will replace this properly. |
| `handleCheckout()` plan_type missing flex case | ⬜ Fix pending | Maps 8+ subjects to `'unlimited'` — should be `'flex'` |
| Blueprint V4 Netlify references | ⬜ Docx update needed | Hosting migrated to Cloudflare Pages in May 2026. Blueprint V4 may still contain Netlify references — verify and update using `/docx` skill. |

---

## 18. Claude API Usage in This Project

### In `agent.js` (nightly agent)
```js
// Model selection
const model = 'claude-opus-4-5'; // Use Opus for question generation quality
// Or: 'claude-sonnet-4-6' for faster/cheaper generation

// API call pattern
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': process.env.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
  },
  body: JSON.stringify({
    model: 'claude-opus-4-5',
    max_tokens: 4096,
    messages: [{ role: 'user', content: prompt }]
  })
});
```

### In `mark-written.js` (Cloudflare Pages Function — live)
```js
// Never expose ANTHROPIC_API_KEY in browser code
// Always proxy through the Cloudflare Pages Function
// POST /mark-written
// Body: { userId, question, maxMarks, keywords, studentAnswer, bandDescriptors, subject }
// Response: { aiMarked, marksAwarded, grade, feedback, improvement, keyConceptsFound, marksRemaining }
```

### Diagram extraction (planned upgrade)
```python
# In extract_maths_diagrams.py upgrade
import anthropic
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
# Use claude-opus-4-5 with vision for diagram detection
```

---

## 19. Cost Reference

| Service | Free Tier | Your Current Cost |
|---|---|---|
| Supabase | 50,000 users, 500MB DB | $0 |
| Cloudflare Pages | Unlimited bandwidth, 100K function requests/day | $0 |
| GitHub | Unlimited public repos | $0 |
| Stripe | No monthly fee | 1.75% + 30¢/txn of revenue only |
| Claude API (agent) | Pay per use | ~$2–5/mo |
| Claude Pro (owner) | N/A | $20/mo |
| Google OAuth | Free forever | $0 |
| **TOTAL** | | **~$22–25/mo + % of revenue** |

At 1,000 active subscribers: ~$105/mo in AI + infra costs (≈1.3% of revenue).

---

## 20. Blueprint V4 — Agent Roster Summary

The Autonomous Operations Blueprint V4 defines 22 agents across 5 clusters. Full specs in `CramIT_Autonomous_Operations_Blueprint_V4.docx` at `C:\Claude Code Space\CRAMIT QUIZ Code Folder\Documents\`. See §24 for the revised build order and decisions.

**Revised status per agent (June 2026 review):**

| # | Agent | Decision | Reason |
|---|-------|----------|--------|
| 1 | Content Agent | ✅ Build Phase 1 | Already 80% built as `agent.js` |
| 2 | Incident & Monitoring | ⚡ Replace uptime with UptimeRobot (free) | Custom logic only needed for Supabase/Stripe health checks |
| 3 | Service Desk | ✅ Build Phase 2 | Scales support without owner time |
| 4 | Billing & Subscription | ✅ Build Phase 2 | Replaces `handleUpgradeFlex()` stub, handles churn |
| 5 | Accounts / Finance | ✅ Build Phase 3 | Manual is fine until 500+ subscribers |
| 6 | Marketing | ⚠️ Build Phase 4 — draft-only mode first | $15–60/mo AI cost. Start at autonomy_level=0 |
| 7 | Notification & Engagement | ✅ Build Phase 3 | Needs `user_progress` data — can't replace with generic SaaS |
| 8 | Referral & Partnerships | ⏳ Defer | Needs contact list. Build after 50+ students |
| 9 | Analytics & Insights | ✅ Build Phase 3 | Needs Supabase data — PostHog can't replace |
| 10 | QA / Testing | ✅ Build Phase 1 | Catches regressions before students see them |
| 11 | Development Agent | ⚡ Replaced by Claude Code | This is the Development Agent |
| 12 | Compliance | ✅ Build Phase 5 | Monthly, low urgency pre-launch |
| 13 | Data Protection | ✅ Build Phase 5 | Monthly audit + deletion requests |
| 14 | Competitor Intelligence | ⏳ Defer Phase 5 | Nice-to-have, manual weekly browse is fine early |
| 15 | Onboarding | ✅ Build Phase 2 | Trial → paid conversion. Highest revenue impact |
| 16 | Pricing Optimisation | ✅ Build Phase 5 | Proposals only — never changes prices autonomously |
| 17 | SEO & Content Marketing | ⏳ Defer | Needs blog infrastructure + `cramit.com.au` domain first |
| 18 | Feedback Synthesis | ✅ Build Phase 5 | Weekly aggregation of content_issues + feature_requests |
| 19 | UX / Design | ⚡ Replaced by Claude Code | Proposals on-demand via Claude Code |
| 20 | Database & Infrastructure | ✅ Build Phase 1 | Daily capacity monitoring, SSL cert checks |
| 21 | Syllabus & Standards | ✅ Build Phase 3 | Core differentiator — NESA band descriptors |
| 22 | Security & Threat | ✅ Build Phase 2 | Student data, Australian Privacy Act exposure |

**Effective agent count: ~19 custom agents** (3 replaced: Development, UX/Design = Claude Code; uptime monitoring = UptimeRobot)

All agents communicate through `agent_tasks` table in Supabase. Each has a kill switch + `autonomy_level` in `agent_config` table.

---

## 21. Question Expansion Strategy (Stage 3 Discussion)

### Background
The Maths Standard 2 standalone file (v5.4) was expanded from 90 to 318 questions using a **variant** strategy — 3 variants per non-image question, each with different numbers and a different correct answer position (A/B/C/D rotated), totalling 4 questions per concept. The `variant: true` flag marks expanded questions; the HSC 90/Extended 318 toggle controls which set students see.

### Decision by subject

| Subject | Variant approach | Reasoning |
|---|---|---|
| **Maths Standard 2** | ✅ Already done — 318 questions in v5.4 | Calculation questions = easy to variant. Rotate A/B/C/D as correct answer. |
| **Multimedia** | ⬜ Generate additional questions from NESA reference docs | Mostly conceptual definitions — can't just "change the numbers". Generate new questions on same topics from marking guidelines and syllabus notes. |
| **HMS** | ⬜ Generate additional questions from NESA reference docs + HMS study materials | Protocol-based (RICER, TOTAPS). Can use different injury scenarios/sports/body parts. Also has marking guidelines in NESA Exams folder. |
| **VET Construction** | ❌ Skip entirely | Mostly visual (tool identification from images). Not worth generating variants or additional questions without images. |

### Variant rules for Maths (already applied, for reference)
- Skip any question that has a diagram/image (`image` or `optionImages` field present)
- Write 3 variants per skippable question: different numbers, different answer options, correct answer in a different position (A/B/C/D each correct once across the 4 questions)
- Each variant has a full step-by-step `solution` block
- Mark with `variant: true`
- Python-verify all calculations before committing

### Additional question generation for Multimedia + HMS (Stage 3 plan)
- Source material: NESA marking guidelines (in `NESA Exams Folder`), syllabus documents, standalone HTML files
- Use Claude to generate questions in the exact JS object format
- Questions must be genuinely new (not paraphrases of existing questions)
- MC questions: 4 options, 1 correct, rotate correct answer position
- Add `variant: true` flag so they only appear in Extended mode
- Target: ~2x the original question count per subject

---

## 22. Design System Decisions

### Confirmed design direction (May 2026)
- **Warm earth-tone system is locked** — `--accent: #C17D3C` amber, Syne + DM Sans fonts, `--bg: #FAF8F5`
- The standalone Maths v5.4 file uses a DIFFERENT dark navy design — this is the standalone study tool only, NOT the CramIT brand
- All index.html work must use the CramIT warm earth-tone tokens

### Mobile-first principles (applied in Stage 1, carry forward)
- Touch targets: `min-height: 52px` on touchscreen devices via `@media (hover:none) and (pointer:coarse)`
- Safe-area-inset: `padding-bottom: max(28px, calc(env(safe-area-inset-bottom) + 12px))` on quiz footer
- Progress bar: 5px, amber glow `box-shadow: 0 0 8px rgba(193,125,60,0.5)`
- Check button: pulse animation on appear (`checkPulse` keyframe)
- All design decisions must translate to native mobile app (same hex values usable in React Native/Flutter)

### Three-track product architecture (FUNDAMENTAL — June 2026)

CramIT has **three distinct HTML files** serving three different audiences. These must NEVER be merged:

| | Landing Page (`landing.html`) | Mobile PWA (`index.html`) | Desktop Portal (`portal.html`) |
|---|---|---|---|
| **Audience** | Public — not yet a student | Logged-in student on phone | Logged-in student on laptop |
| **Purpose** | Convert visitors → trial signups | Quick quiz sessions, installed on phone | Deep study sessions, progress history |
| **Auth required** | ❌ None — fully public | ✅ Supabase `sbClient` | ✅ Supabase `sbClient` |
| **Layout** | Marketing-focused, hero + features + CTA | Single column, full-screen, tap targets 52px+ | Sidebar nav + main content canvas |
| **Navigation** | Scrolling sections + sign up CTA | Card-based home → picker → quiz | Left sidebar: Dashboard, Study, History, Written |
| **Design** | Same warm earth-tone tokens | Same tokens — mobile-first | Same tokens — denser, hover states |
| **Status** | ⬜ Planned — build before launch | ✅ Live | ⬜ Planned Stage 10 |

**Why the landing page is fundamental:**
- `index.html` home screen is student-centric — assumes auth already exists
- Organic traffic (Google, social) hits a dead-end without a public conversion page
- Trial signups without a landing page = no organic growth
- `landing.html` is NOT the same as `index.html` — they serve different audiences and must be separate files

**Landing page must include:**
- Hero: what CramIT is, who it's for
- Subject list with sample questions (no auth needed)
- Pricing table
- "Start free trial" CTA → redirects to `index.html` (triggers auth + trial flow)
- Social proof (results, student quotes when available)
- SEO-targeted content (HSC, NESA, past papers)

**Desktop Portal planned pages:**
1. **Dashboard** — per-subject progress rings, streak, recent activity
2. **Study** — three-column picker: subject + topics + year → start quiz
3. **History** — every question answered, filterable by subject/date/result
4. **Written Response** — split panel: question left, answer right, AI feedback below

**Competitor reference for portal:** Studitory (`studitory.app`) — take sidebar + split-panel patterns only.

**Key rules:**
- `portal.html` uses the same `sbClient`, same `user_progress` table, same pricing logic — its own layout only
- `landing.html` has NO `sbClient` dependency — fully static, no auth code
- Do NOT modify `index.html` when building either the portal or the landing page

---

---

## 21. Stage 11 — Cloudflare Migration (✅ COMPLETE — May 2026)

Netlify is gone. CramIT now runs entirely on Cloudflare Pages.

### What was migrated
| Layer | Before | After |
|---|---|---|
| Hosting + static files | Netlify | Cloudflare Pages (`cramit-quiz.pages.dev`) |
| Serverless functions | `netlify/functions/` (CommonJS) | `functions/` (ESM Cloudflare Pages Functions) |
| Function URLs | `/.netlify/functions/{name}` | `/{name}` (the `functions/` folder name is NOT in the URL) |
| Env vars | Netlify Dashboard | Cloudflare Pages → Settings → Secrets |

### Cloudflare Pages Function pattern (ESM — always use this)
```js
import Stripe from 'stripe';

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);  // env.VAR not process.env.VAR
  const body = await request.json();
  // ... business logic ...
  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}
```

### Lessons learned (do not repeat these mistakes)
- **No `wrangler.toml`** — for a git-connected Pages project, `wrangler.toml` blocks the dashboard from managing secrets. Delete it.
- **No `require()`** — Cloudflare Workers are ESM only. Always `import`.
- **No `process.env`** — use `env.VARIABLE_NAME` from the `context` parameter.
- **Function URL routing** — `functions/customer-portal.js` → served at `/customer-portal`. Never `/functions/customer-portal`.
- **UTF-8 encoding** — when doing find-replace on `index.html` in PowerShell 5.1, always use `[System.IO.File]::ReadAllText(path, UTF8NoBOM)` and `WriteAllText`. Never `Get-Content | Set-Content` — it corrupts UTF-8.
- **Stripe Sandbox vs Test mode** — Stripe has two separate test environments. Customer data lives in the **Sandbox**. Use the Sandbox `sk_test_` key in Cloudflare, not the plain Test mode key. They look identical but are different accounts.
- **Build command** — set to `npm install` so Cloudflare installs the `stripe` npm package before compiling functions.

### Still to do (R2 image storage — Phase 2)
Images are currently served from git repo via Cloudflare Pages static files — this works fine. R2 migration is optional and only needed if the `diagrams/` folder becomes too large for git.
- Create R2 bucket `cramit-assets`, enable public access
- Upload `diagrams/` folder
- Add `const IMAGE_BASE_URL = 'https://pub-XXXX.r2.dev'` to `index.html`
- Prefix image paths in `renderQuestion()` with `IMAGE_BASE_URL`

---

---

## 23. Staging Environment & Release Strategy

### Environment architecture
```
main branch          → cramit-quiz.pages.dev          (LIVE — real students)
staging branch       → staging.cramit-quiz.pages.dev   (TEST — owner only)
agent/* branches     → auto-preview URLs               (AGENT SANDBOX)
```
Cloudflare Pages auto-creates preview URLs for every branch — no extra config needed.

### Branch protection rules (set on GitHub before any agent work)
- `main`: Require PR + 1 approval (owner). No direct pushes — not even from owner.
- `staging`: Require PR. No approval needed (agents can self-merge here after passing tests).
- `agent/*`: No restrictions — agents commit freely here.

### Staging Supabase project
- Separate free-tier Supabase project — NOT the production database
- Same schema as production (copy `schema.sql`)
- Seeded with test accounts and test subscription data
- All agents run against staging Supabase during development and Level 0–1 testing

### Agent release pipeline (for every new agent)
```
1. Build agent → commit to agent/{name} branch
2. Test against staging Supabase + staging Cloudflare preview
3. Set autonomy_level = 0 (notify only) — run for 2 weeks
4. Review email notifications — confirm actions are correct
5. Promote to autonomy_level = 1 (propose) — run for 1 week
6. Review proposals — confirm all are approved without changes
7. Promote to autonomy_level = 2 (act + notify) — run for 2 weeks
8. Review action logs — confirm no surprises
9. Promote to autonomy_level = 3 (fully autonomous)
```
Total: ~5–6 weeks from build to fully autonomous. Live app is protected throughout.

### Agent autonomy levels
| Level | Name | Behaviour |
|-------|------|-----------|
| 0 | Notify | Runs, emails owner "I would do X", does nothing |
| 1 | Propose | Creates PR or `agent_tasks` entry, waits for approval |
| 2 | Act + Notify | Acts immediately, emails owner what it did |
| 3 | Autonomous | Acts, logs, escalates only on exception |

### Risk ratings by agent
| Agent | Risk if buggy | Max autonomy_level at launch |
|-------|--------------|------------------------------|
| Content Agent | Commits wrong questions | Level 1 (PR only — human reviews questions) |
| Billing & Subscription | Wrong Stripe charge | Level 1 until Stripe is live mode |
| Security & Threat | Locks out real students | Level 1 always — never auto-ban |
| Service Desk | Wrong email to student | Level 0/1 for first month |
| Onboarding | Spam to students | Hard limit: max 1 email per student per 24h in code |
| Development | Merges bad code | Level 1 always — PR only, never auto-merges to main |

### Shared agent safety wrapper
Every agent imports from `agents/lib/safety.js`:
```js
export async function agentGuard(agentName, action, payload, executeFn) {
  const config = await getAgentConfig(agentName);        // from agent_config table
  if (!config.enabled) return { skipped: 'disabled' };  // kill switch
  if (await exceedsDailySpend(agentName, config.max_daily_spend)) {
    await escalate(agentName, 'Daily spend limit reached', payload);
    return { skipped: 'spend_limit' };
  }
  await logAction(agentName, action, payload);            // always log before acting
  if (config.autonomy_level === 0) {
    await notifyOwner(agentName, action, payload);        // notify only
    return { skipped: 'notify_only' };
  }
  return await executeFn();                               // act
}
```

---

## 24. Agent Build Order — Revised (June 2026)

Build sequence based on business impact and dependency order:

### Phase 1 — Before launch (core stability)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Content Agent (expand `agent.js`) | NESA monitoring + question generation | Already 80% built |
| QA / Testing Agent | Playwright tests on every deploy | Catches regressions before students |
| Database & Infrastructure Agent | Daily Supabase/CF capacity checks | Prevents surprise outages |
| UptimeRobot (not custom) | HTTP uptime monitoring | Free, 2-minute setup |

### Phase 2 — First students (student-facing automation)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Onboarding Agent | Day 0/1/3/7/14 email sequence | Trial → paid conversion |
| Billing & Subscription Agent | Payment events, churn prevention | Replaces handleUpgradeFlex() stub |
| Service Desk Agent | Classify + auto-resolve student queries | Scale support without owner time |
| Security & Threat Agent | Hourly suspicious login scan | Australian Privacy Act obligation |

### Phase 3 — Growing (business intelligence)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Analytics & Insights Agent | Daily KPI briefing from Supabase data | Need visibility on what's working |
| Notification & Engagement Agent | Re-engagement emails, new content alerts | Retention = revenue |
| Accounts / Finance Agent | Weekly P&L from Stripe + costs | Understand unit economics |
| Syllabus & Standards Agent | Maintain NESA band descriptors | Core product differentiator |

### Phase 4 — Scaling (growth engine)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Marketing Agent | Social content — draft-only mode first | $15–60/mo AI cost, start cautiously |
| SEO & Content Marketing Agent | Blog posts targeting HSC keywords | Needs `cramit.com.au` domain first |
| Referral & Partnerships Agent | Tutor outreach | Needs 50+ students for social proof |

### Phase 5 — Full automation
| Agent | What it does |
|-------|-------------|
| Feedback Synthesis Agent | Weekly aggregation of all feedback |
| Compliance Agent | Monthly NESA terms + Privacy Act check |
| Data Protection Agent | Monthly audit + deletion request handling |
| Competitor Intelligence Agent | Weekly competitor pricing/feature scan |
| Pricing Optimisation Agent | Monthly pricing proposals (never autonomous) |

**Permanently replaced by Claude Code (not built):** Development Agent, UX/Design Agent

---

## 25. Question JSON Migration — ✅ COMPLETE (2026-06-05)

### What was done
All question data previously hardcoded in `index.html` was extracted to individual JSON files in `subjects/`. `index.html` reduced from 11,195 → 2,502 lines (−78%).

### File structure
One JSON file per subject (all years combined):
```
subjects/
├── index.json                     ← list of all subject files
├── mathematics-standard-2.json    ← all years, MC + written + variants
├── pdhpe-hms.json                 ← all years, MC + written
├── multimedia.json                ← all years, MC + written
├── vet-construction.json          ← all years, MC + written
└── mathematics-advanced-2024.json ← agent-generated (existing)
```

**Why one file per subject (not per subject+year):**
- Year filter already works client-side from the `year:` field on each question — no need to split files
- Maths at full size (~409 questions) is only ~300–400KB — fast on mobile
- Agent appends new year's questions to the existing subject file
- Simple loading: one fetch per subject

### Files created
| File | MC | Written | Size |
|---|---|---|---|
| `subjects/mathematics-standard-2.json` | 318 (incl. variants) + 73 tips | 101 | 608 KB |
| `subjects/pdhpe-hms.json` | 57 | 17 | 118 KB |
| `subjects/multimedia.json` | 60 | 29 | 118 KB |
| `subjects/vet-construction.json` | 75 | 23 | 103 KB |

JSON format: `{ id, name, icon, accentColor, mcQuestions[], writtenQuestions[], tips{} }` — same field names as the old JS objects (q, options, answer, solution, etc.).

### How loading works in index.html
- `const subjectCache = {}` — in-memory cache, persists for the session
- `async function loadSubjectData(key)` — fetches `/subjects/{id}.json` once, caches in `subjectCache[key]`
- `openPicker(key)` is async — shows "Loading questions…" on first open, instant on repeat
- `SUBJECTS[key].getMC(filters)` and `getWritten(filters)` read from `subjectCache[key]`
- `getMasterArray(subjectKey, mode)` reads from `subjectCache[subjectKey]`
- `getTipForQuestion(q)` reads `subjectCache.maths.mcQuestions` and `subjectCache.maths.tips`
- `SUBJECTS[key].categories` and `.topics` are set to `null` at init; patched by `loadSubjectData()` after first fetch

### Agent compatibility
- All subjects are now consistently JSON — the Content Agent writes to `subjects/*.json` for all subjects
- `subjects/index.json` is the single source of truth for what subjects exist
- Extraction scripts committed to repo: `extract_subjects.cjs`, `migrate_index.cjs` (kept for reference)

---

*CLAUDE.md — CramIT Project — Last updated: 2026-06-08 — Sliding segmented filter controls complete. All filter chips replaced with animated seg-controls. applyFilter() pattern documented. Categories/topics null-guard in place.*
*Repo: https://github.com/bustachat/CramIT-Quiz*
*Supabase: https://ohqtefjawaphtsebnaxg.supabase.co*
