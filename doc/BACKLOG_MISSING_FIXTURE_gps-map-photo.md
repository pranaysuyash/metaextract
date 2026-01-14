# Backlog: Missing test fixture — gps-map-photo.jpg

**Failing path**
- `tests/persona-files/sarah-phone-photos/gps-map-photo.jpg`

**Observed failure**
- Pytest collection crashed with an INTERNALERROR because the test expected the image file above but it was not present. See CI run: https://github.com/pranaysuyash/metaextract/actions/runs/20994114591

**Minimal fix options**

1) Commit the fixture into the repository ✅ (recommended for deterministic tests)
   - Add a small placeholder image to `tests/persona-files/sarah-phone-photos/gps-map-photo.jpg` and commit.
   - Pros: deterministic; minimal test change; simple to review.
   - Cons: adds binary to repo (keep small and licensed/created by project).
   - Example git steps:
     - `git add tests/persona-files/sarah-phone-photos/gps-map-photo.jpg`
     - `git commit -m "tests: add missing gps-map-photo.jpg fixture"

2) Generate fixture at test setup (create on-demand) 🛠️
   - Modify the test or a `pytest` fixture to create a small placeholder image when the file is missing (use Pillow).
   - Pros: no binary in repo; tests remain reproducible on CI/local.
   - Cons: adds code, less obvious than a static fixture; must ensure Pillow is a runtime/test dependency.
   - Minimal snippet to use in a fixture:
     ```py
     from PIL import Image
     import os

     def ensure_gps_fixture(path):
         os.makedirs(os.path.dirname(path), exist_ok=True)
         if not os.path.exists(path):
             Image.new("RGB", (10, 10), (128, 128, 128)).save(path)
     ```

3) Skip the test when the fixture is absent ⚠️ (least preferred)
   - Update the test to skip if the file is missing: `if not os.path.exists(path): pytest.skip("fixture missing: gps-map-photo.jpg")`
   - Pros: quick, non-invasive.
   - Cons: hides missing data and may reduce test coverage; may mask regressions.

**Recommendation**
- Prefer option (1) to restore deterministic, auditable test behavior.
- If adding binaries to the repo is not acceptable, use option (2) (create-on-demand), ensuring the test remains explicit about the generated fixture.

**Notes**
- Do not change CI workflows or dispatch additional runs now (per direction).
- This is a single backlog item; no further patches or CI dispatches will be performed unless you direct me.

---
_Logged by GitHub Copilot — single backlog item created for review._