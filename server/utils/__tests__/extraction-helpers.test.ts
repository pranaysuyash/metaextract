import fs from 'fs';
import path from 'path';
import { findPythonExecutable } from '../extraction-helpers';

describe('findPythonExecutable', () => {
  afterEach(() => {
    delete process.env.PYTHON_EXECUTABLE;
    // Clean up any temporary venv we created
    const tmpVenv = path.join(process.cwd(), 'server', '..', '..', '.venv');
    try {
      if (fs.existsSync(tmpVenv))
        fs.rmSync(tmpVenv, { recursive: true, force: true });
    } catch (e) {
      // ignore
    }
  });

  it('respects PYTHON_EXECUTABLE env override', () => {
    process.env.PYTHON_EXECUTABLE = '/custom/python';
    expect(findPythonExecutable()).toBe('/custom/python');
  });

  it('returns venv candidate if exists', () => {
    // Create a fake venv python binary so the function picks it up
    const candidate = path.join(
      process.cwd(),
      'server',
      '..',
      '..',
      '.venv',
      'bin',
      'python3'
    );
    fs.mkdirSync(path.dirname(candidate), { recursive: true });
    fs.writeFileSync(candidate, '');

    const result = findPythonExecutable();
    expect(result).toContain('.venv');
  });

  it('falls back to python3 when no candidate exists', () => {
    // Ensure .venv does not exist
    const tmpVenv = path.join(process.cwd(), 'server', '..', '..', '.venv');
    if (fs.existsSync(tmpVenv))
      fs.rmSync(tmpVenv, { recursive: true, force: true });

    const result = findPythonExecutable();
    expect(result).toBe('python3');
  });
});
