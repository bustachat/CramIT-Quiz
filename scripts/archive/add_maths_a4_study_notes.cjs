// One-off script: appends the A4 Non-linear Relationships studyNotes
// topic to subjects/mathematics-standard-2.json (fifth Maths Study Mode
// topic). Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_a4_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'a4-nonlinear-relationships')) {
  console.log('a4-nonlinear-relationships already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const a4 = {
  id: 'a4-nonlinear-relationships',
  icon: '📉',
  title: 'A4 — Non-linear Relationships',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Simultaneous equations (break-even & comparisons)',
          html: '<ul>\n<li>Two linear equations (e.g. a cost equation and a revenue equation, or two payment plans) can be compared by finding where they\'re <b>equal</b> — this is the "break-even point"</li>\n<li>Solved either <b>graphically</b> (the intersection point of the two lines) or <b>algebraically</b> (set the two expressions equal and solve)</li>\n<li>Before the intersection point one option is better; after it, the other is — always check which side of the break-even point the question is actually asking about</li>\n</ul>'
        },
        {
          heading: 'Quadratic graphs — parabolas',
          html: '<ul>\n<li><b><em>y</em> = <em>ax</em>² + <em>bx</em> + <em>c</em></b> — if <em>a</em> &gt; 0 the parabola opens <b>upward</b> (a minimum turning point); if <em>a</em> &lt; 0 it opens <b>downward</b> (a maximum turning point)</li>\n<li><em>c</em> is the <em>y</em>-intercept (the value when <em>x</em> = 0)</li>\n<li>To recognise a parabola\'s graph, check which way it opens first (sign of <em>a</em>), then check the <em>y</em>-intercept matches</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Projectile motion (quadratics in context)',
          html: '<ul>\n<li>Height over time for a thrown/launched object is modelled by a <b>downward-opening parabola</b>, e.g. <em>h</em> = −5<em>t</em>² + 80<em>t</em></li>\n<li>The object is on the ground when <em>h</em> = 0 — this happens at the start (<em>t</em> = 0) and again when it lands, so solving <em>h</em> = 0 gives the <b>total time in the air</b></li>\n<li>The negative coefficient on <em>t</em>² reflects gravity pulling the object back down — it\'s always negative in these models</li>\n</ul>'
        },
        {
          heading: 'Exponential graphs',
          html: '<ul>\n<li><b><em>y</em> = <em>a</em>(<em>b</em>)ˣ</b> — <em>a</em> is the starting value (at <em>x</em> = 0), <em>b</em> is the growth/decay factor</li>\n<li><em>b</em> &gt; 1 → <b>growth</b> (curve rises, gets steeper); 0 &lt; <em>b</em> &lt; 1 → <b>decay</b> (curve falls, flattening toward — but never reaching — zero)</li>\n<li>This is the exact same shape as F4\'s compound interest formula — money and populations both follow <em>y</em> = <em>a</em>(<em>b</em>)ˣ</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Recognising a graph from its equation',
      headers: ['Equation form', 'Shape', 'Key feature'],
      rows: [
        [ { label: 'Equation form', html: '<em>y</em> = <em>ax</em>² + <em>bx</em> + <em>c</em>, <em>a</em> &gt; 0' }, { label: 'Shape', html: 'Parabola, opens upward' }, { label: 'Key feature', html: 'Minimum turning point' } ],
        [ { label: 'Equation form', html: '<em>y</em> = <em>ax</em>² + <em>bx</em> + <em>c</em>, <em>a</em> &lt; 0' }, { label: 'Shape', html: 'Parabola, opens downward' }, { label: 'Key feature', html: 'Maximum turning point' } ],
        [ { label: 'Equation form', html: '<em>y</em> = <em>a</em>(<em>b</em>)ˣ, <em>b</em> &gt; 1' }, { label: 'Shape', html: 'Exponential growth' }, { label: 'Key feature', html: 'Rises, gets steeper, never touches zero' } ],
        [ { label: 'Equation form', html: '<em>y</em> = <em>a</em>(<em>b</em>)ˣ, 0 &lt; <em>b</em> &lt; 1' }, { label: 'Shape', html: 'Exponential decay' }, { label: 'Key feature', html: 'Falls, flattens toward zero, never reaches it' } ],
        [ { label: 'Equation form', html: '<em>y</em> = <em>k</em>/<em>x</em>' }, { label: 'Shape', html: 'Reciprocal (hyperbola)' }, { label: 'Key feature', html: 'Two curved branches, never touches either axis' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Direct & inverse variation',
          html: '<ul>\n<li><b>Direct variation</b>: <em>y</em> varies directly with <em>x</em>ⁿ means <em>y</em> = <em>kx</em>ⁿ — if <em>x</em> is scaled by a factor, <em>y</em> is scaled by that factor raised to the power <em>n</em> (e.g. volume ∝ side³: doubling the side multiplies volume by 2³ = 8)</li>\n<li><b>Inverse variation</b>: <em>y</em> varies inversely with <em>x</em> means <em>y</em> = <em>k</em>/<em>x</em>, so <em>xy</em> = <em>k</em> is always constant — if <em>x</em> is scaled by a factor, <em>y</em> is <b>divided</b> by that same factor (e.g. double the workers, half the time)</li>\n<li>To solve either type: find <em>k</em> from the one pair of values you\'re given, then substitute the new value to find the unknown</li>\n</ul>'
        },
        {
          heading: 'Reading exponential growth/decay models',
          html: '<ul>\n<li>In <em>y</em> = <em>a</em>(<em>b</em>)ᵗ, <em>a</em> is always the <b>initial value</b> (read it off directly at <em>t</em> = 0 — no calculation needed)</li>\n<li>The base <em>b</em> tells you the growth/decay <b>rate per period</b>: <em>b</em> = 1.055 means +5.5% per period; <em>b</em> = 0.97 means −3% per period (a decay of 3%)</li>\n<li>Only the value of <em>b</em> determines growth vs. decay — <em>a</em> just sets the starting point and doesn\'t affect the shape</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: '"Varies with" word problems',
      html: '<p>Whenever a question says a quantity "varies directly/inversely with" another, don\'t scale intuitively — write the variation equation, substitute the given pair to solve for <em>k</em>, then use that same <em>k</em> for the new situation. This is especially important for inverse variation, where doubling one quantity <b>halves</b> the other, not doubles it.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Exponential growth/decay here (<em>y</em> = <em>a</em>(<em>b</em>)ˣ) is the same structure as <b>F4 — Investments &amp; Loans</b>\'s compound interest formula — just with different variable names. Simultaneous linear equations build on the straight-line graphs covered in <b>A2 — Linear Relationships</b>.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Determine whether the graph of y = −3x² + 2 opens upward or downward, and state whether it has a maximum or minimum turning point.',
      a: 'The coefficient of <em>x</em>² is negative (<em>a</em> = −3), so the parabola opens <b>downward</b> and has a <b>maximum</b> turning point.'
    },
    {
      q: 'An object\'s height is modelled by h = −5t² + 40t. Determine how long the object is in the air.',
      a: 'The object is at ground level when <em>h</em> = 0: −5<em>t</em>² + 40<em>t</em> = 0 → <em>t</em>(−5<em>t</em> + 40) = 0 → <em>t</em> = 0 or <em>t</em> = 8. It starts at <em>t</em> = 0 and lands at <em>t</em> = 8, so it is in the air for <b>8 seconds</b>.'
    },
    {
      q: 'The number of bacteria in a culture is modelled by y = 500(1.08)ⁿ, where n is the time in minutes. State the initial number of bacteria and determine whether the population is growing or shrinking.',
      a: 'Initial number (at <em>n</em> = 0): <em>y</em> = 500(1.08)⁰ = <b>500</b>. Since the base 1.08 is greater than 1, the population is <b>growing</b>, by 8% each minute.'
    },
    {
      q: 'The time to complete a task varies inversely with the number of workers. It takes 5 workers 12 hours to finish the job. Determine how long it would take 8 workers, working at the same rate.',
      a: 'Inverse variation: workers × time = <em>k</em>. <em>k</em> = 5 × 12 = 60. For 8 workers: time = 60 ÷ 8 = <b>7.5 hours</b>.'
    },
    {
      q: 'A cube\'s volume varies directly with the cube of its side length. Determine the factor by which the volume increases if the side length is tripled.',
      a: 'Volume ∝ side³, so tripling the side length multiplies the volume by 3³ = <b>27</b>.'
    },
    {
      q: 'Explain how to identify, from its equation alone, whether a graph shows exponential growth or exponential decay.',
      a: 'Write the equation in the form <em>y</em> = <em>a</em> × <em>b</em>ˣ. If the base <em>b</em> is greater than 1, the graph shows growth (values increase); if <em>b</em> is between 0 and 1, it shows decay (values decrease, flattening toward zero). The value of <em>a</em> is just the starting value and has no effect on whether it\'s growth or decay — only <em>b</em> determines that.'
    }
  ]
};

data.studyNotes.push(a4);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: A4 — Non-linear Relationships, ' + a4.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
