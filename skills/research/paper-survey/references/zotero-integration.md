# Zotero Integration

Zotero is optional in this skill.

Use Zotero when the user wants one of these:

- check whether papers already exist in the library
- inspect existing notes, annotations, or collections
- capture selected papers into Zotero
- tag or organize shortlisted items

Keep responsibilities clear:

- `paper-survey` owns search strategy, reading strategy, and synthesis
- Zotero MCP owns library operations

Recommended usage:

1. Search the existing library first if the user likely already collected relevant papers.
2. Avoid duplicate imports when DOI, title, or citation key already matches.
3. Capture only selected shortlist or core papers unless the user explicitly wants full-batch import.
4. Keep Zotero note-writing optional unless the user asks for it or a stable workflow later justifies defaults.
