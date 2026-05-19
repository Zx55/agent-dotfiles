# [Project Name] Architecture

## Purpose

State what this architecture document is responsible for.

Typical responsibilities:

- defining the system shape
- defining top-level component boundaries
- defining cross-cutting architectural rules
- describing what should stay stable as the project grows

## Design Goals

List the goals that should shape the architecture.

Examples:

- local-first
- auditable
- extensible
- small public surface
- stable contracts
- operational simplicity

## Non-Goals

Explicitly list what the current phase is not trying to solve.

This protects the project from premature complexity.

## System Model

Describe the main conceptual layers, object families, or responsibility areas.

This section should answer:

- what major parts the system is composed of
- how those parts relate to one another
- what kind of responsibilities each part owns

## Primary Components

For each major component, document:

- what it owns
- what it does not own
- what inputs and outputs it deals with
- what dependencies it is allowed to take

Good component sections are clear enough that later review can detect boundary drift.

## Core Boundaries

Define the most important architectural boundaries.

Typical examples:

- adapter boundary
- application or use-case boundary
- persistence boundary
- provider or integration boundary
- runtime or orchestration boundary

For each boundary, explain:

- the owner
- the allowed dependency direction
- what should remain outside that boundary

## Truth Or State Model

If the project deals with domain truth, derived state, cache state, or workflow state, define the model here.

Clarify which artifacts are authoritative and which are derived.

## Write Model

Describe how state changes are supposed to happen.

Cover:

- what can be written automatically
- what requires review or approval
- what invariants every write path must preserve

## Phase Notes

Document current-phase architectural limits and temporary simplifications.

This section should help later contributors distinguish intentional simplifications from accidental omissions.
