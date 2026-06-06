---
name: zotero-paper-capture
description: Capture single papers or small batches of paper PDFs into Zotero with the user's library hygiene preferences. Use when the user asks to add, import, save, or put a paper, PDF, arXiv paper, DOI paper, or research article into Zotero outside a full literature survey. Dedupe first, import verified PDFs, remove import tags, delete low-value import notes, keep the PDF, and place papers into suitable existing collections.
---

# Zotero Paper Capture

## Scope

Use this skill for daily Zotero paper capture, especially single-paper or small-batch imports.

Do not use this for Zotero MCP installation or repair. If Zotero MCP is unavailable, report that capture is blocked and use the Zotero MCP installation workflow only when the user explicitly asks to repair setup.

## Defaults

- Organize papers by collections, not tags.
- Remove all tags from newly imported paper items.
- Delete low-value notes created by the import, such as arXiv metadata, acceptance notes, project links, homepage links, or venue-only comments.
- Keep PDF attachments.
- Preserve user-created notes, annotations, existing PDFs, existing metadata, and collection membership.
- Do not create new collections unless the user explicitly asks, or no existing collection fits and the user approves the proposed parent and name.

## Workflow

1. Dedupe before importing.
   - Search Zotero by DOI, arXiv ID, exact title, and stable URL when available.
   - If an exact item already exists, do not re-import. Place the existing item in the best collection instead.
   - Do not clean tags or notes from an existing item unless the user explicitly asks to normalize it.

2. Verify the local PDF before import.
   - Ensure the download command finished successfully.
   - Check the file is plausibly sized for a paper PDF.
   - Confirm the PDF has `%%EOF` and `startxref` markers when using shell checks.
   - Prefer a parser check with `pypdf` or another available PDF parser before `zotero_add_from_file`.

3. Import missing items from a verified local PDF.
   - Use `zotero_add_from_file` with an absolute local path.
   - Do not pass tags unless the tool requires them. If tags appear from recognizer metadata, remove them after import.

4. Inspect and clean the newly imported item.
   - Fetch metadata and child items.
   - Remove all tags from the new parent item.
   - Delete only low-value notes created by the import.
   - Keep the PDF attachment and any meaningful imported metadata.

5. Place the paper in collections.
   - Inspect existing collections and choose the most specific suitable collection.
   - If the best collection is ambiguous, ask the user to choose.
   - Add the item to the selected collection.

6. Report the result concisely.
   - Include the Zotero item key, title, whether tags were removed, whether notes were deleted, and the collection path or unresolved collection status.
