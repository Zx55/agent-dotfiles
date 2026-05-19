# zotero-add-local-file-plugin

Minimal Zotero plugin for adding a local file as a Zotero stored attachment.

This exists because external Zotero Web API upload paths can create attachment
records that are not immediately readable from the local Zotero storage
directory. This plugin runs inside Zotero and uses Zotero's native API:

```js
Zotero.Attachments.importFromFile(...)
```

## Endpoints

The plugin registers endpoints on Zotero's built-in local server.

### `GET /zotero-add-local-file/ping`

Returns plugin and Zotero version information.

### `POST /zotero-add-local-file/add-from-file`

Requires:

```http
Authorization: Bearer <token>
Content-Type: application/json
```

Body:

```json
{
  "filePath": "/absolute/path/to/paper.pdf",
  "item": {
    "itemType": "preprint",
    "title": "Paper Title",
    "date": "2026-04-22",
    "url": "https://arxiv.org/abs/2604.20796",
    "extra": "arXiv:2604.20796"
  },
  "collectionKeys": ["KI5XJ48K"],
  "attachmentTitle": "paper.pdf"
}
```

## Token

Set the token in Zotero's Run JavaScript window:

```js
Zotero.Prefs.set("extensions.zoteroAddLocalFile.token", "replace-with-a-long-random-token", true);
return Zotero.Prefs.get("extensions.zoteroAddLocalFile.token", true);
```

`add-from-file` refuses requests until this token is configured.

## Build

```bash
npm install
npm run build
```

The XPI is written to `build/zotero-add-local-file-plugin.xpi`.

