// One-off script: appends the M6 Non-right-angled Trigonometry
// studyNotes topic to subjects/mathematics-standard-2.json (tenth Maths
// Study Mode topic). Purely additive — appends to the existing
// studyNotes array.
// Run once: node scripts/archive/add_maths_m6_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'm6-non-right-angled-trig')) {
  console.log('m6-non-right-angled-trig already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const m6 = {
  id: 'm6-non-right-angled-trig',
  icon: '📐',
  title: 'M6 — Non-right-angled Trigonometry',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'The sine rule',
          html: '<ul>\n<li><b><em>a</em>/sin<em>A</em> = <em>b</em>/sin<em>B</em> = <em>c</em>/sin<em>C</em></b> — each side is paired with the angle <b>opposite</b> it</li>\n<li>Use it when you know an angle-side opposite pair, plus one more angle or side</li>\n<li><b>Ambiguous case</b>: solving for an angle can give two valid answers (acute and obtuse), since sin(θ) = sin(180° − θ) — check which fits the rest of the triangle (angle sum = 180°, or a stated condition like "obtuse")</li>\n</ul>'
        },
        {
          heading: 'The cosine rule',
          html: '<ul>\n<li><b><em>c</em>² = <em>a</em>² + <em>b</em>² − 2<em>ab</em> cos<em>C</em></b> — finds an unknown <b>side</b> when you know the other two sides and the <b>included</b> angle</li>\n<li>Rearranged, <b>cos<em>C</em> = (<em>a</em>² + <em>b</em>² − <em>c</em>²) ÷ (2<em>ab</em>)</b> — finds an unknown <b>angle</b> when all three sides are known</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Area of a triangle',
          html: '<ul>\n<li><b>Area = ½<em>ab</em> sin<em>C</em></b> — two sides and the <b>included</b> angle between them (doesn\'t need a right angle or the base/height)</li>\n</ul>'
        },
        {
          heading: 'Choosing the right rule',
          html: '<ul>\n<li>Right angle present → Pythagoras / SOH-CAH-TOA is usually simplest</li>\n<li>2 sides + included angle, need the 3rd side or the area → <b>cosine rule</b> or <b>area formula</b></li>\n<li>3 sides known, need an angle → <b>cosine rule</b> (rearranged)</li>\n<li>An angle-side opposite pair + one more piece → <b>sine rule</b></li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Which rule to use',
      headers: ['What you know', 'What you want', 'Rule'],
      rows: [
        [ { label: 'What you know', html: '2 sides + included angle' }, { label: 'What you want', html: '3rd side' }, { label: 'Rule', html: 'Cosine rule' } ],
        [ { label: 'What you know', html: 'All 3 sides' }, { label: 'What you want', html: 'An angle' }, { label: 'Rule', html: 'Cosine rule (rearranged)' } ],
        [ { label: 'What you know', html: 'An angle-side opposite pair + 1 more' }, { label: 'What you want', html: 'A missing side or angle' }, { label: 'Rule', html: 'Sine rule' } ],
        [ { label: 'What you know', html: '2 sides + included angle' }, { label: 'What you want', html: 'Area' }, { label: 'Rule', html: 'Area = ½<em>ab</em> sin<em>C</em>' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Bearings',
          html: '<ul>\n<li><b>True bearing</b>: measured <b>clockwise from north</b>, always written as 3 digits (000°–360°)</li>\n<li>A <b>compass bearing</b> like S48°W converts to a true bearing by measuring from the stated north/south direction toward east or west</li>\n</ul>'
        },
        {
          heading: 'Compound bearing problems',
          html: '<ul>\n<li>The angle between two bearings measured from the <b>same point</b> is the difference between them (adjust if the angle needed crosses 000°/360°)</li>\n<li><b>Sketch first</b>: draw a north line at every point mentioned, mark the given bearings and distances, then identify the triangle before choosing sine rule, cosine rule, or the area formula</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Sketch before you calculate',
      html: '<p>For any bearings or non-right-angled triangle problem, draw a labelled diagram first — mark north at each relevant point, write in every known side and angle, and identify which triangle you\'re actually solving. Most errors in this topic come from misreading the diagram\'s angles, not from applying the wrong formula.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>This topic builds directly on the basic right-triangle trigonometry (SOH-CAH-TOA, Pythagoras) introduced in <b>M1 — Measurement</b>, extending it to triangles that don\'t have a right angle.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'In triangle ABC, AB = 10 cm, angle A = 40°, angle B = 65°. Use the sine rule to find the length of BC, correct to 1 decimal place.',
      a: 'Angle C = 180° − 40° − 65° = 75°. <em>BC</em>/sin<em>A</em> = <em>AB</em>/sin<em>C</em> → <em>BC</em> = 10 × sin40° ÷ sin75° ≈ <b>6.7 cm</b>.'
    },
    {
      q: 'In triangle PQR, PQ = 8 cm, QR = 6 cm, angle PQR = 110°. Use the cosine rule to find PR, correct to 1 decimal place.',
      a: '<em>PR</em>² = 8² + 6² − 2(8)(6)cos110° = 64 + 36 − 96×(−0.342) ≈ 132.8. <em>PR</em> ≈ <b>11.5 cm</b>.'
    },
    {
      q: 'A triangle has sides a = 7, b = 9, c = 12. Use the cosine rule to find the size of the angle opposite side c, correct to the nearest degree.',
      a: 'cos<em>C</em> = (7² + 9² − 12²) ÷ (2×7×9) = (49 + 81 − 144) ÷ 126 = −14 ÷ 126 ≈ −0.111. <em>C</em> = cos⁻¹(−0.111) ≈ <b>96°</b>.'
    },
    {
      q: 'Calculate the area of a triangle with two sides of 9 cm and 14 cm, and an included angle of 52°, correct to 1 decimal place.',
      a: 'Area = ½(9)(14)sin52° = 63 × 0.788 ≈ <b>49.6 cm²</b>.'
    },
    {
      q: 'A ship sails from port on a bearing of 048°T for 20 km, then changes course to a bearing of 138°T for 15 km. Explain how to find the angle between the two legs of the journey at the turning point.',
      a: 'The angle between two bearings measured from the same point is the difference between them: 138° − 48° = 90°, so the two legs meet at a right angle at the turning point. This angle, together with the two known distances, allows the cosine rule to find the direct distance back to port.'
    },
    {
      q: 'Explain why the sine rule can sometimes give two possible answers for an unknown angle (the ambiguous case), and how to decide which is correct.',
      a: 'Because sin(θ) = sin(180° − θ), an angle and its supplement have the same sine value — so solving the sine rule for an angle can produce both an acute and an obtuse solution. The correct one is chosen by checking which is consistent with the rest of the triangle: the three angles must sum to 180°, and the question may explicitly state that a particular angle is obtuse.'
    }
  ]
};

data.studyNotes.push(m6);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: M6 — Non-right-angled Trigonometry, ' + m6.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
