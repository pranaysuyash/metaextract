import fs from 'fs';
import path from 'path';

const FORBIDDEN_WORDS = [
  'trial',
  'professional',
  'enterprise',
  'super',
  'tier',
];
const FORBIDDEN_REGEX = new RegExp(
  '(["\\\'`])([^"\\\'`]*\\b(?:' +
    FORBIDDEN_WORDS.join('|') +
    ')\\b[^"\\\'`]*)\\1',
  'gi'
);

const collectFiles = (root: string): string[] => {
  const entries = fs.readdirSync(root, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === '__tests__') {
        continue;
      }
      files.push(...collectFiles(fullPath));
    } else if (entry.isFile() && /\.(ts|tsx)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
};

describe('Images MVP copy regression', () => {
  it('does not include tier words in user-facing strings', () => {
    const mvpPagesRoot = path.resolve(__dirname, '..');
    const mvpComponentsRoot = path.resolve(
      __dirname,
      '..',
      '..',
      '..',
      'components',
      'images-mvp'
    );
    const roots = [mvpPagesRoot, mvpComponentsRoot].filter(fs.existsSync);
    const violations: string[] = [];

    roots.forEach(root => {
      collectFiles(root).forEach(filePath => {
        let contents = fs.readFileSync(filePath, 'utf8');
        contents = contents.replace(/\{\/\*[\s\S]*?\*\/\}/g, '');

        let match: RegExpExecArray | null = null;

        for (
          match = FORBIDDEN_REGEX.exec(contents);
          match !== null;
          match = FORBIDDEN_REGEX.exec(contents)
        ) {
          const preview = match[2].slice(0, 120).replace(/\s+/g, ' ').trim();
          console.log('Found:', filePath, preview);
          violations.push(
            `${path.relative(process.cwd(), filePath)}: "${preview}"`
          );
        }
      });
    });

    console.log('Total violations:', violations.length);

    expect(violations).toEqual([]);
  });
});
