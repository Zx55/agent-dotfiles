# Reading Depth

Use three reading depths. Do not deep-read every paper.

## Level 1: Skim

Use for broad triage.

Typical sections:

- title
- abstract
- introduction
- conclusion
- related work headings
- key figures / tables if needed

Goal:

- decide whether the paper belongs in the shortlist
- capture the method family and likely relevance

## Level 2: Comparison Read

Use when a paper matters for context or comparison but is not a core paper.

Focus on:

- problem framing
- key method idea
- training or data assumptions
- evaluation setup
- headline results
- notable limitation

Goal:

- support side-by-side comparison without full deep reading

## Level 3: Deep Read

Use for core papers only.

Read enough to explain:

- the exact problem and setting
- the method pipeline or algorithm
- the critical design choices
- the experimental protocol
- the strongest evidence
- the weakest assumptions or limitations

For deep-reading reports:

- every important strength should be paired with evidence
- every important limitation or risk should be paired with evidence
- evidence should be located as specifically as possible, preferring PDF page number, section, figure/table ID, appendix location, or quoted metric name
- if a claim is inferred rather than directly stated, label it as an inference and explain the basis
- do not add low-value detail merely to make the report longer

When a figure, table, or pipeline diagram is central to understanding the paper, include a visual anchor in the report and store the asset under the survey workspace's `assets/` directory.

If needed, inspect appendices for implementation or evaluation details, but only when those details matter to the survey question.

## Promotion Rules

Upgrade a paper from skim or comparison read to deep read when:

- it is central to the user's question
- it anchors a major method family
- later papers build directly on it
- the comparison would be weak without a precise understanding of it

Do not upgrade a paper just because it is famous.
