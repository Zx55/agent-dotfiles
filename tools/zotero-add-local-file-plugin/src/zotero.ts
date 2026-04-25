import type { AddFromFileRequest, AddFromFileResponse, ZoteroItemInput } from "./types";

const FIELD_NAMES = [
  "title",
  "date",
  "url",
  "DOI",
  "abstractNote",
  "extra",
  "archive",
  "archiveLocation"
] as const;

function assertAbsolutePath(filePath: string): void {
  if (typeof filePath !== "string" || !filePath.startsWith("/")) {
    throw new Error("filePath must be an absolute POSIX path");
  }
}

async function assertFileExists(filePath: string): Promise<void> {
  if (!(await IOUtils.exists(filePath))) {
    throw new Error(`File does not exist: ${filePath}`);
  }
}

function normalizeItem(input: ZoteroItemInput, collectionKeys: string[]): Record<string, unknown> {
  if (!input || typeof input !== "object") {
    throw new Error("item is required");
  }
  if (typeof input.title !== "string" || !input.title.trim()) {
    throw new Error("item.title is required");
  }

  const itemType = input.itemType || "preprint";
  const data: Record<string, unknown> = { itemType };
  for (const field of FIELD_NAMES) {
    const value = input[field];
    if (typeof value === "string" && value.trim()) {
      data[field] = value;
    }
  }
  if (Array.isArray(input.creators)) {
    data.creators = input.creators;
  }
  if (Array.isArray(input.tags)) {
    const tags = input.tags
      .map(tag => {
        if (typeof tag === "string") {
          return tag.trim() ? { tag: tag.trim() } : null;
        }
        if (tag && typeof tag === "object" && typeof tag.tag === "string" && tag.tag.trim()) {
          return { tag: tag.tag.trim() };
        }
        return null;
      })
      .filter(Boolean);
    if (tags.length) {
      data.tags = tags;
    }
  }
  if (collectionKeys.length) {
    data.collections = collectionKeys;
  }
  return data;
}

async function getStoredPath(attachment: any): Promise<string | null> {
  if (typeof attachment.getFilePathAsync === "function") {
    return await attachment.getFilePathAsync();
  }
  if (typeof attachment.attachmentPath === "string") {
    return attachment.attachmentPath;
  }
  return null;
}

async function assertStoredAttachment(attachment: any): Promise<{ storedPath: string | null; storedExists: boolean }> {
  const storedPath = await getStoredPath(attachment);
  const storedExists = storedPath ? await IOUtils.exists(storedPath) : false;
  if (!storedExists) {
    throw new Error("Zotero reported an attachment, but the stored file is not readable");
  }
  return { storedPath, storedExists };
}

function getParentItemID(attachment: any): number | null {
  const parentItemID = attachment.parentItemID ?? attachment.parentID;
  return typeof parentItemID === "number" && parentItemID > 0 ? parentItemID : null;
}

async function buildResponse(
  parentItem: any,
  attachment: any,
  metadataSource: AddFromFileResponse["metadataSource"]
): Promise<AddFromFileResponse> {
  const { storedPath, storedExists } = await assertStoredAttachment(attachment);

  return {
    ok: true,
    metadataSource,
    parentItemID: parentItem.id,
    parentKey: parentItem.key,
    attachmentItemID: attachment.id,
    attachmentKey: attachment.key,
    attachmentTitle: attachment.getField("title"),
    attachmentLinkMode: attachment.attachmentLinkMode,
    attachmentContentType: attachment.attachmentContentType,
    storedPath,
    storedExists
  };
}

async function addTagsIfPresent(item: any, input: ZoteroItemInput): Promise<void> {
  if (!Array.isArray(input.tags) || typeof item.addTag !== "function") {
    return;
  }

  let changed = false;
  for (const tag of input.tags) {
    const tagName = typeof tag === "string" ? tag : tag?.tag;
    if (typeof tagName === "string" && tagName.trim()) {
      changed = item.addTag(tagName.trim()) || changed;
    }
  }
  if (changed) {
    await item.saveTx();
  }
}

async function createFallbackParent(
  request: AddFromFileRequest,
  collectionKeys: string[],
  existingAttachment?: any
): Promise<AddFromFileResponse> {
  const itemData = normalizeItem(request.item, collectionKeys);
  const item = new Zotero.Item(itemData.itemType);
  item.libraryID = Zotero.Libraries.userLibraryID;
  item.fromJSON(itemData);
  const parentItemID = await item.saveTx();
  const parentItem = await Zotero.Items.getAsync(parentItemID);

  if (existingAttachment) {
    existingAttachment.parentID = parentItemID;
    await existingAttachment.saveTx();
    return buildResponse(parentItem, existingAttachment, "fallback");
  }

  const attachment = await Zotero.Attachments.importFromFile({
    file: request.filePath,
    parentItemID,
    title: request.attachmentTitle || request.filePath.split("/").pop() || "Attachment"
  });

  return buildResponse(parentItem, attachment, "fallback");
}

async function recognizeImportedAttachment(
  request: AddFromFileRequest,
  collectionKeys: string[]
): Promise<AddFromFileResponse> {
  const attachment = await Zotero.Attachments.importFromFile({
    file: request.filePath,
    libraryID: Zotero.Libraries.userLibraryID,
    collections: collectionKeys.length ? collectionKeys : undefined
  });

  if (!Zotero.RecognizeDocument || typeof Zotero.RecognizeDocument.recognizeItems !== "function") {
    return createFallbackParent(request, collectionKeys, attachment);
  }
  if (
    typeof Zotero.RecognizeDocument.canRecognize === "function"
    && !Zotero.RecognizeDocument.canRecognize(attachment)
  ) {
    return createFallbackParent(request, collectionKeys, attachment);
  }

  try {
    await Zotero.RecognizeDocument.recognizeItems([attachment]);
  }
  catch (error) {
    Zotero.logError(error);
  }

  const updatedAttachment = await Zotero.Items.getAsync(attachment.id);
  const parentItemID = getParentItemID(updatedAttachment);
  if (!parentItemID) {
    return createFallbackParent(request, collectionKeys, updatedAttachment);
  }

  const parentItem = await Zotero.Items.getAsync(parentItemID);
  await addTagsIfPresent(parentItem, request.item);
  return buildResponse(parentItem, updatedAttachment, "zotero-recognizer");
}

export async function addFromFile(request: AddFromFileRequest): Promise<AddFromFileResponse> {
  if (!request || typeof request !== "object") {
    throw new Error("JSON body is required");
  }

  assertAbsolutePath(request.filePath);
  await assertFileExists(request.filePath);

  const collectionKeys = Array.isArray(request.collectionKeys)
    ? request.collectionKeys.filter(key => typeof key === "string" && key.trim())
    : [];

  return recognizeImportedAttachment(request, collectionKeys);
}
