# Multi-Agent Development Orchestration

Use this reference only after `references/routing.md` selects Multi-Agent Development Orchestration.

The default `devflow-dev` behavior remains Implementation Worker. Multi-agent mode is an explicit orchestration mode for feature and refactor development.

## 1. Shared Truth

- Create or update a durable feature plan before assigning implementation work.
- Prefer `docs/development/features/YYYY-MM-DD-PN.md` for multi-agent feature/refactor plans unless the project already has a better convention.
- Treat the plan as the shared source of truth for goals, non-goals, constraints, selected approach, step plan, acceptance criteria, and resolution status.
- The main agent owns the plan document.
- Subagent tasks must cite the relevant step or acceptance criteria from the plan.
- If the implementation approach changes, update the plan before assigning dependent work.
- Only write the feature plan after the user has approved the plan direction. New feature-plan documents should normally start with `status: approved`.

## 2. Planning And Rounds

- First propose a high-level development plan and priority order for the user to choose from.
- After the user selects the path, expand it into concrete steps with ownership, files, risks, tests, and acceptance criteria.
- Group work into rounds based on dependencies and expected file ownership.
- Prefer assigning tasks with disjoint write scopes in the same round.
- Resolve dependency-blocking tasks before tasks that depend on them.
- Assign each subagent exactly one task per round.
- Do not give one subagent a bundle of unrelated tasks.
- If tasks are numerous or span many rounds, use Plan mode when available.
- After each round is reviewed and tested, report the result to the user and wait before starting the next round. Commit only when the user or approved plan explicitly requires commits.

## 3. Subagent Work Boundaries

- Subagents must use `$devflow-dev` in Implementation Worker mode.
- Subagents must not enter Multi-Agent Development Orchestration.
- Subagents that write or modify code must be spawned with model `gpt-5.5` and reasoning effort `high`.
- When setting `model` or `reasoning_effort`, use `fork_context=false`; full-history forked subagents inherit the main agent's model and reasoning effort and cannot override them.
- Because `fork_context=false` does not copy the main agent's conversation, every subagent prompt must be self-contained.
- Every subagent prompt must include ownership, expected files, do-not-touch areas, acceptance criteria, expected tests, and verification output requirements.
- Include enough plan context for the subagent to apply the plan-critic lens locally; if the subagent finds unclear scope, missing acceptance criteria, or design-boundary risk, it should report the gap instead of guessing.
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
- Validate completion from `git diff`, actual code, tests, and the plan acceptance criteria.
- The main agent owns conflict resolution, integration decisions, final review, and verification.
- The main agent may accept, modify, or reject subagent work.
- If multiple subagents changed overlapping files, the main agent resolves the integration and records the tradeoff.
- Subagents may run targeted tests in their isolated workspace, but the main agent must rerun relevant tests after integration in the main worktree.
- When commits are in scope, commit each accepted task separately.
- Do not combine multiple subagent tasks into one commit unless the user explicitly approves.
- Stage only the files for the task being committed.

## 5. Reporting And Control Flow

- At the end of each round, report what was assigned, accepted, changed, tested, and committed when commits were in scope.
- Summarize remaining steps and the proposed next round.
- Do not automatically start the next round; wait for the user to say to continue.
- Keep unresolved user or unrelated worktree changes separate from subagent task commits.
- If verification fails, report the failing command and decide whether to fix locally, send a follow-up task, or stop for user input.

## Main-Agent Round Checklist

1. Confirm the current feature or implementation plan and acceptance criteria.
2. Inspect the current dirty worktree.
3. Plan the round by dependency order and file ownership.
4. Assign only non-overlapping or intentionally sequenced tasks.
5. Wait for subagents to finish.
6. Review actual diffs, not just summaries.
7. Run targeted tests for each task after integration.
8. If commits are in scope, stage only that task's files.
9. If commits are in scope, commit with one focused commit.
10. Run broader verification when appropriate.
11. Update the plan document with implementation notes or resolution status.
12. Report round outcome and wait for user approval before continuing.
