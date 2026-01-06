const { splitStatements } = require('../scripts/sql-splitter.cjs');

describe('SQL splitter edge cases', () => {
  test('preserves unterminated dollar-quoted blocks as a single part', () => {
    const sql = `
CREATE TABLE a(id int);
DO $abc$
BEGIN
  RAISE NOTICE 'unterminated block';
-- (no closing tag)
`;
    const parts = splitStatements(sql);
    // Expect two parts: CREATE TABLE ... and the unterminated dollar block
    expect(parts.length).toBe(2);
    expect(parts[1]).toContain('$abc$');
    expect(parts[1]).toContain("RAISE NOTICE 'unterminated block'");
  });

  test('handles multiple dollar tags and quoted strings', () => {
    const sql = `
DO $fn$
BEGIN
  PERFORM 'a;string';
END
$fn$;
DO $x$
SELECT 1;
$x$;
`;
    const parts = splitStatements(sql);
    expect(parts.length).toBe(2);
    expect(parts[0]).toMatch(/DO \$fn\$/);
    expect(parts[1]).toMatch(/DO \$x\$/);
  });
});
