const { splitStatements } = require('../scripts/sql-splitter.cjs');

describe('SQL splitter', () => {
  test('preserves dollar-quoted blocks and splits on top-level semicolons', () => {
    const sql = `
CREATE TABLE a(id int);
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1) THEN
    RAISE NOTICE 'hi';
  END IF;
END
$$;
CREATE TABLE b(id int);
`;
    const parts = splitStatements(sql);
    expect(parts.length).toBe(3);
    expect(parts[1]).toMatch(/DO \$\$/);
    expect(parts[1]).toMatch(/END\s*\$\$/);
    expect(parts[1]).toMatch(/RAISE NOTICE 'hi';/);
  });
});
