#!/usr/bin/env node
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config({ path: process.env.DOTENV_PATH || './.env' });

const REQUIRED_TABLES = [
  'users',
  'subscriptions',
  'extraction_analytics',
  'image_mvp_events',
  'trial_usages',
  'credit_balances',
];

const REQUIRED_INDEXES = [
  {
    table: 'extraction_analytics',
    idxAlternatives: [
      'idx_requested_at',
      'idx_extraction_analytics_requested_at',
    ],
  },
  {
    table: 'extraction_analytics',
    idxAlternatives: ['idx_tier', 'idx_extraction_analytics_tier'],
  },
  {
    table: 'extraction_analytics',
    idxAlternatives: ['idx_success', 'idx_extraction_analytics_success'],
  },
  {
    table: 'image_mvp_events',
    idxAlternatives: [
      'idx_user_id',
      'idx_image_mvp_events_user',
      'idx_ui_events_user',
    ],
  },
  {
    table: 'image_mvp_events',
    idxAlternatives: [
      'idx_event_type',
      'idx_image_mvp_events_type',
      'idx_ui_events_product_event',
    ],
  },
  {
    table: 'image_mvp_events',
    idxAlternatives: [
      'idx_created_at',
      'idx_image_mvp_events_created',
      'idx_ui_events_product_created',
    ],
  },
  {
    table: 'trial_usages',
    idxAlternatives: [
      'idx_user_id',
      'idx_trial_usages_email',
      'idx_trial_usages_user',
    ],
  },
  {
    table: 'trial_usages',
    idxAlternatives: ['idx_session_id', 'idx_trial_usages_session'],
  },
];

const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) {
  console.error(
    'DATABASE_URL not set. Run `npm run check:db` first or set DATABASE_URL in .env'
  );
  process.exit(1);
}

const pool = new Pool({ connectionString: dbUrl });

(async () => {
  try {
    console.log('Checking required tables...');
    // Check for relations (tables or views)
    const foundTables = [];
    for (const t of REQUIRED_TABLES) {
      const relRes = await pool.query(
        `SELECT c.relname FROM pg_class c
         JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'public' AND c.relname = $1 AND c.relkind IN ('r','v','m')`,
        [t]
      );
      if (relRes.rowCount > 0) {
        foundTables.push(t);
      }
    }
    REQUIRED_TABLES.forEach(t => {
      console.log(`${t}: ${foundTables.includes(t) ? 'FOUND' : 'MISSING'}`);
    });

    console.log('\nChecking required indexes...');
    for (const idx of REQUIRED_INDEXES) {
      let found = false;
      // If the index is intended for image_mvp_events (a view) check ui_events instead
      const checkTable =
        idx.table === 'image_mvp_events' ? 'ui_events' : idx.table;

      for (const candidate of idx.idxAlternatives) {
        const idxRes = await pool.query(
          `SELECT indexname FROM pg_indexes WHERE tablename = $1 AND indexname = $2`,
          [checkTable, candidate]
        );
        if (idxRes.rowCount > 0) {
          found = true;
          console.log(`${idx.table}.${candidate}: FOUND (on ${checkTable})`);
          break;
        }
      }
      if (!found) {
        // Also check any index on the table that references the key columns by name
        const idxRes2 = await pool.query(
          `SELECT indexname FROM pg_indexes WHERE tablename = $1`,
          [checkTable]
        );
        const names = idxRes2.rows.map(r => r.indexname).join(', ');
        console.log(
          `${idx.table}.${idx.idxAlternatives.join('|')}: MISSING (existing on ${checkTable}: ${names || 'none'})`
        );
      }
    }

    await pool.end();
    process.exit(0);
  } catch (err) {
    console.error(
      'Error while checking tables/indexes:',
      err && err.message ? err.message : err
    );
    try {
      await pool.end();
    } catch (_) {}
    process.exit(2);
  }
})();
