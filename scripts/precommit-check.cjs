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
