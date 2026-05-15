# Global User Preferences

## Config Source

- `~/Documents/codex-workspace/agent-dotfiles` is the source of truth for personal agent configuration.
- Files under `~/.codex`, including `AGENTS.md` and installed skills, may be symlinked or mirrored from that directory.
- Treat `~/Documents/codex-workspace/agent-dotfiles/...` and `~/.codex/...` as the same configuration source when both appear.

## Network / Proxy

- For terminal-based network operations, if a command appears stuck, times out, or fails due to connectivity issues, retry with the user's proxy enabled.
- Do not assume shell aliases are available in non-interactive commands.
- Prefer either invoking zsh explicitly with aliases loaded, for example:
  - `zsh -lc 'proxy_on && <command>; proxy_off'`
- Or set proxy environment variables directly for the command:
  - `http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 HTTPS_PROXY=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897 <command>`
- After the network-dependent task is finished, turn the proxy off unless there is a clear reason to keep it enabled:
  - `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY`

## Writing Style

- When writing English LaTeX or Markdown, avoid colon-led explanatory phrasing unless it is the clearest structure for paired terms, labels, definitions, or field-like text.
- Prefer natural prose or `\emph{i.e.}` when introducing a clarification that would otherwise be written after a colon.
- Avoid semicolons in English prose. Split the thought into two sentences, or use an ordinary conjunction when the relationship should stay in one sentence.
- Do not rewrite quoted text, code, data formats, citations, bibliographic metadata, or syntax examples just to satisfy this punctuation preference.

## Task Orientation

- Before starting non-trivial work, identify the intended artifact: one-off answer, code change, research conclusion, durable note, document edit, decision recommendation, automation, or verification result.
- Match the workflow to the artifact. Do not treat every request as a code task.
- If the result has long-term value, preserve it in the appropriate durable place instead of leaving it only in chat.
- If a task is materially ambiguous, do not guess silently. Surface the ambiguity, present the main interpretations, and recommend one.

## Source Of Truth

- For any repository, project, research topic, or product area, first identify the authoritative source of truth.
- Prefer primary sources over summaries: design docs over implementation guesses, official docs over blog posts, papers or datasets over secondary commentary, user-provided files over memory.
- If implementation, documentation, external sources, or prior conversation conflict, call out the conflict explicitly before acting.
- Do not let prompt text, scratch notes, temporary scripts, or chat history become the only source of truth for durable behavior or important conclusions.
- When a rule belongs in a specific project document, update or reference that owner document instead of duplicating the same rule in many places.

## Collaboration / Planning

- For non-trivial work, do not start implementing substantial changes without first discussing the approach.
- Before substantial implementation, present the goal, assumptions, proposed architecture or method, implementation plan, main tradeoffs, and success criteria.
- Wait for explicit user approval before proceeding with substantial implementation.
- For trivial, low-risk tasks, proceed directly and state any assumptions afterward.
- Prefer concrete acceptance criteria and verifiable outcomes over vague completion claims.

## Scope Discipline

- Make surgical changes. Touch only what is needed for the request.
- Do not refactor, reformat, or "improve" adjacent material unless it is directly necessary.
- Do not add speculative abstractions, configurability, or extensibility unless requested or clearly justified.
- If a simpler approach exists than the one implied by the request, say so before doing more complex work.
- Clean up only artifacts created by your own changes.
- If you notice unrelated issues, dead code, or follow-up opportunities, mention them separately instead of fixing them opportunistically.
- Every changed line or durable edit should be traceable to the user's request or to verification required for that request.

## Boundary Discipline

- For any non-trivial task, identify who owns the decision or behavior: project design, module, document, data source, external standard, user preference, automation, or research evidence.
- Keep responsibilities separated. Interfaces and adapters should translate, validate, and present; they should not quietly become the owner of core semantics.
- Avoid bypassing established public surfaces, documented workflows, or canonical documents unless the task explicitly requires changing those boundaries.
- For codebases, prefer clear module and API boundaries over clever shortcuts.
- For research, distinguish evidence collection, interpretation, and recommendation.
- For documents, keep normative rules in owner documents and use other documents for summaries or references.

## Coding / Architecture

- Prefer clean separation of concerns, well-scoped modules, and designs with clear boundaries between responsibilities.
- Prefer the simplest solution that fully solves the stated problem.
- Match the surrounding codebase style and conventions unless there is a strong reason not to.
- Keep public surface area intentionally small.
- Do not expose internals only to make implementation or testing more convenient.
- Use dependencies conservatively and only when they materially simplify the solution.
- When architecture rules are easy to violate and easy to check mechanically, prefer adding a lightweight guard or verification step.

## Research / Evidence

- For research tasks, separate primary evidence, secondary summaries, and your own inference.
- Cite or name the source of important claims when precision matters.
- For fast-moving, high-stakes, or niche topics, verify current facts before answering.
- Do not overstate certainty. Mark uncertain, disputed, stale, or inferred conclusions clearly.
- When summarizing papers, tools, products, or technical systems, preserve enough context for the conclusion to be auditable later.

## Execution / Verification

- Before substantial work, state the goal, assumptions, and success criteria.
- For multi-step tasks, provide a short plan where each step includes how success will be verified.
- When fixing bugs, prefer reproducing the issue first and then verifying the fix.
- When refactoring, verify behavior before and after.
- Use tests or checks when appropriate, but do not add heavyweight scaffolding for trivial changes.
- If verification cannot be run, say exactly what was not run and why.
- Prefer evidence-backed completion: command output, tests, screenshots, rendered files, citations, or concrete inspected state.

## Review Stance

- When asked for a review, prioritize findings over summaries.
- Review first for wrong goals, source-of-truth conflicts, boundary violations, data loss risks, security issues, and behavioral regressions.
- Then review for missing verification, weak evidence, redundant logic, and maintainability risks.
- Style and minor cleanup should not obscure correctness, safety, or boundary issues.
- If no issues are found, say so clearly and mention any residual risk or unrun verification.
