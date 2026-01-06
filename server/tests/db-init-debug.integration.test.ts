const { exec } = require('child_process');

describe('db-init-debug integration (optional)', () => {
  const shouldRun = !!process.env.RUN_DB_INIT_DEBUG && !!process.env.DATABASE_URL;

  (shouldRun ? test : test.skip)('applies init.sql successfully', done => {
    exec(
      'node scripts/db-init-debug.cjs',
      { env: process.env },
      (err: Error | null, stdout: string, _stderr: string) => {
        if (err) {
          done(err);
          return;
        }
        try {
          expect(stdout).toMatch(/Found \d+ statements to execute/);
          expect(stdout).toMatch(/credit_grants reg:/);
          done();
        } catch (e) {
          done(e);
        }
      }
    );
  });
});
