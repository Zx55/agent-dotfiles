# Zotero Integration

Zotero capture is default for selected core papers in this skill.

Use Zotero to:

- check whether papers already exist in the library
- capture selected core papers into Zotero
- attach PDFs when available
- inspect child notes and attachments after import
- remove imported tags from newly captured papers
- place papers into collections for organization
- optionally inspect existing notes, annotations, or collections when useful

Keep responsibilities clear:

- `paper-survey` owns search strategy, reading strategy, and synthesis
- Zotero MCP owns library operations

## Tool Selection

Zotero MCP exposes many tools. For this skill, use a narrow default tool surface.

Default allowed tools:

- `zotero_search_items` for dedupe by title, DOI, arXiv ID, or stable URL
- `zotero_add_by_url` for arXiv, DOI, and landing-page imports
- `zotero_add_by_doi` when a DOI is available
- `zotero_add_from_file` when the source is a local PDF
- `zotero_get_item_metadata` to verify that an existing item is the same paper
- `zotero_get_item_children` to inspect PDFs, notes, and attachments
- `zotero_update_item` only to remove tags from newly captured items
- `zotero_delete_note` only under the low-value note rule below
- `zotero_get_collections` to choose the target collection
- `zotero_manage_collections` to place captured papers into the target collection

Conditionally allowed tools:

- `zotero_create_collection` only when the user explicitly asks to create a collection, or no existing collection is reasonably suitable and the user approves the proposed name and parent

Do not use these tools by default:

- `zotero_merge_duplicates`
- `zotero_batch_update_tags`
- `zotero_update_note`
- `zotero_create_annotation`
- `zotero_create_area_annotation`
- `zotero_update_search_database`
- `scite_*`
- feed tools such as `zotero_list_feeds` or `zotero_get_feed_items`

Use non-default tools only when the user explicitly asks or the current survey has a concrete need that cannot be handled by the default tools.

## Destructive Operations

Avoid destructive or broad library operations during `paper-survey`.

Allowed deletion:

- `zotero_delete_note` may be used only for notes created by the current import that contain low-value arXiv metadata, such as acceptance notes, homepage links, or venue-only comments.

Allowed item update:

- `zotero_update_item` may be used only to remove tags from items newly captured in the current survey run.
- Do not update title, authors, abstract, DOI, URL, date, publication fields, or existing user-managed metadata during `paper-survey`.
- Do not run broad tag cleanup with `zotero_batch_update_tags` during `paper-survey`.

Allowed collection creation:

- `zotero_create_collection` may be used only after choosing a proposed collection name and parent, and only when the user approves or has explicitly requested collection creation.
- Do not create temporary test collections during normal survey runs.
- Do not assume collection creation can be automatically rolled back; collection deletion is not available through the default Zotero MCP tool surface.

Never delete or overwrite:

- user-created notes
- annotations
- PDF attachments
- existing item metadata
- tags on existing library items outside the current survey import
- duplicates via merge/delete operations
- collections, unless the user explicitly approves creation

Default capture rule:

1. Capture the selected core papers, usually about `5`.
2. Search the library before importing each paper.
3. Avoid duplicate imports when DOI, arXiv ID, title, or stable URL already matches.
4. Prefer importing the paper with a real PDF attachment when available.
5. After import, inspect child items.
6. Delete low-value arXiv import notes when they only contain acceptance, homepage, or venue metadata.
7. Remove all tags from newly imported items.
8. Choose the best existing collection for the survey topic.
9. Add each newly imported core paper, and any already-existing core paper used by the survey, to that collection.
10. Organize papers by collections, not tags.
11. Preserve useful user-created notes, annotations, and PDF attachments.
12. Do not capture the full shortlist unless the user explicitly asks for full-batch import.

## Collection Placement

Use the existing collection tree as the classification system.

Default behavior:

- choose one primary target collection for the survey topic before importing
- prefer the most specific existing collection that matches the paper's role in the survey
- place both newly imported and already-existing core papers into the target collection
- do not create new collections unless the user asks, or no existing collection is reasonably suitable and the user approves the proposed collection name and parent
- if no suitable collection exists and collection creation is not approved, record `collection unresolved` in the final report instead of inventing a category

If Zotero MCP is unavailable, read $zotero-mcp-installation skill and help the user install, configure, or repair Zotero MCP before capture. If setup cannot be completed in the current run, record the unresolved capture status in the final report.
