# Multi-Agent Review Remediation

Use this reference only after `references/routing.md` selects Multi-Agent Review Remediation.

The default `devflow-rev` behavior remains Review-Only. Multi-agent mode is an explicit orchestration mode for review-driven repair work.

## 1. Shared Truth

- Create or update a durable review report before assigning implementation work.
- Treat the review report as the shared source of truth for findings, repair direction, boundary constraints, acceptance criteria, and resolution status.
- The main agent owns the review report.
- Subagent tasks must cite the relevant finding or acceptance criteria from the review report.
- If review findings are reclassified during discussion, update the report before assigning dependent work.

## 2. Task Planning And Rounds

- Plan tasks before spawning subagents.
- Group work into rounds based on dependencies and expected file ownership.
- Prefer assigning tasks with disjoint write scopes in the same round.
- Resolve dependency-blocking tasks before tasks that depend on them.
- Assign each subagent exactly one task per round.
- Do not give one subagent a bundle of unrelated tasks.
- If tasks are numerous or span many rounds, use Plan mode when available.
- After each round is reviewed, tested, and committed, report the result to the user and wait before starting the next round.

## 3. Subagent Work Boundaries

- Subagents are implementation workers and should normally use `$devflow-dev`.
- Every subagent prompt must include ownership, expected files, do-not-touch areas, acceptance criteria, and expected tests.
- Tell subagents they are not alone in the codebase.
- Tell subagents not to commit.
- Tell subagents not to revert or overwrite changes made by others.
- Tell subagents to modify only their assigned file range.
- If a subagent finds a conflict, rollback need, or scope problem, it should report the issue to the main agent instead of resolving it by reverting unrelated work.
- Subagents should list changed files, key decisions, validation commands, failures, risks, and blockers when finished.
- Spawn subagents only as needed and close them after their assigned task is integrated or rejected.
- Prefer fresh subagents for later tasks unless reuse is clearly useful.

## 4. Main-Agent Review, Integration, And Commits

- Use subagent summaries as orientation only.
- Validate completion from `git diff`, actual code, tests, and the review report acceptance criteria.
- The main agent owns conflict resolution, integration decisions, final review, and verification.
- The main agent may accept, modify, or reject subagent work.
- If multiple subagents changed overlapping files, the main agent resolves the integration and records the tradeoff.
- Subagents may run targeted tests in their isolated workspace, but the main agent must rerun relevant tests after integration in the main worktree.
- Commit each accepted task separately.
- Do not combine multiple subagent tasks into one commit unless the user explicitly approves.
- Stage only the files for the task being committed.

## 5. Reporting And Control Flow

- At the end of each round, report what was assigned, accepted, changed, tested, and committed.
- Summarize remaining findings and the proposed next round.
- Do not automatically start the next round; wait for the user to say to continue.
- Keep unresolved user or unrelated worktree changes separate from subagent task commits.
- If verification fails, report the failing command and decide whether to fix locally, send a follow-up task, or stop for user input.

## Main-Agent Round Checklist

1. Confirm the current review report and acceptance criteria.
2. Inspect the current dirty worktree.
3. Plan the round by dependency order and file ownership.
4. Assign only non-overlapping or intentionally sequenced tasks.
5. Wait for subagents to finish.
6. Review actual diffs, not just summaries.
7. Run targeted tests for each task after integration.
8. Stage only that task's files.
9. Commit with one focused commit.
10. Run broader verification when appropriate.
11. Report round outcome and wait for user approval before continuing.
