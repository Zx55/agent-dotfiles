# Testing Guidelines

## Purpose

Explain what good testing means in this repository.

The goal should emphasize:

- protecting the right contract
- placing tests at the right ownership boundary
- creating clear failure signals
- avoiding weak or redundant tests

## Testing Philosophy

### Ownership-First Placement

Explain that test placement should start from ownership:

- what behavior changed
- which layer owns that behavior
- what contract should stay stable

### Clear Failure Signals

Explain that a test should fail for a clear reason.

Different test locations should imply different meanings:

- public-surface drift
- internal contract drift
- private implementation regression

### Contract-Focused Coverage

Explain that test strength matters more than test count.

Prefer tests that protect stable behavior callers rely on.

## Placement Rules

Define where each kind of test should live.

Typical categories:

- public contract tests
- internal stable contract tests
- file-local implementation tests

For each category, explain:

- what belongs there
- what kind of failure it should signal
- what kinds of setup are acceptable

## Coverage Expectations

Explain the normal coverage shape for non-trivial behavior changes.

Typical expectations:

- a success path
- a boundary path
- a failure or regression path

## Symmetry Rules

If the project has parallel features or mirrored surfaces, explain that coverage should usually stay symmetric.

Give examples relevant to the project if available.

## Error Semantics

If callers depend on distinct error meanings, require tests to assert those distinctions explicitly.

Warn against tests that only prove that an error occurred without checking which contract failed.

## Contract Tests Vs Smoke Tests

Explain the difference between:

- contract tests that lock stable output or semantics
- smoke tests that only provide lightweight confidence

Encourage contributors to choose one on purpose instead of mixing the two casually.

## High-Value Test Patterns

List the test patterns that are especially useful in the repository.

Possible examples:

- stable output structure
- empty and non-empty state coverage
- ordering and limit behavior
- compatibility transitions
- persistence invariants
- config normalization

## Low-Value Test Smells

List the test patterns that create maintenance cost without much signal.

Possible examples:

- duplicate coverage at multiple boundaries for the same contract
- tests that mirror implementation details too closely
- tests that only assert success without checking structure
- tests that require widened visibility instead of moving inward
