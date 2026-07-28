// One-off script: appends the M1 Measurement studyNotes topic to
// subjects/mathematics-standard-2.json (third Maths Study Mode topic,
// after F1 Money Matters and F4 Investments & Loans). Purely additive —
// appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_m1_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'm1-measurement')) {
  console.log('m1-measurement already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const m1 = {
  id: 'm1-measurement',
  icon: '📏',
  title: 'M1 — Measurement',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Accuracy & percentage error',
          html: '<ul>\n<li>No measurement is exact — it\'s accurate to <b>half the smallest unit</b> used, e.g. a length given "to the nearest cm" carries an error of ±0.5 cm</li>\n<li><b>Percentage error</b> = (limit of accuracy ÷ measured value) × 100% — smaller relative to a bigger measured value means a smaller percentage error, even if the absolute error is the same</li>\n</ul>'
        },
        {
          heading: 'Significant figures & standard form',
          html: '<ul>\n<li>Leading zeros are never significant; trailing zeros after a decimal point are</li>\n<li><b>Standard form</b>: <em>a</em> × 10ⁿ, where 1 ≤ <em>a</em> &lt; 10 — a very small number has a large <b>negative</b> exponent</li>\n<li>To order numbers in standard form, compare the exponents first — only compare the <em>a</em> values if the exponents are equal</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Upper & lower bounds',
          html: '<ul>\n<li>When two rounded measurements are combined (e.g. multiplied for area), the bounds <b>don\'t</b> combine directly</li>\n<li>To find the <b>minimum</b> result, use the minimum value of every measurement; for the <b>maximum</b>, use every maximum value</li>\n<li>E.g. a rectangle measured 8 cm × 5 cm to the nearest cm: min area = 7.5 × 4.5, max area = 8.5 × 5.5</li>\n</ul>'
        },
        {
          heading: 'Perimeter of common & composite shapes',
          html: '<ul>\n<li><b>Rectangle</b> 2(<em>l</em>+<em>w</em>) · <b>Square</b> 4<em>s</em> · <b>Triangle</b> <em>a</em>+<em>b</em>+<em>c</em> · <b>Circle</b> circumference = π<em>d</em> = 2π<em>r</em></li>\n<li>For a composite shape\'s perimeter, only count the <b>actual outer boundary</b> — don\'t include any internal join lines between the shapes making it up</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Area formulas — quick reference',
      headers: ['Shape', 'Formula'],
      rows: [
        [ { label: 'Shape', html: '<b>Rectangle</b>' }, { label: 'Formula', html: '<em>A</em> = <em>lw</em>' } ],
        [ { label: 'Shape', html: '<b>Triangle</b>' }, { label: 'Formula', html: '<em>A</em> = ½<em>bh</em>' } ],
        [ { label: 'Shape', html: '<b>Parallelogram</b>' }, { label: 'Formula', html: '<em>A</em> = <em>bh</em>' } ],
        [ { label: 'Shape', html: '<b>Trapezium</b>' }, { label: 'Formula', html: '<em>A</em> = ½(<em>a</em>+<em>b</em>)<em>h</em> — <em>a</em>, <em>b</em> are the two parallel sides' } ],
        [ { label: 'Shape', html: '<b>Circle</b>' }, { label: 'Formula', html: '<em>A</em> = π<em>r</em>²' } ],
        [ { label: 'Shape', html: '<b>Sector</b>' }, { label: 'Formula', html: '<em>A</em> = (θ/360) × π<em>r</em>² — θ is the sector angle in degrees' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Volume of solids — building blocks',
          html: '<ul>\n<li><b>Prism</b> (any cross-section): <em>V</em> = <em>A</em>×<em>h</em> — cross-sectional area × the length/height perpendicular to it</li>\n<li><b>Cylinder</b>: <em>V</em> = π<em>r</em>²<em>h</em></li>\n<li><b>Cone</b>: <em>V</em> = <sup>1</sup>&frasl;<sub>3</sub>π<em>r</em>²<em>h</em></li>\n<li><b>Pyramid</b>: <em>V</em> = <sup>1</sup>&frasl;<sub>3</sub> × base area × <em>h</em></li>\n<li><b>Sphere</b>: <em>V</em> = <sup>4</sup>&frasl;<sub>3</sub>π<em>r</em>³</li>\n</ul>'
        },
        {
          heading: 'Composite solids — combining volumes',
          html: '<ul>\n<li>Split the solid into simple shapes from the list above, then <b>add</b> volumes for stacked/joined pieces (e.g. a cone on a cylinder, a hemisphere on a cylinder) or <b>subtract</b> for a hollow/cut-out piece</li>\n<li>Watch for a <b>hemisphere</b> — it\'s exactly half a sphere\'s volume, ½ × <sup>4</sup>&frasl;<sub>3</sub>π<em>r</em>³</li>\n<li>Make sure every piece uses the <b>same radius</b> where they join (e.g. a cylinder and the cone/hemisphere sitting on top of it)</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Scale drawings',
          html: '<ul>\n<li>A scale like <b>1 : 3000</b> means 1 unit on the drawing = 3000 of the same unit in real life — multiply a drawn <b>length</b> by the scale factor to get the real length</li>\n<li><b>Area scales by the square</b> of the linear scale factor — real area = drawn area × (scale factor)². This is the most common thing to forget: don\'t just multiply area by the scale factor once</li>\n</ul>'
        },
        {
          heading: 'The trapezoidal rule',
          html: '<ul>\n<li>Estimates the area of an irregular region from a series of <b>equally spaced</b> parallel measurements <em>y</em>₀, <em>y</em>₁, <em>y</em>₂, …</li>\n<li>For 2 strips (3 measurements): <b>Area ≈ (<em>h</em>/2)(<em>y</em>₀ + 2<em>y</em>₁ + <em>y</em>₂)</b> — <em>h</em> is the common width between measurements; every "interior" reading is doubled, only the first and last are counted once</li>\n<li>Used for things like a block of land or a cross-section that isn\'t a standard shape</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Capture–recapture (Lincoln index)',
          html: '<ul>\n<li>Estimates a population too large to count directly (e.g. fish in a lake)</li>\n<li>Capture and tag a sample of size <em>n</em>₁, release them, then later capture a second sample of size <em>n</em>₂ and count how many are tagged (<em>m</em>)</li>\n<li>Estimated population <b><em>N</em> ≈ (<em>n</em>₁ × <em>n</em>₂) ÷ <em>m</em></b> — assumes tagged individuals mix back in evenly and the population doesn\'t change between samples</li>\n</ul>'
        },
        {
          heading: 'Circle segments & basic trigonometry',
          html: '<ul>\n<li>For a chord across a circle (e.g. the water surface in a pipe), use <b>Pythagoras</b> with the radius, half the chord length, and the distance from the centre to the chord: <em>r</em>² = (½ chord)² + distance² — rearrange for whichever length is unknown</li>\n<li>In a right-angled triangle with a known hypotenuse and angle: <b>opposite = hypotenuse × sin(angle)</b>, <b>adjacent = hypotenuse × cos(angle)</b></li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Composite shapes and solids',
      html: '<p>Before calculating anything, sketch the shape or solid and label which simple pieces it\'s built from — then decide whether you\'re <b>adding</b> them (stacked or joined) or <b>subtracting</b> (a hole or cut-out). Most errors on these questions come from mixing up which operation applies, not from the formulas themselves.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Rounding, accuracy and percentage error covered here apply throughout the course — whenever a written question gives you a measured or scaled value, check what level of precision (decimal places or significant figures) the question expects in your final answer.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A length is measured as 24.0 cm, correct to one decimal place. Calculate the percentage error in this measurement.',
      a: 'Limit of accuracy = ±0.05 cm (half of the smallest unit, 0.1 cm). Percentage error = (0.05 ÷ 24.0) × 100% ≈ <b>0.21%</b>.'
    },
    {
      q: 'A rectangle\'s sides are measured as 9 cm and 6 cm, both to the nearest centimetre. Find the upper and lower bounds for its area.',
      a: 'Each measurement has a bound of ±0.5 cm. Minimum area = 8.5 × 5.5 = 46.75 cm². Maximum area = 9.5 × 6.5 = 61.75 cm².'
    },
    {
      q: 'A composite solid is a cone (radius 4 cm, height 9 cm) sitting on top of a cylinder with the same radius and height 12 cm. Calculate its total volume, correct to one decimal place.',
      a: 'Cylinder: <em>V</em> = π<em>r</em>²<em>h</em> = π(4)²(12) ≈ 603.2 cm³. Cone: <em>V</em> = ⅓π<em>r</em>²<em>h</em> = ⅓π(4)²(9) ≈ 150.8 cm³. Total = 603.2 + 150.8 ≈ <b>754.0 cm³</b>.'
    },
    {
      q: 'A map has a scale of 1 : 2000. A park is drawn on the map with an area of 3 cm². Calculate the real area of the park in m².',
      a: 'Linear scale factor is 2000, so area scales by 2000² = 4 000 000. Real area = 3 × 4 000 000 = 12 000 000 cm² = <b>1200 m²</b> (dividing by 10 000 to convert cm² to m²).'
    },
    {
      q: 'A researcher tags 60 turtles and releases them back into a bay. Two weeks later, she catches 45 turtles and finds 9 are tagged. Estimate the total turtle population in the bay.',
      a: '<em>N</em> ≈ (<em>n</em>₁ × <em>n</em>₂) ÷ <em>m</em> = (60 × 45) ÷ 9 = <b>300 turtles</b>.'
    },
    {
      q: 'Explain why the trapezoidal rule only gives an estimate of area, not an exact value.',
      a: 'The trapezoidal rule approximates the region between each pair of measurements as a straight-sided trapezium. If the actual boundary curves between those measurement points, the straight edge doesn\'t match the true shape exactly, so the calculated area differs slightly from the real area — the estimate improves as more, closer-together measurements are used.'
    }
  ]
};

data.studyNotes.push(m1);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: M1 — Measurement, ' + m1.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
