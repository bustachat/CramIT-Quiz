# CLAUDE.md — CramIT Project Instructions

> **Strategy for every task: Explore → Plan → Code → Commit**
> Before touching a single line of code, read the relevant files. Then write a plan in plain English. Only then write code. When done, provide exact commit instructions.

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
Netlify auto-deploys on every push to `main`. Remind the owner of this.

---

## 3. Tech Stack — Never Suggest Alternatives

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Single `index.html` — vanilla HTML/CSS/JS | No React, no Vue, no frameworks |
| Hosting | Netlify (free tier) | Functions at `/.netlify/functions/` — NEVER `/api/` |
| Auth | Supabase Auth — email/password + Google OAuth | |
| Database | Supabase (Postgres) — RLS enabled | Client always uses `sbClient` |
| Payments | Stripe — subscription billing | Webhooks verified server-side |
| Webhook handler | Supabase Edge Function named `clever-action` | NOT `stripe-webhook` — this was auto-named |
| AI Agent | Node.js + Anthropic Claude API | Runs via GitHub Actions nightly |
| Repo | GitHub — `bustachat/CramIT-Quiz` | Public repo, main branch |
| Diagram images | Netlify static files at `/diagrams/` | Served from git repo — NOT Supabase Storage. 100GB/mo free vs Supabase's 2GB/mo. Agent auto-deploys new images via git commit. |

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

### 4.2 Netlify
| Setting | Value |
|---|---|
| Build command | None — static site |
| Publish directory | `/` (root) |
| Functions directory | `netlify/functions` |
| Node version | 22 |

**Netlify Environment Variables** (set in Netlify Dashboard → Site → Environment variables):
| Variable | Source |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys |
| `SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Legacy → service_role |

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

Price IDs are stored as constants in `billing.js`, `create-checkout.js`, and `update-subscription.js`. When Stripe switches to live mode, create new Price objects and update all three files.

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

**Agent coordination tables** (from Blueprint V3 — to be deployed):
`agent_tasks`, `agent_logs`, `escalations`, `agent_config`, `content_issues`, `known_issues`, `analytics_snapshots`, `band_descriptors`, `marking_criteria`, `band_mapping`, `written_submissions`

Full schema in `schema.sql` in the repo root.

---

## 6. File Structure

```
cramit-quiz/
├── index.html                  ← Entire PWA app — all quiz logic + billing UI
├── manifest.json               ← PWA manifest (CramIT branding)
├── sw.js                       ← Service worker for offline caching
├── agent.js                    ← Nightly NESA monitor + AI question generator
├── billing.js                  ← Client-side billing module (auth, checkout, pricing calc)
├── subject-selector.html       ← Subject selection UI component
├── package.json                ← { "dependencies": { "stripe": "^14.0.0" } }
├── extract_maths_diagrams.py   ← PDF diagram extractor v3 (PyMuPDF + Pillow + calibration)
├── diagram_registry.json       ← Crop coordinates for all 76 diagram images (2020–2025)
├── process_maths_backlog.js    ← Backlog processor for question generation
├── schema.sql                  ← Supabase table definitions + RLS policies
├── supabase_min.js             ← Local Supabase JS client (loaded via script tag)
├── diagrams/                   ← Exam diagram images — served by Netlify at /diagrams/
│   ├── .gitignore              ← Excludes _debug/ folder from git
│   └── mathematics-standard-2_{year}_Q{n}_{suffix}.jpg
│       suffix = stimulus | A | B | C | D
├── subjects/
│   ├── index.json              ← List of all available subject files
│   └── mathematics-advanced-2024.json
└── netlify/
    └── functions/
        ├── create-checkout.js       ← Creates Stripe Checkout Session
        ├── update-subscription.js   ← Updates Stripe when subjects change
        └── customer-portal.js       ← Opens Stripe billing portal
```

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

### ⬜ Planned Pricing Change — 10-Question Trial (Stage 6)
The current "1 subject free" model leaks revenue from single-subject students. The planned change:
- Remove the permanent free subject
- Replace with a **10-question trial per subject** tracked in `localStorage`
- After 10 questions on any subject, student hits an upgrade prompt
- Student must subscribe to continue (even for a single subject)
- This is **Option A** — keep existing tier structure ($7.99 for 2 subjects), just remove the free tier
- Implementation touches: `canAccess()` in `index.html`, `billing.js`, `create-checkout.js`
- **Do not implement until Stages 1–5 are complete and stable**

---

## 9. Key Code Patterns — Always Follow These

### Netlify function path
```js
// ✅ CORRECT
fetch('/.netlify/functions/create-checkout', { method: 'POST', ... })

// ❌ WRONG — never use /api/
fetch('/api/create-checkout', ...)
```

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
const APP_URL = 'https://YOUR-SITE.netlify.app'; // filled in by owner
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
| Diagram support | `image` field → stimulus above question. `optionImages` array → per-option images inside each button. Paths point to `/diagrams/` (Netlify). | ✅ Done Stage 3 |
| NESA band marking (AI) | AI marks written responses via `/.netlify/functions/mark-written` | ✅ Done Stage 5 |

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

### Image hosting — Netlify `/diagrams/` (NOT Supabase Storage)
All diagram images are committed to the git repo under `diagrams/` and served by Netlify.

**Do NOT use Supabase Storage for exam diagrams.** The `exam-images` bucket in Supabase is retired — it contained old unsplit images (one image per question). The new images are split into stimulus + per-option files.

**Do NOT use `MATHS_IMG` lookup table** — retired in Stage 3. Images are referenced directly on each question object via `image` and `optionImages` fields.

**VET questions** currently use `VET_IMG` with Imgur URLs — keep these until VET diagram extraction is built (post Stage 4).

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
4. Netlify auto-deploys — images immediately available at `/diagrams/filename.jpg`

### Adding diagram support to other subjects
- **VET Construction**: Questions reference `VET_IMG` Imgur URLs — migrate to `/diagrams/` post-launch (low priority)
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
  8. Commits + pushes → Netlify auto-deploys
```

**Agent environment:**
- Runs in GitHub Actions Node.js 22 environment
- Uses `ANTHROPIC_API_KEY` secret from GitHub Settings → Secrets
- Must have `contents: write` permission to commit files
- Claude model to use: `claude-opus-4-5` for quality (or `claude-sonnet-4-6` for speed/cost)

**Written response AI marking** (planned — `/.netlify/functions/mark-written`):
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
- Netlify deployed and building from `main`
- Supabase Edge Function `clever-action` deployed
- Stripe webhook registered pointing to Edge Function
- All secrets added to Netlify and Supabase
- Billing UI wired into `index.html`
- Google login working after redirect URL fix
- `SUPABASE_ANON` and `APP_URL` filled in `index.html`
- **Stage 1 complete** — progress bar glow, year/topic badges on questions, reset confirmation modal, touch targets 52px, safe-area-inset for notched phones
- **Stage 2 complete** — diagram extractor v3, 76 images in `/diagrams/`, calibration mode, stimulus/options split
- **Stage 3 complete** — images wired into quiz renderer (`image` + `optionImages`), `MATHS_IMG` retired, category filter with live counts, HSC 90/Extended 318 toggle
- **Stage 4 complete** — Multimedia + HMS ported into `index.html` with full MC + written question sets
- **Stage 5 complete** — keyword scoring + bandDescriptors on all 42 written questions, upgraded written UI (keyword grid, score heading, colour pills), AI marking via `/.netlify/functions/mark-written` with monthly quota by plan (Free=0, Base=50, Unlimited/Flex=100), student answer display, stem keyword matching, try-again fix, `ANTHROPIC_API_KEY` added to Netlify, SQL migration run in Supabase

### Staged Implementation Roadmap

| Stage | What | Status |
|---|---|---|
| **Stage 1** | Quick wins: reset modal, year/topic badges, progress bar glow, touch targets, safe-area-inset | ✅ **DONE** |
| **Stage 2** | Diagram extractor v3 — stimulus/options split, calibration mode, 76 images committed to repo | ✅ **DONE** |
| **Stage 3** | Wire images into quiz renderer (`image` + `optionImages` on question objects, retire `MATHS_IMG`). Category filter + dynamic counts + HSC 90/Extended 318 toggle | ✅ **DONE** |
| **Stage 4** | Port Multimedia + HMS subjects into index.html | ✅ **DONE** |
| **Stage 5** | Written response + NESA band engine (keyword scoring → Band 1–6 feedback + band-tiered model answers) + AI marking via `/.netlify/functions/mark-written` | ✅ **DONE** |
| **Stage 6** | Pricing model update — 10-question trial replaces 1-free-subject | ⬜ Next |
| **Stage 7** | Agent infrastructure (QA/Testing, Content, Analytics) — separate project | ⬜ |

### ⬜ Still to do (non-staged)

| Task | File(s) | Notes |
|---|---|---|
| Fix remaining billing UI issues | `billing.js`, `index.html` | Test full flow end-to-end in Stripe sandbox |
| Test full payment flow | Stripe sandbox | Use test card `4242 4242 4242 4242` |
| Set `ANTHROPIC_API_KEY` in GitHub Secrets | GitHub Settings | Enables nightly agent |
| Switch Stripe to live mode | Stripe dashboard + Netlify + Supabase secrets | Update all 3 key locations |
| Submit Google OAuth for verification | Google Console | Required for public launch |
| Add custom domain `cramit.com.au` | Netlify → Domain management | Update DNS, update `APP_URL` |
| Deploy agent coordination tables | Supabase SQL editor | From Blueprint V3 Appendix |
| Launch | — | — |

---

## 14. What a "Complete Quiz Engine Upgrade" Means

The biggest priority is bringing `index.html` (the hosted Netlify app) up to the standard of the reference standalone HTML files. Here is the exact feature gap:

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
4. Commit and push — Netlify deploys within ~30 seconds

### Agent method (automatic):
- The nightly `agent.js` handles this automatically once `ANTHROPIC_API_KEY` is set in GitHub Secrets
- Agent commits directly to `main` → Netlify auto-deploys

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
- [ ] Customer portal opens via `/.netlify/functions/customer-portal`

---

## 17. Known Issues

| Issue | Status | Notes |
|---|---|---|
| Stripe is in test/sandbox mode | ⬜ Todo | Switch to live before launch |
| Google OAuth is in Testing mode | ⬜ Todo | Submit for verification |
| `APP_URL` and `SUPABASE_ANON_KEY` were placeholders | ✅ Fixed | Owner filled these in |
| Edge Function named `clever-action` not `stripe-webhook` | ✅ Known, working | Do not rename — webhook registered to this URL |
| Diagram images not rendering in hosted quiz | ✅ Fixed Stage 3 | Images wired via `image`/`optionImages` on question objects. `MATHS_IMG` retired. |
| Written response AI marking not yet built | ✅ Built Stage 5 | `/.netlify/functions/mark-written` live. Quota by plan. Keyword grid fallback. |

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

### In `mark-written.js` (planned Netlify function)
```js
// Never expose ANTHROPIC_API_KEY in browser code
// Always proxy through a Netlify function
// POST /.netlify/functions/mark-written
// Body: { questionId, studentAnswer, maxMarks, markingCriteria }
// Response: { band, marksAwarded, feedback, nextBandModelAnswer }
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
| Netlify | 100GB bandwidth/mo | $0 |
| GitHub | Unlimited public repos | $0 |
| Stripe | No monthly fee | 1.75% + 30¢/txn of revenue only |
| Claude API (agent) | Pay per use | ~$2–5/mo |
| Claude Pro (owner) | N/A | $20/mo |
| Google OAuth | Free forever | $0 |
| **TOTAL** | | **~$22–25/mo + % of revenue** |

At 1,000 active subscribers: ~$105/mo in AI + infra costs (≈1.3% of revenue).

---

## 20. Blueprint V3 — Agent Roster Summary

The Autonomous Operations Blueprint V3 defines 22 agents across 5 clusters. These are **not yet built** — they're the roadmap. Claude should be aware of them when asked about future features:

**Operations (blue):** Content Agent, Incident & Monitoring Agent, Service Desk Agent
**Revenue & Finance (green):** Billing & Subscription Agent, Accounts / Finance Agent
**Growth & Marketing (orange):** Marketing Agent, Notification Agent, Referral Agent, Analytics Agent, SEO Agent, Feedback Synthesis Agent, Onboarding Agent
**Quality & Improvement (purple):** QA / Testing Agent, Development Agent, UX / Design Agent
**Compliance & Strategy (teal):** Compliance Agent, Data Protection Agent, Competitor Intelligence Agent, Pricing Optimisation Agent, Database & Infrastructure Agent, Syllabus & Standards Agent, Security & Threat Agent

All agents communicate through `agent_tasks` table in Supabase. Each has a kill switch in `agent_config` table. Full specs in `CramIT_Autonomous_Operations_Blueprint_V3.docx`.

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

### Landing page (deferred)
The current home screen is student-centric. A general-public-facing landing page is needed before launch — but this is deferred until end-to-end quiz and billing functionality is complete.

---

*CLAUDE.md — CramIT Project — Last updated: May 2026 — Stages 1–5 complete*
*Repo: https://github.com/bustachat/CramIT-Quiz*
*Supabase: https://ohqtefjawaphtsebnaxg.supabase.co*
