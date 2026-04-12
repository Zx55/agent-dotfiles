---
name: creative-ideation
description: Generate project ideas through creative constraints. Use when the user wants to build something, wants inspiration, or needs concrete ideas shaped by time, tools, mood, or medium.
---

# Creative Ideation

Generate project ideas through creative constraints. Constraint plus direction equals creativity.

## How It Works

1. Pick a constraint from the library below, either random or matched to the user's domain and mood
2. Interpret it broadly: a coding prompt can become a hardware project, an art prompt can become a CLI tool
3. Generate 3 concrete project ideas that satisfy the constraint
4. If the user picks one, build it

## The Rule

Every prompt is interpreted as broadly as possible. The prompts provide direction and mild constraint. Without either, there is no creativity.

## Constraint Library

### For Developers

**Solve your own itch:**
Build the tool you wished existed this week. Under 50 lines. Ship it today.

**Automate the annoying thing:**
What is the most tedious part of your workflow? Script it away.

**The CLI tool that should exist:**
Think of a command you have wished you could type. Now build it.

**Nothing new except glue:**
Make something entirely from existing APIs, libraries, and datasets. The original contribution is how you connect them.

**Frankenstein week:**
Take something that does X and make it do Y.

**Subtract:**
How much can you remove from a codebase before it breaks? Strip a tool to its minimum viable function.

**High concept, low effort:**
A deep idea, lazily executed. The concept should be brilliant. The implementation should take an afternoon.

### For Makers and Artists

**Blatantly copy something:**
Pick something you admire and recreate it from scratch. The learning is in the gap between your version and theirs.

**One million of something:**
One million is both a lot and not that much. At scale, ordinary things become interesting.

**Make something that dies:**
A website that loses a feature every day. A chatbot that forgets. A countdown to nothing.

**Do a lot of math:**
Generative geometry, shader golf, mathematical art, computational origami.

### For Anyone

**Text is the universal interface:**
Build something where text is the only interface.

**Start at the punchline:**
Think of something that would be a funny sentence. Work backwards to make it real.

**Hostile UI:**
Make something intentionally painful to use.

**Take two:**
Remember an old project. Do it again from scratch with no looking at the original.

See `references/full-prompt-library.md` for more constraints across communication, scale, philosophy, transformation, and more.

## Matching Constraints to Users

| User says | Pick from |
|-----------|-----------|
| "I want to build something" | Random, any constraint |
| "I'm learning a language" | Blatantly copy something, Automate the annoying thing |
| "I want something weird" | Hostile UI, Frankenstein week, Start at the punchline |
| "I want something useful" | Solve your own itch, The CLI tool that should exist, Automate the annoying thing |
| "I want something beautiful" | Do a lot of math, One million of something |
| "I'm burned out" | High concept, low effort, Make something that dies |
| "Weekend project" | Nothing new except glue, Start at the punchline |
| "I want a challenge" | One million of something, Subtract, Take two |

## Output Format

```text
## Constraint: [Name]
> [The constraint, one sentence]

### Ideas

1. **[One-line pitch]**
   [2-3 sentences: what you'd build and why it's interesting]
   Time: [weekend / week / month] | Stack: [tools]

2. **[One-line pitch]**
   [2-3 sentences]
   Time: ... | Stack: ...

3. **[One-line pitch]**
   [2-3 sentences]
   Time: ... | Stack: ...
```

## Example

```text
## Constraint: The CLI tool that should exist
> Think of a command you've wished you could type. Now build it.

### Ideas

1. **`git whatsup` - show what happened while you were away**
   Compares your last active commit to HEAD and summarizes what changed,
   who committed, and what PRs merged.
   Time: weekend | Stack: Python, GitPython, click

2. **`explain 503` - HTTP status codes for humans**
   Pipe any status code or error message and get a plain-English explanation
   with common causes and fixes.
   Time: weekend | Stack: Rust or Go, static dataset

3. **`deps why <package>` - why is this in my dependency tree**
   Traces a transitive dependency back to the direct dependency that pulled
   it in.
   Time: weekend | Stack: Node.js, lockfile parsing
```

After the user picks one, start building and move into execution.
