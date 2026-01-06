# Python Environment and Extractor

This document describes how the Node server discovers and uses the Python executable for the metadata extraction engine.

## Discovery rules

1. Honor `PYTHON_EXECUTABLE` environment variable if set.
2. Check for common project virtual environments in the following order and use the first match:
   - `.venv/bin/python3`
   - `venv/bin/python3`
   - `.venv/bin/python`
   - `venv/bin/python`
3. Fall back to `python3` on PATH if none of the above exist.

The project exports `findPythonExecutable()` so tests and diagnostics can assert which interpreter will be used.

## Development

- To ensure a reproducible Python runtime, create a venv in project root:

  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r server/extractor/requirements.txt

- Alternatively, set `PYTHON_EXECUTABLE=/absolute/path/to/python` in your environment or `.env`.

## Smoke Test

- Use `npm run smoke-server` to verify a local server is running, or auto-start it and wait for `/api/extract/health` to respond.

## Testing

- Unit tests mock file checks and the Python process; see `server/utils/__tests__/extraction-helpers.test.ts` for `findPythonExecutable` assertions.
- Integration tests continue to mock Python child process, but DTOs are validated to ensure safe behavior when DB save or other services fail.
