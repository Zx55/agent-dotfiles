import { registerEndpoints, unregisterEndpoints } from "./server";

async function startup(): Promise<void> {
  registerEndpoints();
  Zotero.debug("zotero-add-local-file-plugin started");
}

async function shutdown(): Promise<void> {
  unregisterEndpoints();
  Zotero.debug("zotero-add-local-file-plugin stopped");
}

export { startup, shutdown };

