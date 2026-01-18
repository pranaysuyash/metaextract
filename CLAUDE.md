# Claude (and other LLM agents): Repo Instructions

This repo’s canonical agent instructions live in:

- `AGENTS.md` (repo root summary + non-negotiables)
- `doc/AGENTS.md` (development guide + conventions)
- `doc/AUDIT_REMEDIATION_WORKFLOWS.md` (canonical workflow prompts: Audit/Implementation/PR Review/Verification/Hardening/Triage)
- `doc/UI_REVIEW_WORKFLOWS.md` (canonical UI review/audit/spec prompts)

If instructions conflict, prefer the most specific file for the directory you are working in, then prefer `doc/AUDIT_REMEDIATION_WORKFLOWS.md` when running one of its named workflows.

## Non-negotiables

- **Multi-agent safety:** do not delete/remove other agents’ work (code, files, branches/worktrees) as a “cleanup” step unless explicitly instructed by the user. Prefer integrating, documenting, or deprecating behind a flag.
- **No secrets:** never commit `.env`, tokens, credentials.
- **Process management:** when restarting dev, stop only the dev servers (Vite `:5173`, Express `:3000`). Avoid `killall node`; kill by port if needed.

## Pre-commit guardrails (required)

This repo uses a Husky pre-commit hook (`scripts/precommit-check.cjs`) to prevent regressions and accidental deletions/renames.

- **No deletions/renames by default:** staged deletes/renames are blocked unless you intentionally override with `ALLOW_DELETIONS=1` (one-off).
- **Large per-file diffs require semantic review:** if any file’s staged diff (added+removed) exceeds `LARGE_FILE_CHANGE_PCT`% of its `HEAD` line count, you must:
  - stage a review note under `docs/change_reviews/` (template: `node scripts/create-change-review-note.cjs`), and
  - acknowledge review with `ACK_LARGE_FILE_CHANGES=1` (one-off).
- **Semantic review means:** compare `git diff --staged -- <file>` against `git show HEAD:<file>` and document why changes are correct/better; tests alone are not sufficient evidence.

