/**
 * Convert markdown pipe tables in written question `q` fields to HTML <table> tags.
 * Handles: header row, separator row (|---|), body rows.
 */
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('subjects/mathematics-standard-2.json', 'utf8'));

function pipeTableToHtml(tableText) {
  const lines = tableText.trim().split('\n').map(l => l.trim());
  const rows = [];
  let isHeader = true;

  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    // Skip separator rows like |---|---|
    if (/^\|[-| :]+\|$/.test(line)) { isHeader = false; continue; }
    const cells = line.split('|').slice(1, -1).map(c => c.trim());
    rows.push({ cells, isHeader });
    if (isHeader) isHeader = false; // first real row = header
  }

  if (rows.length === 0) return tableText;

  const style = 'border-collapse:collapse;margin:8px 0;width:100%;';
  const thStyle = 'border:1px solid #ccc;padding:6px 10px;background:#f5f5f5;text-align:center;';
  const tdStyle = 'border:1px solid #ccc;padding:6px 10px;text-align:center;';

  let html = `<table style="${style}">`;
  rows.forEach((row, i) => {
    html += '<tr>';
    row.cells.forEach(cell => {
      if (i === 0) {
        html += `<th style="${thStyle}">${cell}</th>`;
      } else {
        html += `<td style="${tdStyle}">${cell}</td>`;
      }
    });
    html += '</tr>';
  });
  html += '</table>';
  return html;
}

function convertTablesInText(text) {
  // Match one or more consecutive pipe-table lines (including separator rows)
  // A pipe table block: lines starting with |, at least 2 rows (header + separator + body)
  return text.replace(/(\|[^\n]+\n)+(\|[^\n]+)/g, (match) => {
    // Only convert if it contains a separator row
    if (/^\|[-| :]+\|/m.test(match)) {
      return pipeTableToHtml(match);
    }
    return match;
  });
}

let count = 0;
data.writtenQuestions.forEach(q => {
  if (q.q && q.q.includes('|') && /^\|[-| :]+\|/m.test(q.q)) {
    const before = q.q;
    q.q = convertTablesInText(q.q);
    if (q.q !== before) {
      count++;
      console.log(`Converted: ${q.year} Q${q.qNum}`);
    }
  }
});

fs.writeFileSync('subjects/mathematics-standard-2.json', JSON.stringify(data, null, 2));
console.log(`\nDone — ${count} questions updated.`);
