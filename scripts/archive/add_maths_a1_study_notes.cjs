// One-off script: appends the A1 Formulae & Equations studyNotes topic
// to subjects/mathematics-standard-2.json (sixth Maths Study Mode topic).
// Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_a1_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'a1-formulae-equations')) {
  console.log('a1-formulae-equations already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const a1 = {
  id: 'a1-formulae-equations',
  icon: '🧮',
  title: 'A1 — Formulae & Equations',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Substituting into formulas',
          html: '<ul>\n<li>Replace each letter with its given value, then follow the <b>order of operations</b> — multiply/divide before add/subtract, and work out anything above or below a fraction bar as its own group first</li>\n<li>Keep units consistent before substituting (e.g. convert minutes to hours if the formula expects hours)</li>\n</ul>'
        },
        {
          heading: 'Translating words into equations',
          html: '<ul>\n<li>Build the equation in the <b>same order</b> the words describe — e.g. "subtract 8, then multiply by 3" becomes 3(<em>x</em> − 8), not 3<em>x</em> − 8</li>\n<li>"Is 2 more than <em>x</em>" means <b>= <em>x</em> + 2</b>; "is 2 less than <em>x</em>" means <b>= <em>x</em> − 2</b> — the direction matters</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Solving linear equations',
          html: '<ul>\n<li>Isolate the unknown using <b>inverse operations</b>, applying the same operation to both sides every time</li>\n<li>Undo operations in <b>reverse order</b> to how they were applied — undo addition/subtraction before multiplication/division</li>\n</ul>'
        },
        {
          heading: 'Equations with fractions',
          html: '<ul>\n<li><b>Multiply every term</b> by the denominator (or the lowest common denominator, if there\'s more than one) first — this clears the fraction so you\'re left with an ordinary linear equation</li>\n<li>Don\'t forget to multiply terms that <b>aren\'t</b> already over a fraction too — every term on both sides needs the same multiplier</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Changing the subject of a formula — worked example (make x the subject of y = (ax − b)/2)',
      headers: ['Step', 'What to do', 'Result'],
      rows: [
        [ { label: 'Step', html: '1' }, { label: 'What to do', html: 'Multiply both sides by 2 (clear the fraction)' }, { label: 'Result', html: '2<em>y</em> = <em>ax</em> − <em>b</em>' } ],
        [ { label: 'Step', html: '2' }, { label: 'What to do', html: 'Add <em>b</em> to both sides' }, { label: 'Result', html: '2<em>y</em> + <em>b</em> = <em>ax</em>' } ],
        [ { label: 'Step', html: '3' }, { label: 'What to do', html: 'Divide both sides by <em>a</em>' }, { label: 'Result', html: '<em>x</em> = (2<em>y</em> + <em>b</em>) ÷ <em>a</em>' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Applying formulas in context',
          html: '<ul>\n<li>Real-world formulas (BAC estimation, electricity billing, wages) combine everything above: <b>substitute</b> known values, then <b>solve or rearrange</b> for whatever\'s unknown</li>\n<li>Read carefully which letter the question wants — sometimes it\'s a direct substitution, other times you need to rearrange first before substituting</li>\n</ul>'
        },
        {
          heading: 'Checking your answer',
          html: '<ul>\n<li>Substitute your solution <b>back into the original equation</b> — both sides should be equal</li>\n<li>For a rearranged formula, check it still works by substituting a value for every letter and confirming both the original and rearranged versions agree</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: '"Make X the subject" questions',
      html: '<p>Treat the target letter exactly like the unknown in an equation you\'re solving — undo whatever has been done to it, in reverse order, keeping both sides balanced at each step. Clear any fractions first. The multiple-choice versions of these questions are really just testing whether you did the steps in the right order.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>The BAC and electricity-billing formulas here reappear as <b>rates</b> in <b>M7 — Rates &amp; Ratios</b> — this topic teaches the algebra (substituting, rearranging), M7 covers reading and using the rate itself.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Given the formula A = P + Prt, find A when P = 2000, r = 0.05 and t = 3.',
      a: '<em>A</em> = 2000 + 2000(0.05)(3) = 2000 + 300 = <b>$2300</b>.'
    },
    {
      q: 'A student thinks of a number x. Subtracting 4 and multiplying the result by 3 gives an answer 5 more than x. Write an equation for this and solve for x.',
      a: '3(<em>x</em> − 4) = <em>x</em> + 5 → 3<em>x</em> − 12 = <em>x</em> + 5 → 2<em>x</em> = 17 → <em>x</em> = <b>8.5</b>.'
    },
    {
      q: 'Make x the subject of the formula y = (px + q)/4.',
      a: 'Multiply both sides by 4: 4<em>y</em> = <em>px</em> + <em>q</em>. Subtract <em>q</em>: 4<em>y</em> − <em>q</em> = <em>px</em>. Divide by <em>p</em>: <b><em>x</em> = (4<em>y</em> − <em>q</em>) ÷ <em>p</em></b>.'
    },
    {
      q: 'Solve the equation x + (x − 1)/3 = 7.',
      a: 'Multiply every term by 3: 3<em>x</em> + (<em>x</em> − 1) = 21 → 4<em>x</em> − 1 = 21 → 4<em>x</em> = 22 → <em>x</em> = <b>5.5</b>.'
    },
    {
      q: 'The formula for BAC (males) is BAC = (10N − 7.5H) ÷ (6.8M), where N = standard drinks, H = hours drinking, M = mass in kg. Calculate the BAC for a 90 kg male who has had 6 standard drinks over 3 hours.',
      a: 'BAC = (10×6 − 7.5×3) ÷ (6.8×90) = (60 − 22.5) ÷ 612 = 37.5 ÷ 612 ≈ <b>0.061</b>.'
    },
    {
      q: 'Explain the general strategy for making a given letter the subject of a formula.',
      a: 'Treat the target letter as the unknown you\'re solving for, and undo the operations applied to it in reverse order — clear any fractions by multiplying through first, then undo addition/subtraction, then undo multiplication/division, keeping both sides balanced at each step, until the target letter is alone on one side.'
    }
  ]
};

data.studyNotes.push(a1);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: A1 — Formulae & Equations, ' + a1.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
