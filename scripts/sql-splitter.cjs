function extractDollarBlocks(sqlText) {
  const blocks = [];
  let out = '';
  let i = 0;

  while (i < sqlText.length) {
    if (sqlText[i] === '$') {
      const m = sqlText.slice(i).match(/^\$([A-Za-z0-9_]*)\$/);
      if (m) {
        const tag = m[1];
        const open = m[0];
        const endTag = `$${tag}$`;
        const endIdx = sqlText.indexOf(endTag, i + open.length);
        if (endIdx === -1) {
          const block = sqlText.slice(i);
          blocks.push(block);
          out += `__DOLLAR_BLOCK_${blocks.length - 1}__`;
          break;
        }
        const block = sqlText.slice(i, endIdx + endTag.length);
        blocks.push(block);
        out += `__DOLLAR_BLOCK_${blocks.length - 1}__`;
        i = endIdx + endTag.length;
        continue;
      }
    }
    out += sqlText[i++];
  }

  return { normalized: out, blocks };
}

function splitStatements(sqlText) {
  const { normalized, blocks } = extractDollarBlocks(sqlText);
  const parts = [];
  let cur = '';
  let i = 0;
  let single = false;
  let dbl = false;

  while (i < normalized.length) {
    const ch = normalized[i];
    if (ch === "'" && !dbl) {
      single = !single;
      cur += ch;
      i++;
      continue;
    }
    if (ch === '"' && !single) {
      dbl = !dbl;
      cur += ch;
      i++;
      continue;
    }
    if (!single && !dbl && ch === ';') {
      parts.push(cur + ';');
      cur = '';
      i++;
      continue;
    }
    cur += ch;
    i++;
  }
  if (cur.trim()) parts.push(cur);

  return parts.map(stmt => stmt.replace(/__DOLLAR_BLOCK_(\d+)__/g, (_, n) => blocks[Number(n)] || ''));
}

module.exports = { extractDollarBlocks, splitStatements };
