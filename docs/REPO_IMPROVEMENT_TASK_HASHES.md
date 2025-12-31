# Task: Fix hashing exports and implement file hashes in modules

## What
- Implement `extract_file_hashes` in `server/extractor/modules/hashes.py` using streaming hashers (md5, sha1, sha256, and crc32).
- Remove or rename `extract_perceptual_hashes` in `server/extractor/modules/hashes.py` to avoid overriding the real implementation.
- Update `server/extractor/modules/__init__.py` exports so:
  - `extract_file_hashes` comes from `hashes.py`.
  - `extract_perceptual_hashes` comes from `perceptual_hashes.py`.

## Why
- The stub in `server/extractor/modules/hashes.py` returns `{}` and overrides the working implementation because `server/extractor/modules/__init__.py` imports it last.
- Any caller that does `from server.extractor.modules import extract_perceptual_hashes` gets the stub, which means no perceptual hashes and missing fields in downstream features.
- The main engine already calculates file hashes in `server/extractor/metadata_engine.py`, but the module layer is inconsistent and confusing.

## Evidence
- `server/extractor/modules/hashes.py` contains TODO stubs for both hash functions.
- `server/extractor/modules/__init__.py` imports `extract_perceptual_hashes` twice, with the stubbed version last.
- `server/extractor/modules/perceptual_hashes.py` has the real imagehash implementation.

## Proposed changes
1. Implement `extract_file_hashes` in `server/extractor/modules/hashes.py` by reusing the streaming hash logic from `server/extractor/metadata_engine.py` (md5, sha1, sha256, crc32).
2. Remove `extract_perceptual_hashes` from `server/extractor/modules/hashes.py`, or rename it to avoid collisions.
3. Update `server/extractor/modules/__init__.py` to export:
   - `extract_file_hashes` from `hashes.py`.
   - `extract_perceptual_hashes` from `perceptual_hashes.py`.
4. Optional: Keep a compatibility alias in `hashes.py` that imports `extract_perceptual_hashes` from `perceptual_hashes.py`, but do not re-export it in `__init__.py` if it collides.

## Acceptance criteria
- `from server.extractor.modules import extract_perceptual_hashes` returns the imagehash implementation and no longer returns `{}`.
- `extract_file_hashes` returns md5, sha1, sha256, and crc32 for a test file.
- No duplicate symbol export for `extract_perceptual_hashes` in `server/extractor/modules/__init__.py`.
- API schema is unchanged; only correctness improves.

## Tests
- Add or run a small unit test in `tests/` that hashes a known file and compares outputs.
- Smoke test: call `extract_perceptual_hashes` on a sample image and ensure output is non-empty (when imagehash dependencies are installed).

## Risks and mitigations
- Missing imagehash dependencies: keep existing ImportError behavior in `server/extractor/modules/perceptual_hashes.py`.
- Backward imports: if any code relies on `hashes.extract_perceptual_hashes`, keep a compatibility alias inside `hashes.py` but avoid overriding the public export.

## Effort
- Estimated: small (1 to 2 hours).
