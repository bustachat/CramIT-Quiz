// functions/_lib/auth.js — shared auth + CORS for Cloudflare Pages Functions.
// Files/dirs prefixed with "_" are excluded from routing but can be imported.
//
// Every billing/AI function verifies the caller's Supabase JWT and derives
// the user identity server-side — request bodies are never trusted for
// user_id / customer_id / subscription_id.

const PROD_ORIGIN = 'https://cramit-quiz.pages.dev';
// When cramit.com.au goes live, add it here.
const EXTRA_ORIGINS = [];

export function corsHeaders(request) {
  const origin = request?.headers?.get('Origin') || '';
  const allowed =
    origin === PROD_ORIGIN ||
    origin.endsWith('.cramit-quiz.pages.dev') || // Cloudflare preview deploys
    EXTRA_ORIGINS.includes(origin)
      ? origin
      : PROD_ORIGIN;
  return {
    'Access-Control-Allow-Origin':  allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Vary': 'Origin',
  };
}

// Verifies the Bearer token against Supabase Auth. Returns the user object
// ({ id, email, ... }) or null if missing/invalid/expired.
export async function requireUser(request, env) {
  const auth = request.headers.get('Authorization') || '';
  if (!auth.startsWith('Bearer ')) return null;
  const token = auth.slice(7);
  try {
    const res = await fetch(`${env.SUPABASE_URL}/auth/v1/user`, {
      headers: {
        'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!res.ok) return null;
    const user = await res.json();
    return user && user.id ? user : null;
  } catch {
    return null;
  }
}

export function unauthorized(cors) {
  return new Response(
    JSON.stringify({ error: 'Not signed in — please sign in and try again.' }),
    { status: 401, headers: { 'Content-Type': 'application/json', ...cors } }
  );
}

// Fetch the authenticated user's subscription row (service-role read).
export async function getSubscriptionRow(userId, env, select = '*') {
  const url = `${env.SUPABASE_URL}/rest/v1/subscriptions?user_id=eq.${encodeURIComponent(userId)}&select=${select}&limit=1`;
  const res = await fetch(url, {
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
    },
  });
  if (!res.ok) throw new Error(`Supabase subscriptions query failed: ${res.status}`);
  const rows = await res.json();
  return rows[0] || null;
}

// Count the authenticated user's selected subjects (service-role read).
export async function countSubjectSelections(userId, env) {
  const url = `${env.SUPABASE_URL}/rest/v1/subject_selections?user_id=eq.${encodeURIComponent(userId)}&select=subject_id`;
  const res = await fetch(url, {
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
    },
  });
  if (!res.ok) throw new Error(`Supabase subject_selections query failed: ${res.status}`);
  const rows = await res.json();
  return rows.length;
}
