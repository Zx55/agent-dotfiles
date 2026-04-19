# Global User Preferences

## Config Source

- `~/Documents/codex-workspace/agent-dotfiles` is the source of truth for personal agent configuration.
- Files under `~/.codex`, including `AGENTS.md` and installed skills, may be symlinked or mirrored from that directory.
- Treat `~/Documents/codex-workspace/agent-dotfiles/...` and `~/.codex/...` as the same configuration source when both appear.

## Network / Proxy

- For terminal-based network operations, if a command appears stuck, times out, or fails due to connectivity issues, try enabling the user's proxy with `proxy_on` and retry.
- `proxy_on` and `proxy_off` are aliases defined in `~/.zshrc`.
- After the network-dependent task is finished, turn the proxy off with `proxy_off` unless there is a clear reason to keep it enabled.

## Collaboration / Planning

- For non-trivial work, do not start implementing substantial changes without first discussing the approach.
- Before substantial implementation, present the proposed architecture, implementation plan, main tradeoffs, and design rationale.
- Wait for explicit user approval before proceeding with substantial implementation.
- For trivial, low-risk tasks, proceed directly and state any assumptions afterward.
- If a request is materially ambiguous, do not guess silently. Surface the ambiguity, present the main interpretations, and recommend one.

## Coding / Architecture

- Prefer clean separation of concerns, well-scoped modules, and designs with clear boundaries between responsibilities.
- Prefer the simplest solution that fully solves the stated problem.
- Do not add speculative abstractions, configurability, or extensibility unless they are requested or clearly justified by the existing code.
- If a simpler approach exists than the one implied by the request, say so before coding.
- Match the surrounding codebase style and conventions unless there is a strong reason not to.

## Change Scope

- Make surgical changes. Touch only what is needed for the request.
- Do not refactor, reformat, or "improve" adjacent code unless it is directly necessary for the requested change.
- Clean up only the artifacts created by your own changes.
- If you notice unrelated issues, dead code, or follow-up opportunities, mention them separately instead of fixing them opportunistically.
- Every changed line should be traceable to the user's request or to verification required for that request.

## Execution / Verification

- Before substantial work, state the goal, assumptions, and success criteria.
- For multi-step tasks, provide a short plan where each step includes how success will be verified.
- Prefer verifiable outcomes over vague completion criteria.
- When fixing bugs, prefer reproducing the issue first and then verifying the fix.
- When refactoring, verify behavior before and after.
- Use tests when appropriate, but do not add heavyweight scaffolding for trivial changes.

## Knowledge Capture

- Use the $llm-wiki skill when work should be preserved in the long-lived research wiki instead of staying as a one-off chat result.
- Typical trigger conditions include deep research with durable value, explicit user requests to add something to the wiki, paper discussions that produce reusable concepts or conclusions, meeting summaries with lasting technical value, tool or product explorations that produce reusable notes, and important external findings that should enter the long-term knowledge base.
- Do not trigger $llm-wiki for trivial lookups, ephemeral discussion, or content that clearly does not belong in the wiki.
- When $llm-wiki is triggered, orient to `~/Documents/codex-workspace/llm-wiki/AGENTS.md` and follow the skill's `references/` as needed.
- Prefer incremental wiki updates over broad rewrites.
