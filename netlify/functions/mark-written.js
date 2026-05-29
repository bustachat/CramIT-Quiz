// netlify/functions/mark-written.js
//
// AI marking for CramIT written-response questions.
// Called by index.html → tryAiMarking()
//
// Flow:
//   1. Validate request body
//   2. Fetch user subscription from Supabase (REST API — no SDK needed)
//   3. Check + lazy-reset monthly AI quota
//   4. Call Claude Sonnet with structured marking prompt
//   5. Increment ai_marks_used in Supabase
//   6. Return { aiMarked, marksAwarded, grade, feedback, improvement, marksRemaining }
//
// On quota exceeded → { quotaExceeded: true, reason, marksRemaining: 0 }
// On any server error → HTTP 500 (frontend falls back to keyword grid silently)
//
// Env vars required (Netlify Dashboard → Site → Environment variables):
//   ANTHROPIC_API_KEY
//   SUPABASE_URL
//   SUPABASE_SERVICE_ROLE_KEY

// ── Quota by plan ──────────────────────────────────────────────────────────
const QUOTA = {
  free:      0,
  base:      50,
  unlimited: 100,
  flex:      100,
};

const SUPABASE_URL         = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const ANTHROPIC_API_KEY    = process.env.ANTHROPIC_API_KEY;

// ── Main handler ────────────────────────────────────────────────────────────
exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const { userId, question, maxMarks, keywords, studentAnswer, bandDescriptors, subject } = body;

  if (!userId || !question || !studentAnswer || !maxMarks) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Missing required fields: userId, question, maxMarks, studentAnswer' }),
    };
  }

  // ── 1. Fetch subscription ──────────────────────────────────────────────
  let sub;
  try {
    sub = await getSubscription(userId);
  } catch (err) {
    console.error('mark-written: subscription fetch error:', err.message);
    return { statusCode: 500, body: JSON.stringify({ error: 'Could not verify subscription' }) };
  }

  const plan = (sub && sub.plan) || 'free';
  const quota = QUOTA[plan] ?? 0;

  // ── 2. Quota check ─────────────────────────────────────────────────────
  if (quota === 0) {
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        quotaExceeded: true,
        reason: 'no_plan',
        message: 'AI marking is available on Base plan and above.',
        marksRemaining: 0,
      }),
    };
  }

  // Lazy monthly reset — if ai_marks_reset_at is >30 days ago, reset the counter
  const resetAt = sub.ai_marks_reset_at ? new Date(sub.ai_marks_reset_at) : new Date(0);
  const daysSinceReset = (Date.now() - resetAt.getTime()) / (1000 * 60 * 60 * 24);
  let aiMarksUsed = sub.ai_marks_used || 0;

  if (daysSinceReset >= 30) {
    // Reset the counter — we'll write this alongside the increment below
    aiMarksUsed = 0;
  }

  if (aiMarksUsed >= quota) {
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        quotaExceeded: true,
        reason: 'quota_reached',
        message: `You've used all ${quota} AI marks for this month. Resets in ~${Math.ceil(30 - daysSinceReset)} day(s).`,
        marksRemaining: 0,
      }),
    };
  }

  // ── 3. Build Claude prompt ─────────────────────────────────────────────
  const keywordList = (keywords || []).join(', ');
  const bandContext = bandDescriptors
    ? `\nBand descriptors for this question:\n- Full marks: ${bandDescriptors.full}\n- Partial marks: ${bandDescriptors.partial}\n- Minimal marks: ${bandDescriptors.minimal}`
    : '';

  const systemPrompt = `You are an expert HSC marker for NSW students. You mark written responses fairly and constructively, following NESA marking guidelines. Always respond with valid JSON only — no prose outside the JSON object.`;

  const userPrompt = `Mark the following student response to an HSC ${subject || 'written'} question.

QUESTION: ${question}
MAXIMUM MARKS: ${maxMarks}
KEY CONCEPTS EXPECTED: ${keywordList || 'See question context'}${bandContext}

STUDENT ANSWER: "${studentAnswer}"

Return a JSON object with exactly these fields:
{
  "marksAwarded": <integer 0–${maxMarks}>,
  "grade": <"excellent" | "good" | "developing">,
  "feedback": "<2–3 sentences: what the student did well and/or what was missing. Be specific and constructive. Do not quote the student's exact words back.>",
  "improvement": "<1–2 sentences: the single most important thing they should add or clarify to reach full marks. If already full marks, write 'Great response — aim to maintain this level of detail in your exam.'>",
  "keyConceptsFound": [<list of key concepts from the expected list that the student addressed>]
}

Grading guide:
- "excellent": ${maxMarks} marks (all key concepts addressed, clear and accurate)
- "good": ${Math.ceil(maxMarks * 0.5)}–${maxMarks - 1} marks (most key concepts present, minor gaps)
- "developing": 0–${Math.floor(maxMarks * 0.4)} marks (key concepts missing or incorrect)

Return ONLY the JSON object. No markdown, no explanation.`;

  // ── 4. Call Claude API ─────────────────────────────────────────────────
  let aiResponse;
  try {
    aiResponse = await callClaude(systemPrompt, userPrompt);
  } catch (err) {
    console.error('mark-written: Claude API error:', err.message);
    return { statusCode: 500, body: JSON.stringify({ error: 'AI marking unavailable' }) };
  }

  // ── 5. Increment quota counter ─────────────────────────────────────────
  try {
    await incrementQuota(userId, daysSinceReset >= 30);
  } catch (err) {
    // Non-fatal — don't block the student from seeing their result
    console.error('mark-written: quota increment error:', err.message);
  }

  const marksRemaining = quota - aiMarksUsed - 1;

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      aiMarked: true,
      marksAwarded:     aiResponse.marksAwarded,
      maxMarks:         maxMarks,
      grade:            aiResponse.grade,
      feedback:         aiResponse.feedback,
      improvement:      aiResponse.improvement,
      keyConceptsFound: aiResponse.keyConceptsFound || [],
      marksRemaining:   Math.max(0, marksRemaining),
    }),
  };
};

// ── Helpers ──────────────────────────────────────────────────────────────────

async function getSubscription(userId) {
  const url = `${SUPABASE_URL}/rest/v1/subscriptions?user_id=eq.${userId}&select=plan,status,ai_marks_used,ai_marks_reset_at&limit=1`;
  const res = await fetch(url, {
    headers: {
      'apikey':        SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
      'Content-Type':  'application/json',
    },
  });
  if (!res.ok) throw new Error(`Supabase GET failed: ${res.status}`);
  const rows = await res.json();
  return rows[0] || null;
}

async function incrementQuota(userId, resetMonth) {
  const now = new Date().toISOString();
  const patch = resetMonth
    ? { ai_marks_used: 1, ai_marks_reset_at: now }
    : { ai_marks_used: null }; // will use RPC increment below

  if (resetMonth) {
    // Full reset + set to 1
    const url = `${SUPABASE_URL}/rest/v1/subscriptions?user_id=eq.${userId}`;
    const res = await fetch(url, {
      method:  'PATCH',
      headers: {
        'apikey':        SUPABASE_SERVICE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
        'Content-Type':  'application/json',
        'Prefer':        'return=minimal',
      },
      body: JSON.stringify({ ai_marks_used: 1, ai_marks_reset_at: now, updated_at: now }),
    });
    if (!res.ok) throw new Error(`Supabase PATCH (reset) failed: ${res.status}`);
  } else {
    // Use Supabase RPC to safely increment (avoids race conditions)
    const url = `${SUPABASE_URL}/rest/v1/rpc/increment_ai_marks`;
    const res = await fetch(url, {
      method:  'POST',
      headers: {
        'apikey':        SUPABASE_SERVICE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
        'Content-Type':  'application/json',
      },
      body: JSON.stringify({ p_user_id: userId }),
    });
    if (!res.ok) {
      // Fallback: plain PATCH if RPC not deployed yet
      const fallbackUrl = `${SUPABASE_URL}/rest/v1/subscriptions?user_id=eq.${userId}`;
      // We can't do "+1" in REST directly, so read then write (slight race risk, acceptable)
      const readRes = await fetch(`${fallbackUrl}&select=ai_marks_used`, {
        headers: {
          'apikey':        SUPABASE_SERVICE_KEY,
          'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
        },
      });
      const rows = await readRes.json();
      const current = (rows[0] && rows[0].ai_marks_used) || 0;
      await fetch(fallbackUrl, {
        method:  'PATCH',
        headers: {
          'apikey':        SUPABASE_SERVICE_KEY,
          'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
          'Content-Type':  'application/json',
          'Prefer':        'return=minimal',
        },
        body: JSON.stringify({ ai_marks_used: current + 1, updated_at: new Date().toISOString() }),
      });
    }
  }
}

async function callClaude(systemPrompt, userPrompt) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method:  'POST',
    headers: {
      'Content-Type':      'application/json',
      'x-api-key':         ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model:      'claude-sonnet-4-5',
      max_tokens: 512,
      system:     systemPrompt,
      messages:   [{ role: 'user', content: userPrompt }],
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Claude API ${res.status}: ${errText}`);
  }

  const data = await res.json();
  const raw  = data.content[0].text.trim();

  // Strip markdown code fences if Claude adds them despite the instruction
  const cleaned = raw.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '').trim();

  try {
    return JSON.parse(cleaned);
  } catch {
    throw new Error(`Claude returned non-JSON: ${raw.substring(0, 200)}`);
  }
}
