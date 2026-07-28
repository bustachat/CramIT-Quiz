// One-off script: appends the S2 Relative Frequency & Probability
// studyNotes topic to subjects/mathematics-standard-2.json (fourteenth
// Maths Study Mode topic). Purely additive — appends to the existing
// studyNotes array.
// Run once: node scripts/archive/add_maths_s2_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 's2-relative-frequency-probability')) {
  console.log('s2-relative-frequency-probability already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const s2 = {
  id: 's2-relative-frequency-probability',
  icon: '🎲',
  title: 'S2 — Relative Frequency & Probability',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Basic probability',
          html: '<ul>\n<li><b>P(event) = favourable outcomes ÷ total possible outcomes</b> (for equally likely outcomes) — express as a fraction, decimal or percentage</li>\n<li><b>Complementary events</b>: P(not A) = 1 − P(A)</li>\n</ul>'
        },
        {
          heading: 'Two-way tables',
          html: '<ul>\n<li>Organises data by <b>two categories at once</b> (e.g. age group × a yes/no response)</li>\n<li>To find a probability from a two-way table: identify the correct row/column <b>total</b> as your denominator, and the specific <b>cell</b> as your numerator</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Tree diagrams for multi-stage events',
          html: '<ul>\n<li>Each branch represents one possible outcome at a stage, labelled with its own probability</li>\n<li><b>Multiply</b> probabilities along a single path to find that specific sequence\'s probability</li>\n<li><b>Add</b> the probabilities of separate paths that all satisfy the same overall event</li>\n</ul>'
        },
        {
          heading: 'With vs. without replacement',
          html: '<ul>\n<li><b>With replacement</b>: the selected item is returned before the next draw, so probabilities stay the <b>same</b> at every stage</li>\n<li><b>Without replacement</b>: the item isn\'t returned, so the total (and the count of whichever type was drawn) <b>decreases</b> — the next stage\'s probabilities change</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Worked example — drawing 2 lollies without replacement (4 mint, 6 vanilla)',
      headers: ['Step', 'Calculation', 'Result'],
      rows: [
        [ { label: 'Step', html: '1. P(first is mint)' }, { label: 'Calculation', html: '4/10' }, { label: 'Result', html: '0.4' } ],
        [ { label: 'Step', html: '2. P(second is vanilla | first was mint)' }, { label: 'Calculation', html: '6/9 (one mint already gone, 9 left total)' }, { label: 'Result', html: '≈ 0.667' } ],
        [ { label: 'Step', html: '3. P(mint then vanilla)' }, { label: 'Calculation', html: '4/10 × 6/9' }, { label: 'Result', html: '≈ 0.267' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Relative frequency',
          html: '<ul>\n<li><b>Relative frequency = number of times an event occurs ÷ total number of trials</b></li>\n<li>Used as an <b>estimate</b> of the true probability when it isn\'t known theoretically (e.g. a possibly biased die) — the more trials carried out, the more reliable the estimate</li>\n</ul>'
        },
        {
          heading: 'Estimating a biased probability',
          html: '<ul>\n<li>If a die is biased so one outcome has a different probability but the <b>rest are all equal</b> to each other, first estimate the biased outcome\'s probability from its relative frequency</li>\n<li>The <b>remaining probability</b> (1 − that estimate) is then shared <b>equally</b> among the other equally-likely outcomes</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Relabel every stage in a "without replacement" tree',
      html: '<p>For "without replacement" problems, the total (and possibly the count of one type) changes for every subsequent branch — write out the new fraction at each stage rather than reusing the first stage\'s numbers. This is the single most common source of errors in multi-stage probability questions.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>The sampling-bias questions that reappear here (radio call-ins, pop-up surveys) are the same self-selected sampling concept taught in <b>S1 — Data Analysis</b> — see that topic for the full explanation.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A bag contains 5 red and 7 green marbles. One marble is drawn at random. Calculate the probability it is red, expressed as a fraction.',
      a: 'P(red) = <b>5/12</b>.'
    },
    {
      q: 'A box has 3 chocolate and 5 strawberry lollies. Kim selects one and eats it, then Sam selects one from the remaining lollies. Calculate the probability both select a chocolate lolly.',
      a: 'P(first chocolate) = 3/8. P(second chocolate | first chocolate) = 2/7. P(both chocolate) = 3/8 × 2/7 = 6/56 = <b>3/28</b>.'
    },
    {
      q: 'A coin is biased so that P(heads) = 0.6. Calculate the probability of getting at least one head in two throws.',
      a: 'P(no heads) = 0.4 × 0.4 = 0.16. P(at least one head) = 1 − 0.16 = <b>0.84</b>.'
    },
    {
      q: 'A ten-sided die is biased so that P(rolling a 1) = 0.3, and the remaining 9 outcomes are all equally likely. Calculate the probability of rolling a 7.',
      a: 'Remaining probability = 1 − 0.3 = 0.7, shared equally among 9 outcomes: 0.7 ÷ 9 ≈ <b>0.078</b>.'
    },
    {
      q: 'Explain the difference between "with replacement" and "without replacement" in a two-stage probability experiment.',
      a: 'With replacement, the selected item is returned before the next draw, so the probabilities are identical at every stage. Without replacement, the item is not returned, so the total number of items (and the count of whichever type was drawn) decreases for the next stage, changing its probabilities.'
    },
    {
      q: 'A die is rolled 120 times and lands on 6 a total of 15 times. Explain how this result is used to estimate the probability of rolling a 6, and state that estimate.',
      a: 'The relative frequency (15 ÷ 120 = 0.125) is used as an estimate of the true probability, since the true probability isn\'t known for a possibly biased die. Estimate: P(6) ≈ <b>0.125</b>. This estimate becomes more reliable the more trials are carried out.'
    }
  ]
};

data.studyNotes.push(s2);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: S2 — Relative Frequency & Probability, ' + s2.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
