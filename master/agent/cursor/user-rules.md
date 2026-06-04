# Cursor User Rules

## Agent Config Source

- Apply these personal `agent-dotfiles` source-of-truth rules only when running on the user's local Mac.
- In SSH, remote container, or cloud-agent environments, do not assume `~/Documents/agent-dotfiles` or local runtime config mirrors exist.
- Treat `~/Documents/agent-dotfiles` as the source of truth for personal agent configuration.
- Runtime config directories may contain copied, symlinked, or mirrored files from `agent-dotfiles`.
- When duplicate skills, rules, hooks, or config files appear, resolve authority by tracing back to `~/Documents/agent-dotfiles`.
- Do not treat runtime mirrors and source files as independent configuration sources.

## Runtime Environment

- Prefer the current project's Python environment when it exists, for example `<project>/.venv/bin/python`.
- Use `~/.local/share/agent-dotfiles/python/bin/python` only when running on the user's local Mac and no project environment exists.
- Fall back to `python3` only when neither option exists.
- Do not install dependencies into system Python.
- Project-specific dependencies belong in that project's own environment.
- On the local Mac, cross-agent or cross-skill packages belong in `~/Documents/agent-dotfiles/master/bootstrap/packages/agent-python.txt`.
- In SSH, remote container, or cloud-agent environments, do not assume local `agent-dotfiles` paths, shared agent Python, local proxy helpers, or macOS app config paths exist.
- On the local Mac, if a terminal network command hangs, times out, or fails from connectivity, retry with the user's proxy helper or explicit proxy environment variables.
- Clear proxy environment variables after the network task unless there is a clear reason to keep them.

## Change Boundaries

- Make surgical changes that are directly traceable to the user's request.
- Do not refactor, reformat, or clean up unrelated code opportunistically.
- Do not revert user changes unless explicitly requested.
- If a simpler approach exists than the requested or implied approach, point it out before doing more complex work.
- Clean up only artifacts created by your own work.
- Every durable edit should be traceable to the user's request or to verification required for that request.

## Coding Standards

- Match the surrounding codebase style and conventions unless there is a strong reason not to.
- Prefer the simplest solution that fully solves the stated problem.
- Keep modules well scoped and public surfaces intentionally small.
- Prefer TypeScript over untyped JavaScript for durable scripts, tools, and application code.
- For Python, write explicit types for function parameters, return values, and non-obvious variables.
- Use dependencies conservatively and only when they materially simplify the solution.
- Do not expose internals only to make implementation or testing easier.
- When architecture rules are easy to violate and easy to check mechanically, prefer adding a lightweight guard or verification step.

## Writing And Review

- In Markdown prose, do not insert hard line breaks just to fit a preferred line width.
- In English Markdown or LaTeX prose, avoid colon-led explanatory phrasing unless it is the clearest structure.
- Avoid semicolons in English prose. Prefer two sentences or an ordinary conjunction.
- Do not rewrite quoted text, code, data formats, citations, bibliographic metadata, or syntax examples just to satisfy writing preferences.
- When asked for a review, lead with findings ordered by severity.
- In reviews, prioritize wrong goals, source-of-truth conflicts, boundary violations, data loss risks, security issues, and behavioral regressions before style concerns.
- If no issues are found, say so clearly and mention residual risk or unrun verification.
