# Global User Preferences

## Config Source

- `~/Documents/codex-workspace/agent-dotfiles` is the source of truth for personal agent configuration.
- Files under `~/.codex`, including `AGENTS.md` and installed skills, may be symlinked or mirrored from that directory.
- Treat `~/Documents/codex-workspace/agent-dotfiles/...` and `~/.codex/...` as the same configuration source when both appear.

## Network / Proxy

- For terminal-based network operations, if a command appears stuck, times out, or fails due to connectivity issues, try enabling the user's proxy with `proxy_on` and retry.
- `proxy_on` and `proxy_off` are aliases defined in `~/.zshrc`.
- After the network-dependent task is finished, turn the proxy off with `proxy_off` unless there is a clear reason to keep it enabled.

## Coding / Architecture

- Do not start implementing substantial changes without first discussing the approach.
- For non-trivial work, first present the proposed architecture, implementation plan, and main tradeoffs.
- Explain the design rationale before making changes, especially why this approach was chosen over simpler or alternative designs.
- Wait for explicit user approval before proceeding with substantial implementation.
- Prefer clean separation of concerns, well-scoped modules, and designs with clear boundaries between responsibilities.

## Knowledge Capture

- Use the $llm-wiki skill when work should be preserved in the long-lived research wiki instead of staying as a one-off chat result.
- Typical trigger conditions include deep research with durable value, explicit user requests to add something to the wiki, paper discussions that produce reusable concepts or conclusions, meeting summaries with lasting technical value, tool or product explorations that produce reusable notes, and important external findings that should enter the long-term knowledge base.
- Do not trigger $llm-wiki for trivial lookups, ephemeral discussion, or content that clearly does not belong in the wiki.
- When $llm-wiki is triggered, orient to `~/Documents/codex-workspace/llm-wiki/AGENTS.md` and follow the skill's `references/` as needed.
- Prefer incremental wiki updates over broad rewrites.
