import fs from 'fs';
import path from 'path';
import * as ts from 'typescript';

const FORBIDDEN_WORDS = [
  'trial',
  'professional',
  'enterprise',
  'super',
  'tier',
];
const FORBIDDEN_WORD_REGEX = new RegExp(
  `\\b(?:${FORBIDDEN_WORDS.join('|')})\\b`,
  'i'
);

type Violation = {
  filePath: string;
  preview: string;
};

function previewText(text: string, limit = 120): string {
  return text.replace(/\s+/g, ' ').trim().slice(0, limit);
}

function scanSourceForForbiddenStrings(
  filePath: string,
  contents: string
): Violation[] {
  const scriptKind = filePath.endsWith('.tsx')
    ? ts.ScriptKind.TSX
    : ts.ScriptKind.TS;
  const sourceFile = ts.createSourceFile(
    filePath,
    contents,
    ts.ScriptTarget.Latest,
    true,
    scriptKind
  );

  const literals: string[] = [];

  const visit = (node: ts.Node) => {
    if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {
      literals.push(node.text);
    } else if (ts.isTemplateExpression(node)) {
      literals.push(node.head.text);
      for (const span of node.templateSpans) {
        literals.push(span.literal.text);
      }
    } else if (ts.isJsxText(node)) {
      const text = node.getText(sourceFile);
      if (text && text.trim()) {
        literals.push(text);
      }
    }

    ts.forEachChild(node, visit);
  };

  visit(sourceFile);

  return literals
    .filter(text => FORBIDDEN_WORD_REGEX.test(text))
    .map(text => ({
      filePath,
      preview: previewText(text),
    }));
}

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
        const contents = fs.readFileSync(filePath, 'utf8');
        const fileViolations = scanSourceForForbiddenStrings(filePath, contents);

        for (const violation of fileViolations) {
          console.log('Found:', filePath, violation.preview);
          violations.push(
            `${path.relative(process.cwd(), violation.filePath)}: "${violation.preview}"`
          );
        }
      });
    });

    console.log('Total violations:', violations.length);

    expect(violations).toEqual([]);
  });
});
