// One-off script: appends the S1 Data Analysis studyNotes topic to
// subjects/mathematics-standard-2.json (thirteenth Maths Study Mode
// topic). Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_s1_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 's1-data-analysis')) {
  console.log('s1-data-analysis already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const s1 = {
  id: 's1-data-analysis',
  icon: '📊',
  title: 'S1 — Data Analysis',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Sampling methods',
          html: '<ul>\n<li><b>Random sample</b> — every member of the population has an equal chance of being chosen</li>\n<li><b>Stratified sample</b> — population split into groups (strata), sample taken from each group <b>proportional to its size</b>: sample from a stratum = (stratum size ÷ population size) × total sample size</li>\n<li><b>Self-selected/voluntary response</b> (e.g. an open online survey) — people choose whether to participate, which usually introduces <b>bias</b> since motivated or opinionated people are over-represented</li>\n</ul>'
        },
        {
          heading: 'Types of data',
          html: '<ul>\n<li><b>Categorical</b> — names/labels (e.g. eye colour) — can\'t be meaningfully averaged</li>\n<li><b>Numerical — discrete</b>: countable whole numbers (e.g. number of siblings)</li>\n<li><b>Numerical — continuous</b>: measured, can take any value in a range (e.g. height)</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Measures of centre & spread',
          html: '<ul>\n<li><b>Mean</b> = sum of all values ÷ number of values</li>\n<li><b>Median</b> = the middle value of the <b>ordered</b> data (average of the two middle values if there\'s an even number)</li>\n<li><b>Mode</b> = the most frequently occurring value</li>\n<li><b>Range</b> = highest − lowest; <b>IQR</b> = <em>Q</em>₃ − <em>Q</em>₁ (spread of the middle 50%, not affected by outliers the way range is)</li>\n</ul>'
        },
        {
          heading: 'Adding a value to a dataset',
          html: '<ul>\n<li>An <b>extreme</b> new value pulls the <b>mean</b> noticeably, since the mean uses every actual value</li>\n<li>The <b>median</b> shifts only a little (or not at all), since it just depends on <b>position</b> in the ordered list — this is why the median is preferred over the mean for skewed data or data with outliers</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Reading common statistical displays',
      headers: ['Display', 'What it shows', 'Key reading skill'],
      rows: [
        [ { label: 'Display', html: '<b>Stem-and-leaf plot</b>' }, { label: 'What it shows', html: 'Every actual data value, split into stem + leaf' }, { label: 'Key reading skill', html: 'Mode = the most-repeated leaf on a stem' } ],
        [ { label: 'Display', html: '<b>Histogram</b>' }, { label: 'What it shows', html: 'Frequency by class interval (grouped data)' }, { label: 'Key reading skill', html: 'Skew direction comes from the <b>tail</b> — long tail right = positive skew, long tail left = negative skew' } ],
        [ { label: 'Display', html: '<b>Box plot</b> (5-number summary)' }, { label: 'What it shows', html: 'Minimum, <em>Q</em>₁, median, <em>Q</em>₃, maximum' }, { label: 'Key reading skill', html: 'Outliers lie beyond <em>Q</em>₁ − 1.5×IQR or <em>Q</em>₃ + 1.5×IQR' } ],
        [ { label: 'Display', html: '<b>Cumulative frequency graph</b>' }, { label: 'What it shows', html: 'Running total of frequency up to each value' }, { label: 'Key reading skill', html: 'Median ≈ value at 50% cumulative frequency; <em>Q</em>₁ ≈ 25%, <em>Q</em>₃ ≈ 75%' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Outliers — the 1.5×IQR rule',
          html: '<ul>\n<li>A value is an outlier if it falls <b>below <em>Q</em>₁ − 1.5×IQR</b> or <b>above <em>Q</em>₃ + 1.5×IQR</b></li>\n<li>Always <b>calculate both boundaries explicitly</b> before deciding — don\'t just eyeball whether a value "looks far away"</li>\n</ul>'
        },
        {
          heading: 'Skewness — reading the shape',
          html: '<ul>\n<li><b>Positively skewed</b> (right-skewed): long tail to the right, most data bunched at the lower end — <b>mean &gt; median</b> (the tail pulls the mean up)</li>\n<li><b>Negatively skewed</b> (left-skewed): long tail to the left — <b>mean &lt; median</b></li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Finding a required score',
          html: '<ul>\n<li>To find the mark needed on a future test to reach a target overall mean: <b>(current total + needed score) ÷ (total number of tests) = target mean</b>, then solve for the needed score</li>\n<li>Find the "current total" first by multiplying the current mean by the number of tests so far</li>\n</ul>'
        },
        {
          heading: 'Working backward from a target',
          html: '<ul>\n<li>The same equation can be rearranged the other way — e.g. given the required future score and target mean, you can find what the <b>earlier</b> mean must have been</li>\n<li>Whichever value is unknown, set up the same total-marks equation and solve for it</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Calculate outlier boundaries, don\'t eyeball them',
      html: '<p>For 5-number-summary/outlier questions, always work out <em>Q</em>₁ − 1.5×IQR and <em>Q</em>₃ + 1.5×IQR explicitly and compare the data value to those numbers. A value can look "far away" on a small scale without technically being an outlier, or vice versa — the calculation is the only reliable check.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>The summary statistics and displays covered here are the foundation for every later statistics topic in the course — comparing datasets, describing distributions, and reading graphs all build on the skills in this topic.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A school has 1200 students, with 180 in Year 8. A stratified sample of 300 students is to be taken. Calculate how many Year 8 students should be included.',
      a: '(180 ÷ 1200) × 300 = <b>45 students</b>.'
    },
    {
      q: 'Explain why a voluntary online survey is likely to produce biased results.',
      a: 'Only people who choose to respond are included, and those with strong opinions or a particular interest in the topic are more likely to participate than a random cross-section of the population. This means the sample isn\'t representative of everyone, unlike genuine random or stratified sampling.'
    },
    {
      q: 'A dataset has Q1 = 8, median = 14, Q3 = 20. Determine whether a value of 33 is an outlier, showing your calculation.',
      a: 'IQR = <em>Q</em>₃ − <em>Q</em>₁ = 20 − 8 = 12. Upper boundary = <em>Q</em>₃ + 1.5×IQR = 20 + 18 = 38. Since 33 &lt; 38, <b>33 is not an outlier</b>.'
    },
    {
      q: 'A histogram of a dataset has a long tail extending to the right, with most values bunched toward the lower end. Describe the skew of this distribution and state whether the mean or median would be higher.',
      a: 'This is <b>positively skewed</b> (right-skewed). The long tail on the right pulls the mean upward more than the median, so the <b>mean is higher than the median</b>.'
    },
    {
      q: 'After 4 tests, a student has a mean mark of 68. Determine the mark needed on the 5th test to raise the mean to 72.',
      a: 'Total after 4 tests = 4 × 68 = 272. Needed total after 5 tests = 5 × 72 = 360. Required mark = 360 − 272 = <b>88</b>.'
    },
    {
      q: 'Explain why the median is less affected than the mean when an extreme value (an outlier) is added to a dataset.',
      a: 'The mean is calculated using the actual value of every data point, so one very large or small number can pull it substantially. The median only depends on the position of the middle value(s) in the ordered dataset — adding one extreme value shifts that middle position only slightly at most, so the median barely changes.'
    }
  ]
};

data.studyNotes.push(s1);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: S1 — Data Analysis, ' + s1.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
