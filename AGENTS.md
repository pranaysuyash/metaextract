# AGENTS.md (Repo Root)

This repo’s agent instructions live in:

- `doc/AGENTS.md` (development guide + conventions)
- `doc/AUDIT_REMEDIATION_WORKFLOWS.md` (canonical workflow/prompt text: Audit/Implementation/PR Review/Verification/Hardening/Triage/etc.)
- `doc/UI_REVIEW_WORKFLOWS.md` (canonical UI review/audit/spec prompts)

If instructions conflict, prefer the most specific file for the directory you are working in, then prefer `doc/AUDIT_REMEDIATION_WORKFLOWS.md` when running one of its named workflows.

Operational note (process management):
When restarting the dev environment, stop only the running dev servers (Vite on :5173, Express on :3000). Do not kill the global Node process (avoid `killall node`). Prefer stopping the `npm run dev` task/terminal or, if a port is stuck, kill by port.

## Multi-agent safety (non-negotiable)

- Assume multiple agents may be working simultaneously; do not delete or discard work you did not create.
- Do not remove git worktrees, branches, or files created by other agents unless the user explicitly instructs you to.
- If you discover work in another branch/worktree (especially untracked files):
  - Prefer committing it on that branch, then merging as requested.
  - If you must move it to `main`, copy it into the main worktree and commit it with a clear message.
  - If you are unsure whether it belongs, create a TODO/checklist doc under `docs/` and commit it (do not delete the work).
- Exception: never commit secrets (e.g. `.env`, tokens, credentials) even if asked to “commit everything”.
