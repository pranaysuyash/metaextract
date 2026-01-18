# Kiro Specs: Repo Guardrails (Read Me First)

Kiro spec files live under `.kiro/specs/` and must follow the repo-wide agent rules:

- Canonical instructions: `AGENTS.md`, `doc/AGENTS.md`
- Workflow prompts: `doc/AUDIT_REMEDIATION_WORKFLOWS.md`, `doc/UI_REVIEW_WORKFLOWS.md`

## Non-negotiables

- Multi-agent safety: do not delete/remove other agents’ work as a “cleanup” step unless explicitly instructed by the user.
- Never commit secrets (`.env`, tokens, credentials).
- Process management: when restarting dev, stop only the dev servers (Vite `:5173`, Express `:3000`). Avoid `killall node`.

## Pre-commit guardrails (required)

This repo uses a Husky pre-commit hook (`scripts/precommit-check.cjs`):

- Deletions/renames are blocked unless `ALLOW_DELETIONS=1` (one-off) and explicitly intended.
- Large per-file diffs require a staged change review note under `docs/change_reviews/` (template: `node scripts/create-change-review-note.cjs`) and `ACK_LARGE_FILE_CHANGES=1`.
- For large diffs, do a semantic review against `HEAD` (`git diff --staged -- <file>` + `git show HEAD:<file>`); tests alone are not enough.

