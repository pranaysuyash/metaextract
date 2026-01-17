# Change Reviews (Large Diffs)

This folder stores **required review notes** for commits that make large per-file changes.

## When is a change review note required?

The pre-commit hook flags any staged change where **a single file’s diff** (added+removed lines)
exceeds `LARGE_FILE_CHANGE_PCT` percent of that file’s current `HEAD` line count.

When flagged:

- Do **not** rely on tests alone.
- Compare against the previous committed version and document why the change is correct.

## How to create a review note

Run:

`node scripts/create-change-review-note.cjs`

Then stage the generated note under `docs/change_reviews/` and retry the commit.

## Override (rare)

If you intentionally want to bypass the note requirement:

- `SKIP_CHANGE_REVIEW_NOTE=1` (one-off)

If you want to bypass the large-diff acknowledgement prompt:

- `ACK_LARGE_FILE_CHANGES=1` (one-off)

