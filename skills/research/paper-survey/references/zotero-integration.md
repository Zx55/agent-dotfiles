# Zotero Integration

Zotero capture is default for selected core papers in this skill.

Use Zotero for four narrow jobs:

- **Dedupe:** check whether selected core papers already exist.
- **Import:** add missing core papers from verified local PDFs.
- **Clean:** remove import noise from newly imported items only.
- **Place:** add all core papers to the chosen Zotero collection.

Keep responsibilities clear:

- `paper-survey` owns search strategy, reading strategy, and synthesis
- Zotero MCP owns library operations

## Tool Selection

Zotero MCP exposes many tools. For this skill, use a narrow default tool surface.

Default allowed tools:

- `zotero_search_items` for dedupe by title, DOI, arXiv ID, or stable URL
- `zotero_add_from_file` for default imports after downloading the paper PDF locally
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

## Default Capture Flow

Use this as a staged checklist. Do not collapse the stages; the PDF gate is what prevents broken Zotero imports.

### 1. Scope

- Capture only the selected core papers, usually about `5`.
- Do not capture the full shortlist unless the user explicitly asks for full-batch import.

### 2. Dedupe

- Search the library before importing each paper.
- Treat DOI, arXiv ID, exact title, and stable URL as duplicate signals.
- If an item already exists, preserve it and use collection placement instead of re-importing.

### 3. Local PDF Import

- For missing items, download the source PDF locally first, preferably under the survey workspace.
- Verify the local PDF with the `PDF Download Completion Gate` below.
- Import only verified PDFs with `zotero_add_from_file`.

### 4. Post-Import Inspection And Cleanup

- Inspect child items after import.
- Delete only low-value notes created by the import, such as arXiv acceptance, homepage, project page, or venue-only comments.
- Remove imported tags from newly imported items.
- Preserve user-created notes, annotations, existing PDFs, and existing metadata.

### 5. Collection Placement

- Choose the best existing collection for the survey topic.
- Add newly imported core papers and already-existing core papers to that collection.
- Organize papers by collections, not tags.
- Record collection path, key, and per-paper placement in the final report.

## PDF Download Completion Gate

Do not rely on a terminal progress display or `file <paper.pdf>` alone. A truncated PDF can still have a valid header and metadata.

Before `zotero_add_from_file`, require all checks in this table:

| Check | Command / Signal | Why It Matters |
| --- | --- | --- |
| Download finished | the download command has exited successfully | prevents importing a still-growing file |
| Size plausible | when HTTP `Content-Length` is available, compare it with `stat -f%z <paper.pdf>` on macOS | catches truncated network downloads |
| EOF marker present | `grep -a "%%EOF" <paper.pdf>` | catches PDFs that only have a valid header/metadata |
| Xref marker present | `grep -a "startxref" <paper.pdf>` | catches incomplete PDF object tables |
| Parser opens file | use `pypdf` check below | catches subtle corruption before Zotero import |

```bash
python3 - <<'PY'
from pathlib import Path
from pypdf import PdfReader
p = Path("<paper.pdf>")
r = PdfReader(str(p), strict=True)
print(len(r.pages))
PY
```

If any check fails:

- keep waiting if the download process is still running
- retry the download if the process exited but the PDF is incomplete
- use the user's proxy rule from the global instructions when the network appears stalled or repeatedly incomplete
- record unresolved capture status instead of importing a broken PDF

## Collection Placement

Use the existing collection tree as the classification system.

Default behavior:

- choose one primary target collection for the survey topic before importing
- prefer the most specific existing collection that matches the paper's role in the survey
- place both newly imported and already-existing core papers into the target collection
- record the full collection path in the final report, such as `A -> B -> C`, along with the target collection key
- record per-paper placement when core papers are placed into different collections
- do not create new collections unless the user asks, or no existing collection is reasonably suitable and the user approves the proposed collection name and parent
- if no suitable collection exists and collection creation is not approved, record `collection unresolved` in the final report instead of inventing a category

If Zotero MCP is unavailable, read $zotero-mcp-installation skill and help the user install, configure, or repair Zotero MCP before capture. If setup cannot be completed in the current run, record the unresolved capture status in the final report.
