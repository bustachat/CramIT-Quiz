#!/usr/bin/env python3
"""Generate Olivier's HMS FA2 Study Tool - olivier-hms-prep.html"""

import json, re

with open('subjects/pdhpe-hms.json', encoding='utf-8') as f:
    data = json.load(f)

fa2_mc = [q for q in data['mcQuestions'] if q.get('topic','').startswith('fa2_')]
fa2_written = [q for q in data['writtenQuestions'] if q.get('topic','').startswith('fa2_')]

Q_JSON = json.dumps(fa2_mc, ensure_ascii=False)
W_JSON = json.dumps(fa2_written, ensure_ascii=False)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Olivier — HMS FA2 Study Guide</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#F0F2F5;color:#1A1A2E;min-height:100vh}

/* ── HEADER ── */
.header{background:linear-gradient(135deg,#1A1A2E 0%,#3B3B6E 100%);color:#fff;padding:20px 20px 0;text-align:center}
.header h1{font-size:clamp(18px,4vw,26px);font-weight:800;letter-spacing:-0.5px}
.header p{font-size:13px;opacity:0.7;margin-top:4px;margin-bottom:16px}
.tabs{display:flex;gap:4px;justify-content:center;flex-wrap:wrap;padding-bottom:0}
.tab-btn{background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;padding:10px 18px;border-radius:10px 10px 0 0;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;white-space:nowrap}
.tab-btn.active{background:#fff;color:#1A1A2E}

/* ── PANELS ── */
.panel{display:none;padding:20px;max-width:900px;margin:0 auto}
.panel.active{display:block}

/* ── TOPIC COLORS ── */
:root{
  --assess:#3B82F6; --methods:#10B981; --principles:#F59E0B;
  --adaptations:#EF4444; --periodisation:#8B5CF6; --nutrition:#F97316;
  --psychology:#06B6D4; --indgroup:#6366F1; --sleep:#0EA5E9;
}

/* ── STUDY CARDS ── */
.topic-section{margin-bottom:24px}
.topic-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)}
.topic-header{padding:14px 18px;display:flex;align-items:center;gap:12px;cursor:pointer;user-select:none}
.topic-header:hover{filter:brightness(0.96)}
.topic-icon{font-size:22px}
.topic-title{font-size:16px;font-weight:700;color:#fff;flex:1}
.topic-count{font-size:12px;color:rgba(255,255,255,0.75);background:rgba(0,0,0,0.2);padding:2px 8px;border-radius:20px}
.chevron{color:rgba(255,255,255,0.8);font-size:14px;transition:transform 0.25s}
.topic-header.open .chevron{transform:rotate(180deg)}
.topic-body{padding:18px;display:none;border-top:1px solid #F0F2F5}
.topic-body.open{display:block}

.note-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
@media(max-width:600px){.note-grid{grid-template-columns:1fr}}
.note-box{background:#F8F9FA;border-radius:10px;padding:12px}
.note-box h4{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;opacity:0.6}
.note-box ul{list-style:none;display:flex;flex-direction:column;gap:5px}
.note-box li{font-size:13px;line-height:1.5;padding-left:14px;position:relative}
.note-box li::before{content:"•";position:absolute;left:0;opacity:0.5}
.note-box li b{color:#1A1A2E}

.exam-tip{border-radius:10px;padding:12px 14px;margin-top:10px;font-size:13px;line-height:1.5}
.exam-tip strong{display:block;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;opacity:0.8}
.soccer-eg{background:#E8F5E9;border-left:3px solid #10B981;border-radius:0 8px 8px 0;padding:10px 12px;margin-top:10px;font-size:13px;line-height:1.5}
.soccer-eg strong{color:#10B981;display:block;font-size:11px;text-transform:uppercase;margin-bottom:2px}

/* ── DIAGRAMS ── */
.diagram-wrap{background:#F8F9FA;border-radius:12px;padding:16px;margin-top:12px;text-align:center}
.diagram-wrap h4{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;opacity:0.5;margin-bottom:12px}
.phases-row{display:flex;gap:8px;margin-top:8px}
.phase-box{flex:1;border-radius:10px;padding:12px 8px;text-align:center}
.phase-box h5{font-size:12px;font-weight:800;margin-bottom:6px;color:#fff}
.phase-box p{font-size:11px;color:rgba(255,255,255,0.85);line-height:1.4}
.howscse-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-top:8px}
@media(max-width:500px){.howscse-grid{grid-template-columns:repeat(4,1fr)}}
.howscse-cell{border-radius:8px;padding:8px 4px;text-align:center}
.howscse-cell .letter{font-size:20px;font-weight:900;line-height:1}
.howscse-cell .word{font-size:9px;margin-top:2px;line-height:1.2;opacity:0.85}
.taper-row{display:flex;flex-direction:column;gap:8px;margin-top:8px;align-items:flex-start;width:100%}
.taper-item{display:flex;align-items:center;gap:10px;width:100%}
.taper-label{font-size:11px;font-weight:700;width:110px;text-align:right;flex-shrink:0}
.taper-bars{display:flex;gap:3px;align-items:flex-end;height:32px}
.tbar{width:22px;border-radius:3px 3px 0 0;background:var(--periodisation)}

/* ── PRACTICE TAB ── */
.topic-pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.pill{border:none;padding:8px 14px;border-radius:20px;font-size:13px;font-weight:600;cursor:pointer;opacity:0.45;transition:all 0.2s;color:#fff}
.pill.active{opacity:1;transform:scale(1.05)}
.q-card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:16px}
.q-meta{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;opacity:0.5}
.q-text{font-size:15px;font-weight:600;line-height:1.5;margin-bottom:16px}
.options{display:flex;flex-direction:column;gap:8px}
.opt-btn{background:#F8F9FA;border:2px solid #E5E7EB;border-radius:10px;padding:12px 14px;font-size:14px;text-align:left;cursor:pointer;transition:all 0.2s;line-height:1.4}
.opt-btn:hover:not(:disabled){background:#F0F2F5;border-color:#D1D5DB}
.opt-btn.correct{background:#DCFCE7;border-color:#10B981;color:#065F46}
.opt-btn.wrong{background:#FEE2E2;border-color:#EF4444;color:#7F1D1D}
.opt-btn.show-correct{background:#DCFCE7;border-color:#10B981;color:#065F46}
.explanation{background:#F0FDF4;border-radius:10px;padding:14px;margin-top:14px;font-size:13px;line-height:1.6;display:none}
.explanation.show{display:block}
.explanation strong{display:block;margin-bottom:4px;color:#10B981;font-size:12px;text-transform:uppercase}
.quiz-nav{display:flex;justify-content:space-between;align-items:center;margin-top:16px}
.quiz-score{font-size:13px;font-weight:600;color:#6B7280}
.btn-next{background:#1A1A2E;color:#fff;border:none;padding:10px 22px;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;display:none}
.btn-next.show{display:block}
.results-card{background:#fff;border-radius:16px;padding:28px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08)}
.results-card h2{font-size:28px;font-weight:900;margin-bottom:8px}
.results-card p{color:#6B7280;margin-bottom:20px}
.btn-retry{background:#1A1A2E;color:#fff;border:none;padding:12px 28px;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer}

/* ── WRITTEN TAB ── */
.written-tabs{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.wt-btn{background:#fff;border:2px solid #E5E7EB;border-radius:10px;padding:10px 18px;font-size:14px;font-weight:700;cursor:pointer;transition:all 0.2s}
.wt-btn.active{border-color:#1A1A2E;background:#1A1A2E;color:#fff}
.scaffold-card{background:#fff;border-radius:16px;padding:22px;box-shadow:0 2px 12px rgba(0,0,0,0.08);display:none}
.scaffold-card.active{display:block}
.scaffold-step{display:flex;gap:14px;margin-bottom:16px;position:relative}
.scaffold-step::after{content:'';position:absolute;left:19px;top:40px;bottom:-16px;width:2px;background:#E5E7EB}
.scaffold-step:last-child::after{display:none}
.step-num{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:900;color:#fff;flex-shrink:0}
.step-content{flex:1;padding-top:8px}
.step-content h3{font-size:15px;font-weight:800;margin-bottom:4px}
.step-content p{font-size:13px;color:#4B5563;line-height:1.5}
.step-content .anchor{background:#FEF3C7;border-radius:8px;padding:10px 12px;margin-top:8px;font-size:13px;line-height:1.5;border-left:3px solid #F59E0B}
.step-content .anchor strong{display:block;font-size:11px;color:#92400E;text-transform:uppercase;margin-bottom:3px}
.mark-badge{display:inline-block;background:#1A1A2E;color:#fff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;margin-bottom:16px}
.expand-btn{background:#F8F9FA;border:1px solid #E5E7EB;border-radius:8px;padding:8px 14px;font-size:13px;font-weight:600;cursor:pointer;margin-top:12px;width:100%;text-align:left}
.model-answer{background:#F0FDF4;border-radius:10px;padding:16px;margin-top:10px;font-size:13px;line-height:1.7;display:none;white-space:pre-wrap}
.model-answer.show{display:block}

/* ── MOCK EXAM TAB ── */
.mock-start{text-align:center;padding:40px 20px}
.mock-start h2{font-size:24px;font-weight:900;margin-bottom:10px}
.mock-start p{color:#6B7280;margin-bottom:8px;font-size:14px;line-height:1.6}
.mock-start ul{text-align:left;display:inline-block;margin:16px 0;font-size:14px;line-height:2}
.btn-start-mock{background:linear-gradient(135deg,#1A1A2E,#3B3B6E);color:#fff;border:none;padding:14px 36px;border-radius:14px;font-size:16px;font-weight:800;cursor:pointer;margin-top:8px}
.mock-active{display:none}
.timer-bar{background:#1A1A2E;color:#fff;padding:14px 20px;border-radius:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;position:sticky;top:0;z-index:10}
.timer-display{font-size:24px;font-weight:900;font-variant-numeric:tabular-nums}
.timer-display.urgent{color:#EF4444}
.mock-progress{font-size:13px;opacity:0.7}
.mock-q-card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:16px}
.mock-q-num{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;opacity:0.5;margin-bottom:8px}
.mock-opt{background:#F8F9FA;border:2px solid #E5E7EB;border-radius:10px;padding:12px 14px;font-size:14px;text-align:left;cursor:pointer;width:100%;margin-bottom:8px;transition:all 0.2s;display:block}
.mock-opt.selected{background:#EEF2FF;border-color:#6366F1}
.mock-opt.mock-correct{background:#DCFCE7;border-color:#10B981;color:#065F46}
.mock-opt.mock-wrong{background:#FEE2E2;border-color:#EF4444;color:#7F1D1D}
.written-section{background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:16px}
.written-section h3{font-size:16px;font-weight:800;margin-bottom:6px}
.written-section .marks{font-size:12px;color:#6B7280;margin-bottom:12px}
.written-section textarea{width:100%;border:2px solid #E5E7EB;border-radius:10px;padding:12px;font-size:14px;line-height:1.6;resize:vertical;min-height:120px;font-family:inherit}
.written-section textarea:focus{outline:none;border-color:#6366F1}
.btn-submit-mock{background:#10B981;color:#fff;border:none;padding:14px 36px;border-radius:14px;font-size:16px;font-weight:800;cursor:pointer;width:100%;margin-top:8px}
.mock-results{display:none;background:#fff;border-radius:16px;padding:28px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08)}
.mock-results h2{font-size:26px;font-weight:900;margin-bottom:6px}
.mock-results p{color:#6B7280;font-size:14px;margin-bottom:20px}
.review-item{text-align:left;padding:14px;border-radius:10px;margin-bottom:10px;font-size:13px;line-height:1.5}
.review-item .ri-q{font-weight:600;margin-bottom:6px}
.review-item .ri-ans{font-size:12px;opacity:0.7}
.btn-new-mock{background:#1A1A2E;color:#fff;border:none;padding:12px 28px;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;margin-top:8px}

/* ── UTILS ── */
.section-title{font-size:18px;font-weight:800;margin-bottom:16px;color:#1A1A2E}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px;margin-right:6px;margin-bottom:6px}
</style>
</head>
<body>

<div class="header">
  <h1>📖 Olivier&#39;s HMS FA2 Study Guide</h1>
  <p>Assessment: Monday 29.6.26 &nbsp;·&nbsp; 10 MC + 3 Written &nbsp;·&nbsp; 50 minutes</p>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('study')">📚 Study</button>
    <button class="tab-btn" onclick="showTab('practice')">⚡ Practice MC</button>
    <button class="tab-btn" onclick="showTab('written')">✍️ Written Help</button>
    <button class="tab-btn" onclick="showTab('mock')">🎯 Mock Exam</button>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════ STUDY TAB -->
<div id="tab-study" class="panel active">
  <p style="font-size:13px;color:#6B7280;margin-bottom:18px;margin-top:4px">Tap any topic to expand. Learn the <b>bold</b> terms. One soccer example per topic.</p>

  <!-- EXERCISE ASSESSMENT -->
  <div class="topic-card">
    <div class="topic-header" style="background:var(--assess)" onclick="toggleTopic(this)">
      <span class="topic-icon">🩺</span>
      <span class="topic-title">Exercise Assessment &amp; Prescription</span>
      <span class="topic-count">8 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>PAR-Q</h4>
          <ul>
            <li><b>Pre-exercise questionnaire</b> — screens for health risks before starting</li>
            <li>Identifies contraindications (e.g. heart conditions)</li>
            <li>Completed before any new exercise program</li>
            <li>Professional clearance if risk identified</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Fitness Testing</h4>
          <ul>
            <li><b>Recreational</b> → baseline health, set general goals</li>
            <li><b>Elite</b> → track performance benchmarks, measure training effect</li>
            <li>Tests: VO₂ max, beep test, 1RM, skinfold, Cooper run</li>
            <li>Results → inform training program design</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#EFF6FF;border-left:3px solid var(--assess)">
        <strong>⚡ Exam Tip</strong>
        Know the KEY DIFFERENCE: recreational = health goal | elite = performance tracking. A 3-mark Q will likely ask you to explain or distinguish these.
      </div>
      <div class="soccer-eg">
        <strong>⚽ Soccer Example</strong>
        A soccer player completes a PAR-Q before pre-season → doctor identifies elevated blood pressure → medically cleared before full training begins. Fitness testing (beep test, VO₂ max) then sets performance benchmarks to track improvement across the season.
      </div>
    </div>
  </div>

  <!-- TRAINING METHODS -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--methods)" onclick="toggleTopic(this)">
      <span class="topic-icon">🏃</span>
      <span class="topic-title">Training Methods</span>
      <span class="topic-count">18 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>Anaerobic</h4>
          <ul>
            <li><b>HIIT</b> — 85-95% MHR, short bursts + recovery</li>
            <li><b>SIT</b> — ALL-OUT maximal sprints, longer rest</li>
            <li><b>Plyometrics</b> — explosive jumps, fast-twitch focus</li>
            <li><b>Resistance</b> — weights, hypertrophy/strength</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Aerobic</h4>
          <ul>
            <li><b>Continuous</b> — steady 60-80% MHR, &gt;20 min</li>
            <li><b>Fartlek</b> — varied speeds, unpredictable terrain</li>
            <li><b>Aerobic interval</b> — work:rest, moderate-high intensity</li>
            <li><b>Circuit</b> — stations, multiple fitness components</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Flexibility</h4>
          <ul>
            <li><b>Static</b> — hold 15–30s → AFTER exercise only</li>
            <li><b>Dynamic</b> — controlled movement → BEFORE exercise</li>
            <li><b>Ballistic</b> — bouncing (injury risk, rarely used)</li>
            <li><b>PNF</b> — contract then relax → GREATEST ROM gains</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Other Methods</h4>
          <ul>
            <li><b>Strength</b> — free/fixed weights, body weight, elastics</li>
            <li><b>Skill &amp; tactical</b> — drills, modified games</li>
            <li>Skill development = sport-specific movements</li>
            <li>Tactical = game sense, decision-making under pressure</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#F0FDF4;border-left:3px solid var(--methods)">
        <strong>⚡ Exam Tip</strong>
        Static = AFTER, Dynamic = BEFORE. PNF = greatest ROM. These distinctions appear in almost every exam. Also know: fartlek mimics game demands (variable intensity).
      </div>
      <div class="soccer-eg">
        <strong>⚽ Soccer Example</strong>
        A soccer midfielder uses <b>fartlek training</b> — alternating between sprinting and jogging mirrors the unpredictable intensity demands of a 90-minute match. Pre-season uses <b>continuous training</b> to build aerobic base before <b>aerobic interval</b> training in-season raises match-intensity.
      </div>
    </div>
  </div>

  <!-- PRINCIPLES OF TRAINING -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--principles)" onclick="toggleTopic(this)">
      <span class="topic-icon">⚖️</span>
      <span class="topic-title">Principles of Training</span>
      <span class="topic-count">10 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>The 6 Principles</h4>
          <ul>
            <li><b>Progressive overload</b> — gradually ↑ load → force adaptation</li>
            <li><b>Specificity</b> — train the energy system/muscle you'll use</li>
            <li><b>Reversibility</b> — stop training → lose gains (use it or lose it)</li>
            <li><b>Variety</b> — change stimulus → prevent staleness + plateaus</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Thresholds + Warm-up</h4>
          <ul>
            <li><b>Aerobic threshold</b> — 55–85% max HR</li>
            <li><b>Anaerobic threshold</b> — above lactate threshold</li>
            <li><b>Warm-up</b> — elevate HR, stretch, skill rehearsal → injury prevention</li>
            <li><b>Cool-down</b> — return to rest, remove waste products</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#FFFBEB;border-left:3px solid var(--principles)">
        <strong>⚡ Exam Tip</strong>
        The 12-marker will ask you to LINK principles → adaptations → performance. Know the chain: progressive overload → cardiac hypertrophy → ↓ resting HR → improved endurance performance.
      </div>
      <div class="soccer-eg">
        <strong>⚽ Soccer Example</strong>
        A soccer player applies <b>progressive overload</b> — increases sprint intervals from 6×30s to 8×30s each week → cardiac hypertrophy develops → resting HR drops from 72 to 58 bpm → can sustain high intensity for a full 90 minutes.
      </div>
    </div>
  </div>

  <!-- PHYSIOLOGICAL ADAPTATIONS -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--adaptations)" onclick="toggleTopic(this)">
      <span class="topic-icon">❤️</span>
      <span class="topic-title">Physiological Adaptations</span>
      <span class="topic-count">10 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>Cardiovascular</h4>
          <ul>
            <li>↓ <b>Resting HR</b> — cardiac hypertrophy (stronger heart)</li>
            <li>↑ <b>Stroke volume</b> — more blood per beat</li>
            <li>↑ <b>Cardiac output</b> — HR × SV = more O₂ delivered</li>
            <li>↑ <b>Haemoglobin</b> — more O₂ carried in blood</li>
            <li>↑ <b>VO₂ max</b> — body uses more oxygen per minute</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Muscular</h4>
          <ul>
            <li><b>Muscle hypertrophy</b> — ↑ cross-section → more force</li>
            <li>↑ <b>Fast-twitch fibres</b> → power + speed (anaerobic)</li>
            <li>↑ <b>Slow-twitch fibres</b> → endurance (aerobic)</li>
            <li>↑ Mitochondrial density → more aerobic energy</li>
            <li>↑ Lung capacity → more O₂ absorbed per breath</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#FEF2F2;border-left:3px solid var(--adaptations)">
        <strong>⚡ Exam Tip</strong>
        Always link the adaptation to a performance outcome. Don't just say "stroke volume increases" — say "stroke volume increases, so more blood is pumped per beat, delivering more O₂ to muscles, allowing the soccer player to maintain high-intensity running for longer."
      </div>
      <div class="soccer-eg">
        <strong>⚽ Soccer Example</strong>
        After pre-season aerobic training, a midfielder's resting HR drops 72 → 58 bpm (<b>cardiac hypertrophy</b>). Stroke volume rises — each heartbeat delivers more O₂. VO₂ max improves — the player can run further at higher intensity without fatiguing.
      </div>
    </div>
  </div>

  <!-- PERIODISATION -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--periodisation)" onclick="toggleTopic(this)">
      <span class="topic-icon">📅</span>
      <span class="topic-title">Periodisation &amp; Yearly Programs</span>
      <span class="topic-count">10 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="diagram-wrap">
        <h4>Phases of Competition</h4>
        <div class="phases-row">
          <div class="phase-box" style="background:#8B5CF6">
            <h5>PRE-SEASON</h5>
            <p>HIGH volume<br>Moderate intensity<br>Build base<br>Team tactics</p>
          </div>
          <div class="phase-box" style="background:#6366F1">
            <h5>IN-SEASON</h5>
            <p>↓ volume<br>HIGH intensity<br>Maintain fitness<br>Peak for games</p>
          </div>
          <div class="phase-box" style="background:#4F46E5">
            <h5>OFF-SEASON</h5>
            <p>1 wk total rest<br>Active recovery<br>Address weaknesses<br>Rehab injuries</p>
          </div>
        </div>
      </div>
      <div class="note-grid" style="margin-top:12px">
        <div class="note-box">
          <h4>Sub-phases</h4>
          <ul>
            <li><b>Macrocycle</b> — full annual plan</li>
            <li><b>Mesocycle</b> — 4–8 week block</li>
            <li><b>Microcycle</b> — 7–10 day block (most detailed)</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Tapering</h4>
          <ul>
            <li><b>Step</b> — 33%→33% reduction (strength athletes)</li>
            <li><b>Linear</b> — gradual equal reduction</li>
            <li><b>Exp. slow decay</b> — big early cut → 40–50% (endurance)</li>
            <li><b>Exp. fast decay</b> — big early cut → 20–30%</li>
          </ul>
        </div>
      </div>
      <div class="diagram-wrap">
        <h4>Tapering Types — Volume Reduction</h4>
        <div class="taper-row">
          <div class="taper-item">
            <span class="taper-label">Step</span>
            <div class="taper-bars">
              <div class="tbar" style="height:32px"></div>
              <div class="tbar" style="height:32px"></div>
              <div class="tbar" style="height:21px"></div>
              <div class="tbar" style="height:21px"></div>
              <div class="tbar" style="height:11px"></div>
              <div class="tbar" style="height:11px"></div>
            </div>
            <span style="font-size:11px;color:#6B7280;margin-left:6px">Best for strength athletes</span>
          </div>
          <div class="taper-item">
            <span class="taper-label">Linear</span>
            <div class="taper-bars">
              <div class="tbar" style="height:32px"></div>
              <div class="tbar" style="height:26px"></div>
              <div class="tbar" style="height:20px"></div>
              <div class="tbar" style="height:14px"></div>
              <div class="tbar" style="height:8px"></div>
            </div>
            <span style="font-size:11px;color:#6B7280;margin-left:6px">Gradual equal reduction</span>
          </div>
          <div class="taper-item">
            <span class="taper-label">Exp. Slow</span>
            <div class="taper-bars">
              <div class="tbar" style="height:32px"></div>
              <div class="tbar" style="height:18px"></div>
              <div class="tbar" style="height:14px"></div>
              <div class="tbar" style="height:13px"></div>
              <div class="tbar" style="height:12px"></div>
            </div>
            <span style="font-size:11px;color:#6B7280;margin-left:6px">Best for endurance athletes</span>
          </div>
          <div class="taper-item">
            <span class="taper-label">Exp. Fast</span>
            <div class="taper-bars">
              <div class="tbar" style="height:32px"></div>
              <div class="tbar" style="height:12px"></div>
              <div class="tbar" style="height:8px"></div>
              <div class="tbar" style="height:7px"></div>
              <div class="tbar" style="height:7px"></div>
            </div>
            <span style="font-size:11px;color:#6B7280;margin-left:6px">Rapid early reduction</span>
          </div>
        </div>
      </div>
      <div class="exam-tip" style="background:#F5F3FF;border-left:3px solid var(--periodisation)">
        <strong>⚡ KEY for 12-marker</strong>
        Soccer team = 1-day rest mini-taper (plays every week). Marathon runner = 2-week full taper (one annual race). This difference is the most commonly tested point in the compare question.
      </div>
    </div>
  </div>

  <!-- NUTRITION -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--nutrition)" onclick="toggleTopic(this)">
      <span class="topic-icon">🍌</span>
      <span class="topic-title">Nutrition &amp; Dietary Requirements</span>
      <span class="topic-count">12 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>Timing</h4>
          <ul>
            <li><b>Pre (3–4hr)</b> — LOW GI carbs, moderate protein, low fat/fibre</li>
            <li><b>During (&gt;60min)</b> — HIGH GI, 30–60g carbs/hr, 200–300mL fluid every 15–20min</li>
            <li><b>Post</b> — HIGH GI + protein → glycogen + muscle repair</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Carb Loading</h4>
          <ul>
            <li><b>Who</b> — endurance events &gt;90 minutes only</li>
            <li><b>How</b> — 7–12g/kg body weight/day</li>
            <li><b>Duration</b> — 36–72 hours</li>
            <li><b>Must also</b> — taper training (or it won't work)</li>
            <li>Improves performance by ~2–3%</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Key Nutrients</h4>
          <ul>
            <li><b>Electrolytes</b> — Na, K, Ca, Mg → lost in sweat → cramps if depleted</li>
            <li><b>Iron</b> — haemoglobin production → O₂ transport → deficiency = early fatigue</li>
            <li><b>LOW GI</b> — oats, grainy bread, lentils (slow release)</li>
            <li><b>HIGH GI</b> — gels, bananas, white bread (fast release)</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>RED-S + Hydration</h4>
          <ul>
            <li><b>RED-S</b> — insufficient energy intake → hormonal disruption, bone health</li>
            <li>Affects female athletes most — 25–60% at risk</li>
            <li><b>Fluid</b> — 200–300mL every 15–20min during exercise</li>
            <li>Pale yellow urine = well hydrated</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#FFF7ED;border-left:3px solid var(--nutrition)">
        <strong>⚡ Exam Tip</strong>
        LOW GI before, HIGH GI during/after. Carb loading only works WITH tapering. These are the two most tested nutrition concepts.
      </div>
      <div class="soccer-eg">
        <strong>⚽ Soccer Example</strong>
        A soccer player eats oats + banana (LOW GI) 3hr before kickoff for sustained energy. At half time consumes a sports gel (HIGH GI) for rapid glucose. Post-match: pasta + chicken to replenish glycogen and repair muscle micro-tears.
      </div>
    </div>
  </div>

  <!-- PSYCHOLOGY -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--psychology)" onclick="toggleTopic(this)">
      <span class="topic-icon">🧠</span>
      <span class="topic-title">Psychological Strategies</span>
      <span class="topic-count">12 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="diagram-wrap">
        <h4>Inverted U Hypothesis — Arousal vs Performance</h4>
        <svg viewBox="0 0 320 160" width="100%" style="max-width:360px;display:block;margin:0 auto">
          <line x1="30" y1="140" x2="300" y2="140" stroke="#D1D5DB" stroke-width="2"/>
          <line x1="30" y1="140" x2="30" y2="15" stroke="#D1D5DB" stroke-width="2"/>
          <path d="M 40 135 Q 90 100 115 60 Q 140 20 165 20 Q 190 20 215 60 Q 240 100 275 135" stroke="var(--psychology)" stroke-width="3.5" fill="none" stroke-linecap="round"/>
          <circle cx="165" cy="20" r="5" fill="var(--psychology)"/>
          <circle cx="75" cy="110" r="5" fill="#F59E0B"/>
          <circle cx="255" cy="110" r="5" fill="#EF4444"/>
          <text x="165" y="12" text-anchor="middle" font-size="12" font-weight="800" fill="var(--psychology)">B — OPTIMAL</text>
          <text x="55" y="108" text-anchor="middle" font-size="11" font-weight="700" fill="#F59E0B">A</text>
          <text x="255" y="108" text-anchor="middle" font-size="11" font-weight="700" fill="#EF4444">C</text>
          <text x="40" y="155" font-size="10" fill="#9CA3AF">Low arousal</text>
          <text x="240" y="155" font-size="10" fill="#9CA3AF">High arousal</text>
          <text x="8" y="80" font-size="9" fill="#9CA3AF" transform="rotate(-90,8,80)">Performance</text>
        </svg>
        <div style="display:flex;gap:12px;justify-content:center;margin-top:10px;flex-wrap:wrap">
          <span style="font-size:12px"><span style="color:#F59E0B;font-weight:700">A</span> = Under-aroused: low motivation, poor focus</span>
          <span style="font-size:12px"><span style="color:var(--psychology);font-weight:700">B</span> = Optimal: peak performance</span>
          <span style="font-size:12px"><span style="color:#EF4444;font-weight:700">C</span> = Over-aroused: tense, errors</span>
        </div>
      </div>
      <div class="note-grid" style="margin-top:12px">
        <div class="note-box">
          <h4>Arousal &amp; Anxiety</h4>
          <ul>
            <li><b>Arousal</b> — physiological activation (NOT anxiety)</li>
            <li>Fine motor (archery, golf) → LOW arousal optimal</li>
            <li>Gross motor (weightlifting) → HIGH arousal optimal</li>
            <li><b>Trait anxiety</b> — anxious before EVERY game (personality)</li>
            <li><b>State anxiety</b> — only grand final (situation-specific)</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Strategies</h4>
          <ul>
            <li><b>Mental rehearsal</b> — visualise success at performance speed</li>
            <li><b>Relaxation</b> — meditation, PMR, centred breathing</li>
            <li><b>Concentration</b> — focus on PROCESS not outcome</li>
            <li><b>SMART goals</b> — Specific, Measurable, Achievable, Relevant, <b>Time-bound</b></li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#ECFEFF;border-left:3px solid var(--psychology)">
        <strong>⚡ Exam Tip</strong>
        A 5-mark Q will ask you to apply strategies to BOTH individual (soccer player) AND group (netball team). Use different strategies for each. Individual = mental rehearsal + centred breathing. Group = meditation + concentration skills.
      </div>
    </div>
  </div>

  <!-- INDIVIDUAL VS GROUP -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--indgroup)" onclick="toggleTopic(this)">
      <span class="topic-icon">👥</span>
      <span class="topic-title">Individual vs Group Sports Training</span>
      <span class="topic-count">12 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="diagram-wrap">
        <h4>H-O-W-S-C-S-E Training Session Components</h4>
        <div class="howscse-grid">
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">H</div><div class="word">Health &amp; Safety</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">O</div><div class="word">Overview / Aim</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">W</div><div class="word">Warm-up &amp; Cool-down</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">S</div><div class="word">Skill Instruction</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">C</div><div class="word">Conditioning</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">S</div><div class="word">Strategies &amp; Tactics</div></div>
          <div class="howscse-cell" style="background:#EEF2FF;color:var(--indgroup)"><div class="letter">E</div><div class="word">Evaluation</div></div>
        </div>
      </div>
      <div class="note-grid" style="margin-top:12px">
        <div class="note-box">
          <h4>Individual Sport EXTRA</h4>
          <ul>
            <li>Personal race strategies (sit and kick)</li>
            <li>Individual technique focus</li>
            <li>2-week taper before major event</li>
            <li>Peaks 1–2 times per year</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Group Sport EXTRA</h4>
          <ul>
            <li>Team formations + tactics</li>
            <li>Small-sided games (3v3, 4v3) — simulate game pressure</li>
            <li>1-day rest mini-taper before each game</li>
            <li>Must peak EVERY week of the season</li>
          </ul>
        </div>
      </div>
      <div class="note-box" style="margin-top:12px">
        <h4>Warm-up Phases (in order)</h4>
        <ul>
          <li><b>Phase 1</b> — General body (jog 5–10min) → ↑ heart rate + temperature</li>
          <li><b>Phase 2</b> — Stretching (dynamic) → ↑ ROM, reduce injury risk</li>
          <li><b>Phase 3</b> — Callisthenics → sport-specific exercises</li>
          <li><b>Phase 4</b> — Skill rehearsal → movements specific to the game</li>
        </ul>
      </div>
      <div class="exam-tip" style="background:#EEF2FF;border-left:3px solid var(--indgroup)">
        <strong>⚡ Key Difference — Tapering</strong>
        Marathon runner = 2-week taper (1 annual race). Soccer team = 1-day rest before each weekly game. This is the most tested compare point.
      </div>
    </div>
  </div>

  <!-- SLEEP & HYDRATION -->
  <div class="topic-card" style="margin-top:14px">
    <div class="topic-header" style="background:var(--sleep)" onclick="toggleTopic(this)">
      <span class="topic-icon">💧</span>
      <span class="topic-title">Sleep &amp; Hydration</span>
      <span class="topic-count">8 MC</span>
      <span class="chevron">▼</span>
    </div>
    <div class="topic-body">
      <div class="note-grid">
        <div class="note-box">
          <h4>Sleep</h4>
          <ul>
            <li>Athletes need <b>8–10 hours</b> per night</li>
            <li>Deep sleep → <b>growth hormone</b> → protein synthesis → muscle repair</li>
            <li>Poor sleep → ↑ <b>cortisol</b> → ↑ inflammation → ↑ injury risk</li>
            <li>Basketball players +10hrs → improved shooting by <b>9%</b></li>
            <li>Restores nervous system → better reaction time</li>
          </ul>
        </div>
        <div class="note-box">
          <h4>Hydration</h4>
          <ul>
            <li><b>Dehydration</b> — excessive water loss → ↓ blood volume → ↓ O₂ → fatigue</li>
            <li>Symptoms: headache, cramps, dizziness, slow reactions</li>
            <li>During exercise: <b>200–300mL every 15–20min</b></li>
            <li><b>Pale yellow</b> urine = well hydrated</li>
            <li>Hydration maintains synovial fluid → smoother joints</li>
          </ul>
        </div>
      </div>
      <div class="exam-tip" style="background:#E0F2FE;border-left:3px solid var(--sleep)">
        <strong>⚡ Exam Tip</strong>
        Always link sleep/hydration to a MECHANISM: sleep → growth hormone → protein synthesis. Dehydration → ↓ blood volume → less O₂ to muscles → fatigue. Don't just say "sleep is important."
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════ PRACTICE TAB -->
<div id="tab-practice" class="panel">
  <p class="section-title">⚡ Practice MC</p>
  <div class="topic-pills" id="pill-container">
    <button class="pill active" style="background:var(--assess)" onclick="filterPractice('fa2_assessment')">🩺 Assessment</button>
    <button class="pill" style="background:var(--methods)" onclick="filterPractice('fa2_methods')">🏃 Methods</button>
    <button class="pill" style="background:var(--principles)" onclick="filterPractice('fa2_principles')">⚖️ Principles</button>
    <button class="pill" style="background:var(--adaptations)" onclick="filterPractice('fa2_adaptations')">❤️ Adaptations</button>
    <button class="pill" style="background:var(--periodisation)" onclick="filterPractice('fa2_periodisation')">📅 Periodisation</button>
    <button class="pill" style="background:var(--nutrition)" onclick="filterPractice('fa2_nutrition')">🍌 Nutrition</button>
    <button class="pill" style="background:var(--psychology)" onclick="filterPractice('fa2_psychology')">🧠 Psychology</button>
    <button class="pill" style="background:var(--indgroup)" onclick="filterPractice('fa2_individual_group')">👥 Indiv vs Group</button>
    <button class="pill" style="background:var(--sleep)" onclick="filterPractice('fa2_sleep')">💧 Sleep</button>
  </div>
  <div id="practice-area"></div>
</div>

<!-- ═══════════════════════════════════════════════════════ WRITTEN TAB -->
<div id="tab-written" class="panel">
  <p class="section-title">✍️ Written Answer Scaffolds</p>
  <div class="written-tabs">
    <button class="wt-btn active" onclick="showScaffold('s12')">12-mark</button>
    <button class="wt-btn" onclick="showScaffold('s5')">5-mark</button>
    <button class="wt-btn" onclick="showScaffold('s3')">3-mark</button>
  </div>

  <!-- 12 MARKER -->
  <div id="scaffold-s12" class="scaffold-card active">
    <span class="mark-badge">12 marks — ~20 minutes</span>
    <p style="font-size:13px;color:#6B7280;margin-bottom:20px">The 12-marker will almost certainly ask you to <b>compare a yearly training program</b> for individual vs group sport, or <b>analyse how fitness requirements change across phases</b>. Use this scaffold regardless of the exact wording.</p>
    <div class="scaffold-step">
      <div class="step-num" style="background:#1A1A2E">1</div>
      <div class="step-content">
        <h3>INTRO — Define + State (2 sentences)</h3>
        <p>Define what a yearly training program is. State you will compare individual (marathon runner) vs group (soccer team).</p>
        <div class="anchor"><strong>📝 Anchor phrase</strong>"A yearly training program divides into three phases — pre-season, in-season and off-season — with macrocycles, mesocycles and microcycles enabling detailed planning. These phases differ significantly for a marathon runner (individual) and a soccer team (group sport) due to differences in competition frequency and fitness demands."</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#8B5CF6">2</div>
      <div class="step-content">
        <h3>PRE-SEASON — Compare both athletes</h3>
        <p>High volume, moderate intensity for both. Difference: group adds team tactics + small-sided games.</p>
        <div class="anchor"><strong>📝 Key point</strong>Marathon runner: continuous + fartlek → aerobic base, VO₂ max, running economy.<br>Soccer team: same aerobic base PLUS team formations, set plays, small-sided games (3v3). Group sport needs collective skill alongside individual fitness.</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#6366F1">3</div>
      <div class="step-content">
        <h3>IN-SEASON — The biggest difference</h3>
        <p>Both reduce volume, increase intensity. But tapering is completely different.</p>
        <div class="anchor"><strong>📝 Key point — most marks here</strong>Marathon runner: race-specific speed work, 2-WEEK taper before the annual race, peaks 1–2 times per year.<br>Soccer team: must peak EVERY week — only a 1-DAY rest mini-taper before each game. Extended tapering is impractical with weekly fixtures.</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#4F46E5">4</div>
      <div class="step-content">
        <h3>OFF-SEASON — Both recover</h3>
        <p>1 week total rest → active rest for both. Small differences in focus.</p>
        <div class="anchor"><strong>📝 Key point</strong>Both: 1 week total rest then active rest, address weaknesses.<br>Marathon runner: technical improvements (biomechanics), injury rehab.<br>Soccer team: individual player rehab + maintain base fitness for next pre-season.</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#10B981">5</div>
      <div class="step-content">
        <h3>EVALUATE — Why do the differences exist?</h3>
        <p>One evaluative sentence that explains the root cause of all the differences.</p>
        <div class="anchor"><strong>📝 Anchor phrase</strong>"The fundamental structural difference is competition frequency — a marathon runner tapers for 2 weeks before one annual event, while a soccer team requires near-peak performance every week, making extended tapering impractical and requiring ongoing fatigue management through mini-tapers."</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#6B7280">6</div>
      <div class="step-content">
        <h3>CONCLUSION — 2 sentences max</h3>
        <div class="anchor"><strong>📝 Anchor phrase</strong>"Both programs manipulate volume and intensity to optimise performance at the right time, but differ significantly in tapering strategy, peaking frequency and integration of skill and tactical development — reflecting the fundamental differences between individual endurance and group sport demands."</div>
      </div>
    </div>
    <button class="expand-btn" onclick="toggleModel('model-12')">👁 Show full model answer</button>
    <div id="model-12" class="model-answer">INTRODUCTION
A yearly training program divides into three phases — pre-season, in-season and off-season — with macrocycles, mesocycles and microcycles enabling detailed planning. These phases differ significantly for a marathon runner (individual) and a soccer team (group sport) due to differences in competition frequency and fitness demands.

PRE-SEASON
Both athletes build a fitness base at high volume and moderate intensity. For the marathon runner, pre-season involves continuous training and fartlek to build aerobic capacity, VO₂ max and running economy — directly linked to solo endurance demands. For the soccer team, pre-season also includes aerobic base work but adds team strategies, set plays and small-sided games (3v3) — because group sport performance requires collective skill and tactical cohesion alongside individual fitness.

IN-SEASON
Both shift to lower volume and higher intensity as competition approaches — specificity applied more rigorously. The marathon runner undergoes race-specific speed work targeting lactate threshold. However, the soccer team faces weekly games, requiring near-peak performance every match. The marathon runner can taper for 2 full weeks before a major race, while the soccer team uses only a 1-day rest as a mini-taper before each game — extended tapering is simply impractical when competing weekly.

OFF-SEASON
Both athletes enter recovery — 1 week of total rest followed by active rest. The marathon runner uses this period to address technical weaknesses in running biomechanics, while the soccer team focuses on individual player rehabilitation and general fitness maintenance.

EVALUATE
The fundamental structural difference is competition frequency. A marathon runner peaks 1–2 times per year with a full 2-week taper, maximising physiological preparation. A soccer team must perform at near-peak every week — making extended tapering impractical and requiring ongoing fatigue management through sub-phases and mini-tapers.

CONCLUSION
Both programs manipulate volume and intensity to optimise performance at the right time, but differ significantly in tapering strategy, peaking frequency and the integration of skill and tactical development — reflecting the fundamental differences between individual endurance and group sport demands.</div>
  </div>

  <!-- 5 MARKER -->
  <div id="scaffold-s5" class="scaffold-card">
    <span class="mark-badge">5 marks — ~8 minutes</span>
    <p style="font-size:13px;color:#6B7280;margin-bottom:20px">A 5-marker will likely ask you to <b>explain or compare</b> one concept across individual and group sports, OR explain psychological strategies applied to both.</p>
    <div class="scaffold-step">
      <div class="step-num" style="background:#1A1A2E">1</div>
      <div class="step-content">
        <h3>DEFINE the concept (1 sentence)</h3>
        <p>Name and define the thing being asked about. E.g. "Arousal is a physiological state of activation and readiness to perform."</p>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#6366F1">2</div>
      <div class="step-content">
        <h3>INDIVIDUAL SPORT — apply with example</h3>
        <p>Apply to individual athlete (soccer player or marathon runner). Use specific detail + outcome.</p>
        <div class="anchor"><strong>📝 Formula</strong>[Individual athlete] uses [strategy/concept] by [specific action] which leads to [performance outcome].</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#8B5CF6">3</div>
      <div class="step-content">
        <h3>GROUP SPORT — apply with example</h3>
        <p>Apply to group sport (soccer team or netball team). Must be a DIFFERENT strategy or different application.</p>
        <div class="anchor"><strong>📝 Formula</strong>[Group/team] uses [strategy/concept] by [specific collective action] which leads to [team performance outcome].</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#10B981">4</div>
      <div class="step-content">
        <h3>LINK to performance improvement</h3>
        <p>One sentence connecting both examples to improved performance or reduced anxiety.</p>
      </div>
    </div>
    <button class="expand-btn" onclick="toggleModel('model-5')">👁 Show example 5-mark answer (Psychology)</button>
    <div id="model-5" class="model-answer">Question: Explain how a soccer player and a netball team can each apply psychological strategies to manage stress and anxiety and improve performance.

A soccer player may use mental rehearsal (visualisation) to manage pre-game anxiety — imagining successful passes, positioning and scoring at performance speed. This creates a clear performance blueprint that narrows focus and reduces anxious thoughts, helping the player reach optimal arousal before kickoff. They may also practise centred breathing before a penalty to control over-arousal and prevent muscular tension disrupting their technique.

A netball team may use group meditation before a grand final to manage collective over-arousal — narrowing each player's thoughts and calming physiological stress responses. The coach may also apply concentration/attention skills by asking players to focus on executing set plays (process) rather than worrying about the scoreline (outcome), keeping the team calm and decisive under pressure.

Together, these strategies reduce anxiety, optimise arousal and allow both individual and team athletes to perform closer to their physical and technical potential.</div>
  </div>

  <!-- 3 MARKER -->
  <div id="scaffold-s3" class="scaffold-card">
    <span class="mark-badge">3 marks — ~4 minutes</span>
    <p style="font-size:13px;color:#6B7280;margin-bottom:20px">A 3-marker will ask you to <b>define + explain + example</b>. Three clear sentences, one per mark.</p>
    <div class="scaffold-step">
      <div class="step-num" style="background:#EF4444">1</div>
      <div class="step-content">
        <h3>DEFINE — 1 mark</h3>
        <p>One sentence: what is it? Use the correct terminology.</p>
        <div class="anchor"><strong>📝 Example</strong>"Arousal is a physiological state of physical and mental activation that prepares the body for performance."</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#F59E0B">2</div>
      <div class="step-content">
        <h3>EXPLAIN — 1 mark</h3>
        <p>One sentence: how/why does it work? Mention the mechanism.</p>
        <div class="anchor"><strong>📝 Example</strong>"The inverted U hypothesis shows that as arousal rises to an optimal level, performance improves — but if arousal becomes excessive, muscular tension and mental confusion cause performance to decline."</div>
      </div>
    </div>
    <div class="scaffold-step">
      <div class="step-num" style="background:#10B981">3</div>
      <div class="step-content">
        <h3>EXAMPLE — 1 mark</h3>
        <p>One sentence: sport-specific example with a named outcome.</p>
        <div class="anchor"><strong>📝 Example</strong>"A soccer player who is over-aroused before a penalty kick may experience excessive muscle tension, leading to a loss of precision and a missed shot."</div>
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════ MOCK EXAM TAB -->
<div id="tab-mock" class="panel">
  <div class="mock-start" id="mock-start">
    <h2>🎯 Mock Exam</h2>
    <p>Simulates your actual assessment.<br>50-minute countdown. No feedback until you submit.</p>
    <ul>
      <li>✅ 10 Multiple Choice questions (randomly selected)</li>
      <li>✅ 3 Written questions (3, 5 and 12 marks)</li>
      <li>✅ Timer counts down from 50:00</li>
      <li>⚠️ MC answers revealed after submit — written is self-marked</li>
    </ul>
    <button class="btn-start-mock" onclick="startMock()">Start Mock Exam →</button>
  </div>
  <div class="mock-active" id="mock-active">
    <div class="timer-bar">
      <span style="font-weight:700;font-size:15px">🎯 Mock Exam</span>
      <span id="timer-display" class="timer-display">50:00</span>
      <span id="mock-progress-label" class="mock-progress">Q 1 of 10</span>
    </div>
    <div id="mock-questions"></div>
    <button class="btn-submit-mock" onclick="submitMock()">Submit &amp; See Results</button>
  </div>
  <div class="mock-results" id="mock-results">
    <h2 id="mock-score-title"></h2>
    <p id="mock-score-sub"></p>
    <div id="mock-review"></div>
    <button class="btn-new-mock" onclick="resetMock()">Try Another Mock</button>
  </div>
</div>

<script>
const QUESTIONS = ''' + Q_JSON + ''';
const WRITTEN_Q = ''' + W_JSON + ''';

// ── TABS ──────────────────────────────────────────────────────────────
function showTab(id) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  event.target.classList.add('active');
  if (id === 'practice' && !practiceLoaded) initPractice();
}

// ── STUDY TOPIC TOGGLE ────────────────────────────────────────────────
function toggleTopic(header) {
  const body = header.nextElementSibling;
  const isOpen = body.classList.contains('open');
  header.classList.toggle('open', !isOpen);
  body.classList.toggle('open', !isOpen);
}

// ── PRACTICE MC ───────────────────────────────────────────────────────
let practiceLoaded = false;
let practiceQ = [];
let practiceIdx = 0;
let practiceScore = 0;
let practiceAnswered = false;
let currentTopic = 'fa2_assessment';

function initPractice() {
  practiceLoaded = true;
  filterPractice('fa2_assessment');
}

function filterPractice(topic) {
  currentTopic = topic;
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  practiceQ = QUESTIONS.filter(q => q.topic === topic).sort(() => Math.random() - 0.5);
  practiceIdx = 0;
  practiceScore = 0;
  practiceAnswered = false;
  renderPracticeQ();
}

function renderPracticeQ() {
  const area = document.getElementById('practice-area');
  if (practiceIdx >= practiceQ.length) {
    const pct = Math.round(practiceScore / practiceQ.length * 100);
    const emoji = pct >= 80 ? '🎉' : pct >= 60 ? '💪' : '📚';
    area.innerHTML = `<div class="results-card">
      <h2>${emoji} ${practiceScore} / ${practiceQ.length}</h2>
      <p>${pct}% — ${pct >= 80 ? 'Excellent! You know this topic.' : pct >= 60 ? 'Good effort — review the ones you missed.' : 'Keep practising — review the study notes then try again.'}</p>
      <button class="btn-retry" onclick="filterPracticeRetry('${currentTopic}')">Try Again</button>
    </div>`;
    return;
  }
  const q = practiceQ[practiceIdx];
  const shuffled = q.options.map((o,i) => ({text:o, idx:i})).sort(() => Math.random()-0.5);
  const topicLabel = q.topic.replace('fa2_','').replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase());
  area.innerHTML = `<div class="q-card">
    <div class="q-meta">${topicLabel} &nbsp;·&nbsp; Q ${practiceIdx+1} of ${practiceQ.length}</div>
    <div class="q-text">${q.q}</div>
    <div class="options" id="opts">
      ${shuffled.map(o => `<button class="opt-btn" onclick="selectOpt(this,${o.idx},${q.answer})">${o.text}</button>`).join('')}
    </div>
    <div class="explanation" id="expl">
      <strong>✓ Explanation</strong>${q.explanation || ''}
    </div>
    <div class="quiz-nav">
      <span class="quiz-score">Score: ${practiceScore} / ${practiceIdx}</span>
      <button class="btn-next show" id="btn-next" onclick="nextPractice()" style="display:none">Next →</button>
    </div>
  </div>`;
  practiceAnswered = false;
}

function selectOpt(btn, selectedIdx, correctIdx) {
  if (practiceAnswered) return;
  practiceAnswered = true;
  const opts = document.querySelectorAll('.opt-btn');
  opts.forEach(b => b.disabled = true);
  if (selectedIdx === correctIdx) {
    btn.classList.add('correct');
    practiceScore++;
  } else {
    btn.classList.add('wrong');
    opts.forEach(b => {
      const idx = parseInt(b.getAttribute('onclick').match(/\d+/g)[0]);
      if (idx === correctIdx) b.classList.add('show-correct');
    });
  }
  document.getElementById('expl').classList.add('show');
  document.getElementById('btn-next').style.display = 'block';
}

function nextPractice() {
  practiceIdx++;
  practiceAnswered = false;
  renderPracticeQ();
}

function filterPracticeRetry(topic) {
  practiceQ = QUESTIONS.filter(q => q.topic === topic).sort(() => Math.random()-0.5);
  practiceIdx = 0; practiceScore = 0; practiceAnswered = false;
  renderPracticeQ();
}

// ── WRITTEN SCAFFOLDS ─────────────────────────────────────────────────
function showScaffold(id) {
  document.querySelectorAll('.scaffold-card').forEach(c => c.classList.remove('active'));
  document.querySelectorAll('.wt-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('scaffold-' + id).classList.add('active');
  event.target.classList.add('active');
}

function toggleModel(id) {
  const el = document.getElementById(id);
  el.classList.toggle('show');
  event.target.textContent = el.classList.contains('show') ? '▲ Hide model answer' : '👁 Show full model answer';
}

// ── MOCK EXAM ─────────────────────────────────────────────────────────
let mockTimer, mockTimeLeft = 50*60;
let mockQs = [], mockAnswers = {};

function startMock() {
  document.getElementById('mock-start').style.display = 'none';
  document.getElementById('mock-active').style.display = 'block';
  mockQs = [...QUESTIONS].sort(() => Math.random()-0.5).slice(0,10);
  mockAnswers = {};
  renderMockQuestions();
  mockTimeLeft = 50*60;
  mockTimer = setInterval(() => {
    mockTimeLeft--;
    const m = Math.floor(mockTimeLeft/60), s = mockTimeLeft%60;
    const disp = document.getElementById('timer-display');
    disp.textContent = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    disp.classList.toggle('urgent', mockTimeLeft <= 300);
    if (mockTimeLeft <= 0) { clearInterval(mockTimer); submitMock(); }
  }, 1000);
}

function renderMockQuestions() {
  const written3 = WRITTEN_Q.filter(q=>q.maxMark===3).sort(()=>Math.random()-0.5)[0];
  const written5 = WRITTEN_Q.filter(q=>q.maxMark===5).sort(()=>Math.random()-0.5)[0];
  const written12 = WRITTEN_Q.filter(q=>q.maxMark===12).sort(()=>Math.random()-0.5)[0];
  let html = '<p style="font-size:13px;color:#6B7280;margin-bottom:16px;font-weight:600">SECTION I — Multiple Choice (10 marks)</p>';
  mockQs.forEach((q,i) => {
    const shuffled = q.options.map((o,idx)=>({text:o,idx})).sort(()=>Math.random()-0.5);
    html += `<div class="mock-q-card">
      <div class="mock-q-num">Question ${i+1}</div>
      <div class="q-text">${q.q}</div>
      ${shuffled.map(o=>`<button class="mock-opt" id="mq${i}_${o.idx}" onclick="selectMockOpt(${i},${o.idx},this)">${o.text}</button>`).join('')}
    </div>`;
  });
  html += '<p style="font-size:13px;color:#6B7280;margin:24px 0 16px;font-weight:600">SECTION II — Written Response</p>';
  if(written3) html += `<div class="written-section"><h3>${written3.q}</h3><div class="marks">3 marks — approx. 4 minutes</div><textarea placeholder="Write your answer here..." rows="5"></textarea></div>`;
  if(written5) html += `<div class="written-section"><h3>${written5.q}</h3><div class="marks">5 marks — approx. 8 minutes</div><textarea placeholder="Write your answer here..." rows="8"></textarea></div>`;
  if(written12) html += `<div class="written-section" id="written12"><h3>${written12.q}</h3><div class="marks">12 marks — approx. 20 minutes</div><textarea placeholder="Write your answer here..." rows="16"></textarea><div style="font-size:12px;color:#9CA3AF;margin-top:6px">Tip: Use the Written Help tab scaffold — INTRO → PRE-SEASON → IN-SEASON → OFF-SEASON → EVALUATE → CONCLUSION</div></div>`;
  document.getElementById('mock-questions').innerHTML = html;
}

function selectMockOpt(qIdx, optIdx, btn) {
  const q = mockQs[qIdx];
  document.querySelectorAll(`[id^="mq${qIdx}_"]`).forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  mockAnswers[qIdx] = optIdx;
  document.getElementById('mock-progress-label').textContent = `${Object.keys(mockAnswers).length} of 10 answered`;
}

function submitMock() {
  clearInterval(mockTimer);
  document.getElementById('mock-active').style.display = 'none';
  const results = document.getElementById('mock-results');
  results.style.display = 'block';
  let correct = 0;
  mockQs.forEach((q,i) => { if(mockAnswers[i]===q.answer) correct++; });
  const pct = Math.round(correct/10*100);
  document.getElementById('mock-score-title').textContent = `MC: ${correct}/10 (${pct}%)`;
  document.getElementById('mock-score-sub').textContent = pct>=80?'Excellent MC performance! Check your written answers against the scaffolds.':pct>=60?'Good — review the questions you missed.':'Revisit the Study tab for the topics you found hard.';
  let reviewHtml = '<p style="font-weight:700;font-size:14px;margin-bottom:12px;text-align:left">MC Review:</p>';
  mockQs.forEach((q,i) => {
    const userAns = mockAnswers[i];
    const isCorrect = userAns === q.answer;
    reviewHtml += `<div class="review-item" style="background:${isCorrect?'#DCFCE7':'#FEE2E2'}">
      <div class="ri-q">Q${i+1}: ${q.q.substring(0,80)}${q.q.length>80?'...':''}</div>
      <div class="ri-ans">${isCorrect?'✓ Correct':'✗ Your answer: '+(userAns!==undefined?q.options[userAns]:'Not answered')+' | Correct: '+q.options[q.answer]}</div>
      <div style="font-size:12px;margin-top:4px;opacity:0.8">${q.explanation||''}</div>
    </div>`;
  });
  reviewHtml += '<p style="font-weight:700;font-size:14px;margin:20px 0 8px;text-align:left">Written: Self-mark using the Written Help tab ✍️</p>';
  document.getElementById('mock-review').innerHTML = reviewHtml;
}

function resetMock() {
  document.getElementById('mock-results').style.display = 'none';
  document.getElementById('mock-start').style.display = 'block';
  clearInterval(mockTimer);
  mockTimeLeft = 50*60;
}
</script>
</body>
</html>'''

with open('olivier-hms-prep.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print("Generated: olivier-hms-prep.html")
