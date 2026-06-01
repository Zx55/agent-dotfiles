import { addFromFile } from "./zotero";
import { configuredToken, ENDPOINT_PREFIX, errorResponse, isAuthorized, jsonResponse, TOKEN_PREF } from "./http";
import type { AddFromFileRequest } from "./types";

type EndpointResult = [number, Record<string, string>, string];
type EndpointRequest = {
  method: "GET" | "POST";
  pathname: string;
  headers: Record<string, string | undefined>;
  data?: unknown;
};

const registeredPaths = [
  `${ENDPOINT_PREFIX}/ping`,
  `${ENDPOINT_PREFIX}/add-from-file`
];

function registerEndpoint(path: string, handler: (request: EndpointRequest) => Promise<EndpointResult> | EndpointResult): void {
  Zotero.Server.Endpoints[path] = function Endpoint() {};
  Zotero.Server.Endpoints[path].prototype = {
    supportedMethods: ["GET", "POST"],
    supportedDataTypes: ["application/json"],
    init(request: EndpointRequest) {
      return handler(request);
    }
  };
}

async function addFromFileHandler(request: EndpointRequest): Promise<EndpointResult> {
  if (request.method !== "POST") {
    return errorResponse(405, "Use POST");
  }
  if (!configuredToken()) {
    return errorResponse(403, `Token is not configured. Set ${TOKEN_PREF} in Zotero preferences.`);
  }
  if (!isAuthorized(request.headers)) {
    return errorResponse(401, "Missing or invalid bearer token");
  }
  try {
    const result = await addFromFile(request.data as AddFromFileRequest);
    return jsonResponse(200, result);
  }
  catch (error) {
    Zotero.debug(error);
    return errorResponse(400, error instanceof Error ? error.message : String(error));
  }
}

function pingHandler(): EndpointResult {
  return jsonResponse(200, {
    ok: true,
    plugin: "zotero-add-local-file-plugin",
    version: "0.1.1",
    features: {
      recognizeImportedFiles: true,
      addFromFileMetadataSource: true
    },
    zoteroVersion: Zotero.version,
    tokenConfigured: Boolean(configuredToken()),
    endpoints: registeredPaths
  });
}

export function registerEndpoints(): void {
  registerEndpoint(`${ENDPOINT_PREFIX}/ping`, pingHandler);
  registerEndpoint(`${ENDPOINT_PREFIX}/add-from-file`, addFromFileHandler);
}

export function unregisterEndpoints(): void {
  for (const path of registeredPaths) {
    delete Zotero.Server.Endpoints[path];
  }
}
