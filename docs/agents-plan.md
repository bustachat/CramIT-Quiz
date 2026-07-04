# CramIT — Agent Infrastructure Plan (Stage 9)

Not auto-loaded into every session. Read this only when working on **Stage 9
(agent infrastructure)** — none of it is needed for day-to-day app, billing,
or content work. The authoritative full spec is
`CramIT_Autonomous_Operations_Blueprint_V4.docx` at
`C:\Claude Code Space\CRAMIT QUIZ Code Folder\Documents\`; this file is the
condensed, revised build plan on top of it.

---

## Blueprint V4 — Agent Roster Summary

The Autonomous Operations Blueprint V4 defines 22 agents across 5 clusters.

**Revised status per agent (June 2026 review):**

| # | Agent | Decision | Reason |
|---|-------|----------|--------|
| 1 | Content Agent | ✅ **Built 2026-07-04** | Rebuilt `agent.js` (triage + generation, app schema) + `content-agent.yml` (nightly, PR-only = Level 1). Awaiting `ANTHROPIC_API_KEY` GitHub Secret for first live run. See docs/HISTORY.md. |
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

All agents communicate through an `agent_tasks` table in Supabase (not yet deployed — see CLAUDE.md §5 agent coordination tables). Each has a kill switch + `autonomy_level` in an `agent_config` table.

---

## Staging Environment & Release Strategy

### Environment architecture
```
main branch          → cramit-quiz.pages.dev          (LIVE — real students)
staging branch       → staging.cramit-quiz.pages.dev   (TEST — owner only)
agent/* branches     → auto-preview URLs               (AGENT SANDBOX)
```
Cloudflare Pages auto-creates preview URLs for every branch — no extra config needed. **None of this exists yet** — `staging` branch, branch protection, and the staging Supabase project are all still to-do (see CLAUDE.md pre-launch infrastructure table).

### Branch protection rules (set on GitHub before any agent work)
- `main`: Require PR + 1 approval (owner). No direct pushes — not even from owner.
- `staging`: Require PR. No approval needed (agents can self-merge here after passing tests).
- `agent/*`: No restrictions — agents commit freely here.

### Staging Supabase project
- Separate free-tier Supabase project — NOT the production database
- Same schema as production (copy `db/schema.sql`)
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
Every agent imports from `agents/lib/safety.js` (not yet built):
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

## Agent Build Order — Revised (June 2026)

### Phase 1 — Before launch (core stability)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Content Agent (rebuild `agent.js`) | NESA monitoring + question generation | Schema currently incompatible with app — rebuild is the Stage 9 prerequisite |
| QA / Testing Agent | Playwright tests on every deploy | Catches regressions before students |
| Database & Infrastructure Agent | Daily Supabase/CF capacity checks | Prevents surprise outages |
| UptimeRobot (not custom) | HTTP uptime monitoring | Free, 2-minute setup |

### Phase 2 — First students (student-facing automation)
| Agent | What it does | Why now |
|-------|-------------|---------|
| Onboarding Agent | Day 0/1/3/7/14 email sequence | Trial → paid conversion |
| Billing & Subscription Agent | Payment events, churn prevention | Automates what `handleManageBilling()` currently punts to Stripe's portal |
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
