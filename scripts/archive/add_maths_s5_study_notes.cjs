// One-off script: appends the S5 Normal Distribution studyNotes topic
// to subjects/mathematics-standard-2.json (sixteenth and final Maths
// syllabus category for the initial Study Mode build). Purely
// additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_s5_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 's5-normal-distribution')) {
  console.log('s5-normal-distribution already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const s5 = {
  id: 's5-normal-distribution',
  icon: '🔔',
  title: 'S5 — The Normal Distribution',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'The normal distribution & the empirical rule',
          html: '<ul>\n<li>A symmetric, <b>bell-shaped</b> curve centred on the mean</li>\n<li><b>Empirical (68–95–99.7) rule</b>: about <b>68%</b> of data lies within 1 SD of the mean, <b>95%</b> within 2 SD, <b>99.7%</b> within 3 SD</li>\n</ul>'
        },
        {
          heading: 'Z-scores',
          html: '<ul>\n<li><b><em>z</em> = (<em>x</em> − mean) ÷ SD</b> — measures how many standard deviations a value <em>x</em> is from the mean</li>\n<li><em>z</em> = 0 is exactly at the mean; <b>positive</b> <em>z</em> is above the mean, <b>negative</b> <em>z</em> is below it</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Comparing values from different distributions',
          html: '<ul>\n<li>To compare performance across tests/populations with <b>different means and SDs</b>, convert each value to a <b>z-score</b> first</li>\n<li>The <b>higher z-score</b> is relatively better — even if its actual/raw value is lower than the other</li>\n</ul>'
        },
        {
          heading: 'Finding an actual value from a z-score',
          html: '<ul>\n<li>Rearrange the z-score formula: <b><em>x</em> = mean + <em>z</em> × SD</b></li>\n<li>Substitute the known mean, SD and z-score to find the actual data value</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'The empirical rule at a glance',
      headers: ['Range', '% of data'],
      rows: [
        [ { label: 'Range', html: 'mean ± 1 SD' }, { label: '% of data', html: '≈ 68%' } ],
        [ { label: 'Range', html: 'mean ± 2 SD' }, { label: '% of data', html: '≈ 95%' } ],
        [ { label: 'Range', html: 'mean ± 3 SD' }, { label: '% of data', html: '≈ 99.7%' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Using standard normal (Z) tables',
          html: '<ul>\n<li>Exam tables usually give <b>P(<em>Z</em> &lt; <em>z</em>)</b> or <b>P(0 &lt; <em>Z</em> &lt; <em>z</em>)</b> for positive <em>z</em></li>\n<li>Key symmetry facts: <b>P(<em>Z</em> &lt; 0) = 0.5</b> (half the data is below the mean); <b>P(0 &lt; <em>Z</em> &lt; <em>z</em>) = P(<em>Z</em> &lt; <em>z</em>) − 0.5</b>; <b>P(<em>Z</em> &gt; <em>z</em>) = 1 − P(<em>Z</em> &lt; <em>z</em>)</b></li>\n<li>For negative <em>z</em>, use symmetry: <b>P(<em>Z</em> &lt; −<em>z</em>) = P(<em>Z</em> &gt; <em>z</em>)</b> — the same distance below the mean mirrors above it</li>\n</ul>'
        },
        {
          heading: 'Recognising a normal distribution from a histogram',
          html: '<ul>\n<li>Roughly <b>symmetric</b>, bell-shaped, with a single central peak (<b>unimodal</b>)</li>\n<li>Tapering tails on <b>both</b> sides</li>\n<li>A clearly skewed or multi-peaked histogram is <b>not</b> normal</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Sketch the bell curve first',
      html: '<p>Before using a table or the empirical rule, sketch the bell curve and shade the exact region the question is asking about. This avoids the classic mistake of forgetting to add or subtract 0.5 when converting between a "less than the mean" table value and a one-sided region.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Recognising a normal shape here connects back to <b>S1 — Data Analysis</b>\'s work on histograms and skew — a normal distribution is simply the special case with zero skew.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Test scores are normally distributed with mean 65 and standard deviation 8. Calculate the z-score for a mark of 81.',
      a: '<em>z</em> = (81 − 65) ÷ 8 = 16 ÷ 8 = <b>2</b>.'
    },
    {
      q: 'A distribution has mean 40 and standard deviation 6. Calculate the actual value corresponding to a z-score of −1.5.',
      a: '<em>x</em> = mean + <em>z</em> × SD = 40 + (−1.5)(6) = 40 − 9 = <b>31</b>.'
    },
    {
      q: 'Using the empirical rule, estimate the percentage of data that lies between the mean and 2 standard deviations above the mean.',
      a: '95% lies within 2 SD of the mean (both sides combined), so exactly half of that — <b>47.5%</b> — lies between the mean and 2 SD above it.'
    },
    {
      q: 'A student scored a z-score of 1.6 in English and 2.1 in Maths, relative to their respective class distributions. Explain which subject the student performed better in relative to their class.',
      a: 'The higher z-score (2.1 in Maths) means the student performed further above their class\'s mean, in terms of standard deviations, than in English (1.6) — so relatively, the student did better in <b>Maths</b>, even without knowing the actual raw marks.'
    },
    {
      q: 'A standard normal table gives P(Z < 1.2) = 0.8849. Calculate P(0 < Z < 1.2).',
      a: 'P(0 &lt; <em>Z</em> &lt; 1.2) = P(<em>Z</em> &lt; 1.2) − P(<em>Z</em> &lt; 0) = 0.8849 − 0.5 = <b>0.3849</b>.'
    },
    {
      q: 'Explain two features of a histogram that would suggest the underlying data is normally distributed.',
      a: '(1) The histogram is roughly symmetric about a central value. (2) It has a single peak (unimodal), with the bars tapering off gradually on both sides, rather than being skewed or having multiple separate peaks.'
    }
  ]
};

data.studyNotes.push(s5);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: S5 — The Normal Distribution, ' + s5.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
