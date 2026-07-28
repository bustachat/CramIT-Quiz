// One-off script: appends the M7 Rates & Ratios studyNotes topic to
// subjects/mathematics-standard-2.json (fourth Maths Study Mode topic).
// Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_m7_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'm7-rates-ratios')) {
  console.log('m7-rates-ratios already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const m7 = {
  id: 'm7-rates-ratios',
  icon: '⚖️',
  title: 'M7 — Rates & Ratios',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Ratios — simplifying, dividing & changing',
          html: '<ul>\n<li><b>Simplify</b> a ratio by dividing every term by their highest common factor</li>\n<li>To <b>divide a quantity</b> in a given ratio: total parts = sum of the ratio numbers, then each share = (quantity ÷ total parts) × that number</li>\n<li>Both quantities in a ratio must be in the <b>same units</b> before simplifying — e.g. "20 minutes to one-third of a day" needs converting to the same unit (minutes) first</li>\n<li>If amounts are <b>added or removed</b> (e.g. jelly beans eaten, liquid removed from a mixture), calculate the new individual amounts first, then re-simplify the ratio from those — don\'t adjust the ratio numbers directly</li>\n</ul>'
        },
        {
          heading: 'Scale (model : actual)',
          html: '<ul>\n<li>A scale of <b>1 : <em>n</em></b> means 1 unit on the model/map = <em>n</em> of the same unit in real life</li>\n<li>Model → actual: <b>multiply</b> by <em>n</em>. Actual → model: <b>divide</b> by <em>n</em></li>\n<li>Convert units at the end, not the start — work in one consistent unit throughout the ratio calculation, then convert the answer if the question asks for a different unit</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Speed, distance & time',
          html: '<ul>\n<li><b>Speed = distance ÷ time</b>, so distance = speed × time, and time = distance ÷ speed</li>\n<li>Convert time to match the speed\'s units before dividing — e.g. "3 hours 30 minutes" must become 3.5 hours to use with km/h</li>\n<li>Reading start/end clock times (e.g. 6:42 am to 8:04 am) — find the elapsed time first, converting to hours as a decimal if needed</li>\n</ul>'
        },
        {
          heading: 'Best value (unit pricing)',
          html: '<ul>\n<li><b>Unit price = cost ÷ quantity</b> — the <b>lower</b> unit price is the better deal</li>\n<li>All options must be compared in the <b>same unit</b> (e.g. cost per litre, cost per 100 g) — convert first if the options are given in different sizes</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Converting between speed units',
      headers: ['Conversion', 'Multiply by'],
      rows: [
        [ { label: 'Conversion', html: 'km/h → m/s' }, { label: 'Multiply by', html: '÷ 3.6' } ],
        [ { label: 'Conversion', html: 'm/s → km/h' }, { label: 'Multiply by', html: '× 3.6' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Rates of change (linear)',
          html: '<ul>\n<li>Some quantities change by a <b>fixed amount per unit of time</b> — e.g. blood alcohol concentration (BAC) decreasing by a set amount per hour — the same "flat rate" structure as F1\'s straight-line depreciation</li>\n<li>To find the <b>time to reach a target value</b>: time = (starting value − target value) ÷ rate of change</li>\n</ul>'
        },
        {
          heading: 'Using a rate to estimate a total',
          html: '<ul>\n<li>Count/measure a small, <b>representative sample</b> (e.g. trees in a small section of land), and calculate the rate for that sample (e.g. trees per m²)</li>\n<li><b>Scale up</b>: multiply the rate by the total area/quantity to estimate the full total — this assumes the sample is spread evenly and is genuinely representative</li>\n<li><b>Capture–recapture</b> (tagging and resampling to estimate an animal population) uses this same idea, applied to a ratio of tagged-to-total in each sample — see <b>M1 — Measurement</b> for the full method</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Units, units, units',
      html: '<p>Almost every mistake in this topic comes from mismatched units — minutes vs. hours, cm vs. m, or comparing a 1.5 L price against a 2 L price without converting to a common unit first. Before calculating, check every quantity in the question is in the same unit you need for the formula.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Scale here uses the same ratio idea as F1/F4\'s money problems and M1\'s scale drawings — the difference is just what\'s being scaled (a length or a price, not an area). Capture-recapture population estimation is covered in full under <b>M1 — Measurement</b>.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A drink is made from cordial and water in the ratio 1 : 4. Determine how much cordial is needed to make 3 L of the drink.',
      a: 'Total parts = 1 + 4 = 5. Cordial = (1 ÷ 5) × 3 L = <b>0.6 L</b>.'
    },
    {
      q: 'A car travels 210 km in 3 hours 30 minutes. Calculate its average speed in km/h.',
      a: 'Convert time to hours: 3 h 30 min = 3.5 h. Speed = distance ÷ time = 210 ÷ 3.5 = <b>60 km/h</b>.'
    },
    {
      q: 'Two bottles of juice are for sale: a 1.5 L bottle for $4.50, and a 2 L bottle for $5.60. Determine which is better value.',
      a: 'Unit price: 1.5 L bottle = $4.50 ÷ 1.5 = $3.00/L. 2 L bottle = $5.60 ÷ 2 = $2.80/L. The <b>2 L bottle</b> is better value, since its price per litre is lower.'
    },
    {
      q: 'A model bridge is built at a scale of 1 : 150. Calculate the real length, in metres, of a section that measures 8 cm on the model.',
      a: 'Real length = 8 cm × 150 = 1200 cm = <b>12 m</b>.'
    },
    {
      q: 'A person\'s BAC is 0.090 at midnight and decreases at a constant rate of 0.012 per hour. Calculate how long it takes for their BAC to reach zero.',
      a: 'Time = starting value ÷ rate = 0.090 ÷ 0.012 = <b>7.5 hours</b>.'
    },
    {
      q: 'Explain how a small sample can be used to estimate the number of trees on a large block of land.',
      a: 'Count the trees in a small, representative section of the block, then calculate the rate (trees per unit area, e.g. trees per m²) for that section. Multiply this rate by the total area of the block to estimate the total number of trees — this assumes the trees are spread roughly evenly across the whole block.'
    }
  ]
};

data.studyNotes.push(m7);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: M7 — Rates & Ratios, ' + m7.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
