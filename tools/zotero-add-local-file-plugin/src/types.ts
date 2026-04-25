export type ZoteroItemInput = {
  itemType?: string;
  title: string;
  date?: string;
  url?: string;
  DOI?: string;
  abstractNote?: string;
  extra?: string;
  archive?: string;
  archiveLocation?: string;
  creators?: unknown[];
  tags?: Array<{ tag: string }> | string[];
};

export type AddFromFileRequest = {
  filePath: string;
  item: ZoteroItemInput;
  collectionKeys?: string[];
  attachmentTitle?: string;
};

export type AddFromFileResponse = {
  ok: true;
  metadataSource: "zotero-recognizer" | "fallback";
  parentItemID: number;
  parentKey: string;
  attachmentItemID: number;
  attachmentKey: string;
  attachmentTitle: string;
  attachmentLinkMode: number;
  attachmentContentType: string;
  storedPath: string | null;
  storedExists: boolean;
};

export type ErrorResponse = {
  ok: false;
  error: string;
};
