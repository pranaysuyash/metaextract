#!/usr/bin/env node
const { execSync } = require('child_process');

function stagedNameStatus() {
  try {
    const out = execSync('git diff --staged --name-status', {
      encoding: 'utf8',
    });
    return (out || '')
      .trim()
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean);
  } catch (e) {
    return [];
  }
}

function stagedNumstat() {
  try {
    const out = execSync('git diff --staged --numstat', { encoding: 'utf8' });
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
  } catch (e) {
    return [];
  }
}

function getHeadLineCount(filePath) {
  try {
    const out = execSync(`git show HEAD:${filePath}`, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      maxBuffer: 50 * 1024 * 1024,
    });
    if (!out) return 0;
    // Split is safe for LF-normalized git blobs.
    const lines = out.split('\n');
    return lines[lines.length - 1] === '' ? lines.length - 1 : lines.length;
  } catch (e) {
    return null;
  }
}

function enforceLargeFileChangeReview() {
  const allow = String(process.env.ACK_LARGE_FILE_CHANGES || '') === '1';
  const thresholdPct = Number(process.env.LARGE_FILE_CHANGE_PCT || 35);
  if (!Number.isFinite(thresholdPct) || thresholdPct <= 0) return;

  const changes = stagedNumstat();
  if (!changes.length) return;

  const flagged = [];
  for (const { file, added, removed } of changes) {
    // Binary / unknown line diffs: cannot compute percent reliably.
    if (added === null || removed === null) continue;

    const delta = added + removed;
    if (delta <= 0) continue;

    const headLines = getHeadLineCount(file);
    // New files or untracked-in-HEAD: treat as requiring review if large enough.
    const base = headLines === null ? null : Math.max(headLines, 1);
    const pct = base ? (delta / base) * 100 : null;

    // Heuristic: if we can't compute base, only flag very large diffs.
    const shouldFlag =
      pct !== null ? pct >= thresholdPct : delta >= 500;
    if (shouldFlag) {
      flagged.push({ file, delta, headLines, pct });
    }
  }

  if (!flagged.length) return;

  const lines = [
    `Pre-commit guard: large per-file changes detected (>=${thresholdPct}% of previous file).`,
    'This guard is generic: it cannot prove “better”, but it forces an explicit review step.',
    '',
    ...flagged
      .sort((a, b) => (b.pct || 0) - (a.pct || 0))
      .map(f => {
        const base = f.headLines == null ? 'unknown' : String(f.headLines);
        const pct = f.pct == null ? 'n/a' : `${f.pct.toFixed(1)}%`;
        return `- ${f.file} (delta=${f.delta}, base=${base}, pct=${pct})`;
      }),
    '',
    'Review commands:',
    '  - git diff --staged -- <file>',
    '  - git show HEAD:<file> | less',
    '',
    'To acknowledge you reviewed these diffs, rerun with ACK_LARGE_FILE_CHANGES=1 (one-off).',
  ].join('\n');

  if (!allow) {
    console.error(lines + '\n');
    process.exit(1);
  } else {
    console.warn(lines + '\n');
  }
}

function enforceNoDeletions() {
  const allowDeletions = String(process.env.ALLOW_DELETIONS || '') === '1';
  const statuses = stagedNameStatus();
  if (!statuses.length) return;

  const added = [];
  const modified = [];
  const deleted = [];
  const renamed = [];

  for (const line of statuses) {
    const [status, ...rest] = line.split(/\s+/);
    if (!status) continue;
    if (status === 'A') added.push(rest.join(' '));
    else if (status === 'M') modified.push(rest.join(' '));
    else if (status === 'D') deleted.push(rest.join(' '));
    else if (status.startsWith('R')) renamed.push(rest.join(' '));
  }

  console.log(
    `Staged files: +${added.length} ~${modified.length} -${deleted.length} R${renamed.length}`
  );
  if (deleted.length || renamed.length) {
    const message =
      [
        'Pre-commit guard: file removals/renames detected.',
        'Multi-agent safety rule: do not delete or remove other agents’ work unless explicitly instructed.',
        '',
        ...(deleted.length ? ['Deleted:', ...deleted.map(p => `  - ${p}`)] : []),
        ...(renamed.length ? ['Renamed:', ...renamed.map(p => `  - ${p}`)] : []),
        '',
        'To override intentionally, rerun with ALLOW_DELETIONS=1 (one-off).',
      ].join('\n') + '\n';

    if (!allowDeletions) {
      console.error(message);
      process.exit(1);
    } else {
      console.warn(message);
    }
  }
}

function stagedDiffLines() {
  try {
    const out = execSync('git diff --staged --numstat', { encoding: 'utf8' });
    if (!out) return 0;
    const lines = out
      .trim()
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean);
    let total = 0;
    for (const l of lines) {
      const parts = l.split('\t');
      const added = parts[0] === '-' ? 0 : Number(parts[0] || 0);
      const removed = parts[1] === '-' ? 0 : Number(parts[1] || 0);
      total += added + removed;
    }
    return total;
  } catch (e) {
    return 0;
  }
}

(function main() {
  enforceNoDeletions();
  enforceLargeFileChangeReview();
  const lines = stagedDiffLines();
  console.log(`Staged change size: ${lines} lines`);

  if (lines > 200) {
    console.log(
      'Large change detected — running full checks (type-check + tests)'
    );
    try {
      execSync('npm run check', { stdio: 'inherit' });
      execSync('npm test -- -i --runInBand', { stdio: 'inherit' });
    } catch (e) {
      console.error('Full checks failed — aborting commit');
      process.exit(1);
    }
  } else {
    console.log('Small change — running quick lint and unit tests');
    try {
      execSync('npm run lint --silent', { stdio: 'inherit' });
      execSync(
        'npx jest client/src/__tests__/images-mvp.hook.test.tsx -i --runInBand',
        { stdio: 'inherit' }
      );
    } catch (e) {
      console.error('Quick checks failed — aborting commit');
      process.exit(1);
    }
  }
  process.exit(0);
})();
