#!/usr/bin/env node
import fs from 'fs';
import { Pool } from 'pg';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: process.env.DOTENV_PATH || './.env' });

const migrationPath =
  process.argv[2] || 'server/migrations/006_images_mvp_indexes.sql';
if (!fs.existsSync(migrationPath)) {
  console.error(`Migration file not found: ${migrationPath}`);
  process.exit(1);
}

const sql = fs.readFileSync(migrationPath, 'utf8');
const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) {
  console.error('DATABASE_URL not set. Set it in .env or pass DOTENV_PATH');
  process.exit(1);
}

const pool = new Pool({ connectionString: dbUrl });

(async () => {
  try {
    console.log(`Applying migration: ${migrationPath}`);
    await pool.query('BEGIN');
    await pool.query(sql);
    await pool.query('COMMIT');
    console.log('✅ Migration applied successfully');
    await pool.end();
    process.exit(0);
  } catch (err) {
    console.error(
      '❌ Migration failed:',
      err && err.message ? err.message : err
    );
    try {
      await pool.query('ROLLBACK');
    } catch (_) {}
    try {
      await pool.end();
    } catch (_) {}
    process.exit(2);
  }
})();
