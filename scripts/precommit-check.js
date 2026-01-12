#!/usr/bin/env node
const { execSync } = require('child_process');

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

(async function main() {
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
