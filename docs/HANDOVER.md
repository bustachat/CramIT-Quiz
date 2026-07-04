# CramIT — Session Handover (2026-07-04)

A point-in-time snapshot for whoever (or whichever model) picks this project
up next. Not auto-loaded, not linked from `CLAUDE.md` — read it once at the
start of the next session, then it can be deleted or ignored; it will go
stale fast. The durable references are `CLAUDE.md` (instructions/reference),
`docs/HISTORY.md` (full session log), and `docs/agents-plan.md` (Stage 9).

---

## What happened this session

Started from "do a full code review" and ran the whole arc through to a
clean, documented, tested state. In commit order (all on `main`, all live
on `cramit-quiz.pages.dev`):

1. **`e5fc407`** — 3 critical fixes: written-test submit crash (missing
   modal element IDs), model answers missing from written test results
   (`q.answer` vs `q.modelAnswer` mismatch), PWA icons didn't exist (404s
   broke installability).
2. **`2c42502`** — iOS install banner (Apple never fires
   `beforeinstallprompt`; added manual Add-to-Home-Screen instructions).
3. **`d665c04`** — Security pass: every Cloudflare Function now requires a
   verified Supabase JWT (`functions/_lib/auth.js`); identity derived
   server-side, never trusted from the request body. CORS `*` replaced
   with an origin allowlist. `upgrade-flex.js` deleted (dead,
   unauthenticated Stripe mutation).
4. **`30d463f`** — Follow-up fix: `authHeaders()` was hanging on a stale
   Supabase `getSession()` cross-tab lock, freezing the AI-marking
   spinner. Now races a 4s timeout.
5. **`867e936`** — Docs: confirmed the entitlement SQL migration was run
   in Supabase and auth was verified live.
6. **`bfae24c`** — 3 more bug fixes: trial counter double-incrementing on
   Prev/Next navigation, stale AI-marking results leaking across quiz
   sessions, `handlePaymentReturn()` crashing when the user came back
   from Stripe logged out.
7. **`3cdb85e`** — Housekeeping: deleted 27 orphaned diagram files, the
   dead `mathematics-advanced-2024.json` (incompatible agent schema),
   assorted root scratch files; `db/schema.sql` updated with the
   `user_progress` table + entitlement trigger; `CLAUDE.md` file-tree
   section corrected to match the real repo.
8. **`742c29e`** — Restructured `CLAUDE.md` (84KB → 30KB) into
   `CLAUDE.md` (instructions) / `docs/HISTORY.md` (session log) /
   `docs/agents-plan.md` (Stage 9 planning) to cut per-session token
   cost. Added `scripts/validate_subjects.cjs` + a GitHub Actions
   workflow (`.github/workflows/validate.yml`) that runs it plus a
   syntax check on every Cloudflare function — **first CI in this repo,
   confirmed green** on GitHub.

Also refreshed `~/.claude/CLAUDE.md` (global instructions): current model
table (`opus-4-8`/`sonnet-5`/`haiku-4-5`), removed the obsolete
prompt-caching beta header, added the minimum-cacheable-prefix caveat, and
added a "verify before commit" rule — directly because of item 1 above.

## Verified vs. still-to-verify

**Verified live, in-browser, this session:** written-test submit flow,
model-answer display, PWA icon serving, iOS install banner (all UA
branches), JWT-protected functions (confirmed `/mark-written` returns real
AI feedback with a token, confirmed 401 without one), trial counter fix,
AI-result session isolation, logged-out payment-return banner, CI
workflow (green checkmark confirmed by owner).

**Still open / not yet tested:**
- **Full Stripe sandbox checkout end-to-end** (subscribe 2 subjects with
  `4242 4242 4242 4242` → confirm unlock → billing portal opens → add/
  remove subject → cancel). Called out as pending in `CLAUDE.md` §11
  pre-launch checklist item #1. Timing note: with the entitlement trigger
  live, a slow webhook can make the first `subject_selections` insert
  fail once — the user just re-taps the subject; acceptable but worth
  knowing if it comes up in testing.
- `db/schema.sql`'s `user_progress` table definition was **reconstructed
  from docs, not dumped from the live DB** — verify with `supabase db
  dump` (or equivalent) next time you're in the Supabase CLI, low urgency.

## What's next (not started)

Discussed and deliberately deferred to their own sessions:

1. **Agent pipeline rebuild** — scoped to `agent.js` only (the Content
   Agent), not the full 22-agent Blueprint roster. Needs: a real
   `.github/workflows/` trigger, output schema fixed to match
   `mcQuestions/q/answer` (currently writes `questions/text/correct`),
   and a decision on whether new subjects get registered by updating
   `index.html`'s hardcoded `SUBJECT_ID_MAP`/`SUBJECT_CATALOGUE`
   automatically or the app changes to read `subjects/index.json`
   dynamically. **Recommended: fresh session, model = Fable** (real
   schema/architecture reasoning, not mechanical editing). Bring:
   `docs/agents-plan.md`, `CLAUDE.md` §11 known issues row, `agent.js`
   as it stands today.
2. Everything else on the pre-launch checklist in `CLAUDE.md` §11
   (Google OAuth verification, custom domain, Stripe live mode) —
   owner actions, not code tasks.
3. Bigger builds queued behind the above: `landing.html`, agent fleet
   per `docs/agents-plan.md`, `portal.html`.

## Repo state at handover

- Working tree clean, nothing uncommitted, `main` and `origin/main` in
  sync at `742c29e`.
- CI green on GitHub Actions (`.github/workflows/validate.yml`).
- `node scripts/validate_subjects.cjs` passes with 0 issues (618 MC +
  238 written questions across 4 subjects).
