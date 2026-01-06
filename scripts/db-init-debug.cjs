#!/usr/bin/env node
const fs = require('fs');
const { Client } = require('pg');

const { splitStatements } = require('./sql-splitter.cjs');

async function main() {
  const dbUrl = process.env.DATABASE_URL || process.argv[2];
  if (!dbUrl) {
    console.error('Usage: DATABASE_URL=postgres://... node scripts/db-init-debug.cjs');
    process.exit(2);
  }

  const client = new Client({ connectionString: dbUrl });
  try {
    await client.connect();
    await client.query('SELECT 1');
    await client.query("SET search_path TO public");

    const sql = fs.readFileSync('./init.sql', 'utf8');
    const statements = splitStatements(sql);
    console.log(`Found ${statements.length} statements to execute`);

    for (let i = 0; i < statements.length; i++) {
      const stmt = statements[i].trim();
      if (!stmt) continue;
      try {
        console.log(`Executing statement #${i + 1}: ${stmt.substring(0, 160).replace(/\n/g,' ')}...`);
        await client.query(stmt);
      } catch (err) {
        console.error(`Statement #${i + 1} failed:`, (err && err.message) || err);
        throw err;
      }
    }

    const verify = await client.query("SELECT to_regclass('public.credit_grants') AS reg");
    console.log('credit_grants reg:', verify.rows[0]?.reg);
    await client.end();
  } catch (err) {
    console.error('Failed to apply init.sql:', (err && err.message) || err);
    try { await client.end(); } catch (e) {}
    process.exit(1);
  }
}

main();
