// One-off script: appends the S4 Bivariate Data Analysis studyNotes
// topic to subjects/mathematics-standard-2.json (fifteenth Maths Study
// Mode topic). Purely additive — appends to the existing studyNotes
// array.
// Run once: node scripts/archive/add_maths_s4_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 's4-bivariate-data-analysis')) {
  console.log('s4-bivariate-data-analysis already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const s4 = {
  id: 's4-bivariate-data-analysis',
  icon: '📈',
  title: 'S4 — Bivariate Data Analysis',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Scatterplots & describing association',
          html: '<ul>\n<li>Each point represents one pair of values (<em>x</em>, <em>y</em>)</li>\n<li>Describe the overall pattern by its <b>form</b> (linear or non-linear), <b>direction</b> (positive — both increase together; negative — one increases as the other decreases), and <b>strength</b> (how closely the points cluster around a line)</li>\n</ul>'
        },
        {
          heading: "Pearson's correlation coefficient (r)",
          html: '<ul>\n<li>Ranges from <b>−1 to +1</b> — the <b>sign</b> shows direction, the <b>magnitude</b> (closeness to 1) shows strength</li>\n<li><em>r</em> = +1 is a perfect positive linear relationship, <em>r</em> = −1 a perfect negative one, <em>r</em> = 0 means no linear relationship at all</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Least-squares regression line',
          html: '<ul>\n<li>The "line of best fit" — a straight line (<em>y</em> = <em>mx</em> + <em>b</em>) that minimises the overall distance between the points and the line</li>\n<li>Gives a formula for <b>predicting</b> <em>y</em> from a given <em>x</em></li>\n</ul>'
        },
        {
          heading: 'Interpreting the equation in context',
          html: '<ul>\n<li>The <b>gradient</b> — how much <em>y</em> changes for each 1-unit increase in <em>x</em>, stated in the actual context\'s units (e.g. "weight increases by 0.5 kg per extra year of age")</li>\n<li>The <b><em>y</em>-intercept</b> — the predicted value of <em>y</em> when <em>x</em> = 0. Check this actually makes sense in context; sometimes <em>x</em> = 0 isn\'t realistic (e.g. an age of 0)</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Reading |r| — strength of the relationship',
      headers: ['|r| (magnitude)', 'Strength'],
      rows: [
        [ { label: '|r|', html: '1' }, { label: 'Strength', html: 'Perfect' } ],
        [ { label: '|r|', html: '0.7 to just under 1' }, { label: 'Strength', html: 'Strong' } ],
        [ { label: '|r|', html: '0.4 to just under 0.7' }, { label: 'Strength', html: 'Moderate' } ],
        [ { label: '|r|', html: 'Below 0.4' }, { label: 'Strength', html: 'Weak' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Extrapolation vs. interpolation',
          html: '<ul>\n<li><b>Interpolation</b> — predicting a <em>y</em> value for an <em>x</em> <b>within</b> the range of the original data — generally reliable</li>\n<li><b>Extrapolation</b> — predicting <b>outside</b> that range — less reliable, since the linear pattern observed might not continue to hold</li>\n</ul>'
        },
        {
          heading: 'Correlation is not causation',
          html: '<ul>\n<li>A strong correlation between two variables doesn\'t prove one <b>causes</b> the other</li>\n<li>There could be a <b>third factor</b> influencing both, or the relationship could simply be coincidental</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Interpret in context, in units',
      html: '<p>When asked to interpret a gradient or intercept from a regression equation, always answer in the actual context\'s units and describe what a one-unit change in <em>x</em> means for <em>y</em> — don\'t just restate the numbers from the equation without explaining what they represent.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Bivariate data analysis builds on the single-variable summary statistics and data-display skills from <b>S1 — Data Analysis</b>, extended to look at the relationship <b>between</b> two numerical variables.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A scatterplot shows a strong upward linear trend between hours of exercise per week and resting heart rate improvement. State the likely sign of the correlation coefficient and describe the strength.',
      a: 'Since the trend is upward, the correlation is <b>positive</b>; since it\'s described as strong, |<em>r</em>| would be close to 1 (roughly above 0.7).'
    },
    {
      q: 'A least-squares regression line is given by y = 12 + 3x, relating x (hours of study) to y (test score). Interpret the value of the gradient (3) in context.',
      a: 'For each extra hour of study, the test score is predicted to increase by <b>3 marks</b>, on average.'
    },
    {
      q: 'Explain why extrapolating a regression line beyond the range of the original data can be unreliable.',
      a: 'The linear pattern observed within the data\'s range might not continue to hold outside that range — there\'s no evidence the relationship stays linear (or even exists at all) beyond where data was actually collected, so predictions made there are far less trustworthy.'
    },
    {
      q: 'Two variables have a correlation coefficient of r = −0.85. Describe the direction and strength of this relationship.',
      a: 'The negative sign means the direction is <b>negative</b> (as one variable increases, the other tends to decrease). The magnitude, 0.85, indicates a <b>strong</b> relationship.'
    },
    {
      q: 'Explain why a strong correlation between ice cream sales and shark attacks does not mean one causes the other.',
      a: 'Both variables are likely influenced by a third factor — warmer weather — which increases both ice cream sales and the number of people swimming in the ocean (and therefore shark encounters). The correlation reflects this shared cause, not a direct causal link between ice cream and shark attacks.'
    },
    {
      q: 'A regression line is C = 20 + 4n, where C is total cost in dollars and n is the number of items produced. Interpret the y-intercept (20) in this context.',
      a: 'The <em>y</em>-intercept represents the predicted cost when <em>n</em> = 0 items are produced — i.e. a fixed cost of <b>$20</b> that applies regardless of how many items are made (e.g. a setup or base cost).'
    }
  ]
};

data.studyNotes.push(s4);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: S4 — Bivariate Data Analysis, ' + s4.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
