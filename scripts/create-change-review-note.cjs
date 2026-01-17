#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8' });
}

function trySh(cmd) {
  try {
    return sh(cmd);
  } catch {
    return '';
  }
}

function stagedNumstat() {
  const out = trySh('git diff --staged --numstat');
  if (!out) return [];
  return out
    .trim()
    .split('\n')
    .map(l => l.trim())
    .filter(Boolean)
    .map(line => {
      const parts = line.split('\t');
      const addedRaw = parts[0];
      const removedRaw = parts[1];
      const file = parts.slice(2).join('\t');
      const added = addedRaw === '-' ? null : Number(addedRaw || 0);
      const removed = removedRaw === '-' ? null : Number(removedRaw || 0);
      return { file, added, removed };
    })
    .filter(x => x.file);
}

function getHeadLineCount(filePath) {
  try {
    const out = execSync(`git show HEAD:${filePath}`, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      maxBuffer: 50 * 1024 * 1024,
    });
    if (!out) return 0;
    const lines = out.split('\n');
    return lines[lines.length - 1] === '' ? lines.length - 1 : lines.length;
  } catch {
    return null;
  }
}

function main() {
  const thresholdPct = Number(process.env.LARGE_FILE_CHANGE_PCT || 35);
  const changes = stagedNumstat();
  if (!changes.length) {
    console.log('No staged changes found.');
    process.exit(0);
  }

  const flagged = [];
  for (const { file, added, removed } of changes) {
    if (added === null || removed === null) continue;
    const delta = added + removed;
    if (delta <= 0) continue;
    const headLines = getHeadLineCount(file);
    const base = headLines === null ? null : Math.max(headLines, 1);
    const pct = base ? (delta / base) * 100 : null;
    const shouldFlag = pct !== null ? pct >= thresholdPct : delta >= 500;
    if (shouldFlag) flagged.push({ file, delta, headLines, pct });
  }

  if (!flagged.length) {
    console.log(
      `No large per-file diffs detected (threshold=${thresholdPct}%).`
    );
    process.exit(0);
  }

  const shortSha = trySh('git rev-parse --short HEAD').trim() || 'unknown';
  const now = new Date();
  const stamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(
    2,
    '0'
  )}-${String(now.getDate()).padStart(2, '0')}_${String(
    now.getHours()
  ).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`;

  const dir = path.join(process.cwd(), 'docs', 'change_reviews');
  fs.mkdirSync(dir, { recursive: true });
  const outPath = path.join(dir, `${stamp}_${shortSha}.md`);

  const lines = [];
  lines.push(`# Change Review Note (${stamp})`);
  lines.push('');
  lines.push(`- Base commit: \`${shortSha}\``);
  lines.push(
    `- Threshold: \`${thresholdPct}%\` (env: \`LARGE_FILE_CHANGE_PCT\`)`
  );
  lines.push('');
  lines.push('## Flagged Files');
  for (const f of flagged.sort((a, b) => (b.pct || 0) - (a.pct || 0))) {
    const base = f.headLines == null ? 'unknown' : String(f.headLines);
    const pct = f.pct == null ? 'n/a' : `${f.pct.toFixed(1)}%`;
    lines.push(`- \`${f.file}\` (delta=${f.delta}, base=${base}, pct=${pct})`);
  }
  lines.push('');
  lines.push('## Required Review (fill this in)');
  lines.push('- Old behavior summary (from `git show HEAD:<file>`):');
  lines.push('- New behavior summary (from `git diff --staged -- <file>`):');
  lines.push('- Why this is better (features fixed/added, bugs removed, safety):');
  lines.push('- Compatibility risks / migrations:');
  lines.push('- How you verified (tests, manual checks, fixtures):');
  lines.push('- What you did NOT verify (known gaps):');
  lines.push('');
  lines.push('## Commands');
  lines.push('- `git diff --staged -- <file>`');
  lines.push('- `git show HEAD:<file> | less`');
  lines.push('- `git blame <file>` (if needed)');
  lines.push('');
  lines.push('## Notes');
  lines.push('- Do not rely on tests alone; document semantic correctness.');
  lines.push('');

  fs.writeFileSync(outPath, lines.join('\n'), 'utf8');
  console.log(`Wrote change review note template: ${outPath}`);
  console.log(`Next: git add ${outPath}`);
}

main();

