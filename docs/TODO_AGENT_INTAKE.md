# TODO: Agent Intake / Cross-Worktree Checklist

Use this checklist when multiple agents/worktrees are active and you need to merge/push work without losing anything.

## 1) Discovery
- [ ] `git status -sb` in the primary worktree
- [ ] `git worktree list`
- [ ] `git branch -vv` (note `: gone` upstreams)
- [ ] For each worktree: `git -C <path> status -sb --porcelain=v1`

## 2) Preserve work (do not delete)
- [ ] If a worktree has untracked/modified files: commit them on that branch (preferred)
- [ ] If the user explicitly wants everything on `main`: copy files into the main worktree and commit with a clear message
- [ ] If unsure whether something belongs: leave it in place and add a note here (append-only) rather than deleting

## 3) Safety
- [ ] Never commit secrets (`.env`, tokens, credentials)
- [ ] Avoid destructive commands (`git clean`, `git reset --hard`, `git worktree remove`) unless explicitly instructed

## 4) Verification
- [ ] Run the smallest relevant checks (or `npm test` / `npm run test:ci` when pushing to `main`)
- [ ] Ensure `git rev-list --left-right --count origin/main...main` is `0 0` after pushing
