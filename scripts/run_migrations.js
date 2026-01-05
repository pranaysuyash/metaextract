#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { Pool } from 'pg';
import dotenv from 'dotenv';

// Load environment (allow override via DOTENV_PATH)
dotenv.config({ path: process.env.DOTENV_PATH || './.env' });

const migrationsDir = process.env.MIGRATIONS_DIR || 'server/migrations';
const dbUrl = process.env.DATABASE_URL;

if (!dbUrl) {
  console.error('DATABASE_URL not set. Set it in .env or pass DOTENV_PATH');
  process.exit(1);
}

function loadMigrations(dir) {
  const absDir = path.resolve(dir);
  if (!fs.existsSync(absDir)) {
    throw new Error(`Migrations directory not found: ${absDir}`);
  }
  return fs
    .readdirSync(absDir)
    .filter(f => f.endsWith('.sql'))
    .sort()
    .map(f => ({
      name: f,
      path: path.join(absDir, f),
      sql: fs.readFileSync(path.join(absDir, f), 'utf8'),
    }));
}

async function ensureMigrationsTable(pool) {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS schema_migrations (
      name text PRIMARY KEY,
      applied_at timestamptz NOT NULL DEFAULT now()
    );
  `);
}

async function getApplied(pool) {
  const { rows } = await pool.query('SELECT name FROM schema_migrations');
  const set = new Set();
  rows.forEach(r => set.add(r.name));
  return set;
}

async function applyMigration(pool, migration) {
  console.log(`Applying migration: ${migration.name}`);
  await pool.query('BEGIN');
  try {
    await pool.query(migration.sql);
    await pool.query(
      'INSERT INTO schema_migrations (name) VALUES ($1) ON CONFLICT DO NOTHING',
      [migration.name]
    );
    await pool.query('COMMIT');
    console.log(`✅ Applied: ${migration.name}`);
  } catch (err) {
    await pool.query('ROLLBACK');
    throw err;
  }
}

async function run() {
  const pool = new Pool({ connectionString: dbUrl });
  try {
    const migrations = loadMigrations(migrationsDir);
    await ensureMigrationsTable(pool);
    const applied = await getApplied(pool);

    const pending = migrations.filter(m => !applied.has(m.name));
    if (pending.length === 0) {
      console.log('No pending migrations. Database is up to date.');
      await pool.end();
      return;
    }

    for (const migration of pending) {
      await applyMigration(pool, migration);
    }

    console.log('All pending migrations applied.');
  } catch (err) {
    console.error(
      '❌ Migration run failed:',
      err && err.message ? err.message : err
    );
    process.exitCode = 2;
  } finally {
    try {
      await pool.end();
    } catch (_) {}
  }
}

run();
