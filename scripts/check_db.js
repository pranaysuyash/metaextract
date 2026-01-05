#!/usr/bin/env node
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config({ path: process.env.DOTENV_PATH || './.env' });

const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) {
  console.error('DATABASE_URL not set. See docs/LOCAL_DB_SETUP.md');
  process.exit(1);
}

const pool = new Pool({ connectionString: dbUrl });

(async () => {
  try {
    const res = await pool.query('SELECT 1 AS ok');
    console.log('✅ Database reachable:', res.rows[0]);
    await pool.end();
    process.exit(0);
  } catch (err) {
    console.error(
      '❌ Database check failed:',
      err && err.message ? err.message : err
    );
    try {
      await pool.end();
    } catch (_) {}
    process.exit(2);
  }
})();
