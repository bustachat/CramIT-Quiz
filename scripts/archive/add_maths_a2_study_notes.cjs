// One-off script: appends the A2 Linear Relationships studyNotes topic
// to subjects/mathematics-standard-2.json (seventh Maths Study Mode
// topic). Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_a2_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'a2-linear-relationships')) {
  console.log('a2-linear-relationships already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const a2 = {
  id: 'a2-linear-relationships',
  icon: '📐',
  title: 'A2 — Linear Relationships',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'The linear equation y = mx + c',
          html: '<ul>\n<li><b><em>m</em></b> is the <b>gradient</b> (how steep the line is, and which way it slopes)</li>\n<li><b><em>c</em></b> is the <b><em>y</em>-intercept</b> — the value of <em>y</em> when <em>x</em> = 0</li>\n<li>To find <em>m</em> and <em>c</em> from an equation, rearrange it into <em>y</em> = <em>mx</em> + <em>c</em> form first — e.g. <em>y</em> = 5 − 3<em>x</em> has <em>m</em> = −3, <em>c</em> = 5</li>\n</ul>'
        },
        {
          heading: 'Gradient — what it means',
          html: '<ul>\n<li>Gradient = how much <em>y</em> changes for <b>every 1-unit increase</b> in <em>x</em></li>\n<li><b>Positive</b> gradient → line rises left to right (<em>y</em> increases as <em>x</em> increases)</li>\n<li><b>Negative</b> gradient → line falls left to right (<em>y</em> decreases as <em>x</em> increases)</li>\n<li>Between any two points on the line: gradient = rise ÷ run = change in <em>y</em> ÷ change in <em>x</em></li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Building a linear model from a description',
          html: '<ul>\n<li>A <b>fixed</b> amount (a call-out fee, a base charge) becomes <em>c</em>, the <em>y</em>-intercept</li>\n<li>A <b>rate</b> (cost per minute, per item) becomes <em>m</em>, the gradient</li>\n<li>Combine as <b>total = <em>c</em> + <em>m</em> × (quantity)</b> — but check the units match first (see the exam tip below)</li>\n</ul>'
        },
        {
          heading: 'Reading a graph\'s equation',
          html: '<ul>\n<li>Check where the line crosses the <em>y</em>-axis first — that\'s <em>c</em>, and it immediately rules out any candidate equation with the wrong intercept</li>\n<li>Then check the slope <b>direction</b> (rising or falling) to confirm the sign of <em>m</em>, and the steepness if more than one candidate still matches</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Direct variation vs. a general linear relationship',
      headers: ['Form', 'Graph', 'Key feature'],
      rows: [
        [ { label: 'Form', html: '<em>y</em> = <em>mx</em> (direct variation)' }, { label: 'Graph', html: 'Straight line through the origin' }, { label: 'Key feature', html: '<em>y</em> is directly proportional to <em>x</em> — no constant term' } ],
        [ { label: 'Form', html: '<em>y</em> = <em>mx</em> + <em>c</em>, <em>c</em> ≠ 0' }, { label: 'Graph', html: 'Straight line shifted up/down from the origin' }, { label: 'Key feature', html: 'Doesn\'t pass through (0, 0) unless <em>c</em> happens to be 0' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Profit as a linear model',
          html: '<ul>\n<li><b>Profit = Revenue − Cost</b> — if both Revenue and Cost are linear in the number of items <em>x</em>, Profit is linear too</li>\n<li>The <b>profit gained per extra item</b> sold is the gradient of the profit equation — i.e. Revenue\'s gradient minus Cost\'s gradient</li>\n</ul>'
        },
        {
          heading: 'Matching graphs to equations',
          html: '<ul>\n<li>Eliminate options using the <em>y</em>-intercept first — it\'s usually the fastest check</li>\n<li>Then use the slope direction, and finally steepness (a larger |<em>m</em>| means a steeper line) if more than one option remains</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Match your units before combining rates',
      html: '<p>A very common trap: a rate given "per minute" combined with a variable given in hours. Convert one to match the other <b>before</b> substituting — e.g. "$2 per minute" for <em>t</em> hours of work needs 2 × 60<em>t</em>, not 2<em>t</em>.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Everything in <b>A4 — Non-linear Relationships</b> (parabolas, exponentials) is understood by contrast with the straight-line behaviour covered here — a constant gradient is what makes a relationship linear in the first place. Rearranging <em>y</em> = <em>mx</em> + <em>c</em> for <em>m</em> or <em>c</em> uses the same subject-changing skill from <b>A1 — Formulae &amp; Equations</b>.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'State the gradient and y-intercept of the line y = 5 − 3x.',
      a: 'Rewritten in <em>y</em> = <em>mx</em> + <em>c</em> form: <em>y</em> = −3<em>x</em> + 5. Gradient <em>m</em> = <b>−3</b>, <em>y</em>-intercept <em>c</em> = <b>5</b>.'
    },
    {
      q: 'A plumber charges a $70 call-out fee plus $2.50 per minute. Write an equation for the total charge C, in dollars, for t hours of work.',
      a: 't hours = 60<em>t</em> minutes, so <b><em>C</em> = 70 + 150<em>t</em></b> (since 2.50 × 60 = 150).'
    },
    {
      q: 'A line has a gradient of −4 and passes through (0, 6). Determine the y-value when x = 3.',
      a: '<em>y</em> = 6 + (−4)(3) = 6 − 12 = <b>−6</b>.'
    },
    {
      q: 'Cost C = 4x + 20 and Revenue R = 10x for a business selling x items. Calculate how much profit increases for each additional item sold.',
      a: 'Profit = <em>R</em> − <em>C</em> = 10<em>x</em> − (4<em>x</em> + 20) = 6<em>x</em> − 20. The gradient is 6, so profit increases by <b>$6</b> per additional item.'
    },
    {
      q: 'Explain how to identify whether a straight-line graph represents a direct variation relationship.',
      a: 'A direct variation relationship has the form <em>y</em> = <em>mx</em>, with no constant term, so its graph is a straight line passing through the origin (0, 0). Check whether the line crosses the axes exactly at the origin — if it crosses the <em>y</em>-axis anywhere else, it isn\'t direct variation.'
    },
    {
      q: 'Two candidate equations are y = 2x − 3 and y = −2x − 3. The graph shown falls from left to right. Explain which equation matches.',
      a: 'A graph falling from left to right has a negative gradient. <em>y</em> = 2<em>x</em> − 3 has gradient +2 (rising), while <em>y</em> = −2<em>x</em> − 3 has gradient −2 (falling) — so <b><em>y</em> = −2<em>x</em> − 3</b> matches.'
    }
  ]
};

data.studyNotes.push(a2);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: A2 — Linear Relationships, ' + a2.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
