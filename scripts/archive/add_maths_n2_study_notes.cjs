// One-off script: appends the N2 Network Concepts studyNotes topic to
// subjects/mathematics-standard-2.json (eleventh Maths Study Mode
// topic). Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_n2_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'n2-network-concepts')) {
  console.log('n2-network-concepts already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const n2 = {
  id: 'n2-network-concepts',
  icon: '🕸️',
  title: 'N2 — Network Concepts',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Networks — the basics',
          html: '<ul>\n<li>A <b>vertex</b> is a point/node; an <b>edge</b> is a connection between two vertices</li>\n<li>A <b>weighted</b> edge has a number attached — a distance, time, cost or capacity</li>\n<li>Only which vertices connect to which matters — the exact shape a network is drawn in doesn\'t change what it represents</li>\n</ul>'
        },
        {
          heading: 'Degree of a vertex',
          html: '<ul>\n<li>The <b>degree</b> of a vertex is the number of edges connected to it</li>\n<li><b>Sum of all degrees = 2 × number of edges</b> — every edge is counted at both of the vertices it connects, so the total degree is always <b>even</b></li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Complete bipartite networks (round-robins)',
          html: '<ul>\n<li>If every member of one group must connect to every member of a second group exactly once (with no connections <em>within</em> either group), it\'s a <b>complete bipartite</b> network</li>\n<li>Total edges = (size of group 1) × (size of group 2) — e.g. a chess round-robin between a 3-person team and a 4-person team has 3 × 4 = 12 games</li>\n</ul>'
        },
        {
          heading: 'Counting handshakes (a complete network)',
          html: '<ul>\n<li>If everyone in a group of <em>n</em> people connects to <b>every other</b> person exactly once, total connections = <b><em>n</em>(<em>n</em>−1)/2</b></li>\n<li>This is different from the bipartite case — here everyone is in one single group, connecting to everyone else</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Reference formulas',
      headers: ['Situation', 'Formula'],
      rows: [
        [ { label: 'Situation', html: 'Sum of all vertex degrees' }, { label: 'Formula', html: '2 × number of edges' } ],
        [ { label: 'Situation', html: 'Group of size <em>p</em> vs. group of size <em>q</em>, each connects to every member of the other once' }, { label: 'Formula', html: '<em>p</em> × <em>q</em> edges' } ],
        [ { label: 'Situation', html: '<em>n</em> people, everyone connects to everyone else once' }, { label: 'Formula', html: '<em>n</em>(<em>n</em>−1)/2 connections' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Minimum spanning tree (MST)',
          html: '<ul>\n<li>A set of edges connecting <b>every</b> vertex together, with <b>no cycles</b>, using the smallest possible total weight</li>\n<li><b>Build it greedily</b>: repeatedly add the cheapest available edge that connects a new vertex to the tree so far, without creating a loop — continue until every vertex is included</li>\n</ul>'
        },
        {
          heading: 'Shortest path',
          html: '<ul>\n<li>The path between two vertices with the <b>smallest total weight</b> — not necessarily the fewest edges</li>\n<li>For a small network, systematically list every reasonable route between the two vertices and add up each one\'s weights, then compare</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Don\'t just grab the smallest number',
      html: '<p>For a minimum spanning tree, the cheapest edge in the <b>whole</b> network isn\'t always usable next — it must connect a vertex already in the tree to one that isn\'t, without forming a cycle. For shortest-path questions, make sure you\'ve checked every plausible route, not just the most obvious-looking one — a path with more edges can still have a smaller total weight.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>The vertex/edge language and degree rule introduced here carry straight over into <b>N3</b>\'s network problems.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A network has 5 vertices and 7 edges. Calculate the sum of the degrees of all the vertices.',
      a: 'Sum of degrees = 2 × number of edges = 2 × 7 = <b>14</b>.'
    },
    {
      q: 'Team A has 3 members and Team B has 5 members. Each member of Team A must play each member of Team B exactly once. Calculate the total number of games (edges) in the network.',
      a: '3 × 5 = <b>15 games</b>.'
    },
    {
      q: 'Six friends meet up and each person shakes hands with every other person exactly once. Calculate the total number of handshakes.',
      a: '<em>n</em>(<em>n</em>−1)/2 = 6 × 5 ÷ 2 = <b>15 handshakes</b>.'
    },
    {
      q: 'Explain the rule used to build a minimum spanning tree for a network.',
      a: 'Starting from any vertex, repeatedly add the cheapest available edge that connects a vertex already in the tree to a vertex not yet included, making sure it doesn\'t create a cycle. Continue until every vertex is connected — the resulting set of edges is the minimum spanning tree.'
    },
    {
      q: 'A vertex in a network has degree 5. Explain what this tells you about that vertex.',
      a: 'The vertex has exactly 5 edges connected to it — meaning it directly connects to 5 other vertices in the network.'
    },
    {
      q: 'Two vertices, X and Y, are connected by three possible routes with total weights 18, 22 and 15. Determine the shortest path weight between X and Y, and explain your reasoning.',
      a: 'The shortest path is the route with the <b>smallest total weight</b>, which is 15 — "shortest path" refers to the minimum total weight, not the fewest edges, so the route weighing 15 is the shortest even though it might have more edges than the others.'
    }
  ]
};

data.studyNotes.push(n2);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: N2 — Network Concepts, ' + n2.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
