# LLM Wiki Query Policy

## Purpose

This document explains how the agent should decide between using the wiki first and using web search first.

The goal is to make the wiki a real long-term memory layer without ignoring the need for current information.

## Default Principle

Use the wiki first for stable domain knowledge.

Use the web first for time-sensitive facts.

When both matter, consult the wiki for context and the web for freshness.

## Wiki-First Cases

Prefer the wiki first when the user asks about:

- concepts already likely covered by prior reading
- recurring research themes
- prior comparisons or syntheses
- relationships among papers, tools, and ideas
- historical conclusions from earlier work
- meeting-derived context
- questions that are not obviously about the latest state of the world

Examples:

- what are the main tradeoffs of mixture-of-experts routing
- how have we been thinking about agent harness evaluation
- what did earlier readings suggest about verifier-guided reasoning

## Web-First Cases

Prefer the web first when the user asks about:

- latest model releases
- current product features
- current pricing
- recent benchmark standings
- current leadership, ownership, or policy facts
- anything phrased as latest, recent, today, this week, currently, or newly released

Examples:

- what is the latest OpenAI Agents SDK feature set
- who currently leads a given lab
- what changed in a product this week

## Hybrid Cases

Some questions need both.

Use a hybrid approach when:

- the wiki has background context but the answer depends on new updates
- the user wants current facts interpreted through prior research
- a new source should be compared against existing internal knowledge

Hybrid sequence:

1. read relevant wiki pages for context
2. search the web for freshness
3. answer using both
4. ingest the new information if it has durable value

## Filing Answers Back

When a query produces something durable, do not leave it only in chat.

Good candidates for write-back:

- nontrivial comparisons
- new syntheses
- answers that connect multiple old and new sources
- findings that are likely to matter again

Possible destinations:

- `questions/`
- `syntheses/`
- updated `concept` or `artifact` pages
- updated `topic-map`

## Meetings And Querying

Meetings count as important context for future queries.

When a user asks about:

- why a research direction changed
- what tradeoffs the team previously discussed
- how a paper was interpreted internally

the wiki should surface relevant meeting-derived source-notes if they exist.

## Guardrails

- Do not bypass the wiki just because web search is faster.
- Do not answer current-fact questions from stale wiki pages without verification.
- Do not ingest every search result automatically.
- Do not turn every answer into a new page unless it has durable value.

## Practical Heuristic

If the question sounds like "what do we already know about this", start with the wiki.

If the question sounds like "what is true right now", start with the web.

If the question sounds like "how does this new thing fit with what we already know", use both.
