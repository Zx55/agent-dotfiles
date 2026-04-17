# Review Checklist

## Purpose

Explain what this checklist is for and what kinds of review it should guide.

Typical focus areas:

- boundary integrity
- extensibility
- redundancy control
- testing quality

Clarify that this document is review guidance, not the source of truth for product behavior.

## Review Stance

Define what reviewers should compare first.

Typical rule:

- review against design docs first
- then against implementation

Also list the related documents reviewers should use, such as:

- architecture docs
- workflow docs
- testing guidelines
- surface rules

## How To Use This Checklist

Explain the review order and the intended output style.

Useful prompts:

- what responsibility slice owns this change
- what contract does it expose
- what dependencies is it allowed to take

## Review Workflow

### 1. Boundary

Questions to include:

- Is the owner of the behavior clear?
- Does the change stay in the correct layer?
- Are dependency directions still intentional?
- Has the public surface grown without a real external need?
- Has the change introduced half-wired scaffolding or widened visibility too early?

### 2. Extensibility

Questions to include:

- Can this shape grow without forcing a rewrite of boundaries?
- Is the behavior localized in the natural owner?
- If a second variant appears later, will the design still hold?
- Are request, result, and error types owned by the right module?

### 3. Redundancy

Questions to include:

- Did the change duplicate policy or validation across layers?
- Did it introduce another way to express the same concept?
- Are helpers or mappings beginning to drift?
- Is documentation repeating details that belong in one authoritative place?

### 4. Tests

Questions to include:

- Is coverage placed at the boundary that owns the contract?
- Do tests protect caller-visible behavior instead of accidental internals?
- Are success, boundary, and failure paths covered where they matter?
- Are parallel features covered symmetrically unless there is a reason not to?

### 5. Project Invariants

List the project-level invariants every review should re-check.

These should be copied or adapted from `AGENTS.md` rather than invented ad hoc.

## Output Format

Define the preferred review output categories.

Typical categories:

- `Blocker`
- `Risk`
- `Redundancy`
- `Tests`
- `Recommendation`

For each item, explain:

- what the problem is
- why it matters
- what the smallest repair path is
- whether docs or tests need updates

## Documented Review Workflow

If the project uses durable review documents, explain:

- when to open one
- where to place it
- how it should be named
- what structure it should use

If review docs are not needed in the project, explicitly say so.
