# Global User Preferences

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
