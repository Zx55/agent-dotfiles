# Project Mode

Project mode is for persistent design guidance, not one-off page generation.

Only use project mode when the user clearly wants the selected `DESIGN.md` to influence future UI work in the same project.

## Enter Project Mode When The User Says Things Like

- "use this style for future pages"
- "make this project's frontend follow this reference"
- "wire DESIGN.md into the project workflow"
- "have future agents use this design direction"

## Do Not Enter Project Mode When

- the task is a one-off page
- the user only asked for a mockup or a single redesign
- the project already has a conflicting guidance document and the user did not ask to change it

## Project Mode Steps

1. confirm or fetch the local `DESIGN.md`
2. inspect the local `AGENTS.md` if present
3. add a short UI design reference section
4. keep the wording narrow and implementation-friendly
5. avoid turning `AGENTS.md` into a long design essay

## Suggested AGENTS.md Snippet

Use this as a starting point and adapt to local wording:

```md
## UI Design Reference

This project may include a local `DESIGN.md` file as a visual reference for frontend work.

When implementing UI:
- Use `DESIGN.md` as inspiration for layout rhythm, typography, spacing, color relationships, and component feel.
- Treat it as guidance rather than a strict template.
- Do not copy third-party brand assets, logos, product imagery, or marketing copy.
- Preserve the project's existing stack, component boundaries, and reusable patterns where possible.
- If existing project conventions conflict with `DESIGN.md`, prefer the project's established implementation patterns unless the user asks for a broader redesign.
```

Optional final line when the user wants stronger persistence:

```md
If no visual direction is specified for a new marketing page, consult `DESIGN.md` before introducing a new style direction.
```

## Editing Guidance

When updating `AGENTS.md`:

- preserve the user's existing instructions
- avoid rewriting unrelated sections
- insert the note near other frontend or implementation guidance when possible
- keep the change easy for future agents to notice

## Conflict Rule

If `AGENTS.md` and `DESIGN.md` pull in different directions:

- follow `AGENTS.md` for process and architecture
- use `DESIGN.md` for visual guidance
- ask the user before making a broad redesign that would override local conventions
