# Interactive Mode

Use this reference when Dayu should manage an ongoing multi-turn terminal session rather than answering one question at a time.

## When to prefer `interactive`

Use `interactive` when:

- the user wants to stay focused on one company across many follow-ups
- the research flow is exploratory and each next question depends on the previous answer
- Dayu's own session continuity is useful
- the user explicitly asks for terminal chat mode

Use `prompt` instead when:

- the task is a single well-formed question
- you want one clean result to return directly
- there are only one or two follow-up turns
- the host is operating in a non-interactive workflow and can simply restate the needed context in another `prompt`

## Command

```bash
dayu-cli interactive --base ~/.dayu/workspace
```

Useful option:

```bash
dayu-cli interactive --base ~/.dayu/workspace --new-session
```

Host-side default:

- when the host intentionally starts `interactive`, prefer the `--new-session` form
- only omit `--new-session` when you are deliberately resuming a known interactive session that the same workflow already created

## Session behavior

Dayu's README says `interactive` defaults to resuming the same local multi-turn session. It stores the current binding under:

```text
<workspace>/.dayu/interactive/state.json
```

That means:

- reopening `interactive` may continue the previous Dayu-side thread
- this is good for sustained research on one company when you explicitly want that exact thread
- if you want a fresh start, use `--new-session`

Important boundary:

- `interactive` is a TTY terminal workflow, not a generic non-interactive API-style command
- do not treat it as the default path for normal single-turn host automation
- if you transition from `prompt` into `interactive`, send a recap in the first interactive message instead of assuming Dayu already knows the prior `prompt` answer

## Practical guidance

Choose `interactive` as the primary mode when the user says things like:

- "我们围绕这家公司连续聊几轮"
- "我接下来会连续追问"
- "先别总结，我想边看边问"

In those cases, Dayu's own multi-turn memory can be more natural than reconstructing context through repeated single-turn prompts.

Recommended first message after switching from `prompt`:

- identify the company / ticker
- state which filing or materials are already in scope
- summarize the key conclusion from the earlier `prompt`
- ask the next question you want Dayu to pursue

## Exit caveat

In practice, `interactive` may not exit gracefully in all environments. EOF-style termination can lead to a non-zero exit even after a valid session.

Treat this carefully:

- do not assume exit code `1` means the interactive analysis itself failed
- judge success by whether the session started, accepted input, and returned meaningful answers
- if exit handling becomes a repeated pain point, switch to repeated `prompt` calls
